> ⚠️ **已废弃（v10 遗留）**。v11 起：设计令牌见 `tools/design.py`；版式见 `tools/layouts.py`；
> 检查清单由 `tools/audit.py` 强制执行。本文件仅作历史参考，勿据此实现。

# 质量检查清单 — PPT Generator

生成 HTML 幻灯片前，按 P0→P1→P2→P3 顺序自检。**P0 未通过禁止输出**。

---

## P0（阻断级 — 必须全部通过）

```
□ 所有 class 名均来自 html-template.html <style> 中的定义，未自创新 class
□ 图标使用 Lucide（<i data-lucide="icon-name">），禁止用 emoji 充当图标
□ cover 是第 1 张，closing 是最后 1 张
□ 同一布局类型未连续出现超过 2 张
□ HTML 输出包含完整的 CSS（主题变量 + 基础 + 组件 + 动画）
□ 每张幻灯片均有 data-anim / stagger-list / typewriter / data-counter 其中之一
□ <aside class="notes"> 已添加到每张幻灯片（HTML 模式）
```

## P1（严重 — 应修复）

```
□ 幻灯片总张数满足用户要求的最少张数
□ 每张幻灯片标题 ≤ 20 字
□ bullets 每条 ≤ 40 字；process 每步描述 ≤ 50 字；stats 描述 ≤ 25 字
□ section / quote 幻灯片有 1 张以上，提供视觉节奏
□ 主题 CSS class 与 <body class="theme-XXX"> 一致
□ stats 数字用 data-counter；cover 大标题用 typewriter 或 rise-in
```

## P2（建议 — 优先修复）

```
□ 内容遵循叙事弧：Hook → 背景 → 核心 → 转折 → 收尾
□ grid 卡片已提供 Lucide 图标（见常用图标表）
□ 讲稿（notes）使用对话式语调，150-300 字/张，有 [停顿] 等舞台标记
□ 数据型幻灯片（stats/timeline）有来源说明
□ before_after 对比项措辞平行（结构相似、字数相当）
```

## P3（润色 — 时间允许时处理）

```
□ 动画 delay 递增均匀，整体节奏流畅
□ section 幻灯片 section-number 与章节顺序一致
□ 封面 cover-count 数字与正文内容数量一致
□ Lucide 图标语义与卡片内容匹配（不随机选取）
□ closing 的 cta 文字与演讲场景匹配（非通用"谢谢"）
```

---

## 常用 Lucide 图标速查

| 场景 | 图标名 | 用法 |
|------|--------|------|
| AI / 智能 | `brain` `cpu` `bot` | `<i data-lucide="brain">` |
| 数据 / 图表 | `bar-chart-2` `trending-up` `pie-chart` | |
| 流程 / 工具 | `workflow` `layers` `wrench` `settings` | |
| 用户 / 团队 | `users` `user-check` `building-2` | |
| 目标 / 成果 | `target` `rocket` `zap` `award` | |
| 风险 / 问题 | `alert-triangle` `shield` `lock` | |
| 学习 / 知识 | `book-open` `graduation-cap` `lightbulb` | |
| 连接 / 网络 | `network` `link` `globe` | |
| 时间 / 路线 | `clock` `calendar` `map` `milestone` | |
| 代码 / 技术 | `code-2` `terminal` `database` `cloud` | |

完整图标库：https://lucide.dev/icons
