# 网络数据包校验工具

一个用于校验网络数据采集结果的本地工具，帮助用户快速发现数据包格式不合法、文件缺失等问题。

## 项目结构

```
cn-data-validator/
├── validator_qt.py      # PyQt6 GUI版本（推荐，跨平台兼容）
├── validator.py         # CustomTkinter GUI版本
├── validator_cli.py     # 命令行版本（无需GUI库）
├── validator_psg.py     # PySimpleGUI版本（备选）
├── build_windows.bat    # Windows 一键打包脚本
├── build_macos.sh     # macOS/Linux 一键打包脚本
├── PACKAGING.md        # 打包和问题解决说明
├── BUILD.md           # 详细打包指南
├── README.md          # 本文件
└── utils/
    └── file_scanner.py # 文件扫描器（核心逻辑）
```

## 运行方式

### ⭐ 方式一：PyQt6 GUI 版本（强烈推荐）

**最佳选择**：使用 PyQt6 实现的图形界面，完全兼容 macOS/Windows/Linux，不依赖 tkinter。

```bash
# 安装依赖
pip3 install PyQt6

# 运行
python3 validator_qt.py
```

**优点**：
- ✅ 完美支持 macOS（包括你当前的版本）
- ✅ 真正的图形界面，操作直观
- ✅ 多线程处理，扫描时界面不会卡死
- ✅ 美观的现代化界面
- ✅ 跨平台兼容

### 方式二：命令行版本

命令行版本不依赖 GUI 库，所有平台都可以直接运行：

```bash
python3 validator_cli.py
```

使用方式：
1. 按照提示输入目录路径
2. 查看扫描结果
3. 选择是否导出结果（TXT/CSV格式）

### 方式三：打包成可执行文件（推荐，无需Python环境）

分发给用户无需安装 Python 和任何依赖。

#### Windows 用户

1. 双击运行 `build_windows.bat`
2. 等待自动打包完成
3. 在 `dist` 文件夹中找到生成的 `.exe` 文件

#### macOS/Linux 用户

1. 运行打包脚本：
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```

2. 在 `dist` 文件夹中找到生成的可执行文件

详细打包说明请查看：[BUILD.md](BUILD.md)

## macOS Tkinter 兼容性问题

如果在 macOS 上运行 GUI 版本遇到以下错误：
```
macOS 15 (1507) or later required, have instead 15 (1506) !
```

### 解决方案

1. **立即可用**：使用命令行版本 `validator_cli.py`
2. **打包解决**：使用 PyInstaller 打包 `validator.py` 或 `validator_cli.py`
3. **详细信息**：请查看 [PACKAGING.md](PACKAGING.md)

## 功能说明

### 当前功能

- ✅ 选择数据包目录
- ✅ 递归扫描目录下所有文件
- ✅ 校验文件格式（只允许：ZIP、TAR.GZ、TAR、XLSX）
- ✅ 表格展示所有文件（文件名、路径、大小、格式、状态、详情）
- ✅ 区分合法/非法文件
- ✅ 实时显示扫描进度
- ✅ 导出校验结果（TXT/CSV格式）

### 支持的文件格式

| 格式 | 扩展名 | 状态 |
|------|--------|------|
| ZIP压缩包 | .zip | ✅ 合法 |
| TAR压缩包 | .tar | ✅ 合法 |
| TAR.GZ压缩包 | .tar.gz | ✅ 合法 |
| Excel文件 | .xlsx | ✅ 合法 |
| 其他格式 | * | ❌ 非法 |

## 使用方法

### PyQt6 GUI 版本（validator_qt.py）- 推荐

1. **启动程序**
   ```bash
   python3 validator_qt.py
   ```
   或双击打包后的可执行文件

2. **选择目录**
   - 点击"选择目录"按钮
   - 选择包含数据包的文件夹

3. **开始校验**
   - 点击"开始校验"按钮
   - 等待扫描完成（界面不会卡死）
   - 查看结果表格

4. **导出结果（可选）**
   - 点击"导出结果"按钮
   - 选择导出格式（TXT或CSV）
   - 选择保存位置

### CustomTkinter GUI 版本（validator.py）

**注意**：此版本在 macOS 某些版本上可能遇到 tkinter 兼容性问题。

1. **启动程序**
   - 运行 `python3 validator.py` 或双击打包后的可执行文件

2. **选择目录**
   - 点击"📁 选择数据包目录"按钮
   - 选择包含数据包的文件夹

3. **开始校验**
   - 点击"🔍 开始校验"按钮
   - 等待扫描完成
   - 查看结果表格

4. **导出结果（可选）**
   - 点击"📊 导出结果"按钮
   - 选择导出格式（TXT或CSV）
   - 选择保存位置

### 命令行版本（validator_cli.py）

1. **启动程序**
   ```bash
   python3 validator_cli.py
   ```

2. **选择目录**
   - 输入目录路径（选项1）
   - 或使用文件选择器（选项2，仅支持 macOS/Linux）

3. **查看结果**
   - 程序自动显示扫描统计和非法文件列表

4. **导出结果**
   - 根据提示选择是否导出
   - 选择导出格式（TXT/CSV）
   - 输入保存路径

## 界面说明

### 顶部操作区
- **选择目录按钮**：选择要校验的数据包目录
- **当前目录**：显示当前选择的目录名称
- **开始校验按钮**：执行文件格式校验
- **进度条**：显示扫描进度

### 结果表格
- **文件名**：数据包文件名
- **文件路径**：相对于所选目录的路径
- **大小**：文件大小（自动格式化）
- **格式**：文件类型（ZIP/TAR.GZ/TAR/XLSX/未知）
- **状态**：
  - ✅ 合法：文件格式符合要求
  - ❌ 非法：文件格式不符合要求
- **详情**：告警信息（如"数据包格式非法"）

### 底部状态栏
- 显示当前操作状态和统计信息

### 导出按钮
- 将校验结果导出为文本文件或CSV文件

## 开发计划

### 后续功能
- [ ] 支持压缩包内部文件校验
- [ ] 支持依赖关系检查
- [ ] 支持自定义校验规则
- [ ] 支持批量导出告警列表
- [ ] 支持配置文件管理

## 技术栈

### PyQt6 GUI 版本（推荐）
- **GUI框架**: PyQt6（需安装：`pip3 install PyQt6`）
- **优势**: 完美跨平台支持，不依赖 tkinter，多线程处理
- **兼容性**: Windows / macOS / Linux 全平台兼容

### CustomTkinter GUI 版本
- **GUI框架**: CustomTkinter（需安装：`pip3 install customtkinter`）
- **依赖**: Tkinter（Python 内置，但某些 macOS 版本有兼容性问题）

### 命令行版本
- **界面**: 命令行交互（无需 GUI 库）
- **兼容性**: 全平台兼容，无需额外依赖

### 打包
- **打包工具**: PyInstaller（`pip3 install pyinstaller`）
- **系统要求**:
  - Python 3.6+ (开发环境)
  - Windows / macOS / Linux (运行环境)
  - 打包后无需安装 Python

## 注意事项

1. 程序会递归扫描所选目录下的所有文件和子目录
2. 大量文件时扫描可能需要一些时间，请耐心等待
3. 导出结果时，同名的导出文件会被覆盖
4. macOS 用户如果遇到 tkinter 兼容性问题，建议使用命令行版本或打包后再运行
5. 命令行版本支持手动输入目录路径，即使 GUI 文件选择器不可用也能正常工作

## 故障排除

### 问题：CustomTkinter 版本无法启动
- macOS 显示 "macOS 15 (1507) or later required" 错误
- 其他平台无法显示窗口

**解决方案**：
1. **推荐**：使用 PyQt6 版本 `validator_qt.py`（完美兼容 macOS）
2. 使用命令行版本：`python3 validator_cli.py`
3. 使用 PyInstaller 打包后运行（见 PACKAGING.md）

### 问题：找不到 PyQt6 模块

**解决方案**：
```bash
pip3 install PyQt6
```

### 问题：找不到 customtkinter 模块

**解决方案**：
```bash
pip3 install customtkinter
```

或直接使用 PyQt6 版本或命令行版本，无需安装 customtkinter。

## 联系支持

如有问题或建议，请联系开发团队。
