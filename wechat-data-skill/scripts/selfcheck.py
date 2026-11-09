#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前置自检：跑一遍确认数据源可用。换机器/换人后要做的几乎只有它。

本技能已把 wechat-cli（maomao3334/wechat-cli-plus）的源码与依赖 wheel **vendor 进自身**，
所以前置只剩两个：
  1. Python 3.10+
  2. 微信 PC 端已登录并在运行
首次跑本脚本会自动完成：
  · 在技能目录建 .venv，从 vendor 离线装好自带 wechat-cli（无需 git / 无需去别处找）
  · 微信在运行时，若还没密钥会自动 wechat-cli init 提取
之后日常只要微信开着，直接取数即可。

用法：
  python scripts/selfcheck.py    # 自动建环境 + 提密钥 + 探测数据可读，逐项 ✅/❌
（旧的 --auto 已并入默认行为，保留仅为兼容，无额外作用。）
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import wechat_env

wechat_env.ensure_utf8()


def print_check(ok: bool, msg: str):
    print(("  ✅ " if ok else "  ❌ ") + msg)
    return ok


def external_cli(cfg: dict):
    """自带之外可能存在的 wechat-cli（env/config/PATH），仅用于降级提示。"""
    for s, v in [("WECHAT_CLI", os.environ.get("WECHAT_CLI")),
                 ("config.fetch_cli", cfg.get("fetch_cli"))]:
        if v and Path(v).exists():
            return str(Path(v)), s
    found = shutil.which("wechat-cli")
    if found:
        return str(Path(found)), "PATH"
    return None, ""


def weixin_running() -> list:
    try:
        ps = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace")
        return [ln for ln in ps.stdout.splitlines() if "Weixin.exe" in ln]
    except Exception:
        return []


def probe_sessions(cli: str) -> tuple[bool, str]:
    """探测一次密钥/数据是否可读。返回 (ok, 提示)。"""
    try:
        proc = subprocess.run(
            [cli, "sessions", "--limit", "1", "--format", "json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
            timeout=90,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return True, ""
        return False, (proc.stderr or proc.stdout or "").strip()[:200]
    except Exception as e:
        return False, str(e)


def run_init(cli: str, db: str | None) -> bool:
    """尝试提密钥。成功 True；失败给出手动命令提示（可能要管理员）。"""
    cmd = [cli, "init"]
    if db:
        cmd += ["--db-dir", db]
    print("  未读到密钥 → 自动 wechat-cli init 提取（微信需在运行）……")
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
            timeout=300,
        )
        tail = (proc.stdout or proc.stderr or "").strip()[-300:]
        if proc.returncode == 0:
            print("  init 输出：", tail.replace("\n", "\n      "))
            return True
        print("  ⚠ init 未成功：" + tail.replace("\n", " ") + " — 可能需要管理员权限，请手动执行：")
        print("    ", " ".join(cmd))
        return False
    except subprocess.TimeoutExpired:
        print("  ⚠ init 超时 —— 可能需要管理员权限，请手动执行：")
        print("    ", " ".join(cmd))
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description="wechat-data-skill 前置自检（自动建自带环境+提密钥）")
    ap.add_argument("--auto", action="store_true",
                    help="（已废弃）首次自检本就会自动建环境/提密钥，此参数无额外作用")
    args = ap.parse_args(argv)
    del args  # --auto 仅为兼容，忽略

    print("wechat-data-skill 前置自检\n" + "-" * 44)
    cfg = wechat_env.load_config()
    ok_all = True

    # 1) config（可选）
    if cfg:
        print_check(True, f"config.json 存在：{wechat_env.default_config_path()}")
    else:
        print_check(True, "config.json 缺省 —— 无妨（自带 wechat-cli 已随技能，无需写路径）")

    # 2) 自带 wechat-cli（没有就自动从 vendor 建出来）
    cli, cli_src = None, ""
    try:
        cli = wechat_env.ensure_bundled_cli(print_fn=print)
        cli_src = "技能自带 .venv"
        ok_all &= print_check(True, f"wechat-cli 可用（{cli_src}）：{cli}")
    except Exception as e:
        ok_all &= print_check(False, f"自带 wechat-cli 建立失败：{e}")
        alt, alt_src = external_cli(cfg)
        if alt:
            cli, cli_src = alt, alt_src + "（降级，非本技能自带）"
            print_check(True, f"改用手头已有的 wechat-cli：{cli}")
        else:
            print("  请确认：本机装了 Python 3.10+、可联网（或自带 wheel 匹配本机 Python），再重跑。")

    # 3) db_dir（尽力定位，仅提示）
    db = wechat_env.find_db_storage(cfg)
    if db:
        print_check(True, f"微信消息库目录：{db}")
    else:
        print_check(True, "未定位 db_dir（不影响取数；只有 init --force 补救时才用得上）")

    # 4) 微信进程 —— 密钥来源，必须开
    weixin = weixin_running()
    ok_all &= print_check(bool(weixin), "微信 PC（Weixin.exe）正在运行" +
                          (f"，共 {len(weixin)} 个进程" if weixin else "——请先打开并登录微信"))

    # 5) 密钥/数据可读：不行就自动 init 一次再探
    probe_ok = False
    if cli:
        probe_ok, _ = probe_sessions(cli)
        if not probe_ok and weixin:
            run_init(cli, db)
            probe_ok, _ = probe_sessions(cli)
        elif not probe_ok and not weixin:
            pass  # 第 4 步已提示开微信
    ok_all &= print_check(probe_ok, "密钥/数据可读（sessions 探测）")
    if not probe_ok and cli:
        print("\n  补救：确认微信已打开并登录后重跑自检。仍失败（尤其最近几天取不到但列表有预览）：")
        if db:
            print(f'  运行： {cli} init --force --db-dir "{db}"   再重跑。')
        else:
            print(f"  运行： {cli} init --force   再重跑。")

    print("-" * 44)
    print("自检" + ("通过 ✅" if ok_all else "未全部通过，请按上面 ❌ 项处理"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
