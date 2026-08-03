# Roger Skills

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

### [resume-optimizer-tailor](./resume-optimizer-tailor)
面向求职者的简历优化与定制 Skill。基于已有简历、经历素材和目标岗位，输出完整、真实、有说服力且视觉呈现专业的定制简历版本，并支持多岗位版本管理。

- **完整简历输出**：不是只给修改建议，而是直接生成可用的完整简历
- **岗位定制**：根据目标 JD 强化匹配证据，突出企业真正关心的能力
- **多模式支持**：通用职场、技术岗、产品/运营/市场、管理/高管、应届生、转行、创意设计、学术 CV
- **视觉风格**：标准专业、技术简洁、高管沉稳、创意设计、应届生清爽、双语版
- **HTML/CSS 简历**：可输出单文件网页简历，支持头像预留、侧栏、打印导出 PDF
- **真实性边界**：不编造经历、学历、证书或项目，保守估算需提示用户核实

配套文章：[FDE 火了以后，我越来越觉得：我们需要一套更好的简历写法](./articles/fde-resume-skill-wechat.md)

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
