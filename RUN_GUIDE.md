# 网络数据包校验工具 - 运行指南

## 环境配置完成状态

✅ Python 3.13.0 已安装 (D:\Applications\python3.13.0)
✅ pip 已安装并配置
✅ 项目依赖已安装：
   - customtkinter 5.2.2
   - PySimpleGUI 5.0.8.3
   - PyQt6 6.10.2
   - darkdetect 0.8.0
   - packaging 26.0
✅ 环境变量已配置
✅ 模块导入问题已修复
✅ 功能测试通过

## 如何运行程序

### 方式1：直接运行（推荐）

在项目目录下，使用以下命令运行不同版本：

```bash
# 进入项目目录
cd D:\ai-coder\cn-data-validator

# 运行命令行版本
python validator_cli.py

# 运行CustomTkinter GUI版本
python validator.py

# 运行PySimpleGUI GUI版本
python validator_psg.py

# 运行PyQt6 GUI版本
python validator_qt.py
```

### 方式2：使用完整Python路径

如果环境变量尚未生效（需要重启终端），可以使用完整路径：

```bash
# 进入项目目录
cd D:\ai-coder\cn-data-validator

# 运行命令行版本
"D:\Applications\python3.13.0\python.exe" validator_cli.py

# 运行GUI版本
"D:\Applications\python3.13.0\python.exe" validator.py
```

## 使用说明

### 支持的文件格式

- ZIP文件 (.zip)
- TAR.GZ文件 (.tar.gz)
- TAR文件 (.tar)
- XLSX文件 (.xlsx)

### 各版本特点

#### 1. 命令行版本 (validator_cli.py)
- **优点**：无GUI依赖，适用于无图形界面的环境
- **特点**：交互式命令行界面，支持TXT和CSV导出
- **适用场景**：服务器环境、远程连接、自动化脚本

#### 2. CustomTkinter GUI版本 (validator.py) ⭐推荐
- **优点**：现代GUI界面，易于使用
- **特点**：拖拽文件夹选择，实时进度显示，表格展示结果
- **适用场景**：日常使用，Windows桌面环境

#### 3. PySimpleGUI GUI版本 (validator_psg.py)
- **优点**：简洁的GUI界面
- **特点**：快速启动，简洁操作流程
- **适用场景**：需要快速扫描的场景

#### 4. PyQt6 GUI版本 (validator_qt.py)
- **优点**：跨平台兼容性好
- **特点**：专业的GUI界面，多线程处理
- **适用场景**：需要跨平台运行

## 功能特性

### 1. 目录扫描
- 递归扫描指定目录下的所有文件
- 自动识别文件格式
- 支持大量文件处理

### 2. 格式校验
- 严格检查文件扩展名
- 识别合法和非法的文件格式
- 提供详细的校验报告

### 3. 结果导出
- **TXT格式**：详细的文本报告
- **CSV格式**：表格数据，便于进一步处理
- 包含统计信息和文件详情

### 4. 统计信息
- 总文件数统计
- 合法文件统计
- 非法文件统计
- 文件大小信息

## 环境变量配置说明

已配置的环境变量：
- `D:\Applications\python3.13.0` - Python主目录
- `D:\Applications\python3.13.0\Scripts` - Python脚本目录

**注意**：环境变量修改后，需要重启命令行窗口才能生效。

## 测试验证

### 已完成测试
✅ Python环境测试
✅ pip安装测试
✅ 依赖包安装测试
✅ 模块导入测试
✅ 文件扫描功能测试
✅ 格式校验功能测试

### 测试数据
测试目录：`D:\ai-coder\cn-data-validator\test_data`

测试结果：
- 总文件数: 3
- 合法文件: 2 (valid_data.xlsx, valid_file.zip)
- 非法文件: 1 (invalid_file.txt)

## 常见问题

### Q1: 命令行中显示中文乱码
A: 这是Windows命令提示符的编码问题，不影响功能。可以尝试：
```bash
chcp 65001  # 设置为UTF-8编码
```

### Q2: 环境变量未生效
A: 需要重启命令行窗口或重新登录系统。

### Q3: GUI程序无法启动
A: 确保已安装对应的GUI库，或尝试使用命令行版本。

### Q4: 扫描速度慢
A: 对于大量文件，建议使用PyQt6版本，它支持多线程处理。

## 项目结构

```
D:\ai-coder\cn-data-validator\
├── validator.py              # CustomTkinter GUI版本
├── validator_cli.py          # 命令行版本
├── validator_psg.py          # PySimpleGUI GUI版本
├── validator_qt.py           # PyQt6 GUI版本
├── utils/
│   ├── __init__.py          # 包初始化文件
│   └── file_scanner.py      # 文件扫描核心模块
├── requirements.txt         # 项目依赖
├── INSTALL.md              # 安装指南
├── RUN_GUIDE.md            # 运行指南（本文件）
└── test_data/              # 测试数据目录
```

## 联系与支持

如有问题，请查看：
- `INSTALL.md` - 详细安装指南
- `README.md` - 项目说明
- `BUILD.md` - 构建说明

## 版本信息

- Python版本: 3.13.0
- 项目版本: 初始版本
- 最后更新: 2026-03-06

---

**配置完成！现在可以开始使用网络数据包校验工具了！** 🎉
