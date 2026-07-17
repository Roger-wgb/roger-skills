#!/usr/bin/env python3
"""HTML 演示引擎 —— 与 pptx 共享同一套设计令牌（design.THEMES），但吃满 HTML 的长处：
真渐变、玻璃拟态、光晕、矢量图标（跟色）、动效、演讲者模式、讲稿。

单文件自包含：图标内联为 SVG，字体用系统字体，无外部依赖 —— 离线可用、可直接分发。

用法：
    from html_deck import render_html_deck
    render_html_deck(SLIDES, "out.html", theme="blue")   # SLIDES 规格与 layouts.py 完全一致
"""

import os
import re
import sys
import html as _html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as D

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(SKILL_DIR, "assets", "icons_svg")


# ── 图标内联（矢量，stroke=currentColor 自动跟父级 color）──────
def ic(name, cls="ic"):
    """内联 Lucide SVG。剥掉自带的 width/height（让 CSS 的 1em 控制大小，跟父级 font-size）
    和自带 class（避免和我们的 class 重复），保留 stroke=currentColor（跟父级 color）。"""
    if not name:
        return ""
    p = os.path.join(SVG_DIR, f"{name}.svg")
    if not os.path.exists(p):
        return ""
    svg = open(p, encoding="utf-8").read()
    svg = re.sub(r'\swidth="[^"]*"', '', svg, count=1)
    svg = re.sub(r'\sheight="[^"]*"', '', svg, count=1)
    svg = re.sub(r'\sclass="[^"]*"', '', svg)
    return svg.replace("<svg", f'<svg class="{cls}"', 1)


def esc(s):
    return _html.escape(str(s)).replace("\n", "<br>")


# ── 令牌 → CSS 变量 ─────────────────────────────────────────────
# 颜色键：值是 hex，输出要加 #；其余（字体/留白/圆角…）是原始 CSS 值。
_COLOR_KEYS = {"canvas", "canvas_alt", "card", "card_alt", "border", "border_soft",
               "ink", "ink_body", "ink_muted", "brand", "brand_text", "brand_soft", "brand_on"}
_VARMAP = {
    "canvas": "--canvas", "canvas_alt": "--canvas-alt", "card": "--card", "card_alt": "--card-alt",
    "border": "--border", "border_soft": "--border-soft", "ink": "--ink", "ink_body": "--ink-body",
    "ink_muted": "--ink-muted", "brand": "--brand", "brand_text": "--brand-text",
    "brand_soft": "--brand-soft", "brand_on": "--brand-on",
    # 美学旋钮（设计哲学用来改字体/留白/圆角/字重，不只换色）
    "font": "--font", "font_display": "--font-display", "pad_y": "--pad-y", "pad_x": "--pad-x",
    "radius": "--radius", "wt_display": "--wt-display",
    "card_shadow": "--card-shadow", "card_border": "--card-border",
}


def _vars(d):
    out = []
    for k, v in d.items():
        if k not in _VARMAP:
            continue
        out.append(f"{_VARMAP[k]}:{('#' + v) if k in _COLOR_KEYS else v};")
    return "".join(out)


def _theme_css():
    """6 个颜色主题：与 pptx 同源。每个输出完整颜色变量（深色的 canvas/card/ink
    才能覆盖 :root 默认——之前只覆盖 --brand 是 bug，深色 HTML 会是白底青字）。"""
    out = [":root{" + _vars({**D._LIGHT_BASE, **D.THEMES["red"]}) + "}"]
    for name, t in D.THEMES.items():
        out.append(f'body[data-theme="{name}"]{{' + _vars({**D._LIGHT_BASE, **t}) + "}")
    return "\n".join(out)


# ── 设计哲学：整套视觉语言（调色板 + 字体 + 留白 + 圆架 + 结构规则）──
# 与颜色主题的区别：主题只换强调色；哲学换字体、留白、版式比例、气质。
# 每个都自带完整调色板（不依赖 theme），且对比度经渲染验证达标。
PHILOSOPHIES = {
    # Pentagram —— 信息建筑/编辑风：白底黑字单红、大号衬线标题、奢侈留白、锐角平卡
    "pentagram": {
        "canvas": "FFFFFF", "canvas_alt": "FFFFFF", "card": "FFFFFF", "card_alt": "FAFAFA",
        "border": "E3E3E3", "border_soft": "EFEFEF",
        "ink": "0A0A0A", "ink_body": "2B2B2B", "ink_muted": "5F5F5F",
        "brand": "E63946", "brand_text": "C1121F", "brand_soft": "FBE9EB", "brand_on": "FFFFFF",
        "font_display": "'Songti SC','STSong','Noto Serif SC',Georgia,serif",
        "pad_y": "7.6vh", "pad_x": "6.8vw", "radius": "0px", "wt_display": "700",
        "card_shadow": "none", "card_border": "1px solid var(--border)",
        "_css": [".cover-title{font-size:6.6rem;line-height:1.03;letter-spacing:-.03em}",
                 ".sec-title{font-size:5.8rem}", ".sec-num{font-size:26rem;opacity:.05}",
                 ".h-title{font-size:3.1rem}", ".cover-sub{font-size:1.35rem}",
                 ".rule{height:3px;width:5vw}"],
    },
    # Kenya Hara —— 空的设计：纸白底、近乎无色（灰）、极致留白、轻字重、衬线
    "hara": {
        "canvas": "FAF9F6", "canvas_alt": "FAF9F6", "card": "FFFFFF", "card_alt": "F5F4F1",
        "border": "E6E4DF", "border_soft": "EFEEE9",
        "ink": "2E2E2E", "ink_body": "4A4A4A", "ink_muted": "6B6B6B",
        "brand": "6B6B6B", "brand_text": "444444", "brand_soft": "EEEDE9", "brand_on": "FFFFFF",
        "font_display": "'Noto Serif SC','Songti SC',Georgia,serif",
        "pad_y": "13vh", "pad_x": "13vw", "radius": "0px", "wt_display": "300",
        "card_shadow": "none", "card_border": "1px solid var(--border)",
        "_css": [".cover-title{font-size:2.5rem;font-weight:300;letter-spacing:.04em;line-height:1.5}",
                 ".sec-title{font-size:2.4rem;font-weight:300;letter-spacing:.05em}",
                 ".h-title{font-size:1.6rem;font-weight:300;letter-spacing:.03em}",
                 ".cover-sub{font-size:.98rem}", ".g-label{font-weight:400}",
                 ".rule{width:1vw;height:1px;background:var(--ink-muted)}", ".sec-num{opacity:.03}"],
    },
    # Neo Shen —— 东方水墨：深藏蓝底 + 暖白墨 + 青金强调 + 衬线，诗意留白（深色系）
    "shen": {
        "canvas": "1A1A2E", "canvas_alt": "1F1F35", "card": "24243E", "card_alt": "2A2A48",
        "border": "3A3A55", "border_soft": "2E2E48",
        "ink": "F0EDE4", "ink_body": "CFC9BC", "ink_muted": "9A9484",
        "brand": "C4A868", "brand_text": "D4BC88", "brand_soft": "2A2740", "brand_on": "1A1A2E",
        "font_display": "'Noto Serif SC','Songti SC',Georgia,serif",
        "pad_y": "7vh", "pad_x": "5.5vw", "radius": "3px", "wt_display": "600",
        "card_shadow": "0 8px 30px rgba(0,0,0,.35)", "card_border": "1px solid var(--border)",
        "_css": [".cover-title{letter-spacing:.03em}", ".sec-title{letter-spacing:.04em}",
                 ".sec-num{opacity:.12}"],
    },
    # Müller-Brockmann —— 瑞士网格：白黑红、粗黑体、锐角、粗黑描边、紧字距、绝对功能
    "swiss": {
        "canvas": "FFFFFF", "canvas_alt": "FFFFFF", "card": "FFFFFF", "card_alt": "F2F2F2",
        "border": "111111", "border_soft": "DADADA",
        "ink": "000000", "ink_body": "1A1A1A", "ink_muted": "4D4D4D",
        "brand": "D4001F", "brand_text": "B00019", "brand_soft": "FBE7EA", "brand_on": "FFFFFF",
        "font_display": "'Helvetica Neue',Arial,'PingFang SC','Noto Sans SC',sans-serif",
        "pad_y": "6.5vh", "pad_x": "5.5vw", "radius": "0px", "wt_display": "800",
        "card_shadow": "none", "card_border": "1.5px solid var(--border)",
        "_css": [".cover-title{font-size:6rem;letter-spacing:-.035em;line-height:.98}",
                 ".sec-title{font-size:5.6rem;letter-spacing:-.035em}", ".sec-num{font-size:22rem;opacity:.08}",
                 ".h-title{font-size:2.7rem;letter-spacing:-.02em}",
                 ".kick{letter-spacing:.2em;font-size:.68rem}", ".cover-sub{font-size:1.3rem}"],
    },
}


def _philosophy_css():
    out = []
    for name, p in PHILOSOPHIES.items():
        out.append(f'body[data-philosophy="{name}"]{{' + _vars(p) + "}")
        for rule in p.get("_css", []):
            out.append(f'body[data-philosophy="{name}"] {rule}')
    return "\n".join(out)


CSS = """
:root{--font:"PingFang SC","Microsoft YaHei","Noto Sans SC",-apple-system,sans-serif;
  --font-display:var(--font);--pad-y:6.2vh;--pad-x:4.6vw;--radius:14px;--wt-display:800;
  --card-shadow:0 8px 26px rgba(17,24,39,.06);--card-border:1px solid var(--border)}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font);
  background:#0c0d10;overflow:hidden;height:100vh;width:100vw;color:var(--ink-body)}
.deck{display:flex;height:100vh;transition:transform .5s cubic-bezier(.4,0,.2,1)}
.slide{min-width:100vw;height:100vh;background:var(--canvas-alt);position:relative;
  padding:var(--pad-y) var(--pad-x);overflow:hidden;display:flex;flex-direction:column}
.slide::after{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:var(--brand)}
.ic{width:1em;height:1em;stroke:currentColor;fill:none;stroke-width:2;
  stroke-linecap:round;stroke-linejoin:round;flex:none}

/* 页眉 */
.kick{font-size:.78rem;font-weight:700;letter-spacing:.12em;color:var(--brand-text);
  text-transform:uppercase;margin-bottom:.5vh}
.head{display:flex;align-items:center;gap:.6vw;margin-bottom:.6vh}
.head .ic{font-size:1.7rem;color:var(--brand)}
.h-title{font-size:2rem;font-weight:var(--wt-display);color:var(--ink);line-height:1.2;font-family:var(--font-display)}
.rule{width:2.6vw;height:3px;border-radius:2px;background:var(--brand);margin-top:1vh}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;min-height:0}

/* 卡片 */
.card{background:var(--card);border:var(--card-border);border-radius:var(--radius);
  box-shadow:var(--card-shadow);padding:2.4vh 1.6vw}
.tag{display:inline-flex;align-items:center;font-size:.72rem;font-weight:700;
  color:var(--brand-text);background:var(--brand-soft);padding:.2em .7em;border-radius:6px}
.badge{width:2em;height:2em;border-radius:50%;background:var(--brand);color:var(--brand-on);
  display:inline-flex;align-items:center;justify-content:center;font-weight:700;
  font-size:.9rem;flex:none}
.glow{position:absolute;border-radius:50%;filter:blur(10px);pointer-events:none;
  background:radial-gradient(circle,var(--brand-soft),transparent 68%);opacity:.9}

/* 封面 / 章节 / 封底 */
.cover,.closing{flex-direction:row;padding:0}
.cover-l,.closing-l{flex:1;padding:8vh 4.6vw;display:flex;flex-direction:column;justify-content:center}
.cover-r,.closing-r{width:38%;background:var(--canvas-alt);border-left:3px solid var(--brand);
  padding:7vh 3vw;display:flex;flex-direction:column;justify-content:center;gap:2.4vh;position:relative}
.cover,.closing{background:var(--canvas)}
.cover-tag{align-self:flex-start;margin-bottom:3vh}
.cover-title{font-size:3.4rem;font-weight:900;color:var(--ink);line-height:1.16;letter-spacing:-.01em;font-family:var(--font-display)}
.cover-sub{font-size:1.15rem;color:var(--ink-muted);line-height:1.7;margin-top:2.6vh;max-width:42ch}
.cover-meta{position:absolute;bottom:6vh;left:4.6vw;font-size:.8rem;color:var(--ink-muted)}
.cover-r-item{display:flex;gap:.8vw;align-items:flex-start}
.cover-r-item b{color:var(--brand-text);font-family:ui-monospace,monospace;font-size:.85rem}
.cover-r-item span{color:var(--ink-body);font-size:.98rem;line-height:1.5}

.section{align-items:flex-start;justify-content:center}
.section .body{justify-content:center}
.sec-num{position:absolute;right:4vw;top:50%;transform:translateY(-50%);
  font-size:16rem;font-weight:900;color:var(--brand);opacity:.1;line-height:1;
  font-family:ui-monospace,monospace}
.sec-kick{font-size:.9rem;font-weight:700;letter-spacing:.14em;color:var(--brand-text);text-transform:uppercase}
.sec-title{font-size:3rem;font-weight:900;color:var(--ink);line-height:1.2;margin-top:1.6vh;font-family:var(--font-display)}
.sec-sub{font-size:1.15rem;color:var(--ink-muted);margin-top:2vh;max-width:52ch;line-height:1.7}

/* grid */
.grid{display:grid;gap:1.5vh 1.2vw;flex:1;align-content:center}
.grid.c2{grid-template-columns:repeat(2,1fr)}.grid.c3{grid-template-columns:repeat(3,1fr)}
.g-card{display:flex;flex-direction:column;gap:1vh}
.g-top{display:flex;align-items:center;gap:.6vw}
.g-top .ic{font-size:1.4rem;color:var(--brand)}
.g-label{font-size:1.05rem;font-weight:700;color:var(--ink)}
.g-desc{font-size:.92rem;color:var(--ink-body);line-height:1.6}
.g-std{background:var(--canvas-alt);border-radius:8px;padding:1vh .8vw;margin-top:.4vh}
.g-std b{color:var(--brand-text);font-size:.7rem;font-weight:700;display:block;margin-bottom:.3vh}
.g-std span{font-size:.82rem;color:var(--ink-muted);line-height:1.55}

/* numbered / bullets */
.nlist{display:flex;flex-direction:column;gap:1.3vh;flex:1;justify-content:center}
.nrow{display:flex;gap:1.2vw;align-items:center}
.nrow .badge{font-family:ui-monospace,monospace}
.n-body b{font-size:1.05rem;font-weight:700;color:var(--ink);display:block;margin-bottom:.3vh}
.n-body span{font-size:.95rem;color:var(--ink-body);line-height:1.6}
.blist{display:flex;flex-direction:column;gap:1.1vh;flex:1;justify-content:center}
.brow{display:flex;gap:1vw;align-items:center}
.brow span{font-size:1rem;color:var(--ink-body);line-height:1.55}

/* two column */
.two{display:grid;grid-template-columns:1fr 1fr;gap:1.4vw;flex:1;align-content:center}
.col-head{padding:1.2vh 1vw;border-radius:12px 12px 0 0;font-weight:700;font-size:1.02rem}
.col.l .col-head{background:var(--brand);color:var(--brand-on)}
.col.r .col-head{background:var(--ink);color:var(--canvas)}
.col-items{border:1px solid var(--border);border-top:none;border-radius:0 0 12px 12px;
  background:var(--card);padding:1vh 0}
.col-item{display:flex;gap:.7vw;align-items:flex-start;padding:.9vh 1vw}
.col-item .badge{width:1.5em;height:1.5em;font-size:.72rem}
.col.r .col-item .badge{background:var(--ink);color:var(--canvas)}
.col-item span{font-size:.92rem;color:var(--ink-body);line-height:1.55}

/* process */
.proc{display:flex;gap:.7vw;flex:1;align-items:center}
.p-step{flex:1;background:var(--card);border:1px solid var(--border);border-radius:14px;
  box-shadow:0 8px 26px rgba(17,24,39,.06);padding:2vh 1vw;align-self:stretch;
  display:flex;flex-direction:column;gap:1vh}
.p-arrow{color:var(--brand);flex:none;font-size:1.3rem;display:flex;align-items:center}
.p-label{font-size:1rem;font-weight:700;color:var(--ink)}
.p-desc{font-size:.88rem;color:var(--ink-body);line-height:1.55}

/* stats */
.stats{display:flex;gap:1.2vw;flex:1;align-items:center;justify-content:center}
.stat{flex:1;background:var(--card);border:1px solid var(--border);border-radius:16px;
  box-shadow:0 10px 30px rgba(17,24,39,.07);padding:4vh 1vw;text-align:center;position:relative;overflow:hidden}
.stat .glow{width:60%;aspect-ratio:1;top:-20%;left:20%}
.stat-num{font-size:3.4rem;font-weight:900;color:var(--brand);line-height:1;position:relative}
.stat-label{font-size:1.05rem;font-weight:700;color:var(--ink);margin-top:1.5vh}
.stat-desc{font-size:.82rem;color:var(--ink-muted);margin-top:.7vh;line-height:1.5}

/* timeline */
.tl{display:flex;flex-direction:column;gap:1.1vh;flex:1;justify-content:center;padding-left:8vw}
.tl-row{display:flex;gap:1.2vw;align-items:stretch;position:relative}
.tl-date{width:6vw;text-align:right;font-size:.85rem;font-weight:700;color:var(--brand-text);
  padding-top:1.4vh;flex:none;margin-left:-8vw}
.tl-dot{width:.9rem;height:.9rem;border-radius:50%;background:var(--brand);flex:none;margin-top:1.6vh;
  box-shadow:0 0 0 4px var(--brand-soft)}
.tl-card{flex:1;background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.3vh 1.1vw;box-shadow:0 6px 20px rgba(17,24,39,.05);display:flex;flex-direction:column;gap:.4vh}
.tl-card b{font-size:1rem;font-weight:700;color:var(--ink)}
.tl-card span{font-size:.85rem;color:var(--ink-body);line-height:1.55}
.tl-tag{align-self:flex-start;margin-top:.4vh}

/* quote */
.quote{align-items:center;justify-content:center;text-align:center}
.q-mark{font-size:7rem;color:var(--brand);line-height:.6;font-family:Georgia,serif;opacity:.9}
.q-text{font-size:2rem;font-weight:700;color:var(--ink);line-height:1.55;max-width:64ch;margin:2vh auto}
.q-author{font-size:1.05rem;font-weight:700;color:var(--brand-text);margin-top:2vh}
.q-role{font-size:.9rem;color:var(--ink-muted);margin-top:.5vh}

/* pyramid */
.pyr{display:flex;flex-direction:column;align-items:center;gap:1vh;flex:1;justify-content:center}
.pyr-row{background:var(--card);border:1px solid var(--border);border-radius:12px;
  box-shadow:0 6px 20px rgba(17,24,39,.05);padding:1.5vh 1.4vw;display:flex;gap:1.2vw;align-items:center}
.pyr-row.top{border-color:var(--brand);border-width:2px}
.pyr-row.top .pyr-label{color:var(--brand-text)}
.pyr-label{font-weight:700;color:var(--ink);font-size:1.02rem;flex:none;min-width:8vw}
.pyr-desc{font-size:.88rem;color:var(--ink-body);line-height:1.5}

/* cycle */
.cycle{position:relative;flex:1;display:flex;align-items:center;justify-content:center}
.cyc-center{position:absolute;width:12vw;height:12vw;border-radius:50%;background:var(--card);
  border:2px solid var(--brand);display:flex;align-items:center;justify-content:center;text-align:center;
  font-weight:700;color:var(--brand-text);font-size:.95rem;padding:1vw;
  box-shadow:0 10px 30px rgba(17,24,39,.08)}
.cyc-node{position:absolute;width:9vw;text-align:center;transform:translate(-50%,-50%)}
.cyc-dot{width:3vw;height:3vw;border-radius:50%;background:var(--brand);color:var(--brand-on);margin:0 auto .6vh;
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.1rem;
  box-shadow:0 0 0 5px var(--brand-soft)}
.cyc-node b{font-size:.92rem;color:var(--ink);display:block}
.cyc-node span{font-size:.75rem;color:var(--ink-muted)}

/* chart（纯 CSS 条形，无外部库）*/
.chart{display:flex;gap:1.6vw;align-items:flex-end;flex:1;justify-content:center;padding:0 4vw 4vh}
.bar-wrap{flex:1;max-width:9vw;display:flex;flex-direction:column;align-items:center;gap:1vh;height:100%;justify-content:flex-end}
.bar{width:100%;background:linear-gradient(var(--brand),var(--brand-text));border-radius:8px 8px 0 0;
  min-height:4px;position:relative;transition:height 1s cubic-bezier(.4,0,.2,1)}
.bar-val{position:absolute;top:-2.4vh;left:0;right:0;text-align:center;font-weight:700;color:var(--brand-text);font-size:.9rem}
.bar-cat{font-size:.85rem;color:var(--ink-body);font-weight:600}

/* closing */
.closing-title{font-size:2.6rem;font-weight:900;color:var(--ink);line-height:1.2}
.closing-sub{font-size:1.05rem;color:var(--ink-muted);margin-top:2vh;line-height:1.6}
.cta-item{display:flex;gap:.7vw;align-items:flex-start;font-size:.98rem;color:var(--ink-body);line-height:1.5}
.cta-item .dot{width:.5em;height:.5em;border-radius:50%;background:var(--brand);margin-top:.5em;flex:none}

/* 导航 + 动效 + 演讲者 */
.nav{position:fixed;bottom:2.4vh;left:50%;transform:translateX(-50%);display:flex;gap:.8vw;
  align-items:center;background:rgba(15,17,21,.55);backdrop-filter:blur(10px);padding:.5vh 1vw;
  border-radius:20px;z-index:100}
.nav button{background:none;border:none;color:rgba(255,255,255,.7);cursor:pointer;font-size:1rem}
.nav .ct{font-family:ui-monospace,monospace;font-size:.8rem;color:rgba(255,255,255,.7);min-width:5ch;text-align:center}
.topbtn{position:fixed;top:2vh;z-index:100;background:rgba(15,17,21,.5);color:rgba(255,255,255,.75);
  border:none;padding:.5vh .9vw;border-radius:8px;font-size:.75rem;cursor:pointer;backdrop-filter:blur(8px)}
.exp{right:2vw}.pres{left:2vw}
[data-anim]{opacity:0;will-change:transform,opacity,filter}
[data-anim].in{opacity:1;transform:none!important;filter:none!important;
  transition:opacity .6s ease,transform .6s cubic-bezier(.34,1.3,.64,1),filter .5s ease}
[data-anim="up"]{transform:translateY(34px)}
[data-anim="left"]{transform:translateX(40px)}[data-anim="right"]{transform:translateX(-40px)}
[data-anim="zoom"]{transform:scale(.8)}[data-anim="blur"]{filter:blur(16px)}
.stag>*{opacity:0;transform:translateY(20px)}
.stag.in>*{opacity:1;transform:none;transition:opacity .5s ease,transform .5s ease}
.stag.in>*:nth-child(1){transition-delay:.05s}.stag.in>*:nth-child(2){transition-delay:.14s}
.stag.in>*:nth-child(3){transition-delay:.23s}.stag.in>*:nth-child(4){transition-delay:.32s}
.stag.in>*:nth-child(5){transition-delay:.41s}.stag.in>*:nth-child(6){transition-delay:.5s}
.notes{display:none}
body.shot .nav,body.shot .topbtn{display:none}
@media print{.nav,.topbtn{display:none}.deck{display:block;transform:none!important}
  .slide{page-break-after:always}body{overflow:visible}}
"""

JS = r"""
const deck=document.getElementById('deck'),slides=[...deck.children].filter(s=>s.classList.contains('slide'));
const ct=document.getElementById('ct');let cur=0;
function anim(s){s.querySelectorAll('[data-anim],.stag').forEach((e,i)=>{
  const d=parseInt(e.dataset.delay??i*90);setTimeout(()=>e.classList.add('in'),d);});
  s.querySelectorAll('[data-count]').forEach(e=>{const t=+e.dataset.count,dur=1200,t0=performance.now();
    const tk=n=>{const p=Math.min((n-t0)/dur,1),v=1-Math.pow(1-p,3);
    e.textContent=Math.round(v*t)+(e.dataset.suf||'');if(p<1)requestAnimationFrame(tk);};requestAnimationFrame(tk);});
  s.querySelectorAll('.bar').forEach(b=>{b.style.height=b.dataset.h;});}
function reset(s){s.querySelectorAll('[data-anim],.stag').forEach(e=>e.classList.remove('in'));
  s.querySelectorAll('.bar').forEach(b=>b.style.height='0');}
function upd(){deck.style.transform=`translateX(-${cur*100}vw)`;ct.textContent=`${cur+1} / ${slides.length}`;
  anim(slides[cur]);sync();}
function go(d){const p=cur;cur=Math.max(0,Math.min(slides.length-1,cur+d));if(cur!==p)reset(slides[p]);upd();}
document.addEventListener('keydown',e=>{if([' ','ArrowRight','ArrowDown','PageDown'].includes(e.key)){e.preventDefault();go(1);}
  if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();go(-1);}
  if(e.key==='f'||e.key==='F')document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  if(e.key==='s'||e.key==='S')openPres();});
let tx=0;deck.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:1});
deck.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>50)go(dx<0?1:-1);});
const ch=new BroadcastChannel('ppt-pres');let pw=null;
function openPres(){if(pw&&!pw.closed){pw.focus();sync();return;}
  pw=window.open('','pres','width=1200,height=760');
  pw.document.write('<!DOCTYPE html><meta charset=UTF-8><title>演讲者</title><style>body{margin:0;background:#161616;color:#fff;font-family:system-ui;height:100vh;display:grid;grid-template-rows:1fr auto;gap:10px;padding:12px}.n{background:#222;border-radius:10px;padding:18px;overflow:auto;font-size:17px;line-height:1.7}.n b{color:#fff}.b{display:flex;gap:14px;align-items:center;justify-content:space-between}#tm{font:600 40px ui-monospace,monospace}button{background:#333;border:none;color:#ddd;padding:8px 16px;border-radius:6px;cursor:pointer}</style><div class=n id=nb>讲稿</div><div class=b><span id=sn></span><span id=tm>00:00</span><button onclick=tg()>▶</button></div><script>const ch=new BroadcastChannel("ppt-pres");let r=0,s=0,iv;ch.onmessage=e=>{document.getElementById("nb").innerHTML=e.data.notes||"（此页无讲稿）";document.getElementById("sn").textContent=e.data.cur+" / "+e.data.total};function tg(){r=!r;if(r)iv=setInterval(()=>{s++;let m=String(s/60|0).padStart(2,"0"),c=String(s%60).padStart(2,"0");document.getElementById("tm").textContent=m+":"+c},1e3);else clearInterval(iv)}<\/script>');
  pw.document.close();setTimeout(sync,300);}
function sync(){if(!pw||pw.closed)return;const n=slides[cur].querySelector('.notes');
  ch.postMessage({cur:cur+1,total:slides.length,notes:n?n.innerHTML:''});}
// 截图模式 ?shot=N：无动画定位到第 N 页、动画直接到终态、隐藏导航 —— 供 chrome 逐页截图
const sp=new URLSearchParams(location.search);
if(sp.has('shot')){cur=Math.max(0,Math.min(slides.length-1,+sp.get('shot')||0));
  document.body.classList.add('shot');deck.style.transition='none';
  deck.style.transform=`translateX(-${cur*100}vw)`;const s=slides[cur];
  s.querySelectorAll('[data-anim],.stag').forEach(e=>e.classList.add('in'));
  s.querySelectorAll('.bar').forEach(b=>b.style.height=b.dataset.h);
  s.querySelectorAll('[data-count]').forEach(e=>e.textContent=e.dataset.count+(e.dataset.suf||''));
  ct.textContent=`${cur+1} / ${slides.length}`;
}else{upd();}
"""


# ══════════════════════════════════════════════════════════════
#  版式 —— 与 layouts.py 的 spec 结构一致
# ══════════════════════════════════════════════════════════════

def _head(spec):
    k = f'<div class="kick" data-anim="up">{esc(spec["kicker"])}</div>' if spec.get("kicker") else ""
    icon = f'{ic(spec["icon"])}' if spec.get("icon") else ""
    return (f'{k}<div class="head" data-anim="up" data-delay="60">{icon}'
            f'<div class="h-title">{esc(spec["title"])}</div></div>'
            f'<div class="rule" data-anim="up" data-delay="120"></div>')


def _notes(spec):
    return f'<aside class="notes">{spec["notes"]}</aside>' if spec.get("notes") else ""


def cover(spec):
    pts = "".join(
        f'<div class="cover-r-item" data-anim="up" data-delay="{300+i*90}">'
        f'<b>{i+1:02d}</b><span>{esc(p)}</span></div>'
        for i, p in enumerate(spec.get("points", [])[:6]))
    r = (f'<div class="cover-r">{pts}</div>' if pts else
         (f'<div class="cover-r" style="align-items:center;justify-content:center">'
          f'<span class="ic" style="font-size:5rem;color:var(--brand)">{ic(spec["icon"])}</span></div>'
          if spec.get("icon") else '<div class="cover-r"></div>'))
    tag = f'<div class="tag cover-tag" data-anim="up">{esc(spec["tag"])}</div>' if spec.get("tag") else ""
    meta = f'<div class="cover-meta">{esc(spec["meta"])}</div>' if spec.get("meta") else ""
    sub = f'<div class="cover-sub" data-anim="up" data-delay="260">{esc(spec["subtitle"])}</div>' if spec.get("subtitle") else ""
    return (f'<section class="slide cover">'
            f'<div class="cover-l">{tag}'
            f'<div class="cover-title" data-anim="up" data-delay="120">{esc(spec["title"])}</div>'
            f'{sub}{meta}</div>{r}{_notes(spec)}</section>')


def section(spec):
    num = f'<div class="sec-num">{esc(spec["number"])}</div>' if spec.get("number") else ""
    k = f'<div class="sec-kick" data-anim="up">{esc(spec["kicker"])}</div>' if spec.get("kicker") else ""
    sub = f'<div class="sec-sub" data-anim="up" data-delay="180">{esc(spec["subtitle"])}</div>' if spec.get("subtitle") else ""
    return (f'<section class="slide section">{num}<div class="body">{k}'
            f'<div class="sec-title" data-anim="up" data-delay="80">{esc(spec["title"])}</div>'
            f'{sub}</div>{_notes(spec)}</section>')


def grid(spec):
    items = spec["items"][:6]
    cols = "c3" if len(items) > 4 else ("c2" if len(items) > 1 else "c2")
    if len(items) == 3:
        cols = "c3"
    cards = ""
    for it in items:
        icon = f'{ic(it["icon"])}' if it.get("icon") else ""
        tag = f'<span class="tag">{esc(it["tag"])}</span>' if it.get("tag") else ""
        std = (f'<div class="g-std"><b>完成标准</b><span>{esc(it["std"])}</span></div>'
               if it.get("std") else "")
        desc = f'<div class="g-desc">{esc(it["desc"])}</div>' if it.get("desc") else ""
        cards += (f'<div class="card g-card"><div class="g-top">{icon}{tag}</div>'
                  f'<div class="g-label">{esc(it["label"])}</div>{desc}{std}</div>')
    return (f'<section class="slide"><div class="head-wrap">{_head(spec)}</div>'
            f'<div class="body"><div class="grid {cols} stag">{cards}</div></div>'
            f'{_notes(spec)}</section>')


def numbered_list(spec):
    rows = "".join(
        f'<div class="nrow card"><span class="badge">{i+1:02d}</span>'
        f'<div class="n-body"><b>{esc(it["title"])}</b><span>{esc(it["desc"])}</span></div></div>'
        for i, it in enumerate(spec["items"][:5]))
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="nlist stag">{rows}</div></div>{_notes(spec)}</section>')


def bullets(spec):
    rows = "".join(
        f'<div class="brow card"><span class="badge">{i+1}</span><span>{esc(b)}</span></div>'
        for i, b in enumerate(spec["bullets"][:6]))
    src = f'<div style="font-size:.78rem;color:var(--ink-muted);margin-top:1.5vh;font-style:italic">{esc(spec["source"])}</div>' if spec.get("source") else ""
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="blist stag">{rows}</div>{src}</div>{_notes(spec)}</section>')


def two_column(spec):
    def col(cls, title, pts):
        items = "".join(
            f'<div class="col-item"><span class="badge">{i+1}</span><span>{esc(p)}</span></div>'
            for i, p in enumerate(pts[:6]))
        return (f'<div class="col {cls}"><div class="col-head">{esc(title)}</div>'
                f'<div class="col-items">{items}</div></div>')
    left = col("l", spec.get("left_title", ""), spec.get("left_points", []))
    right = col("r", spec.get("right_title", ""), spec.get("right_points", []))
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="two"><div data-anim="right">{left}</div>'
            f'<div data-anim="left" data-delay="150">{right}</div></div></div>{_notes(spec)}</section>')


def process(spec):
    steps = spec["steps"][:5]
    parts = []
    for i, st in enumerate(steps):
        desc = f'<div class="p-desc">{esc(st.get("desc",""))}</div>' if st.get("desc") else ""
        parts.append(f'<div class="p-step" data-anim="up" data-delay="{i*140}">'
                     f'<span class="badge">{i+1:02d}</span>'
                     f'<div class="p-label">{esc(st["label"])}</div>{desc}</div>')
        if i < len(steps) - 1:
            parts.append('<div class="p-arrow"><span class="ic">' + ic("chevron-right") + '</span></div>')
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="proc">{"".join(parts)}</div></div>{_notes(spec)}</section>')


def stats(spec):
    cards = ""
    for i, it in enumerate(spec["stats"][:4]):
        desc = f'<div class="stat-desc">{esc(it["desc"])}</div>' if it.get("desc") else ""
        num = str(it["num"])
        digits = "".join(c for c in num if c.isdigit())
        countable = digits == num and num
        numhtml = (f'<span data-count="{num}" data-suf="{esc(it.get("unit",""))}">0</span>'
                   if countable else esc(num) + esc(it.get("unit", "")))
        cards += (f'<div class="stat" data-anim="zoom" data-delay="{i*130}"><div class="glow"></div>'
                  f'<div class="stat-num">{numhtml}</div>'
                  f'<div class="stat-label">{esc(it["label"])}</div>{desc}</div>')
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="stats">{cards}</div></div>{_notes(spec)}</section>')


def timeline(spec):
    rows = ""
    for it in spec["items"][:6]:
        tag = f'<span class="tag tl-tag">{esc(it["tag"])}</span>' if it.get("tag") else ""
        desc = f'<span>{esc(it.get("desc",""))}</span>' if it.get("desc") else ""
        rows += (f'<div class="tl-row"><div class="tl-date">{esc(it["date"])}</div>'
                 f'<div class="tl-dot"></div><div class="tl-card"><b>{esc(it["title"])}</b>{desc}{tag}</div></div>')
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="tl stag">{rows}</div></div>{_notes(spec)}</section>')


def quote(spec):
    au = f'<div class="q-author" data-anim="up" data-delay="400">{esc(spec["author"])}</div>' if spec.get("author") else ""
    ro = f'<div class="q-role" data-anim="up" data-delay="500">{esc(spec["role"])}</div>' if spec.get("role") else ""
    return (f'<section class="slide quote"><div class="body" style="text-align:center">'
            f'<div class="q-mark" data-anim="up">“</div>'
            f'<div class="q-text" data-anim="blur" data-delay="150">{esc(spec["quote"])}</div>'
            f'<div class="rule" style="margin:2vh auto"></div>{au}{ro}</div>{_notes(spec)}</section>')


def pyramid(spec):
    layers = spec["layers"][:5]
    rows = ""
    for i, ly in enumerate(reversed(layers)):
        top = "top" if i == 0 else ""
        w = 44 + 56 * i / max(len(layers) - 1, 1)
        desc = f'<div class="pyr-desc">{esc(ly.get("desc",""))}</div>' if ly.get("desc") else ""
        rows += (f'<div class="pyr-row {top}" style="width:{w}%" data-anim="up" data-delay="{i*90}">'
                 f'<div class="pyr-label">{esc(ly["label"])}</div>{desc}</div>')
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="pyr">{rows}</div></div>{_notes(spec)}</section>')


def cycle(spec):
    import math
    steps = spec["steps"][:6]
    n = len(steps)
    nodes = ""
    for i, st in enumerate(steps):
        a = math.radians(-90 + i * 360 / n)
        x = 50 + 34 * math.cos(a)
        y = 50 + 40 * math.sin(a)
        desc = f'<span>{esc(st.get("desc",""))}</span>' if st.get("desc") else ""
        nodes += (f'<div class="cyc-node" style="left:{x}%;top:{y}%" data-anim="zoom" data-delay="{i*110}">'
                  f'<div class="cyc-dot">{i+1:02d}</div><b>{esc(st["label"])}</b>{desc}</div>')
    center = f'<div class="cyc-center">{esc(spec["center"])}</div>' if spec.get("center") else ""
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="cycle">{center}{nodes}</div></div>{_notes(spec)}</section>')


def chart(spec):
    cats = spec["categories"]
    series = list(spec["series"].values())[0]
    mx = max(series) or 1
    bars = ""
    for c, v in zip(cats, series):
        h = int(v / mx * 100)
        bars += (f'<div class="bar-wrap"><div class="bar" data-h="{h}%" style="height:0">'
                 f'<span class="bar-val">{esc(v)}</span></div>'
                 f'<div class="bar-cat">{esc(c)}</div></div>')
    return (f'<section class="slide">{_head(spec)}<div class="body">'
            f'<div class="card" style="flex:1;display:flex"><div class="chart">{bars}</div></div>'
            f'</div>{_notes(spec)}</section>')


def closing(spec):
    cta = spec.get("cta", [])
    if isinstance(cta, str):
        cta = [cta]
    items = "".join(
        f'<div class="cta-item" data-anim="up" data-delay="{200+i*70}"><span class="dot"></span>{esc(c)}</div>'
        for i, c in enumerate(cta[:8]))
    sub = f'<div class="closing-sub" data-anim="up" data-delay="140">{esc(spec["subtitle"])}</div>' if spec.get("subtitle") else ""
    return (f'<section class="slide closing"><div class="closing-l">'
            f'<div class="closing-title" data-anim="up">{esc(spec["title"])}</div>'
            f'<div class="rule" data-anim="up" data-delay="100"></div>{sub}</div>'
            f'<div class="closing-r">{items}</div>{_notes(spec)}</section>')


BUILDERS = {
    "cover": cover, "section": section, "grid": grid, "numbered_list": numbered_list,
    "bullets": bullets, "two_column": two_column, "process": process, "stats": stats,
    "timeline": timeline, "quote": quote, "pyramid": pyramid, "cycle": cycle,
    "chart": chart, "closing": closing,
}


def render_html_deck(SLIDES, out_path, theme="red", title="演示文稿", philosophy=None):
    """theme=6 色主题；philosophy=设计哲学（整套视觉语言，自带调色板，覆盖 theme）。"""
    if philosophy is not None and philosophy not in PHILOSOPHIES:
        raise ValueError(f"未知设计哲学「{philosophy}」，可选：{', '.join(PHILOSOPHIES)}")
    if philosophy is None and theme not in D.THEMES:
        raise ValueError(f"未知主题「{theme}」，可选：{', '.join(D.THEMES)}")
    body_attr = f'data-philosophy="{philosophy}"' if philosophy else f'data-theme="{theme}"'
    body = "".join(BUILDERS[s["type"]](s) for s in SLIDES)
    doc = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>
{_theme_css()}
{_philosophy_css()}
{CSS}
</style></head>
<body {body_attr}>
<div class="deck" id="deck">
{body}
</div>
<div class="nav"><button onclick="go(-1)">‹</button><span class="ct" id="ct"></span><button onclick="go(1)">›</button></div>
<button class="topbtn exp" onclick="window.print()">导出 PDF</button>
<button class="topbtn pres" onclick="openPres()">演讲者 (S)</button>
<script>{JS}</script>
</body></html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"生成 HTML {len(SLIDES)} 页 / 主题 {theme} -> {os.path.abspath(out_path)}")
    return out_path
