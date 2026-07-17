#!/usr/bin/env python3
"""设计令牌 + 绘图原语。

这个文件是「把设计简报编译成可执行约束」的地方。
设计简报（散文）说「红色作为视觉锚点」——模型每次理解都不一样，画出来的可能是大红色块。
令牌（数值）说 RED_MAX_AREA = 0.08——闸口能算、能拦、跨环境一致。

所有幻灯片必须通过 primitives 绘图，不允许直接调 add_shape，
否则默认阴影、直角、无描边这些毛病会重新长出来。
"""

import os
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as SHP

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(SKILL_DIR, "assets", "icons")

# ══════════════════════════════════════════════════════════════
#  设计令牌 —— 由「高级企业科技风」设计简报编译而来
# ══════════════════════════════════════════════════════════════

T = {
    # ── 颜色 ──
    # 底：明亮白 + 浅灰，营造通透清爽。注意是「白卡 + 浅灰底」，不能反过来。
    "canvas":     "FFFFFF",   # 页面底
    "canvas_alt": "F5F6F8",   # 冷灰，内容区底
    "card":       "FFFFFF",   # 卡片一律白底
    "card_alt":   "FAFBFC",   # 次级卡片
    "border":     "E5E7EB",   # 细线描边
    "border_soft":"EEF1F5",   # 浅雾灰描边
    "ink":        "111827",   # 石墨黑，标题        · on F5F6F8 = 16.4:1
    "ink_body":   "333333",   # 深灰，正文          · on FFFFFF = 12.6:1
    "ink_muted":  "5B6270",   # 弱化文字            · on F5F6F8 = 5.7:1
                              #   ⚠️ 曾用 #6B7280，实测 4.47:1 —— 差 0.03 不达标，
                              #   肉眼就是「发虚看不清」。别改回去。
    # 红色分两个用途，别混用 —— audit 会逐个算对比度：
    "brand":      "E60012",   # 【填充用】色块、图标、线。白底 4.8:1
                              #   ⚠️ 不要拿它写小字：压 F5F6F8 只有 4.44:1，压 FDEEEF 只有 4.27:1
    "brand_text": "B3000E",   # 【文字用】所有红色文字一律用它 · on F5F6F8 = 6.9:1
    "brand_dark": "B3000E",   # 同上，语义别名
    "brand_soft": "FDEEEF",   # 极浅红底纹（上面的字必须用 brand_text）

    # ── 栅格 8pt ──
    "grid": 8 / 72,           # 8pt -> 英寸
    "page_w": 13.333,
    "page_h": 7.5,
    "margin_x": 0.667,        # 48pt
    "margin_top": 0.556,      # 40pt
    "margin_bottom": 0.5,

    # ── 圆角 8-12px ──
    "radius": 0.11,           # ≈8pt，卡片
    "radius_lg": 0.14,        # ≈10pt，大卡片
    "radius_sm": 0.055,       # ≈4pt，标签

    # ── 描边 ──
    "hairline": 0.75,         # pt

    # ── 字号（标题大而克制，正文清晰耐读）──
    "fs_cover": 40,
    "fs_section": 34,
    "fs_title": 24,
    "fs_card_title": 13,
    "fs_body": 10.5,
    "fs_small": 9,
    "fs_num": 20,

    # ── 行高 ──
    "lh": 1.45,

    # ── 硬约束（audit.py 会照这些数字拦截）──
    "RED_MAX_AREA": 0.08,     # 红色面积上限 8%
    "MIN_CONTRAST": 4.5,      # 正文 WCAG AA
    "MIN_CONTRAST_LG": 3.0,   # 大字（>=18pt bold）
    "MAX_SAME_LAYOUT": 2,     # 连续同版式上限
}

# 默认字体：声明用什么、预览用什么，分开处理。
# 声明 = 分发对象的环境（企业多为 Windows）；预览 = 本机渲染器能读的。
FONT_DECLARE = "Microsoft YaHei"
FONT_FALLBACK = "Noto Sans SC"

# ══════════════════════════════════════════════════════════════
#  配色主题。浅色主题只换强调色（结构=白卡浅灰底不变）；深色主题额外
#  覆盖 canvas/card/ink 一整套结构色。所有对比度都算过（见各主题注释）。
#  换主题 = apply_theme(name)，layouts 里的语义名自动跟随。
#
#  brand_on = 强调色填充上的前景色（badge 圆里的数字、深色卡头文字）。
#  浅色主题多数用白（默认），但暖橙白字不达标(2.62)必须用深字；
#  深色主题的强调色是亮青，上面也要用深字。
# ══════════════════════════════════════════════════════════════

# 浅色基线：apply_theme 每次先重置到这里，再叠加主题 —— 否则深色主题的
# canvas/ink 覆盖会「泄漏」到之后切换的浅色主题上。
_LIGHT_BASE = {
    "canvas": "FFFFFF", "canvas_alt": "F5F6F8", "card": "FFFFFF", "card_alt": "FAFBFC",
    "border": "E5E7EB", "border_soft": "EEF1F5",
    "ink": "111827", "ink_body": "333333", "ink_muted": "5B6270",
    "brand_on": "FFFFFF",
}

THEMES = {
    # ── 浅色（企业科技风，白卡浅灰底）──
    "red":    {"brand": "E60012", "brand_text": "B3000E", "brand_dark": "B3000E", "brand_soft": "FDEEEF"},  # 白字4.8✓
    "blue":   {"brand": "2563EB", "brand_text": "1D4ED8", "brand_dark": "1D4ED8", "brand_soft": "EFF3FD"},  # 白字5.17✓
    "gold":   {"brand": "B08500", "brand_text": "8A6800", "brand_dark": "8A6800", "brand_soft": "F7F1DE",
               "brand_on": "3A2A00"},   # 金色亮，白字不稳，badge 用深棕金字
    "violet": {"brand": "6D28D9", "brand_text": "6D28D9", "brand_dark": "6D28D9", "brand_soft": "F2ECFC"},  # 白字7.1✓
    "warm-orange": {"brand": "FF6B35", "brand_text": "C2410C", "brand_dark": "C2410C", "brand_soft": "FFF0E8",
                    "brand_on": "3A1200"},   # 暖橙活力。白字压橙仅2.62 → badge 用深棕字5.85✓
    # ── 深色（企业深色科技，深底深卡浅字 + 亮青强调）──
    "dark":   {
        "canvas": "0F1420", "canvas_alt": "161D2E", "card": "1F2838", "card_alt": "273143",
        "border": "313C54", "border_soft": "232C40",
        "ink": "F0F3FA", "ink_body": "C5CCDA", "ink_muted": "9CA8BD",   # 浅字压深卡 6-14✓
        "brand": "22D3EE", "brand_text": "22D3EE", "brand_dark": "22D3EE",  # 亮青，压深底 8-9✓
        "brand_soft": "12303A", "brand_on": "0F1420",   # 青色填充上用深字10.18✓
    },
}


def apply_theme(name):
    """切换配色主题。未知名字直接报错，不静默用默认（避免以为换了其实没换）。

    先重置到浅色基线再叠加主题：浅色主题只带 brand 系（结构色回浅色默认），
    深色主题额外带结构色覆盖。这样主题之间不会互相泄漏。
    """
    if name not in THEMES:
        raise ValueError(f"未知主题「{name}」，可选：{', '.join(THEMES)}")
    T.update(_LIGHT_BASE)      # 结构色 + brand_on 先回浅色基线
    T.update(THEMES[name])     # 再叠加主题（brand 系；深色还覆盖结构色）
    _icon_cache.clear()        # 主题变了，图标染色缓存作废
    return name


def _lum_hex(hexc):
    c = [int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def readable_on(fill_key):
    """给定填充色（令牌名或 hex），返回其上可读的前景色（白 或 近黑），
    按对比度自动选。取代手工 brand_on —— 单一 token 无法覆盖所有填充色×主题：
    亮强调色(gold/orange/青)上要深字、暗强调色(red/blue/violet)上要白字、
    ink 填充上要白字，这里一次算对，跨全部主题成立。"""
    hexc = T.get(fill_key, fill_key)
    L = _lum_hex(hexc)
    white_c = 1.05 / (L + 0.05)
    dark_c = (L + 0.05) / (0.0116 + 0.05)   # 近黑 111827 亮度≈0.0116
    return "111827" if dark_c >= white_c else "FFFFFF"


def _c(hex_or_key):
    v = T.get(hex_or_key, hex_or_key)
    return RGBColor.from_string(v)


def snap(v):
    """吸附到 8pt 栅格。"""
    g = T["grid"]
    return round(v / g) * g


# ══════════════════════════════════════════════════════════════
#  绘图原语
# ══════════════════════════════════════════════════════════════

def _noshadow(shape):
    """关掉 PowerPoint 主题默认投影。

    这是旧版最大的「廉价感」来源：python-pptx 的 add_shape 会继承主题阴影，
    渲染出来每个色块外面糊一圈灰边。必须显式关闭。
    """
    shape.shadow.inherit = False


def glow(shape, color="brand", rad_pt=7, alpha=60):
    """给形状注入外发光（OOXML <a:glow>）。python-pptx 不封装，直接写 XML。

    已验证：写出的 XML 与 PowerPoint「格式 → 效果 → 发光」生成的完全一致，
    PowerPoint / Keynote 会渲染。注意 soffice 不可靠渲染此效果、不是好的验证器。

    发光只在深色底上好看（青/紫在深底 = 科幻感）；浅色/白底上打发光会发脏。
    因此只给 dark 主题的强调元素（大数字、强调条、图标）用。

    color: 令牌名或 hex；rad_pt: 发光半径(pt)；alpha: 不透明度(%)。
    """
    hexc = T.get(color, color)
    spPr = shape._element.spPr
    for e in spPr.findall(qn("a:effectLst")):
        spPr.remove(e)
    eff = spPr.makeelement(qn("a:effectLst"), {})
    g = eff.makeelement(qn("a:glow"), {"rad": str(int(rad_pt * 12700))})  # pt→EMU
    clr = g.makeelement(qn("a:srgbClr"), {"val": hexc})
    a = clr.makeelement(qn("a:alpha"), {"val": str(int(alpha * 1000))})
    clr.append(a)
    g.append(clr)
    eff.append(g)
    spPr.append(eff)
    return shape


def rect(slide, x, y, w, h, fill=None, line=None, line_w=None):
    """直角矩形。只用于品牌线、分隔条这类「线」，卡片一律用 card()。"""
    s = slide.shapes.add_shape(SHP.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    _style(s, fill, line, line_w)
    return s


def card(slide, x, y, w, h, fill="card", line="border", radius=None, line_w=None):
    """圆角卡片 —— 内容的默认容器。白底 + 细描边 + 无阴影。"""
    s = slide.shapes.add_shape(SHP.ROUNDED_RECTANGLE,
                               Inches(x), Inches(y), Inches(w), Inches(h))
    # adjustment 是「圆角半径 / 短边」的比值
    r = radius if radius is not None else T["radius"]
    try:
        s.adjustments[0] = min(r / min(w, h), 0.5)
    except (IndexError, ZeroDivisionError):
        pass
    _style(s, fill, line, line_w)
    return s


def oval(slide, x, y, w, h, fill="brand", line=None):
    s = slide.shapes.add_shape(SHP.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    _style(s, fill, line, None)
    return s


def _style(s, fill, line, line_w):
    _noshadow(s)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = _c(fill)
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = _c(line)
        s.line.width = Pt(line_w or T["hairline"])


def brandline(slide):
    """页面底部细长品牌红线 —— 全局统一识别。"""
    rect(slide, 0, T["page_h"] - 0.055, T["page_w"], 0.055, fill="brand")


def rule(slide, x, y, w=0.5, color="brand", thick=0.033):
    """标题下方的强调短线。"""
    rect(slide, x, y, w, thick, fill=color)


def text(slide, s, x, y, w, h, size=None, color="ink_body", bold=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=None,
         font=None, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    _noshadow(tb)          # textbox 也会继承主题阴影，别漏
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = str(s).split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing or T["lh"]
        r = p.add_run()
        r.text = ln
        r.font.name = font or FONT_DECLARE
        r.font.size = Pt(size or T["fs_body"])
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = _c(color)
    return tb


_icon_cache = {}


def icon(slide, name, x, y, size=0.22, color="brand"):
    """内置 Lucide 图标，运行时按当前主题染色。

    color 语义：brand(主题强调色，默认) / ink(深灰) / white(深底上) / 或直接 hex。
    图标 PNG 是描边图，只取它的 alpha 通道当形状，颜色实时染 —— 这样一套图标
    支持全部主题，不必为每个主题预渲染。

    降级：无 Pillow 时回退到预渲染的固定色 PNG（red/ink/white 里挑最近的）。
    图标缺失时静默跳过 —— 图标是增强，不是信息载体，缺一个不该让整份 PPT 失败。
    """
    hexc = {"brand": T["brand"], "red": T["brand"], "accent": T["brand"],
            "ink": T["ink_body"], "white": "FFFFFF"}.get(color, T.get(color, color))

    src = None
    for suf in ("ink", "red", "white"):
        cand = os.path.join(ICON_DIR, f"{name}-{suf}.png")
        if os.path.exists(cand):
            src = cand
            break
    if not src:
        return None

    key = (src, hexc)
    if key not in _icon_cache:
        try:
            import io
            from PIL import Image
            im = Image.open(src).convert("RGBA")
            alpha = im.split()[3]
            rgb = tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4))
            solid = Image.new("RGBA", im.size, rgb + (0,))
            solid.putalpha(alpha)
            buf = io.BytesIO()
            solid.save(buf, "PNG")
            _icon_cache[key] = buf.getvalue()
        except Exception:
            _icon_cache[key] = None   # 无 Pillow：标记走 fallback

    data = _icon_cache[key]
    if data is None:
        return slide.shapes.add_picture(src, Inches(x), Inches(y),
                                        Inches(size), Inches(size))
    import io as _io
    return slide.shapes.add_picture(_io.BytesIO(data), Inches(x), Inches(y),
                                    Inches(size), Inches(size))


def badge(slide, num, x, y, d=0.30, fill="brand", fg=None):
    """强调色圆形编号徽章 —— 统一组件。fg 默认按填充色自动算可读前景
    （readable_on）：亮强调色上深字、暗强调色上白字，跨全部主题都达标。"""
    if fg is None:
        fg = readable_on(fill)
    oval(slide, x, y, d, d, fill=fill)
    text(slide, str(num), x, y + d * 0.16, d, d * 0.7, size=d * 34,
         color=fg, bold=True, align=PP_ALIGN.CENTER)


def tag(slide, s, x, y, w=None, h=0.22, fill="brand_soft", fg="brand_dark", size=None):
    """浅红标签。前景默认 brand_dark —— brand 压 brand_soft 只有 4.27:1，不达标。"""
    import measure as _M
    size = size or T["fs_small"]
    w = w or (_M.text_width_pt(str(s), size) / 72 + 0.2)
    card(slide, x, y, w, h, fill=fill, line=None, radius=T["radius_sm"])
    text(slide, s, x, y, w, h, size=size, color=fg,
         bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return w


def page_header(slide, title, kicker=None, icon_name=None):
    """页眉：左对齐、无灰带、红短线。取代旧版那条笨重的灰色标题带。

    高度按标题实际度量推算，不写死 —— 写死就会像 v1 那样让红线压在标题上。
    """
    import measure as _M
    x, y = T["margin_x"], T["margin_top"]
    if kicker:
        text(slide, kicker, x, y - 0.24, 8, 0.2, size=T["fs_small"],
             color="brand_text", bold=True)
    ix = x
    th = _M.height_in(title, T["fs_title"], 11.5)
    if icon_name and icon(slide, icon_name, x, y + (th - 0.26) / 2, 0.26, "red"):
        ix = x + 0.38
    text(slide, title, ix, y, 11.5, th, size=T["fs_title"], color="ink", bold=True)
    rule(slide, x, y + th + 0.09, 0.44)
    return snap(y + th + 0.34)   # 内容区起始 y


def set_bg(slide, key="canvas"):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = _c(key)


def notes(slide, txt):
    if txt:
        slide.notes_slide.notes_text_frame.text = txt
