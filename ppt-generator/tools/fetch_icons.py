#!/usr/bin/env python3
"""构建期脚本：把 Lucide 图标预渲染成 PNG 打包进 skill。

使用者【不需要】运行这个。图标已经预渲染在 assets/icons/ 里随 skill 分发。
只有想扩充图标库时才跑，需要：网络 + rsvg-convert（brew install librsvg）。

用法：
    python3 fetch_icons.py                # 拉默认图标集
    python3 fetch_icons.py brain cpu zap  # 追加指定图标

Lucide 是 ISC 协议，可自由商用。
"""

import os
import re
import subprocess
import sys
import shutil

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(SKILL_DIR, "assets", "icons")
CDN = "https://unpkg.com/lucide-static@latest/icons/{}.svg"

# 三种用色：品牌红（强调）/ 深灰（正文卡片）/ 白（深色底上）
COLORS = {"red": "#E60012", "ink": "#333333", "white": "#FFFFFF"}

# 商业/咨询/AI 场景常用图标集
DEFAULT_ICONS = [
    # 战略 · 目标
    "target", "compass", "map", "milestone", "flag", "route", "telescope",
    # 流程 · 结构
    "workflow", "git-branch", "git-merge", "network", "layers", "boxes",
    "component", "blocks", "shapes", "combine",
    # 数据 · 度量
    "bar-chart-3", "line-chart", "pie-chart", "trending-up", "trending-down",
    "gauge", "activity", "database", "table-2", "sigma",
    # AI · 技术
    "brain", "cpu", "bot", "sparkles", "zap", "wand-2", "binary", "terminal",
    # 人 · 组织
    "users", "user-check", "user-cog", "handshake", "presentation",
    "graduation-cap", "briefcase", "building-2",
    # 文档 · 卡片
    "file-text", "clipboard-list", "clipboard-check", "notebook-pen",
    "book-open", "scroll-text", "files", "archive",
    # 验证 · 质量
    "shield-check", "badge-check", "check-check", "scan-line", "microscope",
    "flask-conical", "test-tube", "search-check",
    # 运营 · 循环
    "refresh-cw", "repeat", "recycle", "history", "timer", "calendar-clock",
    "bell-ring", "radio",
    # 商业 · 价值
    "coins", "wallet", "receipt", "trending-up-down", "hand-coins",
    "chart-no-axes-combined", "percent", "banknote",
    # 状态 · 提示
    "circle-check", "circle-alert", "triangle-alert", "info", "lightbulb",
    "key-round", "lock", "unlock",
    # 方向 · 连接
    "arrow-right", "arrow-up-right", "chevrons-right", "move-right",
    "corner-down-right", "split", "merge", "waypoints",
    # 平台 · 系统
    "server", "cloud", "settings-2", "sliders-horizontal", "plug",
    "puzzle", "package", "container",
    # 场景 · 入口
    "message-square", "message-circle-question", "phone-call", "mail",
    "megaphone", "eye", "focus", "scan-search",
]


def need(cmd, hint):
    if not shutil.which(cmd):
        sys.exit(f"❌ 缺 {cmd}。{hint}")


def fetch(name):
    """下载 SVG，返回源码；失败返回 None。"""
    r = subprocess.run(["curl", "-sL", "-m", "20", CDN.format(name)],
                       capture_output=True, text=True)
    svg = r.stdout
    return svg if svg.startswith("<") and "<svg" in svg else None


def render(svg, name, color_key, hex_color, size=256):
    svg = svg.replace('stroke="currentColor"', f'stroke="{hex_color}"')
    svg = re.sub(r'stroke-width="[\d.]+"', 'stroke-width="2"', svg)
    tmp = os.path.join(ICON_DIR, f".{name}.tmp.svg")
    out = os.path.join(ICON_DIR, f"{name}-{color_key}.png")
    with open(tmp, "w") as f:
        f.write(svg)
    try:
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size),
                        "-b", "none", tmp, "-o", out], check=True,
                       capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        os.path.exists(tmp) and os.remove(tmp)


def main():
    need("curl", "系统应自带")
    need("rsvg-convert", "请先 brew install librsvg（仅扩充图标时需要）")
    os.makedirs(ICON_DIR, exist_ok=True)

    icons = sys.argv[1:] or DEFAULT_ICONS
    ok, fail = 0, []
    for i, name in enumerate(icons, 1):
        svg = fetch(name)
        if not svg:
            fail.append(name)
            continue
        if all(render(svg, name, k, v) for k, v in COLORS.items()):
            ok += 1
        else:
            fail.append(name)
        if i % 20 == 0:
            print(f"  ... {i}/{len(icons)}")

    print(f"\n✅ 成功 {ok} 个图标 × {len(COLORS)} 色 = {ok * len(COLORS)} 个 PNG")
    print(f"   位置：{ICON_DIR}")
    if fail:
        print(f"⚠️  失败（图标名可能有误）：{', '.join(fail)}")


if __name__ == "__main__":
    main()
