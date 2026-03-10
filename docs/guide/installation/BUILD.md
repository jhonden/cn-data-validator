# 打包指南

本文档介绍如何在 Windows、macOS 和 Linux 上打包网络数据包校验工具。

## 快速开始

### Windows 用户

1. 双击运行 `build_windows.bat`
2. 等待打包完成
3. 在 `dist` 文件夹中找到生成的 `.exe` 文件

### macOS/Linux 用户

1. 运行打包脚本：
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```

2. 在 `dist` 文件夹中找到生成的可执行文件

---

## 详细说明

### Windows 打包

#### 前置要求

- Python 3.6 或更高版本
- 网络连接（用于安装依赖）

#### 使用打包脚本

1. 打开命令提示符（CMD）或 PowerShell
2. 进入项目目录：
   ```cmd
   cd C:\path\to\cn-data-validator
   ```
3. 运行打包脚本：
   ```cmd
   build_windows.bat
   ```
4. 脚本会自动：
   - 检查并安装 PyInstaller
   - 检查并安装 PyQt6
   - 打包 PyQt6 GUI 版本
   - 询问是否同时打包命令行版本
5. 生成的文件在 `dist\` 文件夹中

#### 手动打包（可选）

如果脚本无法运行，可以手动执行：

```cmd
# 安装依赖
pip install pyinstaller PyQt6

# 打包 GUI 版本
pyinstaller --onefile --windowed --name="网络数据包校验工具" validator_qt.py

# 打包命令行版本
pyinstaller --onefile --name="网络数据包校验工具-CLI" validator_cli.py
```

### macOS 打包

#### 前置要求

- Python 3.6 或更高版本
- Xcode 命令行工具（通常已安装）

#### 使用打包脚本

```bash
# 添加执行权限
chmod +x build_macos.sh

# 运行脚本
./build_macos.sh
```

#### 手动打包

```bash
# 安装依赖
pip3 install pyinstaller PyQt6

# 打包 GUI 版本
pyinstaller --onefile --windowed --name="网络数据包校验工具" validator_qt.py

# 打包命令行版本
pyinstaller --onefile --name="网络数据包校验工具-CLI" validator_cli.py
```

### Linux 打包

与 macOS 相同，使用 `build_macos.sh` 脚本或手动打包。

---

## 打包选项说明

### PyInstaller 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--onefile` | 打包成单个可执行文件 | `--onefile` |
| `--windowed` | GUI 模式，不显示控制台窗口 | `--windowed` |
| `--name` | 指定可执行文件名 | `--name="工具"` |
| `--icon` | 指定图标文件（.ico/.icns） | `--icon=icon.ico` |
| `--clean` | 清理之前的构建缓存 | `--clean` |

### GUI 版本 vs 命令行版本

| 版本 | 参数 | 说明 |
|------|------|------|
| GUI 版本 | `--windowed` | 无控制台窗口，适合图形界面程序 |
| 命令行版本 | 不加 `--windowed` | 有控制台窗口，可以查看输出 |

---

## 输出文件说明

打包完成后，在项目目录下会生成以下结构：

```
cn-data-validator/
├── build/              # 构建临时文件（可删除）
├── dist/               # 打包输出目录（重要！）
│   ├── 网络数据包校验工具.exe       # Windows GUI 版本
│   └── 网络数据包校验工具-CLI.exe   # Windows 命令行版本
├── *.spec              # PyInstaller 规格文件（可删除）
└── validator_qt.py     # 源代码
```

只需分发 `dist` 文件夹中的可执行文件即可。

---

## 分发给用户

### Windows

将 `dist\网络数据包校验工具.exe` 发送给用户：
- 用户可以直接双击运行
- 无需安装 Python 或任何依赖
- 兼容 Windows 7/8/10/11

### macOS

将 `dist/网络数据包校验工具` 发送给用户：
- 用户可以直接运行
- 无需安装 Python 或任何依赖
- 兼容 macOS 10.15+

### Linux

将 `dist/网络数据包校验工具` 发送给用户：
- 用户可以直接运行
- 无需安装 Python 或任何依赖
- 兼容主流 Linux 发行版

---

## 常见问题

### 问题 1：打包后文件太大

**原因**：PyInstaller 会将所有依赖都打包进去。

**解决**：
- 这是正常现象，PyQt6 打包后的文件通常在 50-100MB
- 用户不需要安装任何东西，这是优势

### 问题 2：杀毒软件报毒

**原因**：某些杀毒软件会误报未签名的可执行文件。

**解决**：
- 可以申请代码签名证书
- 或告知用户这是误报，可以添加信任

### 问题 3：Windows 上无法运行（提示缺少 DLL）

**原因**：可能是某些系统组件缺失。

**解决**：
- 安装 Visual C++ Redistributable
- 或使用静态编译

### 问题 4：macOS 上提示"已损坏"

**原因**：macOS 的 Gatekeeper 保护机制。

**解决**：
```bash
# 移除隔离属性
xattr -cr dist/网络数据包校验工具

# 或右键点击 → 打开 → 确认打开
```

---

## 自定义打包

### 添加自定义图标

**Windows (.ico)**：
```cmd
pyinstaller --onefile --windowed --icon=app.ico --name="工具" validator_qt.py
```

**macOS (.icns)**：
```bash
pyinstaller --onefile --windowed --icon=app.icns --name="工具" validator_qt.py
```

### 修改元数据

编辑生成的 `.spec` 文件，然后重新打包：
```python
a = Analysis(
    ['validator_qt.py'],
    pathex=[],
    binaries=[],
    datas=[],
    name='网络数据包校验工具',
    version='1.0.0',
    description='网络数据包校验工具',
    ...
)
```

---

## 自动化打包（CI/CD）

### GitHub Actions 示例

创建 `.github/workflows/build.yml`：

```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install pyinstaller PyQt6
      - run: pyinstaller --onefile --windowed --name="工具" validator_qt.py
      - uses: actions/upload-artifact@v2
        with:
          name: windows-build
          path: dist/

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip3 install pyinstaller PyQt6
      - run: pyinstaller --onefile --windowed --name="工具" validator_qt.py
      - uses: actions/upload-artifact@v2
        with:
          name: macos-build
          path: dist/
```

---

## 技术支持

如有问题，请参考：
- [PyInstaller 官方文档](https://pyinstaller.org/)
- [PyQt6 官方文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- 项目 README.md
