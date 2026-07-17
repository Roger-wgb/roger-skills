# Claude Skills

个人 Claude Code / Agent Skills 集合。每个子目录是一个独立 skill，含 `SKILL.md` 与配套工具/资源。

## Skills

### [ppt-generator](./ppt-generator)
从结构化内容（Markdown / .docx / 纯文本）生成**路演级**演示文稿，输出可编辑 `.pptx` 或浏览器演讲 `.html`。

- **设计系统**：企业科技风令牌（白卡浅灰底、圆角、细描边、强调色仅作锚点），6 种配色主题（红/蓝/金/紫/暖橙/深色），图标随主题染色
- **HTML 设计哲学**：Pentagram（编辑出版）/ Hara（空の设计）/ Shen（东方水墨）/ Swiss（瑞士网格），令牌化 + 渲染验证
- **质量闸口**：生成后跑硬检查——文字溢出 / 越界 / 重叠 / WCAG 对比度 / 强调色占比 / 版式节奏，P0 不过不许交付
- **渲染自审**：有 LibreOffice / Chrome 时导出每页 PNG + montage 逐页复核（"看见胜于推算"）
- **依赖分级**：仅 `python-pptx` 即可生成；渲染器缺失时明确降级告知，不静默交付

14 种版式 · 107 个 Lucide 图标 · 原生可编辑图表 · 演讲者模式 · 讲稿。

## 使用

把某个 skill 目录放进 `~/.claude/skills/`（或 `~/.agents/skills/`）即可被 Claude Code 识别。

## 结构约定

```
<skill-name>/
  SKILL.md          # skill 定义（frontmatter + 说明）
  tools/            # 可执行脚本
  assets/           # 字体、图标等资源
  references/       # 参考文档
```
