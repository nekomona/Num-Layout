# 定数绘版使用指南

[项目概览](../README.zh-CN.md) · [交互演示](demo/index.html) · [测试](../test/README.md) · [参与贡献](../CONTRIBUTING.zh-CN.md)

定数绘版（Num-Layout）把数值输入和几何拾取接入 Virtuoso Layout 的常用命令。
当前按 Virtuoso IC23.1 适配；其他版本的字段名称和回调行为可能不同。

本页首次打开时会按浏览器语言选择中英文。也可以用右上角的 **EN / 中文** 手动切换，
选择后会同时应用到首页、使用指南和交互演示。

**目录：** [安装](#安装) · [工具栏与预览](#工具栏与预览) ·
[命令速查](#使用) · [X/Y 输入](#xy-输入与绝对位置) ·
[Copy 数量](#copy-数量n) · [数值输入与拾取](#j-数值输入) ·
[Contour](#为矩形做-contour) · [交互演示](#交互演示) · [仓库结构](#仓库结构)

## 安装

最新版本可从 [GitHub Releases](https://github.com/nekomona/Num-Layout/releases/latest) 下载。
发布页会同时提供 `nlayout-<tag>.tar.gz` 压缩包和对应的 `.sha1` 校验文件；解压后按下文
加载 `nlayout/numeric_assist.il` 即可。

从代码仓库部署时，运行文件都在 `nlayout/` 中，移动或上传时请保留原来的目录结构：

```text
nlayout/
  numeric_assist.il
  numeric_assist.drf
  wire_refresh.py
  icons/
    numeric_assist.png
    remove_steiners.png
```

从代码仓库直接加载时，在 Virtuoso CIW 中使用绝对路径：

```skill
load("/path/to/numeric-assist/nlayout/numeric_assist.il")
```

加载后会自动安装键位和工具栏。若希望启动 Virtuoso 时自动加载，可把同一行加入
自己的 `.cdsinit`。在 CIW 中执行 `vbnUninstall()`，即可恢复之前的键位并移除工具栏。

远程部署前，先在虚拟环境中安装 `virtuoso-bridge`，并配置 SSH 和 GUI 角色。随后在仓库根目录执行：

```sh
python deploy.py
# 可选：指定远程主机上的绝对安装目录。
python deploy.py --remote-dir /path/to/numeric-assist
```

部署脚本会通过 bridge 完成以下工作：上传 `nlayout/`、校验文件哈希、备份已有的 `.il`，
再加载插件。例如指定 `--remote-dir /opt/numeric-assist` 时，主文件会安装到
`/opt/numeric-assist/numeric_assist.il`，辅助脚本、显示资源和 `icons/` 放在同一目录。

Wire 刷新辅助程序依赖 GUI 主机上的 Python 3、libX11 和 XTest 扩展，并从 Virtuoso
继承 `DISPLAY` 与 `XAUTHORITY`。

## 工具栏与预览

工具栏上的标尺按钮用于开关 Num-Layout。按钮按下时，辅助功能处于启用状态。
路由节点加扫帚图标用于清除当前版图中的不可见 Steiner，原地编辑（edit-in-place）时也可使用。
清理完成后会报告删除数量；是否保存 cellview 仍由用户决定。工具栏注册在 Layout
会话的 **Window > Toolbars** 中。

候选轮廓显示为黄色；已选轮廓和测量箭头显示为洋红色。拾取范围遵循当前可见图层和
层次显示设置。插件使用 `numeric_assist.drf` 中自带的高亮数据。

确认 Wire 宽度后，`wire_refresh.py` 会先把指针沿 X 方向移动 32 像素、沿 Y 方向移动
16 像素，40 ms 后再移回原位。归位前会检查目标窗口、焦点、鼠标按键状态以及指针是否
被用户移动；只要检测到用户输入，就放弃归位。诊断状态可在 CIW 中查看：

```skill
list(vbnWireRefreshBusy vbnWireRefreshStatus)
```

指针成功归位，并不代表 Virtuoso 的动态拖动预览（rubberband）一定已经重绘。请在 Virtuoso
中按测试说明实际确认。

## 使用

先启动 **Rectangle**、**Path**、**Wire**、**Measurement (K)**、**Stretch**、
**Move** 或 **Copy**；也可以只选中一个矩形，再通过 Shift+J 进入 Contour。

| 当前命令 | 快捷键 | 确认数值后的效果 |
| --- | --- | --- |
| Path | J | 设置当前 Path 的宽度 |
| Wire | J | 设置当前 Wire 段的宽度 |
| Rectangle | J | 设置矩形宽高；输入格式为 `X,Y` |
| Measurement (K) | J | 设置新建两点标尺的长度 |
| Stretch | J | 选中一条边或端点时设置最终长度；选中整体或多个对象时设置位移 |
| Stretch | Shift+J | 设置 Stretch 的位移量 |
| Move | J | 设置 Move 的位移量 |
| Move | Shift+J | 设置参考点的绝对位置 |
| Copy | J | 设置每个副本的位移，并保留副本数量 |
| Copy | Shift+J | 设置第一个副本参考点的绝对位置 |
| Copy | N | 设置正整数副本数量，不放置副本 |
| 仅选中一个矩形、无活动命令 | Shift+J | 启动 Contour |

### X/Y 输入与绝对位置

在 Move、Copy、Stretch、Measurement 和 Rectangle 中输入逗号，数值会切换为 `X,Y` 格式。
两个分量都支持小数和负号，Backspace 正常编辑文本。同一分量里再输入一个逗号或小数点会被忽略。

| 场景 | `10,20` | `10,` | `,20` |
| --- | --- | --- | --- |
| J Move/Copy 或相对 Stretch | X 位移 10，Y 位移 20 | X 位移 10，Y 为 0 | X 为 0，Y 位移 20 |
| J 局部 Stretch 尺寸 | 宽 10，高 20 | 宽 10，高不变 | 高 20，宽不变 |
| J Rectangle | 宽 10，高 20 | 宽 10，高不变 | 高 20，宽不变 |
| J Measurement | 终点为起点加 (10,20) | 水平位移 10 | 垂直位移 20 |
| Shift+J Move/Copy | 目标位置 (10,20) | 目标 X=10，Y 不变 | 目标 Y=20，X 不变 |

使用 **Shift+J Move/Copy** 时，目标位置以当前命令的参考点为基准。若命令尚未记录参考点，
Num-Layout 会使用所选对象合并包围盒的中心。坐标以当前显示窗口为准，原地编辑时也一样。
只输入一个数值时，只会修改 X 或 Y；具体修改哪个轴，由指针相对参考点的方向决定，光标提示会标出当前轴。
绝对坐标可以为负。

显式输入 X/Y 时不受角度捕捉限制，但目标坐标仍会吸附到制造网格。相对距离仍遵循当前命令的
正交、45° 对角或任意角度模式。在 Move/Copy 的 J 与 Shift+J 之间切换，不会丢失尚未确认的输入、
已拾取的边或副本数量。重复 Copy 时，第一个目标使用命令指定的位置，后续目标重复相同位移；
每个 Step 目标都会提前预览。

绘制 **Rectangle** 时，在放下第一个角点前按 J，会填写 Specify Size 字段，供后续放置使用；
放下第一个角点后按 J，则会在指针所在象限预览并完成矩形。省略的分量会沿用已有字段值或当前暂定尺寸。
第一个角点之后，单值输入会根据鼠标方向选择一个轴；第一个角点之前，单值输入表示宽度。

调整**矩形尺寸**时，先用 partial Stretch 选中一条边或角点，再按 J 输入最终宽高，对边保持不动。
整体或多个对象的 Stretch 仍按相对位移处理，Shift+J Stretch 也一样。

逗号前的数值会保留为 X，包括预填值或拾取值。若要从空的 X 开始，先用 Escape 清除预填值；
在逗号后拾取只会填入 Y，不会覆盖已有的 X。单独输入 `,` 无法确认，尺寸值必须为正数。
N 仍然只接受整数；Path/Wire 宽度和 Contour 偏移只接受单值。最近一次成功的 X/Y 输入会记在
坐标模式中，单值模式则各自保留自己的记忆值。

### Copy 数量（N）

在 Copy 命令中按 **N**，用 `0`–`9` 输入正整数，然后用 **Enter**、**Space**、再次按 **N**
或点击画布确认。光标标签显示 `COPY COUNT`。小数会被忽略，0 不能确认。N 不拾取几何，
也不会改变已经记住的 J 距离。N 打开时按 **J** 或 **Shift+J**，会先应用待确认的数量，
再打开相对或绝对输入，但不会放置副本。数量为空或非法时，N 会保持打开，方便继续修改。

确认后，**Copies → Type: Step → Number** 会更新，数值输入关闭，Copy 仍在等待放置。
此步骤不会执行 Copy 的 Apply，也不会添加点。副本随后按 Copy 的原有流程放置。

进入 N 时，Copy 的副本数量会重置为 **1**。确认过的数量在打开 J 后仍会保留，因此可以先设数量、
再设位移。J 会按输入距离的连续倍数预览每个对象的 Step 目标，提示中带有数量，例如
`12 | COPY DISTANCE [3 copies]`。确认 J 后，所有副本一次放置完成。

取消任一辅助输入、再次进入 N 或离开 J，都会把数量重置为 **1**；若通过 J 确认，重置发生在放置之后。
Escape 会先清除 N 中的数字，再按一次则关闭数值输入，Copy 仍保持活动。Copy 之外，N 保持原有绑定；
关闭 Num-Layout 同样会恢复默认行为。卸载时会恢复之前的 N 输入函数（enter function）绑定，
正常 N 绑定不会被替换。

### J 数值输入

按下快捷键后，根据当前模式输入 `0`–`9`、`.`、`,`、`-` 或 Backspace。当前数值和模式会显示在指针旁；
只要有合法数值等待确认，就会显示结果轮廓。输入期间，Num-Layout 接管 Virtuoso 的点输入绑定，
退出后再恢复原来的放大镜绑定。

也可以直接点击图形边，用该边的长度作为数值。再选一条平行边，数值会改为两条边的间距；
若第二条边与之垂直，或继续选择第三条边，则重新开始单边测量。标尺的边也可以拾取。

对于 Wire 路径段，点击中心线或端点会取 Wire 的实际宽度；点击侧边会取侧边长度；再点击一条平行侧边，
则取两侧间距。黄色悬停线和洋红色选择箭头会标出正在测量的位置。拾取 Wire 时使用鼠标的原始位置，
这样 Virtuoso 的 Wire 捕捉不会把侧边点击误判为中心线点击。

边拾取会沿实例层次进入叶子图形，包括 PCell 几何和阵列元素。长度先经过实例变换，再换算到当前编辑
cellview 的坐标。Contour 也可以使用实例内部的矩形作为 pivot；被调整的源矩形仍位于当前编辑的 cellview 中。

下次打开 J 时会预填最近一次确认的数值。直接确认即可复用，输入数字则会替换预填值。Escape 会先清除预填值，
再关闭辅助。Wire 和 Path 拾取使用 Virtuoso 捕捉前的鼠标位置；点击 Wire 纵向中心线的任意位置（包括端点）
都会拾取其宽度。

指针所在边显示为黄色，选中的边和长度箭头显示为洋红色。Contour 之外，可用 **Enter**、**Space**、
再次按同一快捷键或点击空白画布确认。已选边时按 Escape 会回到数值输入；有数字时按 Escape 会清除数字；
输入为空时按 Escape 会关闭 Num-Layout，当前命令继续运行。用于拾取边或确认数值的点击由 Num-Layout
处理，不会再让当前命令添加点。

设置绝对 Stretch 长度时，要在按 J 之前用 Stretch 选中一条**边或端点**。若选中的是整体或多个对象，
J 会把数值作为位移量，输入、预览和捕捉方向都与 Move 相同。标尺或直线 Path 使用端点间距离；其他图形则按
Stretch 方向取 X 或 Y 方向的包围范围。Shift+J 使用从当前命令参考点指向光标的方向。

Wire 中，J 会更新 Create Wire 表单的 `wireWidth` 字段。确认前，当前段的轮廓按该宽度预览；确认后
Wire 命令仍保持活动，后续点沿用新宽度。

对于 **Measurement (K)**，先放置第一个点，把指针移向目标方向，再按 J。输入或拾取长度并确认后，
会保存一条对应长度的标尺，确认前用线段预览结果，活动中的 Measurement 命令随后结束。端点会吸附到制造网格，
因此斜向长度可能有少量网格误差。在对 group 内容或实例做原地编辑时，标尺使用当前编辑 cell 的坐标，
以保持指定位置。

对于 **Copy**，先选对象并启动 Copy。按 J 输入相对位移，按 Shift+J 输入绝对位置。单值相对距离遵循
Copy 表单的捕捉模式。若 Copy 尚未记录参考点，Num-Layout 会把所选对象合并包围盒的中心作为方向原点。
确认时使用 Copy 表单 Pitch 模式下的 X/Y 字段和 Apply 动作，并保留当前的 Single、Step 或 Array 设置。

## 为矩形做 Contour

确保没有活动命令，选中一个矩形后按 Shift+J。输入正的偏移量，或拾取一条边、两条平行边的间距。按 Enter
或 Space 进入下一阶段。第二阶段默认选择单边（edge）：按顺时针或逆时针点击四条边，定义两个不同的 X 边界
和两个不同的 Y 边界。按 **Shift+J** 切换到矩形（rectangle）模式；若指针下同时有矩形和边，矩形优先。
按 **J** 回到只选边的模式。切换模式会保留当前边或 pivot；重新选一个矩形则会替换已选边集合。源矩形的原边界
也可以作为 pivot。拾取矩形时允许与显示边界有少量距离，确认后会根据选中的边重建四边 pivot，边段不必一直延伸到角点。

只有选中有效的 pivot 后，Enter 或 Space 才会进入第三阶段。把指针移到 pivot 内侧或外侧预览结果，
再点击或确认，即可调整并移动最初选中的矩形。偏移量同时作用于四条边。若向内缩进会使任一维度消失，
则只能选择向外。每次 Escape 回退一个阶段；处在数值阶段时，第一次 Escape 只清除数字，再按才退出。

Move、Copy 的 J/Shift+J，以及 Stretch 的两种位移模式，都会跟随当前命令的分段捕捉方式：正交、
45° 对角或任意角度。表单提供水平或垂直模式时也会遵循。捕捉模式请在 Virtuoso 表单中修改；Num-Layout
绘制预览和应用数值时会读取这项设置。

辅助功能会把目标坐标吸附到工艺制造网格。Stretch 完成后，它会根据绝对目标坐标设置矩形范围、
选中的 Path 点和直线 Path/标尺端点，避免相对位移产生半格误差。没有可编辑点的图形则直接采用
Stretch 的结果。指定的斜向长度可能会落到最近的网格坐标。

## 交互演示

在浏览器中打开[演示网站](demo/index.html)。这是一个自包含的静态站点，由 `index.html`、`style.css`
和 `app.js` 组成。可以直接打开 HTML 文件，也可以在仓库根目录启动本地服务：

```sh
python -m http.server 8000 --bind 127.0.0.1
```

然后访问 `http://127.0.0.1:8000/docs/demo/`。选择工具、修改数值，并通过 **Play / Pause**、
**Next step** 或步骤按钮控制播放。当前工具可以写入 URL，例如 `index.html#copy` 或 `index.html#contour`。

首次打开时会根据浏览器语言自动选择中文或英文。右上角的 **EN / 中文** 会同时切换整个界面、
教程与概览链接；手动选择会被记住。也可以在 URL 后加 `?lang=en` 或 `?lang=zh-CN` 强制指定语言。

选择工具后，动画会从头播放，并默认开启 **单页循环**。用 **Speed**（0.25×–3×）调速不会丢失当前进度；
关闭单页循环后，动画只播放一次。每轮结束后会等待 3 秒，这个等待时间不受播放速度影响。指针从空白区域出发，
在最后一步末尾回到原位，操作栏随后显示 **完成。**

**循环展示**是另一套模式，在用户还没点击任何内容时默认开启。一个工具的动画结束后等待 3 秒，
再从第一步播放下一项；最后一项结束后回到第一项继续播放。切换时，工具列表左侧的活动标记会滑到下一项。
点击任意工具、演示画布内部，或操作任一播放和数值控件，都会关闭循环展示，方便停在当前工具中检查；
之后可以随时点 **循环展示** 重新开启。循环展示关闭后，**单页循环**仍控制当前动画是否重复。

下拉选项变更、按 Enter、离开输入框，或停止输入 3 秒后，**尝试数值**会自动重播。合法小数会先规范化再播放；
非法输入会显示错误，并保留上一次有效值。**应用并重播**也会用当前值从头播放。

动画会让指针先移到目标，再显示悬停高亮。每次输入都会按下对应的键帽；数字在 1× 速度下每 260 ms 出现一位。
点击和其他命令键之后至少保留 1.2 秒，方便看清结果。光标气泡沿用插件的实际标签文本，说明文字放在面板底栏。
演示中的小数会四舍五入到四位，Copy 数量仍为整数。这些规则仅用于演示，不改变插件本身的精度。

命令名和光标气泡标签保持英文，以便与真实 Virtuoso 界面对应；其余界面文字和说明均已提供中文。

如需部署到网站，请参阅[GitHub 与 GitLab Pages 部署说明](PUBLISHING.md)。

在试验场中可以修改每个工具的数值，并按自己的节奏查看输入、预览和确认过程。

| 演示 | 可以试什么 | 动画 |
| --- | --- | --- |
| [拾取尺寸](demo/index.html#pick) | 从单边长度切换到平行边间距 | [观看](media/pick.gif) |
| [Path / Wire](demo/index.html#width) | 修改宽度并确认 | [观看](media/width.gif) |
| [Rectangle](demo/index.html#rectangle) | 用 `X,Y` 输入宽和高 | [观看](media/rectangle.gif) |
| [Measurement](demo/index.html#measure) | 设置标尺长度 | [观看](media/measure.gif) |
| [Stretch](demo/index.html#stretch) | 设置局部选择后的最终 X 尺寸 | [观看](media/stretch.gif) |
| [Move](demo/index.html#move) | 对比相对位移与绝对位置 | [观看](media/move.gif) |
| [Copy](demo/index.html#copy) | 先设置 N，再用 J 设置 Step 位移 | [观看](media/copy.gif) |
| [Contour](demo/index.html#contour) | 围绕 pivot 切换向内/向外 | [观看](media/contour.gif) |
| [Steiner 清理](demo/index.html#cleanup) | 删除合成 Steiner 标记，保留图形 | [观看](media/cleanup.gif) |

重新生成动画，或录制真实、隔离的 Virtuoso 会话时，请参阅[演示录制说明](../test/DEMO_MEDIA.md)。

## 仓库结构

`nlayout/` 包含 SKILL 程序和全部部署资源；根目录的 `deploy.py` 负责安装。
`tools/generate_icons.py` 用于重新生成 `nlayout/icons/` 中的图标，需要 Pillow。`docs/` 保存公开文档，
`docs/demo/` 是交互演示，`docs/media/` 是审核后的图片和动画。`test/` 包含测试脚本与手工检查步骤。
本地 agent 指令放在 `.local/agent/`，截图、验证报告和其他测试输出放在 `artifacts/`；这两个目录都被 Git 忽略。

开发流程、测试要求和提交前检查见[贡献指南](../CONTRIBUTING.zh-CN.md)。
