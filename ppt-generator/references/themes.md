> ⚠️ **已废弃（v10 遗留）**。v11 起：设计令牌见 `tools/design.py`；版式见 `tools/layouts.py`；
> 检查清单由 `tools/audit.py` 强制执行。本文件仅作历史参考，勿据此实现。

# 主题变量速查 — PPT Generator

共 8 个主题。HTML 模式：将变量块复制到 `<style>` 开头，并设置 `<body class="theme-XXX">`。

| 主题名 | body class | 适用场景 |
|--------|-----------|---------|
| red-gray（默认） | `theme-red-gray` | 通用 |
| professional-blue | `theme-blue` | 商务报告、战略 |
| modern-dark | `theme-dark` | 科技、AI、开发者 |
| clean-white | `theme-white` | 简洁、教育 |
| warm-orange | `theme-orange` | 创业、营销 |
| corporate | `theme-corporate` | 企业、咨询 |
| forest | `theme-forest` | 自然、可持续 |
| aurora | `theme-aurora` | 科技渐变感 |

---

```css
/* red-gray（默认） */
body.theme-red-gray{--ink:#1a1a1a;--ink-2:rgba(26,26,26,0.6);--paper:#fff;--paper-2:#f2f2f2;--paper-3:#e8e8e8;--accent:#cc0000;--accent-2:rgba(204,0,0,0.1);--highlight:#ff2442}

/* professional-blue */
body.theme-blue{--ink:#1f3a6e;--ink-2:rgba(31,58,110,0.6);--paper:#fff;--paper-2:#f0f4f8;--paper-3:#dce8f4;--accent:#2e86c1;--accent-2:rgba(46,134,193,0.1);--highlight:#f39c12}

/* modern-dark */
body.theme-dark{--ink:#0f0f23;--ink-2:rgba(221,226,240,0.5);--paper:#0f0f23;--paper-2:#181830;--paper-3:#222245;--accent:#7c3aed;--accent-2:rgba(124,58,237,0.2);--highlight:#00d9ff}
body.theme-dark .slide-title{color:var(--highlight)}
body.theme-dark .slide-title-line{background:var(--highlight)}
body.theme-dark .slide-section,body.theme-dark .slide-quote{background:#07071a!important}
body.theme-dark .slide-cover .cover-left,body.theme-dark .slide-closing .closing-right{background:#07071a}
body.theme-dark .bullet-text,body.theme-dark .numbered-desc,body.theme-dark .tl-title,body.theme-dark .tl-desc,body.theme-dark .grid-card-body,body.theme-dark .process-body,body.theme-dark .col-item,body.theme-dark .stat-label,body.theme-dark .stat-desc,body.theme-dark .ba-item,body.theme-dark .pyramid-desc,body.theme-dark .cycle-label,body.theme-dark .cycle-desc,body.theme-dark .hier-grandchild{color:#dde2f0}
body.theme-dark .numbered-title{color:var(--highlight)}
body.theme-dark .bullet-card,body.theme-dark .numbered-content,body.theme-dark .tl-content,body.theme-dark .process-body,body.theme-dark .ba-content{background:var(--paper-2)}
body.theme-dark .col-item{background:var(--paper-2);border-left-color:var(--accent)}
body.theme-dark .col-right .col-item{border-left-color:var(--highlight)}
body.theme-dark .matrix-row:nth-child(2) .matrix-q{background:var(--paper-2)}
body.theme-dark .matrix-row:nth-child(2) .matrix-q:nth-child(2){background:var(--paper-3)}

/* clean-white */
body.theme-white{--ink:#181818;--ink-2:rgba(24,24,24,0.55);--paper:#fff;--paper-2:#f5f5f5;--paper-3:#ebebeb;--accent:#ff4d4d;--accent-2:rgba(255,77,77,0.1);--highlight:#ff4d4d}

/* warm-orange */
body.theme-orange{--ink:#1c1208;--ink-2:rgba(28,18,8,0.6);--paper:#fffbf7;--paper-2:#fdf0e8;--paper-3:#f5e0cc;--accent:#ff6b35;--accent-2:rgba(255,107,53,0.1);--highlight:#ffd93d}

/* corporate-clean */
body.theme-corporate{--ink:#0d1b4b;--ink-2:rgba(13,27,75,0.58);--paper:#fff;--paper-2:#f4f6fb;--paper-3:#e8edf8;--accent:#0d1b4b;--accent-2:rgba(13,27,75,0.08);--highlight:#c9a84c}
body.theme-corporate .slide::before{background:var(--highlight)}
body.theme-corporate .slide-title-line,.theme-corporate .cover-line{background:var(--highlight)}

/* forest-ink */
body.theme-forest{--ink:#1a2e1a;--ink-2:rgba(26,46,26,0.62);--paper:#f5f0e8;--paper-2:#ede8dc;--paper-3:#e0d9ca;--accent:#2d5a27;--accent-2:rgba(45,90,39,0.1);--highlight:#8b6914}

/* aurora */
body.theme-aurora{--ink:#1e1240;--ink-2:rgba(30,18,64,0.62);--paper:#fafafe;--paper-2:#f0eeff;--paper-3:#e4dfff;--accent:#6d28d9;--accent-2:rgba(109,40,217,0.1);--highlight:#06b6d4}
body.theme-aurora .slide::before{background:linear-gradient(90deg,#6d28d9,#06b6d4,#10b981);height:3px}
body.theme-aurora .slide-title-line{background:linear-gradient(90deg,#6d28d9,#06b6d4);width:5vw}
```
