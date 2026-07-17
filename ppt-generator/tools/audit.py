#!/usr/bin/env python3
"""生成后硬闸口。P0 不过，不许交付。

检查项的来源都是真实翻车记录（2026-07，一份 42 页 deck）：

  溢出       v1 有 3 处文字超框（第5张超 138pt）—— 无度量、盲拼坐标
  对比度     v1 全部 8 张章节页红压红 #FF2442 on #CC0000 = 1.3:1
             v2 原型又复发一次：标签 4.27:1、弱化文字 4.47:1
  红色占比   v1 大红色块满天飞
  版式雷同   v1 连续多张同版式，montage 一看就是「一堆灰块」
  字体存在   v1 声明 Microsoft YaHei，而 mac 上没有 —— 带病文件
  默认阴影   v1 每个形状继承主题投影，糊一圈灰边

特别注意两类「几何上完全正常」的问题：对比度不足、红色超标。
它们不溢出、不重叠、不越界 —— 纯几何检测（overflow test）会全部放行。
这正是本 audit 与通用 overflow 检查的区别。

用法：
    python3 audit.py deck.pptx           # 人类可读
    python3 audit.py deck.pptx --json
    python3 audit.py deck.pptx --layout  # 顺带导出 layout JSON
"""

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.util import Emu

import measure as M
from design import T

EMU_IN = 914400.0


# ── 对比度 ────────────────────────────────────────────────────

def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def _rgb(color_obj):
    try:
        v = color_obj.rgb
        return (v[0], v[1], v[2]) if not isinstance(v, str) else (
            int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    except Exception:
        return None


def _shape_fill_rgb(sh):
    try:
        if sh.fill.type is not None and sh.fill.type == 1:  # solid
            return _rgb(sh.fill.fore_color)
    except Exception:
        pass
    return None


# ── 几何 ──────────────────────────────────────────────────────

def _box(sh):
    return (sh.left / EMU_IN, sh.top / EMU_IN,
            sh.width / EMU_IN, sh.height / EMU_IN)


def _overlap_area(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ox = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    oy = max(0, min(ay + ah, by + bh) - max(ay, by))
    return ox * oy


def layout_json(prs):
    """导出每页每个形状的位置尺寸 —— 供几何检测与人工排查。"""
    out = []
    for i, s in enumerate(prs.slides, 1):
        shapes = []
        for sh in s.shapes:
            x, y, w, h = _box(sh)
            shapes.append({
                "type": str(sh.shape_type).split()[0],
                "x": round(x, 3), "y": round(y, 3),
                "w": round(w, 3), "h": round(h, 3),
                "text": (sh.text_frame.text[:40] if sh.has_text_frame else ""),
            })
        out.append({"page": i, "shapes": shapes})
    return out


# ── 检查项 ────────────────────────────────────────────────────

def check_overflow(prs):
    """文字是否超出自己的文本框 —— 用真实字体度量。"""
    bad = []
    for i, s in enumerate(prs.slides, 1):
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            txt = sh.text_frame.text
            if not txt.strip():
                continue
            sizes = [r.font.size.pt for p in sh.text_frame.paragraphs
                     for r in p.runs if r.font.size]
            if not sizes:
                continue
            size = max(sizes)
            # 必须读【实际】行距。写死 1.45 会把用 1.28 行距的封面标题误判成溢出。
            lss = [p.line_spacing for p in sh.text_frame.paragraphs
                   if isinstance(p.line_spacing, (int, float))]
            ls = max(lss) if lss else T["lh"]
            x, y, w, h = _box(sh)
            need = M.height_in(txt, size, w, ls)
            if need > h + 0.02:
                bad.append({"page": i, "over_in": round(need - h, 3),
                            "size": size, "text": txt[:30].replace("\n", "⏎")})
    return bad


def check_out_of_canvas(prs):
    """元素是否跑出画布。

    装饰形状出血（如封面故意超出边界的圆）是设计手法，不是 bug —— 不报。
    只有【承载文字的框】跑出画布才是真问题：字会被裁掉。
    完全在画布外的形状也报（那多半是算错了坐标）。
    """
    pw, ph = prs.slide_width / EMU_IN, prs.slide_height / EMU_IN
    bad = []
    for i, s in enumerate(prs.slides, 1):
        for sh in s.shapes:
            x, y, w, h = _box(sh)
            has_text = sh.has_text_frame and sh.text_frame.text.strip()
            outside = (x < -0.02 or y < -0.02 or
                       x + w > pw + 0.02 or y + h > ph + 0.02)
            if not outside:
                continue
            if has_text:
                bad.append({"page": i, "box": [round(v, 2) for v in (x, y, w, h)],
                            "text": sh.text_frame.text[:24].replace("\n", "⏎")})
            elif x + w <= 0 or y + h <= 0 or x >= pw or y >= ph:
                bad.append({"page": i, "box": [round(v, 2) for v in (x, y, w, h)],
                            "text": f"[完全在画布外] {str(sh.shape_type).split()[0]}"})
    return bad


def check_overlap(prs, min_ratio=0.35):
    """文本框之间是否明显重叠（形状可以互相叠，文字不该叠文字）。"""
    bad = []
    for i, s in enumerate(prs.slides, 1):
        tbs = [sh for sh in s.shapes
               if sh.has_text_frame and sh.text_frame.text.strip()]
        for a in range(len(tbs)):
            for b in range(a + 1, len(tbs)):
                ba, bb = _box(tbs[a]), _box(tbs[b])
                ov = _overlap_area(ba, bb)
                small = min(ba[2] * ba[3], bb[2] * bb[3])
                if small > 0 and ov / small > min_ratio:
                    bad.append({
                        "page": i, "ratio": round(ov / small, 2),
                        "a": tbs[a].text_frame.text[:18].replace("\n", "⏎"),
                        "b": tbs[b].text_frame.text[:18].replace("\n", "⏎")})
    return bad


def check_contrast(prs):
    """文字与其背后色块的对比度。几何检测抓不到的一类问题。"""
    bad = []
    for i, s in enumerate(prs.slides, 1):
        # 收集本页所有实心色块，按面积从小到大（小块在上，优先作为背景）
        fills = []
        for sh in s.shapes:
            c = _shape_fill_rgb(sh)
            if c:
                x, y, w, h = _box(sh)
                fills.append((x, y, w, h, c))
        page_bg = (255, 255, 255)
        try:
            f = s.background.fill
            if f.type == 1:
                page_bg = _rgb(f.fore_color) or page_bg
        except Exception:
            pass

        for sh in s.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            tx, ty, tw, th = _box(sh)
            cx, cy = tx + tw / 2, ty + th / 2
            bg = page_bg
            best = None
            for (x, y, w, h, c) in fills:
                if x <= cx <= x + w and y <= cy <= y + h:
                    a = w * h
                    if best is None or a < best:
                        best, bg = a, c
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if not r.text.strip():
                        continue
                    fg = _rgb(r.font.color)
                    if not fg:
                        continue
                    size = r.font.size.pt if r.font.size else T["fs_body"]
                    need = (T["MIN_CONTRAST_LG"]
                            if (size >= 18 and r.font.bold) or size >= 24
                            else T["MIN_CONTRAST"])
                    cr = contrast(fg, bg)
                    if cr < need:
                        bad.append({
                            "page": i, "ratio": round(cr, 2), "need": need,
                            "fg": "#%02X%02X%02X" % fg, "bg": "#%02X%02X%02X" % bg,
                            "size": size, "text": r.text[:24]})
                        break
    return bad


def check_red_area(prs):
    """红色面积占比。设计简报说『红色只做锚点』—— 这是它的可执行形式。"""
    pw, ph = prs.slide_width / EMU_IN, prs.slide_height / EMU_IN
    page_area = pw * ph
    reds = []
    for key in ("brand", "brand_dark"):
        h = T[key]
        reds.append((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))

    def is_red(c):
        r, g, b = c
        return r > 120 and r > g * 2.2 and r > b * 2.2

    bad = []
    for i, s in enumerate(prs.slides, 1):
        area = 0.0
        for sh in s.shapes:
            c = _shape_fill_rgb(sh)
            if c and is_red(c):
                _, _, w, h = _box(sh)
                area += w * h
        ratio = area / page_area
        if ratio > T["RED_MAX_AREA"]:
            bad.append({"page": i, "ratio": round(ratio, 3),
                        "limit": T["RED_MAX_AREA"]})
    return bad


def check_font_exists(prs):
    """声明的字体在本机是否存在 —— v1 声明微软雅黑，mac 上没有，是带病文件。"""
    import glob
    names = Counter()
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if r.text.strip() and r.font.name:
                            names[r.font.name] += 1
    installed = set()
    for d in ("/System/Library/Fonts", "/Library/Fonts",
              os.path.expanduser("~/Library/Fonts"), "/usr/share/fonts",
              "C:/Windows/Fonts"):
        for f in glob.glob(os.path.join(d, "**", "*"), recursive=True):
            installed.add(os.path.basename(f).split(".")[0].lower())
    missing = []
    for n, cnt in names.items():
        key = n.lower().replace(" ", "")
        if not any(key in i.replace(" ", "") or i.replace(" ", "") in key
                   for i in installed if i):
            missing.append({"font": n, "runs": cnt})
    return missing


def check_rhythm(prs):
    """连续同版式 —— montage 上「一堆一模一样的灰块」就是这么来的。

    按形状构成指纹判断，不依赖调用方申报类型。
    """
    sigs = []
    for s in prs.slides:
        c = Counter(str(sh.shape_type).split()[0] for sh in s.shapes)
        sigs.append(tuple(sorted(c.items())))
    bad, run, start = [], 1, 0
    for i in range(1, len(sigs)):
        if sigs[i] == sigs[i - 1]:
            run += 1
        else:
            if run > T["MAX_SAME_LAYOUT"]:
                bad.append({"from": start + 1, "to": i, "count": run})
            run, start = 1, i
    if run > T["MAX_SAME_LAYOUT"]:
        bad.append({"from": start + 1, "to": len(sigs), "count": run})
    return bad


def check_shadow(prs):
    """是否有【带填充的】形状继承了主题默认阴影 —— v1 「廉价感」的一大来源。

    无填充的 textbox 即使 inherit=True 也看不出阴影，报了是噪音。
    """
    n = 0
    for s in prs.slides:
        for sh in s.shapes:
            if _shape_fill_rgb(sh) is None:
                continue
            try:
                if sh.shadow.inherit:
                    n += 1
            except Exception:
                pass
    return n


# ── 汇总 ──────────────────────────────────────────────────────

def run(path):
    prs = Presentation(path)
    return {
        "pages": len(prs.slides),
        "exact_metrics": M.is_exact(),
        "P0": {
            "overflow": check_overflow(prs),
            "out_of_canvas": check_out_of_canvas(prs),
            "contrast": check_contrast(prs),
        },
        "P1": {
            "overlap": check_overlap(prs),
            "red_area": check_red_area(prs),
            "font_missing": check_font_exists(prs),
        },
        "P2": {
            "rhythm": check_rhythm(prs),
            "inherited_shadow": check_shadow(prs),
        },
    }


def report(r):
    L = []
    A = L.append
    A("═" * 62)
    A(f"  audit · {r['pages']} 页" +
      ("" if r["exact_metrics"] else "  ⚠️ 度量为估算模式，溢出结论仅供参考"))
    A("═" * 62)

    p0 = r["P0"]
    n0 = sum(len(v) for v in p0.values())
    A("")
    A(f"【P0】不过不许交付 —— {'✅ 全部通过' if n0 == 0 else f'❌ {n0} 项'}")
    for x in p0["overflow"][:8]:
        A(f"  ❌ 溢出  第{x['page']}页 超 {x['over_in']}in ({x['size']}pt) 「{x['text']}」")
    for x in p0["out_of_canvas"][:8]:
        A(f"  ❌ 越界  第{x['page']}页 {x['box']} 「{x['text']}」")
    for x in p0["contrast"][:8]:
        A(f"  ❌ 对比度 第{x['page']}页 {x['ratio']}:1 < {x['need']} "
          f"({x['fg']} on {x['bg']}, {x['size']}pt) 「{x['text']}」")

    p1 = r["P1"]
    n1 = sum(len(v) for v in p1.values())
    A("")
    A(f"【P1】应修 —— {'✅ 通过' if n1 == 0 else f'⚠️ {n1} 项'}")
    for x in p1["overlap"][:5]:
        A(f"  ⚠️ 重叠  第{x['page']}页 {int(x['ratio']*100)}% 「{x['a']}」×「{x['b']}」")
    for x in p1["red_area"][:5]:
        A(f"  ⚠️ 红色超标 第{x['page']}页 {int(x['ratio']*100)}% > {int(x['limit']*100)}%")
    for x in p1["font_missing"][:5]:
        A(f"  ⚠️ 字体 「{x['font']}」本机未安装（{x['runs']} 处）")
        A(f"     · 若分发对象装有此字体（如 Windows + 微软雅黑）→ 正常，仅本机预览会替换")
        A(f"     · 若分发对象也没有 → 换成对方有的字体，否则排版会跑掉")

    p2 = r["P2"]
    A("")
    A("【P2】建议")
    for x in p2["rhythm"]:
        A(f"  · 版式雷同 第{x['from']}-{x['to']}页 连续 {x['count']} 张同构")
    if p2["inherited_shadow"]:
        A(f"  · {p2['inherited_shadow']} 个形状继承了主题默认阴影（应显式关闭）")
    if not p2["rhythm"] and not p2["inherited_shadow"]:
        A("  ✅ 通过")

    A("")
    A("═" * 62)
    A("  ⛔ P0 未通过，禁止输出" if n0 else "  ✅ 可以交付")
    A("═" * 62)
    return "\n".join(L), n0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法: python3 audit.py deck.pptx [--json] [--layout]")
    path = sys.argv[1]
    res = run(path)
    if "--layout" in sys.argv:
        lj = os.path.splitext(path)[0] + ".layout.json"
        with open(lj, "w") as f:
            json.dump(layout_json(Presentation(path)), f,
                      ensure_ascii=False, indent=1)
        print(f"layout JSON -> {lj}")
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0)
    text, n0 = report(res)
    print(text)
    sys.exit(1 if n0 else 0)
