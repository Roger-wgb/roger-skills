---
name: wechat-data-skill
description: 抓取微信聊天记录（个人单聊/群聊都支持），按需输出四种形态：① 某时间段原始聊天记录（不加工）② HTML 报告（聊天对象信息卡+总结+对话回看）③ 某时间段聊天总结 ④ 按用户自定义要求输出。技能自带 wechat-cli，前置仅 Python+微信；首次跑 scripts/selfcheck.py 自动建环境并提密钥。大跨度自动分批（默认 2000 行/批）。
---

# Wechat Data Skill

抓取本机微信聊天记录（**个人单聊与群聊均可**，按昵称/备注/群名自动匹配），把结果按用户要的形态交付。
本技能对运行它的 AI Agent 无偏好（Claude Code / Cursor / 其他支持 skills 目录的 agent 均可用），只按本文档与脚本工作。

**wechat-cli 已随本技能自带**（`vendor/`），不再需要安装它的人去别处找或装。

## 前置（换机器/换人）
1. **Python 3.10+**（跑脚本 & 建自带环境）。
2. **微信 PC 端已登录并保持运行**（密钥来源；只有它没法随包）。
3. 不需要 git、不需要自己装 wechat-cli、不需要 Node/npm。

首次使用只跑一次自检，它会**自动**完成建自带环境和提密钥：

```bash
python scripts/selfcheck.py
```

- 没有 `.venv` → 自动从 `vendor/` 离线装好自带 wechat-cli（默认不需联网；wheel 不匹配才联网回退）。
- 微信在运行但还没密钥 → 自动 `wechat-cli init` 提取。
- 逐项 ✅/❌；把 ❌ 按提示处理完再继续。**此后只要微信开着就能取数。**

## 三要素（每次解析出来）
1. **聊天对象**：昵称 / 备注 / 群名
2. **时间范围**：起止日期（没给时默认最近 7 天到今天）
3. **输出模式**：下面 1~4 的一种，或当场自定义

## 抓取（所有模式共用）

```bash
python scripts/fetch_chat.py --chat "<聊天对象>" --since YYYY-MM-DD --until YYYY-MM-DD
```

产出（默认 `out/`）：

- `raw_chat.txt` —— 原文行，按时间升序，不加工；**首行标明聊天对象与 username**，交付前确认命中的人/群正确（名字可能撞车，用 username 对一下）。
- `messages.json` —— 结构化消息 + 元信息（chat / username / is_group / chat_kind / span / total / truncated）。

**大跨度（一年两年、几万条）自动分批，不会丢也不会超长**：默认单批上限 `--batch-lines 2000` 行，
超出时脚本把时间窗自动对半细分、逐段取全后按序落盘，产出 `raw_chat_0001.txt / raw_chat_0002.txt …`
（各 ≤2000 行）＋同名 `messages_*.json` ＋ `manifest.json`（批次清单：时段→文件、条数、是否完整）。
要更大/更小每批就调 `--batch-lines`。总行数 ≤2000 时保持单文件，行为不变。
极端情况某**同一天**消息超过 `--day-cap`（默认 50000）才会在 manifest 标 `truncated` 并提示。

## 四种输出

### 模式 1：原始记录（不加工）
抓取后直接把 `raw_chat.txt` 交付，**不重排、不改写、不加总结**。
（多批时交付 `raw_chat_*.txt`＋`manifest.json`，或交付整个 out 目录路径；别只挑第一份。）

### 模式 3：时间段总结
抓取后，按 `references/summary_prompt.md` 对原文做总结，写 `out/summary.md` 交付。
（多批时：用户要整段结论就把每批都读一遍再归纳；只要其中一段，按 manifest 的时段对应文件读。超长时别把几万行原文一股脑塞进上下文，分批读、每批先记要点。）

### 模式 2：HTML 报告（信息卡 + 总结 + 对话回看）
1. 先按模式 3 生成总结；
2. 渲染（HTML 必须满足 `references/html_output_requirements.md`）：
```bash
python scripts/render_html.py \
  --messages out/messages.json \
  --summary out/summary.md \
  --output out/report.html
```
交付 `report.html`（单文件，浏览器直接打开）。

### 模式 4：按用户自定义要求输出
抓取拿到原文后，**严格照用户当场给的输出定义**组织（格式、维度、只看某类消息等都行）。用户要求优先于 `references/summary_prompt.md`。

## 边界与注意
- 可回溯深度 = 本机数据库实际保留量（单聊/群同此），不是工具限制。
- 新 `message_N.db` 会缺近期密钥导致取不到最新：`init --force` 可解（自检失败时会给出该命令）。
- `me` 是用户自己；群聊里其余是成员名；单聊里另一端是对方。
- 图片/附件默认只取到占位；需要媒体文件再跑抓取器的 `--media`。
- 改本机/装东西这类动作（如重建 `.venv`、`wechat-cli init`）前仍应跟使用者说明一句；`.venv` 坏了 `selfcheck` 会自动重建。
