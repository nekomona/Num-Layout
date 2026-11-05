# Numeric Layout Assist — 用户教程

[English](numeric_assist_guide.md) · [简体中文](numeric_assist_guide.zh-CN.md)

[项目概览](../README.zh-CN.md) · [交互演示](demo/index.html) · [测试](../test/README.md) · [参与贡献](../CONTRIBUTING.zh-CN.md)

Numeric Layout Assist 为原生 Virtuoso Layout 命令加入数值输入和几何拾取。
当前以 Virtuoso IC23.1 为目标版本；其他版本的原生表单字段和回调行为可能不同。

**目录：** [安装](#安装) · [工具栏与预览](#工具栏与预览) ·
[命令速查](#使用) · [X/Y 输入](#xy-输入与绝对位置) ·
[Copy 数量](#copy-数量n) · [几何拾取与确认](#j-数值输入) ·
[Contour](#为矩形做-contour) · [交互演示](#交互演示) ·
[仓库结构](#仓库结构)

## 安装

可部署的运行文件都在 `src/` 中。请保持它们的相对路径不变：

```text
src/
  numeric_assist.il
  numeric_assist.drf
  wire_refresh.py
  icons/
    numeric_assist.png
    remove_steiners.png
```

如果直接从代码仓库加载，在 Virtuoso CIW 中使用绝对路径：

```skill
load("/path/to/numeric-assist/src/numeric_assist.il")
```

加载脚本时会安装快捷键绑定和工具栏。要在 Virtuoso 启动时自动加载，可将上面的
命令行加入自己的 `.cdsinit`。在 CIW 中运行 `vbnUninstall()` 可恢复之前的绑定并
移除工具栏。

远程部署时，请先在虚拟环境中安装 `virtuoso-bridge`，并配置 SSH 与 GUI 角色。
在本仓库中运行：

```sh
python deploy.py
# 可选：指定远程主机上的绝对安装目录。
python deploy.py --remote-dir /path/to/numeric-assist
```

部署脚本会把 `src/` 的内容上传到安装目录、校验文件哈希、备份已安装的 `.il`，
再通过 bridge 加载插件。例如，`--remote-dir /opt/numeric-assist` 会安装
`/opt/numeric-assist/numeric_assist.il`，辅助脚本、显示资源文件和 `icons/`
会放在同一目录。Wire 刷新辅助程序需要 GUI 主机上的 Python 3、libX11 和
XTest 扩展，并从 Virtuoso 继承 `DISPLAY` 与 `XAUTHORITY`。

## 工具栏与预览

标尺图标用于开关 Numeric Assist；按钮处于按下状态时表示辅助功能已启用。
路由节点与扫帚图标会删除当前版图中的不可见 Steiner，包括 edit-in-place 场景。
清理后会报告删除数量，保存操作仍由用户决定。工具栏注册在 Layout 会话的
**Window > Toolbars** 管理器中。

候选轮廓显示为黄色；已选轮廓和测量箭头显示为洋红色。拾取会遵循当前可见图层和
层次显示级别。插件从 `numeric_assist.drf` 加载自己的高亮 packet。

确认 Wire 宽度后，`wire_refresh.py` 会先沿 X 方向移动指针 32 像素、沿 Y 方向移动
16 像素，再在 40 ms 后返回。返回前会检查目标窗口、焦点、按住的鼠标按键以及指针
是否被用户移动；若期间有用户输入，则取消返回。可通过以下 CIW 表达式查看诊断状态：

```skill
list(vbnWireRefreshBusy vbnWireRefreshStatus)
```

指针成功返回并不等于原生 rubberband 一定重绘。请按测试说明在 Virtuoso 中做交互验证。

## 使用

先启动原生 **Rectangle**、**Path**、**Wire**、**Measurement (K)**、**Stretch**、
**Move** 或 **Copy** 命令；也可以只选择一个矩形，然后进入 Contour。

| 当前命令 | 快捷键 | 确认数值的含义 |
| --- | --- | --- |
| Path | J | 当前 Path 的宽度 |
| Wire | J | 当前 Wire 段的宽度 |
| Rectangle | J | 矩形宽高；输入 `X,Y` |
| Measurement (K) | J | 新建两点标尺的长度 |
| Stretch | J | 单条选中边/端点的最终长度；整体或多个对象时为位移 |
| Stretch | Shift+J | Stretch 的位移大小 |
| Move | J | Move 位移大小 |
| Move | Shift+J | 参考点的绝对位置 |
| Copy | J | 每个副本的位移，并保留副本数量 |
| Copy | Shift+J | 第一个副本参考点的绝对位置 |
| Copy | N | 正整数副本数量，不放置副本 |
| 仅选中一个矩形、无活动命令 | Shift+J | 启动 Contour |

### X/Y 输入与绝对位置

在 Move、Copy、Stretch、Measurement 和 Rectangle 中，输入逗号会切换到 `X,Y`。
每个分量都支持小数和前置负号，Backspace 正常编辑文本；同一分量中的第二个逗号
或第二个小数点是无效输入，会被忽略。

| 场景 | `10,20` | `10,` | `,20` |
| --- | --- | --- | --- |
| J Move/Copy 或相对 Stretch | X 位移 10，Y 位移 20 | X 位移 10，Y 为 0 | X 为 0，Y 位移 20 |
| J 局部 Stretch 尺寸 | 宽 10，高 20 | 宽 10，高不变 | 高 20，宽不变 |
| J Rectangle | 宽 10，高 20 | 宽 10，高不变 | 高 20，宽不变 |
| J Measurement | 终点为起点 + (10,20) | 水平位移 10 | 垂直位移 20 |
| Shift+J Move/Copy | 目标位置 (10,20) | 目标 X=10，Y 不变 | 目标 Y=20，X 不变 |

对于 **Shift+J Move/Copy**，目标是原生命令的参考点。若没有记录参考点，Numeric
Assist 会使用所选对象合并包围盒的中心。坐标采用当前显示窗口的坐标系，包括
edit-in-place。输入**单个数值**时，只修改 X 或 Y，轴由指针相对参考点的方向决定，
光标提示会显示当前轴。绝对坐标允许负数。

显式 X/Y 分量不受角度吸附约束，但目标坐标仍会落在制造网格上。标量相对距离保留
原生命令的正交、45 度或任意角度行为。Move/Copy 中在 J 与 Shift+J 间切换会保留
尚未提交的输入、已拾取的边和副本数量。重复 Copy 时，第一个目标使用命令指定位置，
后续目标重复相同位移；所有 Step 目标都会预览。

绘制 **Rectangle** 时，在第一个角点前按 J 会设置原生 Specify Size 字段，供后续放置
使用；放下第一个角点后，J 会在指针所在象限中预览并完成矩形。省略的尺寸会保留
现有原生字段值或当前暂定矩形尺寸。第一个角点之后，单个数值会根据鼠标方向选择轴；
第一个角点之前，单个数值表示宽度。

调整**矩形尺寸**时，先用原生 partial Stretch 选择边或角点，再用 J 输入最终宽/高，
对边保持不动。整体或多个对象的 Stretch 仍使用相对位移；Shift+J Stretch 也保持
相对模式。

逗号前的数值会保留为 X，包括预填值或拾取值。如果要从空 X 开始，请先用 Escape
清除预填值；在逗号后拾取会填入 Y，同时保留已有 X。空的 `,` 不能确认；尺寸必须为
正数。N 仍只接受整数；Path/Wire 宽度和 Contour 偏移保持为标量。最近一次成功的
X/Y 输入会在笛卡尔模式下记住，标量模式保留各自的标量记忆。

### Copy 数量（N）

在原生 Copy 中按 **N**，用 `0`–`9` 输入正整数，再用 **Enter**、**Space**、再次
按 **N** 或点击画布确认。光标标签显示 `COPY COUNT`。小数会被忽略，零不能确认。
N 不拾取几何，也不改变已记住的 J 距离。N 打开时按 **J** 或 **Shift+J** 会先应用
待确认数量，再打开相对或绝对输入，但不会立即放置副本。非法或空数量会保持 N
打开，方便继续修改。

确认后，原生 **Copies → Type: Step → Number** 会被设置，数值输入关闭，Copy 仍等待
放置。此时不会调用 Copy 的 Apply，也不会添加点；随后按原生 Copy 流程放置副本。

进入 N 会把原生副本数量重置为 **1**。确认后的 N 数量在打开 J 时仍会保留，所以可以先
用 N 确定副本数，再用 J 设置位移。J 会按输入距离的连续倍数预览每个选中对象的每个
Step 副本目标，提示中包含数量，例如 `12 | COPY DISTANCE [3 copies]`。确认 J 后会
一次放置所有副本。

取消任一辅助输入、再次进入 N 或退出 J 都会把数量重置为 **1**；若由 J 确认，
重置发生在放置完成之后。Escape 会先清除 N 的数字；再按一次 Escape 会关闭数值输入，
同时保留原生 Copy。Copy 之外，N 保持原有原生绑定；关闭 Numeric Assist 也会恢复
N 的原生行为。卸载时会恢复之前的 N enterfunction 绑定，正常 N 绑定不会被替换。

### J 数值输入

按下快捷键后，根据当前模式输入 `0`–`9`、`.`、`,`、`-` 或 Backspace。当前输入与模式
显示在光标旁；有合法数值待确认时会出现结果轮廓。数值输入期间，Numeric Assist 会
临时占用 Virtuoso 的物理点绑定，关闭辅助后再恢复原来的放大镜绑定。

也可以点击图形边直接使用其长度。选择第二条平行边后，数值变为两条边的间距；
选择垂直的第二条边或任意第三条边，会重新开始一次单边测量。标尺的边也可以拾取。

对于 wire 路径段，点击中心线或端点会使用 wire 的实际宽度；点击侧边会使用该侧边长；
再点击一条平行侧边则使用两侧间距。黄色悬停线和洋红色选择箭头会标出正在测量的具体
特征。拾取 wire 时使用原始鼠标位置，避免原生 Wire 吸附把侧边点击变成中心线点击。

边拾取会沿实例层次进入叶子图形，包括 PCell 几何和阵列元素。测得长度会先按实例
变换转换，再以当前编辑 cellview 的坐标表示。Contour 也可以使用实例内部的矩形作为
pivot；被调整的源矩形仍位于当前编辑 cellview 中。

下次打开 J 时会预填最近一次确认的数值。直接确认可复用它，输入数字会替换预填值。
Escape 会先清除预填值，再关闭辅助。Wire 和 Path 的拾取使用原生吸附前的鼠标位置；
点击 wire 纵向中心线上的任意位置（包括端点）都会拾取其宽度。

指针下的边显示为黄色；已选边与长度箭头显示为洋红色。Contour 之外，可用 **Enter**、
**Space**、再次按同一快捷键或点击空白画布确认。已选边时按 Escape 会返回数值输入；
有数字时按 Escape 会清除数字；空输入时按 Escape 会关闭 Numeric Assist，并保留原生
命令。用于拾取边或确认数值的点击会被 Numeric Assist 消耗，不会给原生命令添加点。

绝对 Stretch 长度要求在按 J 前用原生 Stretch 选择一条**边或端点**。若选择整体或
多个对象，J 使用位移大小，并提供与 Move 相同的数值输入、预览和吸附方向。标尺或直线
Path 使用端点间距离；其他图形按 Stretch 方向使用 X 或 Y 包围范围。Shift+J 使用从
原生命令参考点指向光标的方向。

Wire 中，J 会更新原生 Create Wire 表单的 `wireWidth` 字段。确认前，当前段轮廓使用
该宽度；确认后原生 Wire 命令仍保持活动，后续点会使用新宽度。

对于 **Measurement (K)**，先放置第一个点，朝目标方向移动指针，再按 J。输入或拾取
长度并确认后，会创建对应长度的已保存标尺，确认前用线段预览结果，活动 Measurement
命令随后结束。端点会吸附到制造网格，所以斜向长度可能有少量网格误差。在下降后的
group 内容或实例中 edit-in-place 时，标尺采用当前编辑 cell 的坐标，以保持指定位置。

对于 **Copy**，先选择对象并启动原生 Copy。按 J 输入相对位移，按 Shift+J 输入绝对
位置。标量相对距离遵循 Copy 表单的吸附模式。若 Copy 尚未记录参考点，Numeric Assist
使用所选对象合并包围盒中心作为方向原点。确认时会使用原生 Copy 表单 Pitch 模式下的
X/Y 字段和 Apply 动作，并保留当前 Single、Step 或 Array 设置。

## 为矩形做 Contour

在没有活动命令时选择一个矩形，然后按 Shift+J。输入正偏移，或拾取一条边、平行边间距。
按 Enter 或 Space 进入下一阶段。第二阶段从 **edge** 模式开始：点击四条边，定义两个
不同的 X 边界和两个不同的 Y 边界。按 **Shift+J** 切换到 **rectangle** 模式；指针处
同时存在矩形及其边时，矩形优先。按 **J** 返回仅拾取边的模式。切换模式会保留当前
边或 pivot 选择；拾取新矩形会替换已有边集合。源矩形原边界也可作为 pivot。矩形拾取
允许与显示边界有少量距离；确认后会根据选中的边重建四边 pivot，边段不必延伸到角点。

只有已选中有效 pivot 后，Enter 或 Space 才会进入第三阶段。将指针移至 pivot 内侧或
外侧可预览结果，再点击或确认即可调整并移动最初选中的矩形。偏移作用于四条边。若向内
缩进会使任一维度消失，则只能选择向外。每次 Escape 回退一个阶段；从数值阶段开始时，
第一次 Escape 先清除数字，再退出。

Move 和 Copy 的 J/Shift+J，以及 Stretch 的两种位移模式，都会在决定位移方向时遵循
原生命令当前的分段吸附模式：正交、对角（45 度增量）或任意角度。表单提供水平或垂直
模式时也会遵循。请在原生表单中切换吸附模式；Numeric Assist 在绘制预览和应用数值时
读取该设置。

辅助功能会把目标坐标吸附到工艺制造网格。原生 Stretch 完成后，它会根据绝对目标坐标
设置矩形范围、选中 Path 点和直线 Path/标尺端点，避免原生相对位移产生半格舍入误差。
没有可编辑点的图形使用原生 Stretch 的结果。指定的斜向长度可能被吸附到最近的网格坐标。

## 交互演示

在浏览器中打开[演示网站](demo/index.html)。它是自包含的静态站点，由 `index.html`、
`style.css` 和 `app.js` 组成。可以直接打开 HTML 文件，也可以在仓库根目录启动本地服务：

```sh
python -m http.server 8000 --bind 127.0.0.1
```

然后访问 `http://127.0.0.1:8000/docs/demo/`。选择工具、修改数值，并使用
**Play / Pause**、**Next step** 或步骤按钮。工具选择可以加入书签，例如
`index.html#copy` 或 `index.html#contour`。

选择工具后，动画会从头播放，并默认开启 **Loop**。用 **Speed**（0.25×–3×）调整速度，
当前进度不会丢失；关闭 **Loop** 可只播放一次。每轮完成后等待三秒，任何播放速度下该
等待都保持三秒。指针从空白区域出发，并在最后一步的末尾回到原位，随后操作栏显示
**Done.**。

下拉选项变化、按 Enter、离开输入框或停止输入三秒后，**Try a value** 会自动回放。
合法小数会先规范化再播放；非法输入会显示错误并保留上一次有效值。
**Apply & replay** 也会使用当前值从头播放。

动画会让指针先移动到目标，再显示 hover 高亮。每次输入事件都会按下对应键帽；数字以
1× 速度每 260 ms 显示一个字符。点击和其他命令键之后至少保留 1.2 秒用于观察结果。
光标气泡使用插件实际标签文本，解释性文字显示在面板底栏。演示中的小数四舍五入到四位，
Copy 数量仍为整数。这些规则只用于插画，不改变原生插件精度。

如需托管站点，可使用与仓库地址无关的
[GitHub 与 GitLab Pages 部署流程](PUBLISHING.md)。

所有场景都使用合成几何，只解释输入、预览和确认过程；它们不会执行 SKILL，也不复刻
Cadence UI。坐标采用理想网格。原生吸附、层次、表单回调和指针刷新行为仍须在 Virtuoso
中验证。

| 演示 | 试一下 | 动画 |
| --- | --- | --- |
| [拾取尺寸](demo/index.html#pick) | 从单边长度切换到平行边间距 | [观看](media/pick.gif) |
| [Path / Wire](demo/index.html#width) | 修改宽度并确认 | [观看](media/width.gif) |
| [Rectangle](demo/index.html#rectangle) | 以 `X,Y` 输入宽和高 | [观看](media/rectangle.gif) |
| [Measurement](demo/index.html#measure) | 设置标尺长度 | [观看](media/measure.gif) |
| [Stretch](demo/index.html#stretch) | 设置局部选择的最终 X 尺寸 | [观看](media/stretch.gif) |
| [Move](demo/index.html#move) | 对比相对位移和绝对位置 | [观看](media/move.gif) |
| [Copy](demo/index.html#copy) | 先设置 N，再用 J 设置 Step 位移 | [观看](media/copy.gif) |
| [Contour](demo/index.html#contour) | 围绕 pivot 切换向内/向外 | [观看](media/contour.gif) |
| [Steiner 清理](demo/index.html#cleanup) | 删除合成 Steiner 标记并保留图形 | [观看](media/cleanup.gif) |

重新生成动画或录制真实、隔离的 Virtuoso 会话时，请参阅
[演示录制说明](../test/DEMO_MEDIA.md)。

## 仓库结构

`src/` 包含 SKILL 程序和所有部署资源；根目录的 `deploy.py` 负责安装。
`tools/generate_icons.py` 可重新生成 `src/icons/` 中的图标，需要 Pillow。
`docs/` 保存公开使用文档；`docs/demo/` 是交互演示，`docs/media/` 是审核后的文档资源。
`test/` 保存测试脚本和手工检查步骤。本地 agent 指令放在 `.local/agent/`；截图、验证报告
和其他测试输出放在 `artifacts/`。两个本地目录都被 Git 忽略。

开发流程、测试要求和提交前检查见 [贡献指南](../CONTRIBUTING.zh-CN.md)。
