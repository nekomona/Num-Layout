<p align="center">
  <img src="docs/media/banner.svg" alt="Numeric Layout Assist — 光标即精确。" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-6b45b9?style=flat-square" alt="MIT 许可证"></a>
  <a href="docs/numeric_assist_guide.zh-CN.md"><img src="https://img.shields.io/badge/Virtuoso-IC23.1-527c79?style=flat-square" alt="Virtuoso IC23.1"></a>
  <a href="src/numeric_assist.il"><img src="https://img.shields.io/badge/built_with-SKILL-bb667f?style=flat-square" alt="使用 SKILL 构建"></a>
</p>

<p align="center">
  <a href="README.md">English</a> &nbsp;·&nbsp; <a href="README.zh-CN.md"><b>简体中文</b></a>
</p>

<p align="center">
  <b><a href="docs/numeric_assist_guide.zh-CN.md">用户教程</a></b> &nbsp;·&nbsp;
  <b><a href="docs/demo/index.html">交互演示</a></b> &nbsp;·&nbsp;
  <a href="docs/numeric_assist_guide.zh-CN.md#安装">安装</a> &nbsp;·&nbsp;
  <a href="test/README.md">测试</a> &nbsp;·&nbsp;
  <a href="CONTRIBUTING.zh-CN.md">参与贡献</a>
</p>

为原生 **Virtuoso Layout** 命令补上精确数值输入。直接从版图上拾取长度或间距，
也可以输入已知尺寸，并在提交前于光标旁预览结果。**J** 负责数值输入，
**Shift+J** 提供绝对定位与 Contour，**N** 设置 Copy 数量。

## 动起来看看

<p align="center">
  <a href="docs/demo/index.html"><img src="docs/media/overview.gif" alt="四种工具的 2×2 演示：拾取尺寸、设置 Path 宽度、创建精确标尺、连续复制；同一时间只有一个面板播放。" width="100%"></a>
</p>

**尺寸拾取 → Path 宽度 → Measurement → Copy。** 四个面板依次播放，每次切换前
停留一秒。动画使用合成几何，仅用于说明。打开
[交互演示](docs/demo/index.html) 可以修改数值、调整播放速度并逐步查看所有工具。
站点可直接打开 HTML 文件运行；[本地预览说明](docs/numeric_assist_guide.zh-CN.md#交互演示)
和 [Pages 部署](docs/PUBLISHING.md) 见单独文档。

## 工具一览

| 工具 | 它能帮你做什么 | 查看 / 体验 |
| --- | --- | --- |
| **尺寸拾取** | 读取边长度、wire 宽度或平行边间距 | [GIF](docs/media/pick.gif) · [试用](docs/demo/index.html#pick) |
| **Path / Wire** | 绘制时设置宽度 | [GIF](docs/media/width.gif) · [试用](docs/demo/index.html#width) |
| **Rectangle** | 一次输入宽和高 | [GIF](docs/media/rectangle.gif) · [试用](docs/demo/index.html#rectangle) |
| **Measurement** | 给新标尺一个精确长度 | [GIF](docs/media/measure.gif) · [试用](docs/demo/index.html#measure) |
| **Stretch** | 设置局部选择的最终尺寸，或整体移动 | [GIF](docs/media/stretch.gif) · [试用](docs/demo/index.html#stretch) |
| **Move** | 使用相对位移或绝对坐标 | [GIF](docs/media/move.gif) · [试用](docs/demo/index.html#move) |
| **Copy + count** | 设置数量和间距，并预览每个 Step 目标 | [GIF](docs/media/copy.gif) · [试用](docs/demo/index.html#copy) |
| **Contour** | 围绕指定 pivot 向内或向外调整矩形 | [GIF](docs/media/contour.gif) · [试用](docs/demo/index.html#contour) |
| **Steiner 清理** | 删除当前版图中的不可见 Steiner 对象 | [GIF](docs/media/cleanup.gif) · [试用](docs/demo/index.html#cleanup) |

工具栏上的标尺按钮用于开关 Numeric Assist。完整命令行为、安装方法、网格处理与
快捷键恢复说明见 **[用户教程](docs/numeric_assist_guide.zh-CN.md)**。

## 致谢

本项目在开发和 Virtuoso 测试过程中使用了 [Virtuoso Bridge Lite](https://github.com/Arcadia-1/virtuoso-bridge-lite) —— 一个轻巧好用的 Virtuoso 开发桥接工具。
