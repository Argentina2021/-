# 百家数科 — 气泡交互展示

雄安科技展企业气泡交互页面，1920×1080 全屏展示，适用于一体机触摸操作并投影到大屏。

## 功能

- Canvas 渲染 3D 半透明气泡，企业名称显示在气泡内（MiSans VF）
- 空中漂浮物理：浮力、重力、空气阻力、气流扰动
- 背景视频 + plus-lighter 混合
- 左右滑动浏览多屏企业，点击气泡展开企业介绍
- 介绍卡片支持上下滚动；点击卡片外区域或 Esc 回到气泡墙

## 本地预览

```bash
python -m http.server 8080
```

浏览器打开：http://localhost:8080/bubbles.html

## 主要文件

| 文件 | 说明 |
|------|------|
| `bubbles.html` | 主页面 |
| `js/bubbles-app.js` | 气泡引擎与交互 |
| `js/card-renderer.js` | 企业卡片渲染 |
| `companies.js` | 企业数据 |
| `product_images.js` | 产品图片映射 |
| `bg.mp4` | 背景视频 |
| `fonts/` | MiSans VF 字体 |
