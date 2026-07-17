#!/usr/bin/env python3
"""版式组件库。

规则：
  1. 一律通过 design.py 的原语绘图，不直接 add_shape —— 否则默认阴影/直角会长回来
  2. 所有容器高度按 measure 度量的内容算，不撑满栅格 —— 否则要么溢出要么大片死空白
  3. 红色只出现在：图标、编号徽章、标签、短线、底部品牌线、关键数字
  4. 红色文字一律 brand_text，不用 brand（对比度不够）
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

import design as D
import measure as M
from design import T

PAD = 0.2
GAP = D.snap(0.22)


def _content_box(y0):
    return (T["margin_x"], y0,
            T["page_w"] - 2 * T["margin_x"],
            T["page_h"] - y0 - T["margin_bottom"])


def _new(prs, bg="canvas_alt"):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    D.set_bg(s, bg)
    return s


# ══════════════════════════════════════════════════════════════

def cover(spec, prs):
    """封面：明亮通透，红只做锚点。不是一整块红。"""
    s = _new(prs, "canvas")
    # 右栏：浅灰块 + 红竖线。栏内放要点，让它承载信息而不是当空装饰。
    RX = 8.13
    D.rect(s, RX, 0, T["page_w"] - RX, T["page_h"], fill="canvas_alt")
    D.rect(s, RX, 0, 0.035, T["page_h"], fill="brand")
    pts = spec.get("points") or []
    if pts:
        iw = T["page_w"] - RX - 0.95
        hs = [M.height_in(p, 10.5, iw - 0.4) for p in pts[:6]]
        iy = max((T["page_h"] - (sum(hs) + 0.34 * (len(pts[:6]) - 1))) / 2, 0.6)
        for k, p in enumerate(pts[:6]):
            D.text(s, f"{k+1:02d}", RX + 0.42, iy - 0.02, 0.34, 0.2, size=9,
                   color="brand_text", bold=True)
            D.text(s, p, RX + 0.86, iy, iw - 0.4, hs[k], size=10.5, color="ink_body")
            iy += hs[k] + 0.34
    elif spec.get("icon"):
        D.icon(s, spec["icon"], RX + (T["page_w"] - RX) / 2 - 0.45, 3.0, 0.9, "red")

    x = T["margin_x"]
    if spec.get("tag"):
        D.tag(s, spec["tag"], x, 1.5, h=0.26, size=9.5)
    ttl = spec["title"]
    th = M.height_in(ttl, T["fs_cover"], 7.6, 1.28)
    D.text(s, ttl, x, 2.05, 7.6, th, size=T["fs_cover"], color="ink",
           bold=True, line_spacing=1.28)
    D.rule(s, x, 2.05 + th + 0.28, 0.62, thick=0.042)
    if spec.get("subtitle"):
        D.text(s, spec["subtitle"], x, 2.05 + th + 0.55, 7.4, 0.9,
               size=13.5, color="ink_muted")
    if spec.get("meta"):
        D.text(s, spec["meta"], x, T["page_h"] - 0.95, 7.4, 0.3,
               size=9, color="ink_muted")
    D.brandline(s)
    return s


def section(spec, prs):
    """章节页：浅灰底 + 深灰大字 + 红数字。取代 v1 的整页红底（红压红 1.56:1）。"""
    s = _new(prs, "canvas_alt")
    x = T["margin_x"]
    num = spec.get("number", "")
    if num:
        # 大号红数字：红色文字不计入填充面积，是「锚点」的正确用法
        D.text(s, num, 9.4, 1.5, 3.3, 3.2, size=150, color="brand_text",
               bold=True, align=PP_ALIGN.RIGHT)
    if spec.get("kicker"):
        D.text(s, spec["kicker"], x, 2.55, 7.5, 0.24, size=T["fs_small"],
               color="brand_text", bold=True)
    ttl = spec["title"]
    th = M.height_in(ttl, T["fs_section"], 7.8, 1.3)
    D.text(s, ttl, x, 2.95, 7.8, th, size=T["fs_section"], color="ink",
           bold=True, line_spacing=1.3)
    D.rule(s, x, 2.95 + th + 0.22, 0.55, thick=0.04)
    if spec.get("subtitle"):
        D.text(s, spec["subtitle"], x, 2.95 + th + 0.45, 7.6,
               M.height_in(spec["subtitle"], 12.5, 7.6),
               size=12.5, color="ink_muted")
    D.brandline(s)
    return s


def grid(spec, prs):
    """卡片网格。卡高按内容度量，行内等高，整块纵向居中。"""
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    items = spec["items"][:6]
    n = len(items)
    # 列数要让最后一行填满，否则会留洞。
    # 3 项按 2 列 = 2+1，右下角空一格（v2 实测，很扎眼）。
    cols = spec.get("cols") or (n if n <= 3 else (3 if n > 4 else 2))
    cw = (aw - GAP * (cols - 1)) / cols
    tw = cw - 2 * PAD

    def h_of(it):
        h = PAD + 0.24 + 0.16
        h += M.height_in(it["label"], T["fs_card_title"], tw) + 0.1
        h += M.height_in(it.get("desc", ""), T["fs_body"], tw) + PAD
        if it.get("std"):
            h += 0.14 + 0.008 + 0.14 + _std_h(it["std"], tw)
        return h

    rows = [items[i:i + cols] for i in range(0, len(items), cols)]
    rh = [max(h_of(i) for i in r) for r in rows]
    top = y0 + max((ah - (sum(rh) + GAP * (len(rows) - 1))) / 2, 0)

    cy = top
    for ri, row in enumerate(rows):
        for ci, it in enumerate(row):
            _card_item(s, it, x0 + ci * (cw + GAP), cy, cw, rh[ri], tw)
        cy += rh[ri] + GAP
    D.brandline(s)
    return s


def _std_h(std, tw):
    return 0.1 + 0.16 + M.height_in(std, T["fs_small"], tw - 0.24) + 0.12


def _card_item(s, it, cx, cy, cw, ch, tw):
    D.card(s, cx, cy, cw, ch, radius=T["radius_lg"])
    ix, iy = cx + PAD, cy + PAD
    if it.get("icon"):
        D.icon(s, it["icon"], ix, iy, 0.24, "red")
    if it.get("tag"):
        D.tag(s, it["tag"], ix + (0.34 if it.get("icon") else 0), iy + 0.015, h=0.21)
    ty = iy + 0.24 + 0.16
    lh = M.height_in(it["label"], T["fs_card_title"], tw)
    D.text(s, it["label"], ix, ty, tw, lh, size=T["fs_card_title"],
           color="ink", bold=True)
    by = ty + lh + 0.1
    if it.get("desc"):
        dh = M.height_in(it["desc"], T["fs_body"], tw)
        D.text(s, it["desc"], ix, by, tw, dh, size=T["fs_body"], color="ink_body")
        by += dh
    if it.get("std"):
        ly = by + 0.14
        D.rect(s, ix, ly, tw, 0.008, fill="border")
        sy = ly + 0.008 + 0.14
        sh = _std_h(it["std"], tw)
        D.card(s, ix, sy, tw, sh, fill="canvas_alt", line=None, radius=T["radius_sm"])
        D.text(s, "完成标准", ix + 0.12, sy + 0.1, 0.7, 0.14, size=7.5,
               color="brand_text", bold=True)
        D.text(s, it["std"], ix + 0.12, sy + 0.26, tw - 0.24,
               M.height_in(it["std"], T["fs_small"], tw - 0.24),
               size=T["fs_small"], color="ink_muted")


def numbered_list(spec, prs):
    """编号列表：白卡 + 红圆徽章。取代 v1 那条 1.1in 宽的实心红块。"""
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    items = spec["items"][:5]
    tw = aw - 1.0 - PAD

    def h_of(it):
        h = PAD + M.height_in(it["title"], T["fs_card_title"], tw) + 0.08
        h += M.height_in(it["desc"], T["fs_body"], tw) + PAD
        return max(h, 0.72)

    hs = [h_of(i) for i in items]
    g = D.snap(0.15)
    top = y0 + max((ah - (sum(hs) + g * (len(items) - 1))) / 2, 0)
    cy = top
    for i, it in enumerate(items):
        h = hs[i]
        D.card(s, x0, cy, aw, h)
        D.badge(s, f"{i+1:02d}", x0 + 0.28, cy + h / 2 - 0.17, d=0.34)
        tx = x0 + 0.82
        D.text(s, it["title"], tx, cy + PAD,
               tw, M.height_in(it["title"], T["fs_card_title"], tw),
               size=T["fs_card_title"], color="ink", bold=True)
        D.text(s, it["desc"], tx,
               cy + PAD + M.height_in(it["title"], T["fs_card_title"], tw) + 0.08,
               tw, M.height_in(it["desc"], T["fs_body"], tw),
               size=T["fs_body"], color="ink_body")
        cy += h + g
    D.brandline(s)
    return s


def bullets(spec, prs):
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    items = spec["bullets"][:6]
    tw = aw - 0.9 - PAD
    hs = [max(M.height_in(b, T["fs_body"], tw) + 2 * PAD, 0.6) for b in items]
    g = D.snap(0.12)
    cy = y0 + max((ah - (sum(hs) + g * (len(items) - 1))) / 2, 0)
    for i, b in enumerate(items):
        D.card(s, x0, cy, aw, hs[i])
        D.badge(s, i + 1, x0 + 0.24, cy + hs[i] / 2 - 0.14, d=0.28)
        D.text(s, b, x0 + 0.72, cy + PAD, tw,
               M.height_in(b, T["fs_body"], tw), size=T["fs_body"],
               color="ink_body")
        cy += hs[i] + g
    if spec.get("source"):
        D.text(s, spec["source"], x0, T["page_h"] - 0.42, aw, 0.2,
               size=8, color="ink_muted", italic=True)
    D.brandline(s)
    return s


def two_column(spec, prs):
    """双栏对比。左栏红头（小面积填充），右栏深灰头。"""
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    cw = (aw - GAP) / 2
    tw = cw - 2 * PAD - 0.42

    cols = [("left", spec.get("left_title", ""), spec.get("left_points", []), "brand"),
            ("right", spec.get("right_title", ""), spec.get("right_points", []), "ink")]
    for ci, (_, htitle, pts, hc) in enumerate(cols):
        cx = x0 + ci * (cw + GAP)
        hs = [max(M.height_in(p, T["fs_body"], tw) + 0.26, 0.5) for p in pts[:6]]
        total = 0.46 + 0.14 + sum(hs) + 0.1 * (len(hs) - 1) + PAD
        D.card(s, cx, y0, cw, min(total, ah), radius=T["radius_lg"])
        D.card(s, cx, y0, cw, 0.46, fill=hc, line=None, radius=T["radius_lg"])
        D.rect(s, cx, y0 + 0.32, cw, 0.14, fill=hc)
        D.text(s, htitle, cx + PAD, y0, cw - 2 * PAD, 0.46, size=11.5,
               color=D.readable_on(hc), bold=True,
               anchor=MSO_ANCHOR.MIDDLE)
        iy = y0 + 0.46 + 0.14
        for j, p in enumerate(pts[:6]):
            D.badge(s, j + 1, cx + PAD, iy + 0.04, d=0.24,
                    fill="brand" if ci == 0 else "ink")
            D.text(s, p, cx + PAD + 0.36, iy, tw,
                   M.height_in(p, T["fs_body"], tw), size=T["fs_body"],
                   color="ink_body")
            iy += hs[j] + 0.1
    D.brandline(s)
    return s


def process(spec, prs):
    """流程：白卡 + 红徽章 + 箭头图标。"""
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    steps = spec["steps"][:5]
    n = len(steps)
    arrow = 0.3
    cw = (aw - arrow * (n - 1)) / n
    tw = cw - 2 * PAD
    hs = []
    for st in steps:
        h = PAD + 0.34 + 0.14 + M.height_in(st["label"], T["fs_card_title"], tw) + 0.08
        h += M.height_in(st.get("desc", ""), T["fs_body"], tw) + PAD
        hs.append(h)
    ch = max(hs)
    top = y0 + max((ah - ch) / 2, 0)
    for i, st in enumerate(steps):
        cx = x0 + i * (cw + arrow)
        D.card(s, cx, top, cw, ch, radius=T["radius_lg"])
        D.badge(s, f"{i+1:02d}", cx + PAD, top + PAD, d=0.34)
        ty = top + PAD + 0.34 + 0.14
        lh = M.height_in(st["label"], T["fs_card_title"], tw)
        D.text(s, st["label"], cx + PAD, ty, tw, lh, size=T["fs_card_title"],
               color="ink", bold=True)
        if st.get("desc"):
            D.text(s, st["desc"], cx + PAD, ty + lh + 0.08, tw,
                   M.height_in(st["desc"], T["fs_body"], tw),
                   size=T["fs_body"], color="ink_body")
        if i < n - 1:
            D.icon(s, "chevrons-right", cx + cw + 0.05, top + ch / 2 - 0.1, 0.2, "red")
    D.brandline(s)
    return s


def stats(spec, prs):
    """大数字。红色数字 = 设计简报里的『数据强调』。"""
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    items = spec["stats"][:4]
    n = len(items)
    cw = (aw - GAP * (n - 1)) / n
    ch = min(2.6, ah)
    top = y0 + max((ah - ch) / 2, 0)
    for i, it in enumerate(items):
        cx = x0 + i * (cw + GAP)
        D.card(s, cx, top, cw, ch, radius=T["radius_lg"])
        D.rect(s, cx + cw / 2 - 0.22, top + 0.34, 0.44, 0.035, fill="brand")
        D.text(s, f"{it['num']}{it.get('unit','')}", cx, top + 0.6, cw, 1.0,
               size=52, color="brand_text", bold=True, align=PP_ALIGN.CENTER,
               line_spacing=1.0)
        D.text(s, it["label"], cx + 0.15, top + 1.62, cw - 0.3, 0.3,
               size=12, color="ink", bold=True, align=PP_ALIGN.CENTER)
        if it.get("desc"):
            D.text(s, it["desc"], cx + 0.18, top + 1.98, cw - 0.36,
                   M.height_in(it["desc"], T["fs_small"], cw - 0.36),
                   size=T["fs_small"], color="ink_muted", align=PP_ALIGN.CENTER)
    D.brandline(s)
    return s


def timeline(spec, prs):
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    items = spec["items"][:6]
    line_x = x0 + 1.55
    cx = line_x + 0.38
    cw = aw - (cx - x0)
    tw = cw - 2 * PAD

    def tag_w(it):
        return (M.text_width_pt(it["tag"], 8) / 72 + 0.2) if it.get("tag") else 0

    def h_of(it):
        # 标题让出标签的宽度，否则标签会压在标题上（v2 实测重叠 89%）
        ttw = tw - (tag_w(it) + 0.14 if it.get("tag") else 0)
        h = PAD + M.height_in(it["title"], T["fs_card_title"], ttw) + 0.06
        h += M.height_in(it.get("desc", ""), T["fs_body"], tw) + PAD
        return max(h, 0.6)

    hs = [h_of(i) for i in items]
    g = D.snap(0.12)
    total = sum(hs) + g * (len(items) - 1)
    top = y0 + max((ah - total) / 2, 0)
    D.rect(s, line_x, top + 0.2, 0.014, total - 0.4, fill="border")
    cy = top
    for i, it in enumerate(items):
        D.text(s, it["date"], x0, cy + 0.16, 1.35, 0.24, size=10,
               color="brand_text", bold=True, align=PP_ALIGN.RIGHT)
        D.oval(s, line_x - 0.055, cy + 0.19, 0.125, 0.125, fill="brand")
        D.card(s, cx, cy, cw, hs[i])
        twg = tag_w(it)
        ttw = tw - (twg + 0.14 if twg else 0)
        lh = M.height_in(it["title"], T["fs_card_title"], ttw)
        D.text(s, it["title"], cx + PAD, cy + PAD, ttw, lh,
               size=T["fs_card_title"], color="ink", bold=True)
        if it.get("desc"):
            D.text(s, it["desc"], cx + PAD, cy + PAD + lh + 0.06, tw,
                   M.height_in(it["desc"], T["fs_body"], tw),
                   size=T["fs_body"], color="ink_body")
        if twg:
            D.tag(s, it["tag"], cx + cw - twg - PAD, cy + PAD - 0.02,
                  w=twg, h=0.19, size=8)
        cy += hs[i] + g
    D.brandline(s)
    return s


def quote(spec, prs):
    """金句：浅灰底 + 大号红引号 + 深灰大字。不是红底白字。"""
    s = _new(prs, "canvas_alt")
    x = T["margin_x"] + 0.5
    w = T["page_w"] - 2 * x
    # 引号框按 110pt 实际行高给足，否则 audit 会（正确地）判它溢出
    D.text(s, "“", x - 0.15, 1.05, 1.5, 110 * 1.45 / 72, size=110,
           color="brand_text", bold=True)
    q = spec["quote"]
    qh = M.height_in(q, 26, w, 1.55)
    D.text(s, q, x, 2.5, w, qh, size=26, color="ink", bold=True,
           align=PP_ALIGN.CENTER, line_spacing=1.55)
    D.rule(s, T["page_w"] / 2 - 0.28, 2.5 + qh + 0.34, 0.56, thick=0.035)
    if spec.get("author"):
        D.text(s, spec["author"], x, 2.5 + qh + 0.58, w, 0.28, size=12,
               color="brand_text", bold=True, align=PP_ALIGN.CENTER)
    if spec.get("role"):
        D.text(s, spec["role"], x, 2.5 + qh + 0.88, w, 0.24, size=10,
               color="ink_muted", align=PP_ALIGN.CENTER)
    D.brandline(s)
    return s


def pyramid(spec, prs):
    """棱锥：层宽递减，仅顶层用红填充（面积可控）。"""
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    layers = spec["layers"][:5]
    n = len(layers)
    lh = min((ah - 0.1 * (n - 1)) / n, 1.0)
    top = y0 + max((ah - (lh * n + 0.1 * (n - 1))) / 2, 0)
    max_w = aw * 0.88
    # spec["layers"] 约定 [0]=底层 … [-1]=顶层；画的时候从顶往下画。
    # i=0 是顶层，必须最窄 —— 曾把宽度算反，画出倒金字塔。
    for i, ly in enumerate(reversed(layers)):
        w = max_w * (0.44 + 0.56 * i / max(n - 1, 1))
        x = x0 + (aw - w) / 2
        y = top + i * (lh + 0.1)
        is_top = (i == 0)
        # 顶层曾用整块红填充 —— 实测红色占比 11% 超 8% 上限。
        # 改为白卡 + 红描边 + 左侧红竖条，锚点效果一样，面积降到 1% 以内。
        D.card(s, x, y, w, lh, fill="card",
               line="brand" if is_top else "border",
               line_w=1.2 if is_top else None, radius=T["radius"])
        if is_top:
            D.rect(s, x + 0.001, y + 0.14, 0.05, lh - 0.28, fill="brand")
        lw = min(2.0, w * 0.32)
        D.text(s, ly["label"], x + 0.24, y, lw, lh, size=12,
               color="brand_text" if is_top else "ink", bold=True,
               anchor=MSO_ANCHOR.MIDDLE)
        if ly.get("desc"):
            dw = w - lw - 0.52
            D.text(s, ly["desc"], x + 0.24 + lw + 0.14, y, dw, lh,
                   size=9.5, color="ink_body", anchor=MSO_ANCHOR.MIDDLE)
    D.brandline(s)
    return s


def cycle(spec, prs):
    """循环：环形节点 + 中心。v1 这里标签重叠 69%，所以标签位置按象限避让。"""
    import math
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    _, _, aw, ah = _content_box(y0)
    steps = spec["steps"][:6]
    n = len(steps)
    cx, cy = T["page_w"] / 2, y0 + ah / 2
    R = min(ah * 0.42, 2.15)          # v2 用 0.34 -> 整页发空，节点缩成小点
    for i, st in enumerate(steps):
        a = math.radians(-90 + i * 360 / n)
        nx, ny = cx + R * math.cos(a), cy + R * math.sin(a)
        D.oval(s, nx - 0.3, ny - 0.3, 0.6, 0.6, fill="brand")
        D.text(s, f"{i+1:02d}", nx - 0.3, ny - 0.3, 0.6, 0.6, size=14,
               color=D.readable_on("brand"), bold=True, align=PP_ALIGN.CENTER,
               anchor=MSO_ANCHOR.MIDDLE)
        # 标签按象限外推：左半边右对齐、右半边左对齐、正上/正下居中。
        # 固定宽度居中会让左右标签朝圆心伸展、互相压（v2 实测重叠 36%）。
        lw = 1.95
        ca, sa = math.cos(a), math.sin(a)
        lxc, lyc = cx + (R + 0.46) * ca, cy + (R + 0.46) * sa
        if abs(ca) < 0.34:                       # 正上 / 正下
            lx, al = lxc - lw / 2, PP_ALIGN.CENTER
            ly = lyc + (0.12 if sa > 0 else -0.52)
        elif ca > 0:                             # 右半边
            lx, al = lxc + 0.1, PP_ALIGN.LEFT
            ly = lyc - 0.2
        else:                                    # 左半边
            lx, al = lxc - lw - 0.1, PP_ALIGN.RIGHT
            ly = lyc - 0.2
        D.text(s, st["label"], lx, ly, lw, 0.24, size=11, color="ink",
               bold=True, align=al)
        if st.get("desc"):
            D.text(s, st["desc"], lx, ly + 0.24, lw,
                   M.height_in(st["desc"], 8.5, lw), size=8.5,
                   color="ink_muted", align=al)
    if spec.get("center"):
        D.oval(s, cx - 0.62, cy - 0.62, 1.24, 1.24, fill="card")
        D.oval(s, cx - 0.62, cy - 0.62, 1.24, 1.24, fill=None, line="brand")
        D.text(s, spec["center"], cx - 0.55, cy - 0.55, 1.1, 1.1, size=10,
               color="brand_text", bold=True, align=PP_ALIGN.CENTER,
               anchor=MSO_ANCHOR.MIDDLE)
    D.brandline(s)
    return s


def chart(spec, prs):
    """原生可编辑图表 —— v1 完全没有图表，这是补上的一整块能力。

    kind: bar | column | line | pie | doughnut
    """
    s = _new(prs)
    y0 = D.page_header(s, spec["title"], spec.get("kicker"), spec.get("icon"))
    x0, _, aw, ah = _content_box(y0)
    D.card(s, x0, y0, aw, ah - 0.1, radius=T["radius_lg"])

    kinds = {"bar": XL_CHART_TYPE.BAR_CLUSTERED,
             "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
             "line": XL_CHART_TYPE.LINE_MARKERS,
             "pie": XL_CHART_TYPE.PIE,
             "doughnut": XL_CHART_TYPE.DOUGHNUT}
    cd = CategoryChartData()
    cd.categories = spec["categories"]
    for name, vals in spec["series"].items():
        cd.add_series(name, vals)
    gf = s.shapes.add_chart(kinds.get(spec.get("kind", "column")),
                            Inches(x0 + 0.3), Inches(y0 + 0.28),
                            Inches(aw - 0.6), Inches(ah - 0.72), cd)
    ch = gf.chart
    ch.has_title = False
    if len(spec["series"]) > 1 or spec.get("kind") in ("pie", "doughnut"):
        ch.has_legend = True
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(9)
        ch.legend.font.name = D.FONT_DECLARE
    else:
        ch.has_legend = False
    try:
        for p in ch.plots:
            p.gap_width = 60
            for pt, col in zip(p.series[0].points,
                               ["brand"] * len(spec["categories"])):
                pt.format.fill.solid()
                pt.format.fill.fore_color.rgb = D._c(col)
    except Exception:
        pass
    D.brandline(s)
    return s


def closing(spec, prs):
    s = _new(prs, "canvas")
    # 右栏放宽到 5.2in：v2 用 4.43in，八条 CTA 挤在窄边上很局促
    RX = 8.13
    D.rect(s, RX, 0, T["page_w"] - RX, T["page_h"], fill="canvas_alt")
    D.rect(s, RX, 0, 0.035, T["page_h"], fill="brand")
    x = T["margin_x"]
    ttl = spec["title"]
    th = M.height_in(ttl, 32, 7.0, 1.3)
    D.text(s, ttl, x, 2.3, 7.0, th, size=32, color="ink", bold=True,
           line_spacing=1.3)
    D.rule(s, x, 2.3 + th + 0.26, 0.55, thick=0.04)
    if spec.get("subtitle"):
        D.text(s, spec["subtitle"], x, 2.3 + th + 0.5, 6.9,
               M.height_in(spec["subtitle"], 12, 6.9), size=12, color="ink_muted")
    if spec.get("cta"):
        items = spec["cta"] if isinstance(spec["cta"], list) else [spec["cta"]]
        items = items[:8]
        iw = T["page_w"] - RX - 0.95
        hs = [M.height_in(i, 10, iw) for i in items]
        iy = max((T["page_h"] - (sum(hs) + 0.2 * (len(items) - 1))) / 2, 0.5)
        for k, it in enumerate(items):
            D.oval(s, RX + 0.42, iy + 0.055, 0.08, 0.08, fill="brand")
            D.text(s, it, RX + 0.66, iy, iw, hs[k], size=10, color="ink_body")
            iy += hs[k] + 0.2
    D.brandline(s)
    return s


BUILDERS = {
    "cover": cover, "section": section, "grid": grid,
    "numbered_list": numbered_list, "bullets": bullets,
    "two_column": two_column, "process": process, "stats": stats,
    "timeline": timeline, "quote": quote, "pyramid": pyramid,
    "cycle": cycle, "chart": chart, "closing": closing,
}


def render_deck(SLIDES, out_path, append_to=None, theme="red"):
    """theme: red(默认) / blue / green / gold / ink / violet。见 design.THEMES。

    追加模式下 theme 也生效 —— 但同一份 deck 别混主题，视觉会打架。
    """
    from pptx import Presentation
    import os
    D.apply_theme(theme)
    if append_to and os.path.exists(append_to):
        prs = Presentation(append_to)
        before = len(prs.slides)
    else:
        prs = Presentation()
        prs.slide_width = Inches(T["page_w"])
        prs.slide_height = Inches(T["page_h"])
        before = 0
    for spec in SLIDES:
        s = BUILDERS[spec["type"]](spec, prs)
        D.notes(s, spec.get("notes", ""))
    prs.save(out_path)
    print(f"{'追加' if append_to else '生成'} {len(prs.slides)-before} 张 / 共 {len(prs.slides)} 张")
    return out_path
