# 打包说明 - 解决 macOS Tkinter 兼容性问题

## 问题描述

在 macOS 上运行时遇到错误：
```
macOS 15 (1507) or later required, have instead 15 (1506) !
```

这是 Python 的 tkinter 库与 macOS 系统版本不兼容导致的。

## 解决方案

**使用 PyInstaller 打包可以解决这个问题**。PyInstaller 会将 tkinter 嵌入到可执行文件中，不再依赖系统的 tkinter 库。

### 方案一：使用命令行版本（立即可用）

如果无法立即解决 GUI 问题，可以先使用命令行版本：

```bash
python3 validator_cli.py
```

命令行版本提供了完整的功能，包括：
- 目录选择
- 文件校验
- 结果导出（TXT/CSV）

### 方案二：使用 PyInstaller 打包（推荐）

#### 1. 安装 PyInstaller

```bash
pip3 install pyinstaller
```

#### 2. 打包 GUI 版本

```bash
pyinstaller --onefile --windowed --name="网络数据包校验工具" validator.py
```

或者打包命令行版本：

```bash
pyinstaller --onefile --name="网络数据包校验工具" validator_cli.py
```

#### 3. 打包参数说明

- `--onefile`: 打包成单个可执行文件
- `--windowed`: GUI 模式（不显示控制台窗口），命令行版本不需要此参数
- `--name="程序名"`: 指定生成的可执行文件名

#### 4. 打包后的文件

打包完成后，可执行文件位于 `dist/` 目录：
- `dist/网络数据包校验工具`（macOS）
- `dist/网络数据包校验工具.exe`（Windows）

#### 5. 分发

将 `dist/` 目录下的可执行文件分发给用户，用户直接双击即可运行，无需安装 Python。

## 其他方案

### 方案三：安装 PyInstaller 并测试

即使当前无法运行 tkinter GUI，打包后的可执行文件可能可以正常工作。尝试打包并测试：

```bash
# 安装 PyInstaller
pip3 install pyinstaller

# 打包 GUI 版本
pyinstaller --onefile --windowed --name="测试版" validator.py

# 测试运行
./dist/测试版
```

### 方案四：使用不同的 Python 版本

某些 Python 版本可能对 macOS 有更好的兼容性。可以尝试：

```bash
# 使用 Homebrew 安装较新的 Python
brew install python@3.11

# 使用新版本运行
python3.11 validator.py
```

## 当前可用的文件

- `validator.py` - GUI 版本（需要 tkinter，打包后可用）
- `validator_cli.py` - 命令行版本（立即可用）
- `validator_psg.py` - PySimpleGUI 版本（未测试）
- `utils/file_scanner.py` - 文件扫描器（核心逻辑）

## 建议

1. **立即可用**: 使用 `validator_cli.py` 命令行版本
2. **长期方案**: 使用 PyInstaller 打包 `validator.py` 或 `validator_cli.py`
3. **用户分发**: 只需提供打包后的可执行文件，用户无需安装 Python 或依赖

## 技术说明

Tkinter 兼容性问题仅影响开发环境和直接运行 Python 脚本的情况。通过 PyInstaller 打包后，所有依赖（包括 tkinter）都嵌入到可执行文件中，不受系统版本影响。
