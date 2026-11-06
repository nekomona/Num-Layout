# 为定数绘版做贡献

欢迎为定数绘版（NumLayoutPlug，简称 NLayout）提交问题报告、范围明确的修复、测试、文档和新示例。

## 先讨论较大的改动

较大的行为改动、新命令集成或部署结构调整，请先开 issue 讨论。小修复和文档改动可以直接提 PR。

请勿在 issue、commit、测试或文档中包含生产 cell 名、私有库或 PDK 路径、主机名、用户名、
私有版图截图或凭据。测试请使用一次性测试库和合成几何。

## 项目结构

| 路径 | 用途 |
| --- | --- |
| `src/` | 部署到 Virtuoso 的运行文件；请保持相对路径不变 |
| `docs/` | 公开 README、使用指南、发布说明和演示素材 |
| `test/` | 离线测试、实机验证脚本和手工检查 |
| `tools/` | 文档和图标生成器 |
| `.local/` | 被忽略的本地 agent 指令和工作笔记 |
| `artifacts/` | 被忽略的截图、报告、录制素材和构建输出 |

## 准备开发环境

插件运行时不需要 Python。处理文档和离线检查时，建议使用 Python 3.12 虚拟环境：

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r test/demo-requirements.txt
uv pip install --python .venv/bin/python -r test/pages-requirements.txt
```

Windows 下把 `.venv/bin/python` 换成 `.venv/Scripts/python.exe`。实机检查还需要
`virtuoso-bridge`、已配置的 Virtuoso 会话和专用可写测试库；运行前请阅读
[测试说明](test/README.md)。

## 修改时注意

- 一次 PR 尽量只解决一个问题；除非 issue 明确要求，不要改动现有用户快捷键。
- 沿用命令本身的处理顺序：先预览，用户确认后再应用。取消时要恢复临时绑定和表单状态。
- 修改 Wire 刷新辅助程序，或其他能在无 Virtuoso 环境下验证的逻辑时，请补上或更新离线测试。
- SKILL 行为要用合成几何在 Virtuoso 中手工验证。不要改现有用户版图，也不要使用生产库。
- 改动安装步骤、按键行为、截图或公开链接时，请同步更新中英文 README 和使用指南，并保持章节结构一致。
- 文档源文件修改后，要重新生成随仓库提交的文档产物。

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

请说明用户看到的问题、修改后的行为和已执行的检查；仍需在真实 Virtuoso 中验证的内容也要写明。
无关的清理不要混进同一个 PR。提交贡献即表示同意按本仓库的 [MIT 许可证](LICENSE) 提供修改。
