#!/usr/bin/env python3
"""HTML deck 自审：Chrome headless 逐页截图 + montage。

与 pptx 的 preview.py 对称 —— 让生成者看见 HTML 成品。
HTML deck 是横向一屏一页，靠 ?shot=N 参数无动画定位到第 N 页再截。

用法：
    python3 preview_html.py deck.html          # 每页 PNG + montage
    python3 preview_html.py deck.html --pages 1,5,9
"""

import glob
import os
import re
import shutil
import subprocess
import sys

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    return None


def count_slides(html_path):
    txt = open(html_path, encoding="utf-8").read()
    return len(re.findall(r'class="slide[ "]', txt))


def render(html_path, outdir=None, scale=2, pages=None, montage_cols=6):
    chrome = find_chrome()
    if not chrome:
        return None, "未找到 Chrome/Chromium/Edge，HTML 无法截图自审"

    html_path = os.path.abspath(html_path)
    n = count_slides(html_path)
    if n == 0:
        return None, "HTML 里没找到 .slide"
    idx = [p - 1 for p in pages] if pages else range(n)

    outdir = outdir or os.path.join(os.path.dirname(html_path), "_preview_html")
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)

    for i in idx:
        out = os.path.join(outdir, f"page-{i+1:02d}.png")
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={scale}", "--window-size=1280,720",
             "--default-background-color=00000000",
             f"--screenshot={out}", f"--virtual-time-budget=1200",
             f"file://{html_path}?shot={i}"],
            capture_output=True, timeout=60)

    pngs = sorted(glob.glob(os.path.join(outdir, "page-*.png")))
    if not pngs:
        return None, "Chrome 截图失败"

    montage = None
    if len(pngs) > 1 and shutil.which("magick"):
        montage = os.path.join(outdir, "montage.png")
        subprocess.run(["magick", "montage"] + pngs +
                       ["-tile", f"{montage_cols}x", "-geometry", "320x+5+5",
                        "-background", "#C8C8C8", montage],
                       capture_output=True, timeout=300)
        if not os.path.exists(montage):
            montage = None
    return {"pages": pngs, "montage": montage, "dir": outdir}, None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法: python3 preview_html.py deck.html [--pages 1,5,9]")
    pages = None
    if "--pages" in sys.argv:
        pages = [int(x) for x in sys.argv[sys.argv.index("--pages") + 1].split(",")]
    res, err = render(sys.argv[1], pages=pages)
    if err:
        sys.exit(f"❌ {err}")
    print(f"✅ {len(res['pages'])} 页 -> {res['dir']}")
    if res["montage"]:
        print(f"   montage: {res['montage']}")
