> ⚠️ **已废弃（v10 遗留）**。v11 起：设计令牌见 `tools/design.py`；版式见 `tools/layouts.py`；
> 检查清单由 `tools/audit.py` 强制执行。本文件仅作历史参考，勿据此实现。

# HTML 幻灯片结构速查 — PPT Generator

所有 class 名来自 `assets/html-template.html`，禁止自创。
图标统一使用 Lucide：`<i data-lucide="icon-name"></i>`，禁止 emoji。

---

```html
<!-- COVER -->
<div class="slide slide-cover">
  <div class="cover-left">
    <div class="cover-tag">系列标签</div>
    <div class="cover-title typewriter">主标题</div>
    <div class="cover-line"></div>
    <div class="cover-subtitle" data-anim="fade-up" data-delay="900">副标题</div>
  </div>
  <div class="cover-right">
    <div class="cover-count">
      <div class="cover-count-num">07</div>
      <div class="cover-count-label">个核心观点</div>
    </div>
  </div>
</div>

<!-- SECTION -->
<div class="slide slide-section">
  <div class="section-number">01</div>
  <div class="section-tag">CHAPTER 01</div>
  <div class="section-line"></div>
  <div class="section-title" data-anim="rise-in" data-delay="300">章节标题</div>
  <div class="section-subtitle" data-anim="fade-up" data-delay="600">章节副标题说明</div>
</div>

<!-- BULLETS -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">幻灯片标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="bullet-cards stagger-list">
      <div class="bullet-card">
        <div class="bullet-num">1</div>
        <div class="bullet-text">要点内容文字</div>
      </div>
      <!-- 重复 bullet-card，最多 6 条 -->
    </div>
  </div>
</div>

<!-- PROCESS -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">流程标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="process-flow">
      <div class="process-step" data-anim="fade-up" data-delay="0">
        <div class="process-header">
          <div class="process-num">01</div>
          <div class="process-label">步骤名称</div>
        </div>
        <div class="process-body">步骤描述文字</div>
      </div>
      <div class="process-arrow">▶</div>
      <!-- 重复 process-step + process-arrow，最多 5 步 -->
    </div>
  </div>
</div>

<!-- GRID (2列用cols-2，3列用cols-3) -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">方格标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="grid-cards cols-2 stagger-list">
      <div class="grid-card">
        <div class="grid-card-top">
          <div class="grid-card-num">01</div>
          <div class="grid-card-icon"><i data-lucide="target"></i></div>
          <div class="grid-card-label">卡片标题</div>
        </div>
        <div class="grid-card-body">卡片描述内容</div>
      </div>
      <!-- 重复 grid-card，最多 6 个 -->
    </div>
  </div>
</div>

<!-- NUMBERED_LIST -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">编号列表标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="numbered-list stagger-list">
      <div class="numbered-item">
        <div class="numbered-num">01</div>
        <div class="numbered-divider"></div>
        <div class="numbered-content">
          <div class="numbered-title">项目标题</div>
          <div class="numbered-desc">项目详细描述内容</div>
        </div>
      </div>
      <!-- 重复 numbered-item，最多 5 个 -->
    </div>
  </div>
</div>

<!-- TWO_COLUMN -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">对比标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="two-col">
      <div class="col-block col-left" data-anim="slide-right" data-delay="0">
        <div class="col-header">左栏标题</div>
        <div class="col-item"><div class="col-dot">1</div>要点文字</div>
        <!-- 重复 col-item -->
      </div>
      <div class="col-block col-right" data-anim="slide-left" data-delay="200">
        <div class="col-header">右栏标题</div>
        <div class="col-item"><div class="col-dot">1</div>要点文字</div>
      </div>
    </div>
  </div>
</div>

<!-- MATRIX -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">矩阵标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="matrix-wrap" style="position:relative;">
      <div class="matrix-row">
        <div class="matrix-q">
          <div class="matrix-q-label">左上象限</div>
          <div class="matrix-q-desc">描述</div>
        </div>
        <div class="matrix-q">
          <div class="matrix-q-label">右上象限</div>
          <div class="matrix-q-desc">描述</div>
        </div>
      </div>
      <div class="matrix-row">
        <div class="matrix-q">
          <div class="matrix-q-label">左下象限</div>
          <div class="matrix-q-desc">描述</div>
        </div>
        <div class="matrix-q">
          <div class="matrix-q-label">右下象限</div>
          <div class="matrix-q-desc">描述</div>
        </div>
      </div>
      <div class="matrix-x-label">← 横轴说明 →</div>
    </div>
  </div>
</div>

<!-- PYRAMID (layers 从底到顶写，CSS flex-direction:column-reverse 自动翻转) -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">棱锥标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="pyramid-wrap">
      <div class="pyramid-layer">
        <div class="pyramid-label">底层</div>
        <div class="pyramid-desc">描述</div>
      </div>
      <div class="pyramid-layer">
        <div class="pyramid-label">中层</div>
        <div class="pyramid-desc">描述</div>
      </div>
      <div class="pyramid-layer">
        <div class="pyramid-label">顶层</div>
        <div class="pyramid-desc">描述</div>
      </div>
    </div>
  </div>
</div>

<!-- CYCLE (4步：顶50%15% 右85%50% 底50%85% 左15%50%) -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">循环标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="cycle-wrap">
      <div class="cycle-node" style="top:15%;left:50%;">
        <div class="cycle-circle">01</div>
        <div class="cycle-label">步骤一</div>
        <div class="cycle-desc">简短描述</div>
      </div>
      <div class="cycle-node" style="top:50%;left:85%;">
        <div class="cycle-circle">02</div>
        <div class="cycle-label">步骤二</div>
        <div class="cycle-desc">简短描述</div>
      </div>
      <div class="cycle-node" style="top:85%;left:50%;">
        <div class="cycle-circle">03</div>
        <div class="cycle-label">步骤三</div>
        <div class="cycle-desc">简短描述</div>
      </div>
      <div class="cycle-node" style="top:50%;left:15%;">
        <div class="cycle-circle">04</div>
        <div class="cycle-label">步骤四</div>
        <div class="cycle-desc">简短描述</div>
      </div>
      <div class="cycle-center-text">循环</div>
    </div>
  </div>
</div>

<!-- HIERARCHY -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">层次结构标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="hierarchy-wrap">
      <div class="hier-row" style="margin-bottom:1.5vh;">
        <div class="hier-node hier-root">根节点</div>
      </div>
      <div style="height:2vh;width:2px;background:var(--accent);opacity:0.3;margin:0 auto;"></div>
      <div class="hier-row" style="margin-bottom:1vh;">
        <div class="hier-node hier-child">子节点A</div>
        <div class="hier-node hier-child">子节点B</div>
        <div class="hier-node hier-child">子节点C</div>
      </div>
    </div>
  </div>
</div>

<!-- QUOTE -->
<div class="slide slide-quote">
  <div class="quote-mark">"</div>
  <div class="quote-text" data-anim="blur-in" data-delay="300">引用内容文字，可以较长，会自动换行</div>
  <div class="quote-rule"></div>
  <div class="quote-author" data-anim="fade-up" data-delay="800">— 作者姓名</div>
  <div class="quote-role">职务 / 来源</div>
</div>

<!-- TIMELINE -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">时间轴标题</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="timeline-wrap stagger-list">
      <div class="timeline-item">
        <div class="tl-date">2024 Q1</div>
        <div class="tl-dot"></div>
        <div class="tl-content">
          <div class="tl-title">里程碑标题</div>
          <div class="tl-desc">详细说明</div>
          <div class="tl-tag">可选标签</div>
        </div>
      </div>
      <!-- 重复 timeline-item，最多 6 条 -->
    </div>
  </div>
</div>

<!-- STATS / BIG NUMBERS (cols-2 / cols-3 / cols-4) -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">核心数据一览</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="stats-grid cols-3">
      <div class="stat-card" data-bg="80" data-anim="zoom-pop" data-delay="0">
        <div class="stat-num"><span data-counter="80" data-suffix="%">0%</span></div>
        <div class="stat-label">指标名称</div>
        <div class="stat-desc">数据来源说明</div>
      </div>
      <!-- 重复 stat-card，delay 递增 150ms -->
    </div>
  </div>
</div>

<!-- BEFORE / AFTER -->
<div class="slide">
  <div class="slide-header">
    <div class="slide-title">转型前后对比</div>
    <div class="slide-title-line"></div>
  </div>
  <div class="slide-body">
    <div class="before-after">
      <div class="ba-panel ba-before" data-anim="slide-right" data-delay="0">
        <div class="ba-label">BEFORE</div>
        <div class="ba-content">
          <div class="ba-item">改变前状态1</div>
          <div class="ba-item">改变前状态2</div>
        </div>
      </div>
      <div class="ba-divider">
        <div class="ba-arrow">→</div>
        <div class="ba-divider-label">转变</div>
      </div>
      <div class="ba-panel ba-after" data-anim="slide-left" data-delay="300">
        <div class="ba-label">AFTER</div>
        <div class="ba-content">
          <div class="ba-item">改变后状态1</div>
          <div class="ba-item">改变后状态2</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- CLOSING -->
<div class="slide slide-closing">
  <div class="closing-left">
    <div class="closing-title" data-anim="fade-up">谢谢</div>
    <div class="closing-line"></div>
    <div class="closing-subtitle" data-anim="fade-up" data-delay="300">副标题或联系方式</div>
  </div>
  <div class="closing-right">
    <div class="closing-cta" data-anim="fade-left" data-delay="400">行动号召文字<br>第二行</div>
  </div>
</div>
```
