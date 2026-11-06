# 为 Numeric Layout Assist 做贡献

<a href="CONTRIBUTING.md" data-language-choice="en">English</a> · <a href="CONTRIBUTING.zh-CN.md" data-language-choice="zh">简体中文</a>

感谢你帮助改进 Numeric Layout Assist。欢迎提交问题报告、范围明确的修复、测试、文档和
新示例。

## 先讨论较大的改动

在开始较大的行为改动、新增命令集成或部署结构调整之前，请先开 issue。小型修复和文档
修正可以直接提交 pull request。

请勿在 issue、commit、测试或文档中包含生产 cell 名、私有库或 PDK 路径、主机名、用户名、
私有版图截图或凭据。测试请使用一次性测试库和合成几何。

## 项目结构

| 路径 | 用途 |
| --- | --- |
| `src/` | 部署到 Virtuoso 的运行文件；请保持相对路径不变 |
| `docs/` | 公开 README、用户教程、发布说明和演示素材 |
| `test/` | 离线测试、实机验证脚本和手工检查 |
| `tools/` | 文档和图标生成器 |
| `.local/` | 被忽略的本地 agent 指令和工作笔记 |
| `artifacts/` | 被忽略的截图、报告、录制素材和构建输出 |

## 开发环境

原生插件没有 Python 运行时依赖。文档和离线检查建议使用 Python 3.12 虚拟环境：

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r test/demo-requirements.txt
uv pip install --python .venv/bin/python -r test/pages-requirements.txt
```

Windows 下请将 `.venv/bin/python` 替换为 `.venv/Scripts/python.exe`。实机检查还需要
`virtuoso-bridge`、已配置的 Virtuoso 会话和专用可写测试库；运行前请阅读
[测试说明](test/README.md)。

## 修改原则

- 保持改动集中；除非 issue 明确要求修改行为，否则不要改变现有用户快捷键。
- 遵循原生命令生命周期：先预览，用户确认后再应用；取消时恢复临时绑定和表单状态。
- 修改 Wire 刷新辅助程序或其他可在无 Virtuoso 环境下验证的逻辑时，请新增或更新离线测试。
- 使用合成几何在 Virtuoso 中手工验证原生 SKILL 行为。不要修改现有用户版图或使用生产库。
- 修改安装步骤、按键行为、截图或公开链接时，同时更新英文和中文 README/用户教程，并保持
  章节结构对应，便于验证语言跳转。
- 文档源文件变化后，重新生成受版本控制的文档产物。

## 验证

请在仓库根目录运行与改动相关的检查：

```sh
python -m unittest discover -s test -t . -p "test_*.py" -v
python tools/build_guide.py
python tools/build_pages.py
python test/check_pages.py
```

修改演示或界面时，还应运行：

```sh
python test/check_demo.py
python test/check_demo_media.py
```

若使用 Microsoft Edge，可为浏览器检查传入 `--channel msedge`。生成的页面和 GIF 只有在
人工检查后才能提交；原始录制、报告和截图请放在 `artifacts/` 下。

## Pull request

请说明用户可见的问题和修改后的行为，列出已运行的命令，并注明仍需在真实 Virtuoso 中
检查的内容。不要把无关清理混入同一个 pull request。提交贡献即表示你同意按本仓库的
[MIT 许可证](LICENSE) 提供修改。
