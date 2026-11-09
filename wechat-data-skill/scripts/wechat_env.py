#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共享工具：技能根目录定位、config 读取、wechat-cli 路径解析、自带环境构建。

自 wechat-cli 4.1 起，wechat-cli（maomao3334/wechat-cli-plus）源码与依赖已 **vendor 进本技能**：
  vendor/wechat-cli-plus/   源码快照
  vendor/wheels/            依赖 wheel（click / pycryptodome / zstandard + setuptools/wheel）
首次跑 `selfcheck.py` 会在技能目录里建 `.venv` 并离线装好自带 wechat-cli —— 之后**取数只用它**，
换机器装这个技能的人不再需要自己装/找 wechat-cli（前置只剩：Python 3.10+ 和打开微信）。

wechat-cli 路径解析顺序（fetch_chat 等共用）：
  1) 命令行 --cli（临时覆盖）
  2) 技能自带 .venv 里的 wechat-cli（本技能自带的那个）
  3) 环境变量 WECHAT_CLI
  4) config.json 的 fetch_cli（一般可留空）
  5) PATH 里的 wechat-cli
db_dir 仍是可选的（仅 init --force 补救提示用）；留空时自动探测常见位置。
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_utf8():
    """Windows 控制台默认 GBK，打印 ✅/中文会崩；统一切成 UTF-8。"""
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_config_path() -> Path:
    return skill_root() / "config.json"


def load_config(config_path=None) -> dict:
    cfg_path = Path(config_path) if config_path else default_config_path()
    if not cfg_path.exists():
        return {}
    with open(cfg_path, encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError:
            cfg = {}
    return cfg if isinstance(cfg, dict) else {}


# ---------------- 自带 wechat-cli（vendor）----------------

def bundled_venv() -> Path:
    return skill_root() / ".venv"


def bundled_cli() -> str | None:
    """技能自带 .venv 里的 wechat-cli 可执行文件路径；没建/不存在返回 None。"""
    venv = bundled_venv()
    exe = venv / ("Scripts/wechat-cli.exe" if os.name == "nt" else "bin/wechat-cli")
    return str(exe) if exe.exists() else None


def vendor_dir() -> Path:
    return skill_root() / "vendor"


def _pip(venv_py: Path, args, offline: bool) -> subprocess.CompletedProcess:
    cmd = [str(venv_py), "-m", "pip", "--disable-pip-version-check", "-q", *args]
    if offline:
        cmd += ["--no-index", "--find-links", str(vendor_dir() / "wheels")]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "")[-600:])
    return proc


def _venv_python_ok(venv_py: Path) -> bool:
    """自带的 venv 能不能真的跑起来（拷贝到别的机器/换 Python 后常会失效）。"""
    try:
        proc = subprocess.run([str(venv_py), "-c", "pass"], capture_output=True,
                              timeout=20)
        return proc.returncode == 0
    except Exception:
        return False


def ensure_bundled_cli(print_fn=print) -> str:
    """确保技能自带 wechat-cli 可用（没有/坏了就从 vendor 重建 .venv）。返回可执行路径。

    首选完全离线（只用 vendor/wheels）；若本机 Python 平台与自带 wheel 不匹配（如换了系统），
    自动回退到从 PyPI 在线装。装好之后才返回；失败抛错。
    """
    venv = bundled_venv()
    venv_py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    have = bundled_cli()
    if have:
        if _venv_python_ok(venv_py):
            return have
        print_fn("检测到自带环境异常（可能是拷贝/换机导致）→ 重建……")
        import shutil as _sh
        _sh.rmtree(venv, ignore_errors=True)
    src = vendor_dir() / "wechat-cli-plus"
    if not (src / "pyproject.toml").exists():
        raise RuntimeError("缺少 vendor/wechat-cli-plus（技能包不完整）")
    if not (vendor_dir() / "wheels").exists():
        raise RuntimeError("缺少 vendor/wheels（技能包不完整）")

    print_fn("首次使用：为技能建立自带 wechat-cli 环境（只装在本技能目录里）……")
    if not venv_py.exists():
        proc = subprocess.run([sys.executable, "-m", "venv", str(venv)],
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=300)
        if proc.returncode != 0:
            raise RuntimeError("创建 .venv 失败：" + (proc.stderr or "")[-400:])

    def step(tag, args):
        try:
            _pip(venv_py, args, offline=True)
            print_fn(f"  {tag}（离线 wheel）")
        except RuntimeError:
            print_fn(f"  {tag}：自带 wheel 与本机 Python 不匹配，改从 PyPI 装（需联网一次）……")
            _pip(venv_py, args, offline=False)
            print_fn(f"  {tag}（PyPI）")

    step("安装构建工具 setuptools/wheel", ["install", "setuptools", "wheel"])
    step("安装 wechat-cli-plus", ["install", "-e", str(src)])

    have = bundled_cli()
    if not have:
        raise RuntimeError("自带 wechat-cli 安装未完成，请把上面报错发出来排查。")
    print_fn(f"  自带 wechat-cli 就绪：{have}")
    return have


def resolve_cli(cfg: dict, explicit=None) -> str:
    """解析要用的 wechat-cli。只读不构建；缺自带环境时优先提示先跑 selfcheck。

    顺序：--cli > 自带 .venv > WECHAT_CLI > config.fetch_cli > PATH。
    """
    candidates = []
    if explicit:
        candidates.append(("--cli 参数", explicit))
    if bundled_cli():
        candidates.append(("技能自带 .venv", bundled_cli()))
    if os.environ.get("WECHAT_CLI"):
        candidates.append(("环境变量 WECHAT_CLI", os.environ["WECHAT_CLI"]))
    if cfg.get("fetch_cli"):
        candidates.append(("config.json 的 fetch_cli", cfg["fetch_cli"]))
    try:
        found = shutil.which("wechat-cli")
    except Exception:
        found = None
    if found:
        candidates.append(("PATH 上的 wechat-cli", found))

    for source, path in candidates:
        if path and Path(path).exists():
            return str(Path(path))

    src = "／".join(s for s, _ in candidates) or "（无）"
    raise RuntimeError(
        f"找不到可用的 wechat-cli（已按序找：{src}）。\n"
        "本技能自带它——先运行一次：  python scripts/selfcheck.py\n"
        "脚本会在本技能目录里自动建好自带环境并提密钥。"
    )


def find_db_storage(cfg: dict):
    """定位微信消息库目录（db_dir）。用于 init --force 的提示；找不到就返回 None。

    有多个微信账号时，取最近仍在写入的那个（db_storage 目录 mtime 最新）。"""
    db = (cfg.get("db_dir") or "").strip()
    if db and Path(db).exists():
        return db
    home = Path.home()
    cands = list((home / "xwechat_files").glob("*/db_storage")) if (home / "xwechat_files").exists() else []
    if not cands:
        return None
    return str(max(cands, key=lambda p: p.stat().st_mtime))
