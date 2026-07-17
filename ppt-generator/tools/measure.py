#!/usr/bin/env python3
"""文字度量 —— 生成时就把高度算准，让文字压根没机会溢出。

分两层：
  1. 精确层：Pillow + 真实字体文件量每一行的推进宽度
  2. 降级层：宽度模型（中文 1.0em / 西文查表），无 Pillow 或无字体时兜底

旧版的暗坑：PPT 声明 Microsoft YaHei，PIL 却用 STHeiti 量 —— 量的和画的不是
一个字体，度量结果本身就是错的。所以这里统一用 skill 自带的 Noto Sans SC，
它同时也是预览渲染字体，两端同源。
"""

import os
import unicodedata

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_FONT_PATHS = [
    os.path.join(SKILL_DIR, "assets", "fonts", "NotoSansSC-Regular.otf"),
    os.path.join(SKILL_DIR, "assets", "fonts", "NotoSansSC-Regular.ttf"),
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]

_cache = {}
_font_file = None
_exact = None


def _init():
    global _font_file, _exact
    if _exact is not None:
        return
    try:
        from PIL import ImageFont  # noqa
    except ImportError:
        _exact = False
        return
    for p in _FONT_PATHS:
        if os.path.exists(p):
            try:
                from PIL import ImageFont
                f = ImageFont.truetype(p, 20)
                if f.getlength("客户") > 0:
                    _font_file, _exact = p, True
                    return
            except Exception:
                continue
    _exact = False


def is_exact():
    _init()
    return bool(_exact)


def font_file():
    _init()
    return _font_file


def _pil(size_pt):
    from PIL import ImageFont
    key = round(size_pt, 1)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(_font_file, max(int(round(size_pt)), 1))
    return _cache[key]


def _model_width(s, size_pt):
    """降级模型：CJK/全角 = 1.0em，其余 ≈0.5em。CJK 为主的内容误差很小。"""
    w = 0.0
    for ch in s:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            w += 1.0
        elif ch == " ":
            w += 0.28
        else:
            w += 0.52
    return w * size_pt


def text_width_pt(s, size_pt):
    _init()
    if _exact:
        return _pil(size_pt).getlength(s)
    return _model_width(s, size_pt)


def wrap_lines(s, size_pt, box_w_in):
    """按盒宽折行，返回行数。逐字符累加 —— 中文没有空格，不能按词折。"""
    box_w_pt = box_w_in * 72
    if box_w_pt <= 0:
        return len(s.split("\n")) or 1
    total = 0
    for para in str(s).split("\n"):
        if not para:
            total += 1
            continue
        line_w, lines = 0.0, 1
        for ch in para:
            cw = text_width_pt(ch, size_pt)
            if line_w + cw > box_w_pt and line_w > 0:
                lines += 1
                line_w = cw
            else:
                line_w += cw
        total += lines
    return total


def height_in(s, size_pt, box_w_in, lh=1.45):
    """这段文字在给定宽度下需要多高（英寸）。"""
    return wrap_lines(s, size_pt, box_w_in) * size_pt * lh / 72


def fits(s, size_pt, box_w_in, box_h_in, lh=1.45):
    return height_in(s, size_pt, box_w_in, lh) <= box_h_in + 1e-6


def fit_size(s, box_w_in, box_h_in, ideal_pt, min_pt=8.0, lh=1.45):
    """在盒子里找得下的最大字号。放不下就逐档缩，缩到底线仍放不下返回 None
    —— 那说明内容该拆页了，不该硬塞。"""
    size = ideal_pt
    while size >= min_pt:
        if fits(s, size, box_w_in, box_h_in, lh):
            return round(size, 1)
        size -= 0.5
    return None


def truncate_hint(s, size_pt, box_w_in, box_h_in, lh=1.45):
    """放不下时，估算需要砍到多少字 —— 给拆页/精简提供依据。"""
    max_lines = int(box_h_in * 72 / (size_pt * lh))
    if max_lines <= 0:
        return 0
    per_line = box_w_in * 72 / max(text_width_pt("字", size_pt), 1)
    return int(max_lines * per_line)
