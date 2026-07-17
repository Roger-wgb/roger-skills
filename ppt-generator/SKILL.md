---
name: "ppt-generator"
description: "当用户提供内容（Markdown、.docx 路径、纯文本）并要求生成 PowerPoint 演示文稿、PPT、幻灯片、Slides 时激活。输出路演级 .pptx（PowerPoint 可编辑）或 .html（浏览器演讲）。内置企业科技风设计系统（白卡浅灰底、圆角、细描边、强调色仅作锚点）、6 种配色主题（红/蓝/绿/金/墨/紫，图标随主题染色）、107 个 Lucide 图标、原生可编辑图表、14 种版式。生成后跑硬闸口（文字溢出/越界/重叠/WCAG 对比度/红色占比/版式节奏），有渲染器时导出每页 PNG 与 montage 逐页自审。依赖分级：仅 python-pptx 即可生成；LibreOffice+poppler 可开启渲染自审；缺失时明确告知降级而非静默交付。"
version: "11.0.0"
author: "演示文稿生成专家"
---

# PPT Generator Skill

从结构化内容生成**路演级**演示文稿。输出 `.pptx`（可在 PowerPoint 编辑）或 `.html`（浏览器演讲）。

---

## 0. 先跑环境自检（第一步，不可跳过）

```bash
python3 tools/doctor.py
```

**必须把结论如实告诉用户**，尤其是降级的部分。绝不能默默交一份打折的东西。

| 级别 | 依赖 | 缺了会怎样 |
|---|---|---|
| **必需** | `python-pptx` | 无法生成，直接停 |
| **建议** | Pillow + 中文字体 | 文字度量退化为估算，长文本可能溢出 |
| **建议** | LibreOffice + poppler | **无法自审** —— 落差最大的一档 |
| **仅扩图标** | librsvg + 网络 | 用内置 107 个图标，够用 |

图标已预渲染在 `assets/icons/`（107 个 × 红/深灰/白 = 321 个 PNG），**使用者不需要网络、不需要 librsvg**。

### 无渲染器时必须对用户说的话

> 当前环境没有渲染器，我无法看见生成结果，只能按坐标和度量推算。
> 版式约束（圆角/对比度/红色占比/防溢出）仍然生效，但**换行、重叠、观感问题我无法复核**。
> 装 LibreOffice + poppler 可以让我像人一样逐页检查。

**这条来自真实教训**：v1 的 42 页就是在无渲染器时盲拼交付的，结果 3 处溢出、8 张章节页红压红（1.3:1）、全篇灰块雷同。用户一眼就看出来了，我却没有。

---

## 1. 核心哲学

**结构先于美观，克制胜于炫耀，看见胜于推算。**

1. **一张幻灯片，一个核心信息** —— 宁可多一张
2. **结构优先** —— 先选对布局，再谈美观
3. **层级靠尺寸和字重，不靠颜色**
4. **红色只做锚点** —— 面积 ≤8%，不是背景色
5. **节奏感** —— 连续同版式不超过 2 张
6. **交付前必须自己看过** —— 有渲染器就没有借口

---

## 2. 设计系统：企业科技风（默认）

> 定位：干净、克制、专业、秩序感。大面积留白 + 清晰栅格 + 模块化白卡 + 轻量科技装饰。
> 气质对标大型软件公司 / 企业服务品牌 / 数字化平台，保留轻微未来感，**不做暗黑赛博、不做霓虹、不堆装饰**。

令牌定义在 `tools/design.py` 的 `T`。**改设计从改令牌开始，不要在版式里写死颜色。**

```
底  canvas #FFFFFF / canvas_alt #F5F6F8     ← 浅灰底，不是白底
卡  card #FFFFFF                            ← 白卡，别反过来（灰卡白底会发闷）
线  border #E5E7EB   hairline 0.75pt
字  ink #111827(标题) / ink_body #333333(正文) / ink_muted #5B6270(弱化)
红  brand #E60012【填充用】/ brand_text #B3000E【文字用】/ brand_soft #FDEEEF【底纹】
圆角 8-12px   栅格 8pt   阴影 无   底部固定一条品牌红线
```

红色允许出现的地方，**仅限**：图标、编号徽章、标签、标题短线、底部品牌线、关键数字、重点卡的描边或顶栏（三选一，不叠加）。

### 三条不许违反的规则（都是踩过的坑）

1. **红色文字一律用 `brand_text`**，不用 `brand`。
   `#E60012` 压 `#F5F6F8` = 4.44:1，压 `#FDEEEF` = 4.27:1 —— **都不达标**。差 0.06 也是不达标，肉眼就是"发虚"。
2. **`ink_muted` 是 `#5B6270`，不是 `#6B7280`**。后者实测 4.47:1，就差 0.03。别改回去。
3. **所有形状必须走 `design.py` 的原语**，不许直接 `add_shape()`。
   `python-pptx` 的 `add_shape` 会**继承主题默认阴影**，渲染出来每个色块糊一圈灰边 —— v1 "廉价感"的最大来源。原语里的 `_noshadow()` 负责关掉它，`add_textbox` 也要关。

### 硬约束（`audit.py` 照这些数字拦截）

```python
RED_MAX_AREA = 0.08      # 红色填充面积上限（v1 封面曾 46%）
MIN_CONTRAST = 4.5       # 正文 WCAG AA
MIN_CONTRAST_LG = 3.0    # 大字（≥18pt bold 或 ≥24pt）
MAX_SAME_LAYOUT = 2      # 连续同版式上限
```

> 设计简报是散文，模型每次理解都不一样；令牌是数值，闸口能算、能拦、跨环境一致。
> **这就是为什么设计要求要编译成令牌，而不是贴成 prompt。**

### 配色主题（6 选 1）

企业科技风的**结构**（白卡·浅灰底·圆角·细描边·锚点色只做强调）在所有主题下不变，
变的只是那个强调色。生成时 `render_deck(S, out, theme="blue")` 即可。

| theme | 强调色 | 气质 |
|---|---|---|
| `red`（默认） | `#E60012` | 企业红，方法论/战略 |
| `blue` | `#2563EB` | 企业蓝，科技/平台/B2B |
| `green` | `#059669` | 效率绿，可持续/运营 |
| `gold` | `#B08500` | 咨询金，高端/管理层 |
| `ink` | `#334155` | 墨黑，极简/克制 |
| `violet` | `#6D28D9` | 科技紫，AI/产品 |

- 每套的对比度都验证过（`brand_text` 压底 ≥4.5，白字压 `brand` ≥3.0），换主题不会破坏 WCAG 闸口。
- **图标随主题染色**：图标 PNG 只当形状（取 alpha），颜色运行时染成主题色 —— 一套图标通吃所有主题，不为每个主题预渲染。需要 Pillow；无 Pillow 时回退到预渲染的红/灰/白固定色。
- 主题只换强调色，**没有深色主题**（modern-dark 那种深底白卡需单独重做结构与对比度，当前未实现）。用户明确要深色再单独说。
- 一份 deck 只用一个主题，别混。

---

## 3. 执行流程

### Step 0 · 环境自检 + 参数确认

跑 `doctor.py`，把能力/降级如实告知。然后确认：

| # | 确认项 | 默认 |
|---|--------|------|
| 1 | 输出格式 | 未指定则问：需要在 PowerPoint 里继续编辑吗？ |
| 2 | 页数目标 | 15 分钟 ≈ 10 张；内容多则按内容展开，无上限 |
| 3 | 受众与场合 | 从内容推断 |
| 4 | 风格 | 企业科技风（默认）· 见 §2 |
| 5 | 字体 | 见 §6 —— 这里有个必须问清楚的坑 |
| 6 | 硬性约束 | 必须包含 / 必须避免 |
| 7 | 数据真实性 | 有真实数据直接用；**无则写 `[数据待补充]`，绝不编造** |

**轻量路径**：用户已给全格式+页数+风格时，Step 0 与 Step 2 的确认合并成一次。

### Step 1 · 解析输入

| 输入 | 处理 |
|---|---|
| Markdown | 直接解析标题层级 |
| `.docx` | 用 `zipfile` 读 `word/document.xml`（比装 python-docx 稳，见 §7） |
| 纯文本 | 空行分组，首行为封面 |

### Step 2 · 规划结构 + 大纲确认

按内容特征选版式（见 §4），检查节奏（连续同版式 ≤2），**展示大纲等用户确认**：

```
📋 幻灯片大纲（共 N 张，格式：PPTX，风格：企业科技风）
 #  类型            标题
 1  cover           ...
 2  section         01 · ...
确认生成？
```

≥30 张时附分批计划（每批 20-25 张，`append_to` 追加）。

### Step 3 · 生成

```python
import sys; sys.path.insert(0, "tools")
from layouts import render_deck

SLIDES = [ {...}, ... ]                       # 规格见 §4
render_deck(SLIDES, "out.pptx", theme="red")  # 主题见 §2；追加：append_to=out
```

### Step 4 · 闸口（P0 不过不许交付）

```bash
python3 tools/audit.py out.pptx            # 溢出/越界/对比度/重叠/红色/节奏/字体
python3 tools/audit.py out.pptx --layout   # 顺带导出 layout JSON
```

### Step 5 · 自审（有渲染器时必做）

```bash
python3 tools/preview.py out.pptx          # 每页 PNG + montage
```

然后**真的去看**：

1. **先看 montage** —— 看整体：版式是否统一、哪几页明显太密、风格是否一致、有没有连续雷同。
   单页看不出"雷同"，只有拼成长图才看得出来。
2. **再抽查关键页** —— 封面、最密的页、图表页、结构最复杂的页
3. **发现问题改代码重新生成**，不要手工修 pptx

> ⚠️ **闸口过 ≠ 好看。** `audit.py` 能抓溢出、越界、重叠、对比度、红色超标 —— 这些都是能算的。
> **算不出来的**：文字精不精炼、留白是否得当、视觉是否高级、页面是否太空、图形是否别扭。
> 这些只能靠看渲染图判断。别把 `✅ 可以交付` 当成"做完了"。
>
> 实测：v2 原型 P0 全过，但 montage 一看 —— 棱锥是**倒**的、循环图整页发空。闸口全放行了。

### Step 6 · 报告

告知：完整路径、张数、版式分布、**audit 结论**、**是否经过渲染自审**、有无降级。

---

## 4. 版式速查

`tools/layouts.py`，14 种。所有类型都支持 `notes`（写入演讲者备注）、`kicker`、`icon`。

```python
{"type":"cover","tag":"标注","title":"主标题\n可换行","subtitle":"副标题",
 "meta":"页脚","points":["右栏要点1","要点2"],"icon":"target"}

{"type":"section","number":"01","kicker":"PHASE 01","title":"章节名","subtitle":"简介"}

{"type":"grid","title":"标题","icon":"layers","items":[      # ≤6，>4 自动 3 列
  {"tag":"S1-01","icon":"target","label":"标题","desc":"描述","std":"完成标准(可选)"}]}

{"type":"numbered_list","title":"标题","items":[             # ≤5
  {"title":"项目","desc":"描述"}]}

{"type":"bullets","title":"标题","bullets":["要点"],"source":"注释"}   # ≤6

{"type":"two_column","title":"标题","left_title":"左","right_title":"右",
 "left_points":[...],"right_points":[...]}                   # 每栏 ≤6

{"type":"process","title":"标题","steps":[{"label":"步骤","desc":"说明"}]}   # ≤5

{"type":"stats","title":"标题","stats":[{"num":"80","unit":"%","label":"标签","desc":"说明"}]}  # ≤4

{"type":"timeline","title":"标题","items":[
  {"date":"Q1","title":"里程碑","desc":"说明","tag":"标签"}]}  # ≤6

{"type":"quote","quote":"金句","author":"作者","role":"来源"}

{"type":"pyramid","title":"标题","layers":[                  # ≤5
  {"label":"底层","desc":"..."}, ..., {"label":"顶层","desc":"..."}]}
                                                             # ⚠️ [0]=底层，[-1]=顶层，别搞反

{"type":"cycle","title":"标题","center":"中心","steps":[{"label":"","desc":""}]}  # 3-6

{"type":"chart","title":"标题","kind":"column",              # bar|column|line|pie|doughnut
 "categories":["A","B"],"series":{"系列名":[1,2]}}            # 原生可编辑图表

{"type":"closing","title":"标题","subtitle":"副标","cta":["要点1","要点2"]}  # ≤8
```

### 选型逻辑

| 内容特征 | 版式 |
|---|---|
| 3-5 个有顺序的步骤 | `process` |
| 4-6 个并列项，各有说明 | `grid` |
| 3-5 个要点，描述较长 | `numbered_list` |
| 5-6 个简短要点 | `bullets` |
| 两类事物对比 | `two_column` |
| 层层递进的基础→核心 | `pyramid` |
| 首尾相连的循环 | `cycle` |
| 时间轴 / 路线图 | `timeline` |
| 3-4 个关键数字 | `stats` |
| **有数值可比较** | **`chart`（优先，别用文字堆数字）** |
| 金句 / 核心观点 | `quote` |

### 内容约束

标题 ≤20 字；bullets 每条 ≤40 字（超了升级 `numbered_list`）；`grid` 每项描述 ≤60 字；`process`/`timeline` 每步 ≤50 字。

**放不下就拆页，不要缩字号硬塞。** `measure.fit_size()` 返回 `None` 就是该拆的信号。

**容器高度一律按 `measure` 度量的内容算，不要撑满栅格** —— 撑满的结果是要么溢出、要么卡片下半部一大片死空白（v1 两种都犯了）。

---

## 5. 图标

`assets/icons/` 内置 107 个 Lucide 图标 × 3 色（`red` / `ink` / `white`）。

```python
D.icon(slide, "target", x, y, size=0.24, color="red")
```

命名 = Lucide 官方名。常用：`target` `workflow` `layers` `network` `brain` `bar-chart-3`
`shield-check` `refresh-cw` `users` `file-text` `milestone` `gauge` `database` `sparkles`
`git-branch` `map` `message-square` `clipboard-check` `coins` `settings-2` `lightbulb`

扩充（需网络 + librsvg）：`python3 tools/fetch_icons.py brain cpu zap`

**禁止 emoji 当图标。** 图标缺失时 `D.icon()` 静默跳过 —— 图标是增强，不是信息载体，缺一个不该让整份 PPT 失败。

---

## 6. 字体：一个必须跟用户确认的坑

`python-pptx` 只是把字体名写进文件，**不做任何回退**。回退与否完全取决于打开它的软件。

v1 声明 `Microsoft YaHei`，而 macOS 上没有这个字体 —— 文件"带病"：PowerPoint 替换后看着还行，但换个渲染器中文就全丢。

| 分发对象 | 该声明什么 |
|---|---|
| Windows 为主（企业常见） | `Microsoft YaHei` ← `FONT_DECLARE` 默认 |
| Mac 为主 | `PingFang SC` |
| 混合 / 不确定 | 问用户，别猜 |

`audit.py` 会报"本机未安装"——若分发对象有该字体，这是**提示不是缺陷**。
`preview.py` 渲染时自动换成本机可用字体，只影响预览副本，不动原文件。

---

## 7. 已知环境陷阱（都踩过）

| 现象 | 真相 | 对策 |
|---|---|---|
| `soffice` 存在，但导出的 PDF 没有中文 | LibreOffice 看不到系统字体，静默替换成拉丁字体，中文字符被直接丢弃 | `doctor.py` 用带中文的冒烟测试验证端到端；修法：把中文字体放进 LibreOffice 的 `Contents/Resources/fonts/truetype` |
| `pip install` 报 `libexpat` 错误 | 某些 Homebrew Python 的 pip 是坏的 | 换用 `zipfile` 解析 docx，别装 python-docx |
| `magick` 转 PDF 报 `gs not found` | ImageMagick 光栅化 PDF 需要 ghostscript | 用 `pdftoppm`（poppler），更可靠 |
| `magick` 渲染 Lucide SVG 全透明 | 无 rsvg 委托时，内置 MSVG 处理不了 `fill="none"` 描边图标 | 用 `rsvg-convert` |
| PIL 读不了 `PingFang.ttc` | macOS 新版按需资产字体，很多库读不了 | 用 skill 自带的 Noto Sans SC |
| 度量准但排版仍跑偏 | 度量字体与渲染/声明字体不是同一个 | 统一到 skill 自带字体，两端同源 |

**通用教训：命令存在 ≠ 能用。** 关键链路必须端到端验证。

`doctor.py` 探测渲染器时按候选路径逐个找（PATH → 标准安装位置 → 其他 runtime 的缓存），
**找到就用，找不到就降级**。不硬编码任何特定 runtime 的路径为依赖 —— 那个环境消失了，skill 照常工作。

---

## 8. HTML 模式

复用同一套令牌（§2），骨架见 `assets/html-template.html`。HTML 能吃满设计简报里 pptx 做不到的部分：真渐变、玻璃拟态（`backdrop-filter`）、光晕、动效。

- 动画：`data-anim="fade-up"` + `data-delay`；列表用 `stagger-list`；数字用 `data-counter`；封面标题 `typewriter`
- 讲稿：每张 `<aside class="notes">`，150-300 字，对话式，`<strong>` 标关键词
- 演讲者模式 `S` 键；`window.print()` 导 PDF

### 设计哲学（仅 HTML，`html_deck.PHILOSOPHIES`）

与 6 个颜色主题的区别：**主题只换强调色；哲学换整套视觉语言**——字体、留白、版式比例、圆角、气质。每个哲学 = 一组令牌覆盖（调色板 + `font_display`/`pad_y`/`pad_x`/`radius`/`wt_display`/`card_shadow`/`card_border`）+ 结构 CSS（`_css`），且**对比度经渲染验证达标**（不是 v10 那种没保证的散文描述）。

```python
render_html_deck(SLIDES, "out.html", philosophy="shen")   # philosophy 覆盖 theme
```

现有 4 个（差异最大化）：
| 哲学 | 气质 | 关键 |
|---|---|---|
| `pentagram` | 编辑出版 | 白红 + 衬线粗标题 + 锐角平卡 + 奢侈留白 |
| `hara` | 空の设计 | 纸白底 + 近无色灰 + 轻字重 + 极致留白 |
| `shen` | 东方水墨 | 深藏蓝 + 青金 + 衬线（深色系）|
| `swiss` | 瑞士网格 | 白黑红 + 粗黑体 + 锐角粗描边 + 功能主义 |

加新哲学：往 `PHILOSOPHIES` 加一条（调色板必须过 WCAG——亮强调色配深 `brand_on`、深底配浅字），然后**必须渲染验证**再用。要点：HTML 的 badge/col-head/cyc-dot 已用 `var(--brand-on)`/`var(--canvas)` 自适应，浅强调色/深色哲学不会白字压亮底。

HTML 模式无法用 `audit.py`（它读 pptx）。**对比度和强调色占比要人工照 §2 令牌 + 渲染核对。**

---

## 9. 交付前自查

```
□ doctor.py 跑过，降级情况已如实告知用户
□ audit.py P0 全过
□ 有渲染器 → preview.py 出图，montage 看过，关键页抽查过
□ 无渲染器 → 已明确告知「未经渲染复核」
□ 首张 cover，末张 closing
□ 连续同版式 ≤2
□ 数据均来自用户提供；无来源写 [数据待补充]，未编造
□ 无 emoji 图标、无大红色块、无默认阴影
□ 字体声明与分发对象匹配（§6）
```

**最后一问：我自己看过这份 PPT 吗？** 如果没有，先说清楚，再交付。

---

## 附：工具

| 文件 | 用途 | 谁调用 |
|---|---|---|
| `tools/doctor.py` | 能力探测 + 端到端渲染冒烟测试 | 每次生成前 |
| `tools/design.py` | 设计令牌 + 绘图原语（圆角/关阴影/图标/徽章/标签） | 版式内部 |
| `tools/measure.py` | 真实字体度量（精确层 + 降级模型） | 版式内部 |
| `tools/layouts.py` | 14 种版式 + `render_deck()` | 生成时 |
| `tools/audit.py` | P0/P1/P2 闸口 + layout JSON | 生成后 |
| `tools/preview.py` | 每页 PNG + montage | 生成后（有渲染器时） |
| `tools/fetch_icons.py` | 扩充图标库（构建期，需网络+librsvg） | 极少 |
