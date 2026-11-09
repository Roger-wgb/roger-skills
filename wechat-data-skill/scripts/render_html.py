#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 fetch_chat.py 生成的 messages.json（可再加一份总结）渲染成单文件 HTML 报告。

HTML 输出要求见 references/html_output_requirements.md。
要点：
  - 顶部信息卡：明确「聊天对象」（群名/人名 + 单聊/群聊 + username + 区间 + 条数）
  - 总结区（若有 --summary）
  - 对话现场回看：按天分隔的时间线气泡，me=右侧、对方=左侧，群聊按成员着色
  - 单文件、无外部依赖，浏览器直接打开

示例：
  python render_html.py --messages out/messages.json --summary out/summary.md --output report.html
"""
from __future__ import annotations

import argparse
import html as H
import json
import re
import sys
from pathlib import Path

import wechat_env

wechat_env.ensure_utf8()

PALETTE = [
    "#2f6fb2", "#2f8e6e", "#b2762f", "#8a4fb0", "#b04f6a",
    "#4f8fb0", "#7a8a2f", "#b0692f", "#556b9e", "#2f9e8c",
]

ME_NAMES = {"me", "我", "自己"}


def esc(s):
    return H.escape(str(s), quote=True)


def member_color(name: str, is_group: bool):
    if is_group:
        idx = sum(ord(c) for c in name) % len(PALETTE)
        return PALETTE[idx]
    return "#687067"


def media_chip(content: str):
    """把 [图片]/[视频]/[文件] 等头部标记映射成占位标签，返回 (chip_html, rest)。"""
    m = re.match(r"^\[([^\]]+)\]", content.strip())
    if not m:
        return "", content
    tag = m.group(1)
    rest = content.strip()[m.end():].strip()
    mapping = [
        ("图片", "🖼", "img"), ("视频", "🎬", "video"), ("语音", "🎙", "voice"),
        ("文件", "📎", "file"), ("链接", "🔗", "link"), ("红包", "🧧", "red"),
        ("转账", "💰", "red"), ("系统", "📢", "sys"), ("位置", "📍", "loc"),
    ]
    for key, icon, cls in mapping:
        if key in tag:
            return f'<span class="chip chip-{cls}">{icon} {esc(tag)}</span>', rest
    return "", content


def _inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
    s = re.sub(
        r"(https?://[^\s<]+)",
        r'<a href="\1" target="_blank" rel="noreferrer">\1</a>',
        s,
    )
    return s


def mini_md_to_html(text: str) -> str:
    """极简 Markdown 子集：标题 / 无序列表 / 段落 / 加粗 / 行内代码 / 链接。够总结用。"""
    out = []
    in_list = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        m = re.match(r"^(\s*)(#{1,6})\s+(.*)$", line)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            lvl = len(m.group(2))
            out.append("<h" + str(lvl) + ">" + _inline(m.group(3)) + "</h" + str(lvl) + ">")
            continue
        m = re.match(r"^(\s*)[-*•]\s+(.*)$", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + _inline(m.group(2)) + "</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        out.append("<p>" + _inline(line) + "</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def load_summary(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            return text
        if isinstance(obj, dict):
            parts = []
            for k, v in obj.items():
                if isinstance(v, list):
                    items = "".join("<li>" + esc(x) + "</li>" for x in v if x)
                    if items:
                        parts.append("<h3>" + esc(k) + "</h3><ul>" + items + "</ul>")
                else:
                    if v:
                        parts.append("<h3>" + esc(k) + "</h3><p>" + esc(v) + "</p>")
            return "\n".join(parts)
        return text
    return mini_md_to_html(text)


def build_bubbles(data: dict) -> str:
    msgs = data.get("messages", [])
    is_group = bool(data.get("is_group"))
    out = []
    last_date = None
    last_their_sender = None
    for m in msgs:
        time = m.get("time", "")
        date = time[:10]
        clock = time[11:16] if len(time) >= 16 else ""
        sender = (m.get("sender", "") or "?").strip()
        content = m.get("content", "")
        if date and date != last_date:
            out.append('<div class="day">' + esc(date) + "</div>")
            last_date = date
            last_their_sender = None
        mine = (sender.lower() in ME_NAMES)
        chip, rest = media_chip(content)
        body = chip + ("<div class='content'>" + _inline(rest) + "</div>" if rest else "") if chip \
            else "<div class='content'>" + _inline(content) + "</div>"
        # 名字标签：对方连续发言只显示一次；单聊也显示对方名字，避免“不知道谁”。
        show_name = (not mine) and (sender != last_their_sender)
        name_html = ""
        if show_name:
            name_html = ('<div class="name" style="color:' + member_color(sender, is_group) + '">'
                         + esc(sender) + "</div>")
        if not mine:
            last_their_sender = sender
        out.append(
            '<div class="row ' + ("mine" if mine else "theirs") + '">'
            '<div class="bubble">' + name_html + body
            + '<div class="time">' + esc(clock) + "</div></div></div>"
        )
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="把消息渲染成单文件 HTML 报告")
    ap.add_argument("--messages", required=True, help="messages.json（fetch_chat.py 生成）")
    ap.add_argument("--summary", default=None, help="可选：summary.md / summary.json")
    ap.add_argument("--title", default=None, help="标题（默认用聊天对象+区间）")
    ap.add_argument("--output", default=None, help="输出文件名（默认 report.html）")
    args = ap.parse_args()

    with open(args.messages, encoding="utf-8") as f:
        data = json.load(f)

    summary_html = load_summary(args.summary) if args.summary else ""
    chat = data.get("chat") or "未知会话"
    is_group = bool(data.get("is_group"))
    kind = "群聊" if is_group else "单聊"
    username = data.get("username") or ""
    span = (data.get("since") or "?") + " ~ " + (data.get("until") or "?")
    total = data.get("total", 0)
    truncated = bool(data.get("truncated"))

    title = args.title or (chat + " · " + kind + " · " + span)

    meta_chips = (
        '<span class="kind ' + ("g" if is_group else "p") + '">' + kind + "</span>"
        + ('<span class="usn">' + esc(username) + "</span>" if username else "")
    )
    head = (
        '<header class="card">'
        '<div class="kicker">微信聊天记录 · 时间段报告</div>'
        '<h1>' + esc(chat) + "</h1>"
        '<div class="meta">' + meta_chips + '</div>'
        '<div class="meta-line">区间 ' + esc(span) + " · 共 " + str(total) + " 条"
        + (' · <span class="warn">⚠ 某单日超过容量被截断，可加大 --day-cap 重拉</span>' if truncated else "")
        + "</div>"
        "</header>"
    )

    summary_section = ""
    if summary_html:
        summary_section = ('<section class="card summary"><div class="sec-kicker">总结</div>'
                           '<div class="summary-body">' + summary_html + "</div></section>")

    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    --paper:#f3f5ef; --ink:#20231f; --muted:#687067; --line:#d8ded2;
    --card:#ffffff; --rust:#b45f2a; --green:#287a5b; --blue:#415f8f; --gold:#d39b35;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif; }}
  .wrap {{ max-width:820px; margin:0 auto; padding:20px 14px 56px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
    padding:16px 20px; box-shadow:0 8px 24px rgba(79,48,22,.06); }}
  header.card {{ margin-bottom:16px; }}
  .kicker {{ color:var(--rust); font-size:12px; letter-spacing:.12em; font-weight:700;
    text-transform:uppercase; margin-bottom:6px; }}
  header h1 {{ margin:0 0 6px; font-size:24px; }}
  .meta {{ margin:2px 0 8px; }}
  .kind {{ display:inline-block; padding:1px 8px; border-radius:6px; font-size:12px;
    margin-right:8px; vertical-align:middle; }}
  .kind.g {{ background:#eaf3ec; color:var(--green); }}
  .kind.p {{ background:#e8eef7; color:var(--blue); }}
  .usn {{ color:var(--muted); font-family:ui-monospace,Consolas,monospace; font-size:12px; }}
  .meta-line {{ color:var(--muted); font-size:13px; }}
  .warn {{ color:#c0392b; }}
  section.summary {{ margin:0 0 18px; }}
  .sec-kicker {{ color:var(--green); font-weight:700; font-size:12px; letter-spacing:.1em;
    text-transform:uppercase; margin-bottom:8px; }}
  .summary-body h1,.summary-body h2,.summary-body h3,.summary-body h4 {{ font-size:14px;
    margin:10px 0 4px; color:#20231f; }}
  .summary-body ul {{ margin:4px 0 8px; padding-left:20px; }}
  .summary-body li {{ margin:2px 0; line-height:1.6; }}
  .summary-body p {{ margin:6px 0; line-height:1.65; }}
  .day {{ text-align:center; color:#9a9da5; font-size:12px; margin:16px 0 10px; }}
  .row {{ display:flex; margin:6px 0; }}
  .row.theirs {{ justify-content:flex-start; }}
  .row.mine {{ justify-content:flex-end; }}
  .bubble {{ max-width:80%; background:#fff; border:1px solid var(--line);
    border-radius:12px; padding:7px 12px; }}
  .row.mine .bubble {{ background:#d9f2c5; border-color:#c6e6ab; }}
  .name {{ font-size:11px; color:var(--muted); margin-bottom:2px; }}
  .body {{ font-size:14px; line-height:1.55; word-break:break-word; }}
  .body .content {{ white-space:pre-wrap; }}
  .time {{ font-size:10px; color:#a0a3aa; margin-top:3px; text-align:right; }}
  .chip {{ display:inline-block; font-size:12px; padding:1px 8px; border-radius:6px;
    background:#eef0f2; margin:2px 4px 2px 0; }}
  .chip-img{{background:#e8f3ec;}}.chip-video{{background:#fdeee9;}}.chip-voice{{background:#eef0fd;}}
  .chip-file{{background:#f3efe6;}}.chip-link{{background:#e8eef7;}}.chip-red{{background:#fdecec;}}
  .chip-sys{{background:#eee8f7;}}.chip-loc{{background:#eaf6fb;}}
  a {{ color:#1769aa; word-break:break-all; }}
  footer {{ color:#9a9da5; font-size:11px; margin-top:24px; text-align:center; }}
</style>
</head>
<body>
<div class="wrap">
  {head}
  {summary_section}
  <div class="chat">{bubbles}</div>
  <footer>由 wechat-data-skill 生成 · 原始数据见 raw_chat.txt</footer>
</div>
</body>
</html>
"""
    html_out = page.format(
        title=esc(title), head=head, summary_section=summary_section,
        bubbles=build_bubbles(data),
    )
    out_path = Path(args.output) if args.output else Path(args.messages).parent / "report.html"
    out_path.write_text(html_out, encoding="utf-8")
    print("已写:", out_path)


if __name__ == "__main__":
    sys.exit(main())
