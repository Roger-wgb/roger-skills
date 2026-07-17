#!/usr/bin/env python3
"""把 PPTX 渲染成每页 PNG + montage 总览图，供逐页复核。

这是整套 skill 里最重要的一环：让生成者看见自己的产出。
没有它，就是盲拼坐标 —— 版式可以正确，但没人知道好不好看。

预览字体替换：PPT 通常声明 Microsoft YaHei（分发对象多为 Windows），
但本机渲染器不一定有。渲染前会把字体替换成本机可用的中文字体，
只影响预览副本，不动原文件。

用法：
    python3 preview.py deck.pptx                  # 出图 + montage
    python3 preview.py deck.pptx --pages 5,11,42  # 只出指定页
"""

import glob
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doctor  # noqa: E402


def _swap_font(src, dst, font_name):
    from pptx import Presentation
    prs = Presentation(src)
    for s in prs.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    r.font.name = font_name
    prs.save(dst)


def _render_font_name():
    """挑一个渲染器和 PIL 都认得的中文字体名。"""
    f = doctor.check_font()
    if not f:
        return None
    base = os.path.basename(f)
    if "Noto" in base:
        return "Noto Sans CJK SC"
    if "STHeiti" in base:
        return "Heiti SC"
    if "msyh" in base:
        return "Microsoft YaHei"
    return None


def render(pptx_path, outdir=None, dpi=100, pages=None, montage_cols=6):
    soffice, pdf2png, ok, msg = doctor.check_renderer()
    if not ok:
        return None, f"渲染不可用：{msg}"

    pptx_path = os.path.abspath(pptx_path)
    outdir = outdir or os.path.join(os.path.dirname(pptx_path), "_preview")
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)

    tmp = tempfile.mkdtemp(prefix="pptprev_")
    try:
        src = pptx_path
        fname = _render_font_name()
        if fname:
            src = os.path.join(tmp, "render.pptx")
            _swap_font(pptx_path, src, fname)

        subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                        "--outdir", tmp, src], capture_output=True, timeout=600)
        pdfs = glob.glob(os.path.join(tmp, "*.pdf"))
        if not pdfs:
            return None, "LibreOffice 未能产出 PDF"
        pdf = pdfs[0]

        cmd = [shutil.which("pdftoppm"), "-png", "-r", str(dpi)]
        if pages:
            lo, hi = min(pages), max(pages)
            cmd += ["-f", str(lo), "-l", str(hi)]
        cmd += [pdf, os.path.join(outdir, "page")]
        subprocess.run(cmd, capture_output=True, timeout=600)

        pngs = sorted(glob.glob(os.path.join(outdir, "page-*.png")))
        if not pngs:
            return None, "PDF 转 PNG 失败"

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
    except subprocess.TimeoutExpired:
        return None, "渲染超时"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法: python3 preview.py deck.pptx [--pages 1,5,9]")
    pages = None
    if "--pages" in sys.argv:
        pages = [int(x) for x in sys.argv[sys.argv.index("--pages") + 1].split(",")]
    res, err = render(sys.argv[1], pages=pages)
    if err:
        sys.exit(f"❌ {err}")
    print(f"✅ {len(res['pages'])} 页 -> {res['dir']}")
    if res["montage"]:
        print(f"   montage: {res['montage']}")
