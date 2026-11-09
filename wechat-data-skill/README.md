# wechat-data-skill

抓取本机微信聊天记录（**个人单聊 / 群聊都支持**），输出 4 种形态：原始记录 / HTML 报告 / 时间段总结 / 自定义。
Agent 无关：Claude Code、Cursor、其它支持 skills 目录的 AI Agent 都可用。

**本技能自带 wechat-cli**：源码与依赖 wheel 已随包（`vendor/`），首次跑自检会在技能目录里自动建好环境。
对安装它的人，前置只剩两个——**装过 Python 3.10+、打开微信**。

## 目录
- `SKILL.md` —— 技能入口（指令与工作流）
- `vendor/wechat-cli-plus/` —— wechat-cli（maomao3334/wechat-cli-plus，微信 4.1 用）源码快照（含 LICENSE）
- `vendor/wheels/` —— 它的依赖 wheel（click / pycryptodome / zstandard + 构建工具）
- `.venv/` —— 首次自检自动生成（技能自带的运行环境，**别手动拷/删，坏了自检会自动重建**）
- `config.json` —— 可选配置（默认输出目录；**无需填任何机器路径**）
- `config.example.json` —— 配置模板（含字段说明）
- `scripts/` —— `selfcheck.py`（自动建环境+提密钥）、`fetch_chat.py`（取数）、`render_html.py`（HTML）、`wechat_env.py`（共享）
- `references/` —— `summary_prompt.md`（总结默认参考）、`html_output_requirements.md`（HTML 输出要求）

## 快速开始
```bash
# 1) 唯一一步：前置自检（首次会【自动】建自带 wechat-cli 环境并提密钥）
#    微信需打开并登录
python scripts/selfcheck.py

# 2) 抓某段时间的聊天（≤2000 行单文件；更多自动分批）
python scripts/fetch_chat.py --chat "捡姑娘的小蘑菇" --since 2026-09-01 --until 2026-09-08

# 3) 出 HTML 报告（先有总结再渲染）
python scripts/render_html.py --messages out/messages.json --summary out/summary.md --output out/report.html
```

## 换机器/换人要装什么？→ 就两样
1. **Python 3.10+**（三个脚本只用标准库；建自带环境时也要用）。
2. **微信 PC 端**已安装、已登录、保持运行（密钥来源；只有它没法随包）。

装好后：整个技能文件夹拷过去 → 打开微信登录 → 跑一次 `selfcheck.py` → 完成。
不需要 git、不需要自己装 wechat-cli、不需要 npm，也**不用改任何配置路径**。

> 首次建环境默认完全离线（用随包 wheel）。只有本机 Python 与自带 wheel 不匹配（极少见，如换了操作系统/位数）才需要联网一次从 PyPI 拉依赖。

## config.json（可以完全不填）
自带 wechat-cli 已随技能，`fetch_cli` 不再需要。逐项：

| 键 | 说明 | 必填 |
|---|---|---|
| `default_out_dir` | 默认输出目录（相对技能根或绝对路径） | 否（默认 `out`） |
| `db_dir` | 微信消息库目录，仅 `init --force` 补救提示用 | 否（自动探测最近活跃账号） |
| `fetch_cli` | 只有在想**改用系统里别的** wechat-cli 时才填 | 否（优先级：`--cli` > 技能自带 `.venv` > `WECHAT_CLI` > 本项 > PATH） |

## 数据源要点（踩过的坑）
- **微信 4.1 必须用 fork 版**（本技能已 vendor maomao3334/wechat-cli-plus）；npm 的 jackwener wx.exe 在 4.1 下失效。
- **时间上没有工具限制**，能回溯多远 = 本机数据库实际存了多久（换机/清理会少）。
- **大跨度自动分批**：单批上限 `--batch-lines 2000` 行，超出自动把时间窗对半细分取全后落多文件 + `manifest.json`；别依赖 offset 分页。
- 微信按需新建 `message_N.db`；"近期取不到但列表有预览" = 新库缺密钥 → `wechat-cli init --force`（自检失败时会给命令）。
- 想随 fork 上游更新：把 `C:\Users\Roger\wechat-cli-4x\fork`（或 clone 的新源码）整包换进 `vendor/wechat-cli-plus/`，删掉 `.venv` 再跑自检即可重建。

## 命令参考
```bash
# 取数（超 --batch-lines 行自动分批成多文件 + manifest.json）
python scripts/fetch_chat.py --chat <聊天对象> \
  [--since YYYY-MM-DD] [--until YYYY-MM-DD] \
  [--batch-lines 2000] [--day-cap 50000] [--format both|txt|json] \
  [--out <目录>] [--cli <wechat-cli路径>]

python scripts/render_html.py --messages out/messages.json \
  [--summary out/summary.md] [--output report.html]

python scripts/selfcheck.py   # 首次自动建环境+提密钥；日常跑它看前置是否 OK
```
