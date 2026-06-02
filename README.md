# 百家数科 — 气泡交互展示

雄安科技展企业气泡交互页面，1920×1080 全屏展示。

## 功能

- Canvas 渲染 3D 半透明气泡，企业名称显示在气泡内（MiSans VF）
- 空中漂浮物理：浮力、重力、空气阻力、气流扰动
- 空间纵深：前后虚实、视差
- 背景视频 + plus-lighter 混合
- 点击气泡打开企业产品卡片
- 横向滑动浏览多屏企业

## 本地预览

```bash
python -m http.server 8080
```

浏览器打开：http://localhost:8080/bubbles.html

## 主要文件

| 文件 | 说明 |
|------|------|
| `bubbles.html` | 主页面 |
| `companies.js` | 企业数据 |
| `bg.mp4` | 背景视频 |
| `fonts/` | MiSans VF 字体 |
