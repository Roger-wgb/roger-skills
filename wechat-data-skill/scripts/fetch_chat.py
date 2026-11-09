#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取微信聊天记录（个人单聊 / 群聊均可），时间范围可任填。

数据源 wechat-cli 已随本技能自带（vendor/，首次跑 scripts/selfcheck.py 自动建好）；
也可用 --cli / WECHAT_CLI / config.fetch_cli 临时改用别的。工具本身无时间上限，
可回溯深度 = 本机数据库实际保留量。

自动分批：
  默认单个导出批次上限 --batch-lines 2000 行。当某时间窗取回 == 上限（说明可能被截断），
  会自动把该时间窗对半细分再取，直到每段都能完整取回——因此大范围（几年）导出的结果
  按时间顺序拆成多个文件，不会因"消息太多"丢内容，也不会产生一个超大单文件。
  极端情况：同一天内消息超过 --day-cap（默认 50000）才会放弃并标记 truncated。

输出（--out 目录）：
  单批（≤batch-lines 行）：
    raw_chat.txt   原文行，按时间升序，不加工；首行含明确聊天对象
    messages.json  结构化消息数组 + 元信息
  多批（超过 batch-lines 行）：
    raw_chat_0001.txt / raw_chat_0002.txt …   按时间顺序
    messages_0001.json / …                   各批结构化
    manifest.json                             批次清单（时段→文件、条数、是否完整），可续传

示例：
  python fetch_chat.py --chat "捡姑娘的小蘑菇" --since 2026-09-01 --until 2026-09-08
  python fetch_chat.py --chat "某群" --since 2024-01-01 --until 2026-09-08   # 自动分批
  python fetch_chat.py --chat "某群" --since 2024-01-01 --batch-lines 500    # 更小的每批
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import wechat_env

wechat_env.ensure_utf8()

LINE_RE = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}(?::\d{2})?)\]\s+(.*?):\s*([\s\S]*)$"
)


def utf_env():
    env = dict(os.environ)
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def run_cli(cli: str, args: list) -> dict:
    proc = subprocess.run(
        [cli, *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=utf_env(), timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "wechat-cli 调用失败：\n"
            f"命令: {cli} {' '.join(args)}\n"
            f"STDOUT: {proc.stdout[:500]}\n"
            f"STDERR: {proc.stderr[:500]}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("wechat-cli 返回的不是 JSON（可能是密钥/数据库问题）：\n"
                           + proc.stdout[:500])


def fetch_one(cli: str, chat: str, start: str, end: str, limit: int):
    data = run_cli(
        cli,
        ["history", chat, "--start-time", start, "--end-time", end,
         "--limit", str(limit), "--format", "json"],
    )
    return data.get("messages", []), data


def _split(s: dt.date, e: dt.date):
    """把 [s,e] 从中间切成两半，返回 (左半, 右半)。"""
    if s >= e:
        return (s, s), (s, s)
    days = (e - s).days
    mid = s + dt.timedelta(days=days // 2)
    left = (s, mid)
    right = (mid + dt.timedelta(days=1), e) if mid < e else (mid, mid)
    return left, right


def fetch_split(cli: str, chat: str, since: dt.date, until: dt.date,
                cap: int, day_cap: int):
    """把 [since, until] 按时间窗递归取数，直到每段都完整。

    返回 (segments, meta, any_truncated)：
      - segments：按时间排序 [(start, end, raw_lines)]，每段 raw_lines 数 ≤ cap
      - meta：第一条响应里的会话元信息（chat / username / is_group）
      - any_truncated：某单日超过 day_cap，结果可能不完整
    """
    stack = [(since, until)]
    segments = []
    meta = {}
    any_truncated = False
    while stack:
        s, e = stack.pop()
        lines, resp = fetch_one(cli, chat, s.isoformat(), e.isoformat(), cap)
        if not meta and resp.get("chat"):
            meta = resp
        if len(lines) < cap:
            segments.append((s, e, lines))
            continue
        # 返回 == cap：可能被截断 → 若还能再分就细分
        if s < e:
            (s1, e1), (s2, e2) = _split(s, e)
            stack.append((s2, e2))
            stack.append((s1, e1))
            continue
        # 同一天也超过 cap：用大额 day_cap 尽力一次拉全
        big, resp_big = fetch_one(cli, chat, s.isoformat(), s.isoformat(), day_cap)
        if not meta and resp_big.get("chat"):
            meta = resp_big
        if len(big) < day_cap:
            segments.append((s, e, big))
        else:
            segments.append((s, e, big))
            any_truncated = True  # 当天消息超过 day_cap，极罕见
    segments.sort(key=lambda seg: (seg[0].isoformat(), seg[1].isoformat()))
    return segments, meta, any_truncated


def parse_line(raw: str) -> dict:
    m = LINE_RE.match(raw)
    if not m:
        return {"time": "", "sender": "", "content": raw, "raw": raw}
    date, clock, sender, content = m.groups()
    return {"time": f"{date} {clock}", "sender": sender.strip(),
            "content": content, "raw": raw}


def parse_messages(raw_lines) -> list:
    msgs = [parse_line(l.strip("\n")) for l in raw_lines if isinstance(l, str)]
    msgs = [m for m in msgs if m["time"]]
    msgs.sort(key=lambda m: m["time"])
    return msgs


def main():
    ap = argparse.ArgumentParser(description="抓取微信聊天记录（个人/群），超阈值自动分批")
    ap.add_argument("--chat", required=True, help="会话名称：昵称/备注/群名")
    ap.add_argument("--since", default=None, help="起始日期 YYYY-MM-DD（默认：今天前 7 天）")
    ap.add_argument("--until", default=None, help="结束日期 YYYY-MM-DD（默认：今天）")
    ap.add_argument("--out", default=None, help="输出目录（默认 config.default_out_dir）")
    ap.add_argument("--cli", default=None, help="覆盖 wechat-cli 路径")
    ap.add_argument("--config", default=None, help="config.json 路径")
    ap.add_argument("--batch-lines", type=int, default=2000,
                    help="单个导出批次最多行数，超过自动分批（默认 2000）")
    ap.add_argument("--day-cap", type=int, default=50000,
                    help="同一天内超过此行数才放弃标记截断（默认 50000）")
    ap.add_argument("--format", default="both", choices=["txt", "json", "both"],
                    help="输出（默认 both：raw/messages）")
    args = ap.parse_args()

    if args.batch_lines < 1:
        ap.error("--batch-lines 至少为 1")
    cfg = wechat_env.load_config(args.config)
    cli = wechat_env.resolve_cli(cfg, explicit=args.cli)

    today = dt.date.today()
    since = dt.date.fromisoformat(args.since) if args.since else today - dt.timedelta(days=7)
    until = dt.date.fromisoformat(args.until) if args.until else today
    if since > until:
        since, until = until, since
    since_s, until_s = since.isoformat(), until.isoformat()

    default_out = cfg.get("default_out_dir") or "out"
    out_dir = Path(args.out) if args.out else (
        Path(default_out) if os.path.isabs(default_out) else wechat_env.skill_root() / default_out
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    segments, meta0, any_truncated = fetch_split(cli, args.chat, since, until,
                                                 args.batch_lines, args.day_cap)
    total = sum(len(lines) for _, _, lines in segments)

    # 把（按时间升序的）段落逐行攒成每个严格 ≤batch-lines 的文件；
    # 单段可能正好 cap 条、也可能某天 >day_cap 超长，逐行切才能保证不超发
    chunks = []  # list of list[str]，每份行数 ≤ batch-lines
    cur = []
    for _s, _e, lines in segments:
        for line in lines:
            cur.append(line)
            if len(cur) >= args.batch_lines:
                chunks.append(cur)
                cur = []
    if cur:
        chunks.append(cur)

    resolved = {
        "chat": meta0.get("chat", args.chat),
        "username": meta0.get("username", ""),
        "is_group": bool(meta0.get("is_group")),
        "chat_kind": "?",
    }
    # 区间内零消息时，meta 可能是空的 → 额外探测一次会话身份（仍报空结果）
    if not meta0.get("chat"):
        try:
            _, meta_probe = fetch_one(cli, args.chat, since_s, until_s, 1)
            resolved.update({
                "chat": meta_probe.get("chat", args.chat),
                "username": meta_probe.get("username", ""),
                "is_group": bool(meta_probe.get("is_group")),
            })
        except Exception:
            pass
    resolved["chat_kind"] = "群聊" if resolved["is_group"] else "单聊"

    print(f"聊天对象: {resolved['chat']} [{resolved['chat_kind']}]  username: {resolved['username']}")
    print(f"区间: {since_s} ~ {until_s} | 总条数: {total} | 分批: {len(chunks)} 个文件"
          + (" | ⚠ 存在超过单日容量被截断的时段" if any_truncated else ""))
    if not chunks:  # 0 条也产出一个空文件（带头部），下游不崩
        chunks = [[]]

    written = []
    only_one = len(chunks) == 1 and not any_truncated
    for i, chunk in enumerate(chunks, start=1):
        seq = "" if only_one else f"_{i:04d}"
        msgs = parse_messages(chunk)
        t_first = msgs[0]["time"] if msgs else ""
        t_last = msgs[-1]["time"] if msgs else ""
        if args.format in ("txt", "both"):
            txt_path = out_dir / f"raw_chat{seq}.txt"
            header = (f"聊天对象: {resolved['chat']} ({resolved['chat_kind']}) | "
                      f"username: {resolved['username']} | 区间: {since_s} ~ {until_s} | "
                      f"本批: {len(chunk)} 条" + (f" | {t_first} ~ {t_last}" if t_first else "")
                      + (f"\n批次: {i}/{len(chunks)}" if not only_one else "") + "\n\n")
            txt_path.write_text(header + "\n".join(chunk), encoding="utf-8")
            written.append({"index": i, "raw": txt_path.name,
                            "start": t_first, "end": t_last, "count": len(chunk)})
        if args.format in ("json", "both"):
            js_name = (f"messages{seq}.json")
            payload = {"chat": resolved["chat"], "username": resolved["username"],
                       "is_group": resolved["is_group"], "chat_kind": resolved["chat_kind"],
                       "since": since_s, "until": until_s,
                       "batch": i, "batches": len(chunks),
                       "total_batch": len(chunk), "truncated": any_truncated,
                       "messages": msgs}
            js_path = out_dir / js_name
            js_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                               encoding="utf-8")
            written[-1]["json"] = js_name

    if not only_one:
        manifest = {"chat": resolved["chat"], "username": resolved["username"],
                    "is_group": resolved["is_group"], "chat_kind": resolved["chat_kind"],
                    "since": since_s, "until": until_s, "total": total,
                    "batch_lines": args.batch_lines, "truncated": any_truncated,
                    "batches": written}
        mf_path = out_dir / "manifest.json"
        mf_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print("批次清单:", mf_path)

    for w in written:
        print("  批次 %d: %s （%d 条%s）" % (w["index"], w["raw"], w["count"],
              ("，"+w["start"]+" ~ "+w["end"]) if w.get("start") else ""))
    if any_truncated:
        print("⚠ 某单日消息超过 --day-cap，那一段结果可能不完整；可加大 --day-cap 重跑。")


if __name__ == "__main__":
    sys.exit(main())
