# HTML/CSS 简历页面输出

## 何时输出 HTML/CSS

当用户明确提出以下需求时，输出 HTML/CSS 简历页面结构：

- 想要“好看的简历页面”
- 想要可打印、可导出 PDF 的简历
- 需要带头像、侧栏、标签、项目卡片或作品集链接
- 简历用于作品集网站、个人主页、内推展示、线下面试打印
- 用户要求输出 HTML、CSS、网页简历、在线简历或可视化简历

如果用户只是用于官网投递或 ATS 上传，优先输出文本简历或 ATS 友好版，不默认生成复杂 HTML。

## 输出形态

优先输出单文件 HTML：

```text
index.html
```

要求：

- HTML、CSS 写在同一个文件中
- 不依赖外部 CDN
- 不加载远程字体、远程图片或第三方脚本
- 头像使用占位区域或本地路径占位，不引用真实隐私图片
- 支持浏览器打开和打印导出 PDF

## 页面基础结构

建议结构：

```html
<main class="resume">
  <aside class="sidebar">
    <div class="avatar">头像</div>
    <section class="contact">联系方式</section>
    <section class="skills">核心技能</section>
    <section class="links">作品集链接</section>
  </aside>
  <section class="content">
    <header class="profile">姓名、目标职位、职业摘要</header>
    <section class="experience">工作经历</section>
    <section class="projects">项目经历</section>
    <section class="education">教育背景</section>
  </section>
</main>
```

如果用户选择 ATS 友好版，不使用侧栏结构，改用单栏结构。

## 视觉设计要求

所有 HTML 简历都应满足：

- 信息层级清楚，招聘方 10 秒内能看到姓名、目标岗位、核心优势
- 正文阅读舒适，避免过度装饰
- 色彩克制，主色不超过 1 个，辅助色不超过 2 个
- 头像、标签、卡片、分割线服务于信息表达，而不是抢夺注意力
- 适合 A4 打印，避免分页时切断重要模块
- 打印样式中隐藏无意义阴影和背景噪音

## 头像区域

头像默认只做预留，不强制使用。

建议：

- 尺寸：88px - 120px
- 形状：圆形或 12px 以内圆角方形
- 位置：左侧栏顶部或顶部信息区右侧
- 占位文案：照片 / Photo

提醒：

- 海外岗位通常不建议放照片
- 国内猎聘、脉脉、内推展示、创意简历可使用专业头像
- 不要使用生活照、自拍照或过度修饰照片

## 风格版本

HTML/CSS 只是风格落地方式之一，不独占风格定义。

生成 HTML 简历前，先根据 `references/visual-style-versions.md` 选择风格版本，再把该风格翻译为 HTML/CSS 的布局、颜色、字体、模块和打印样式。

## 打印与 PDF 要求

CSS 应包含打印样式：

```css
@media print {
  body {
    background: #fff;
  }
  .resume {
    box-shadow: none;
    margin: 0;
  }
}
```

建议：

- 页面宽度接近 A4：`210mm`
- 最小正文不小于 10pt 或 13px
- 避免模块被分页切断：`break-inside: avoid`
- 深色背景面积不要过大，避免打印成本高和文字不清晰

## 输出时必须包含

生成 HTML/CSS 时，除代码外，还应简要说明：

- 使用的风格版本
- 适合的投递场景
- 是否适合 ATS
- 头像是否预留
- 如何导出 PDF

不要声称已生成 PDF、图片或 DOCX，除非当前 Agent 实际创建了对应文件。
