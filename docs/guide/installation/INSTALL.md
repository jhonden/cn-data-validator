# Python环境安装指南

## 检查Python安装

首先检查系统是否已安装Python：

```bash
python --version
# 或
python3 --version
```

如果显示版本号（如 Python 3.x.x），则Python已安装。如果显示"未找到命令"或类似错误，则需要安装Python。

## 安装Python

### Windows系统

1. 访问Python官网：https://www.python.org/downloads/

2. 下载最新的Python 3.x版本（推荐3.9或更高版本）

3. 运行安装程序时，**务必勾选"Add Python to PATH"**选项

4. 完成安装后，重新打开命令提示符或终端

5. 验证安装：
```bash
python --version
pip --version
```

### 使用命令行检查当前Python配置

如果之前使用了Windows Store的Python重定向，需要卸载或禁用：

1. 打开"设置" > "应用" > "应用和功能"
2. 搜索"Python"
3. 如果看到"Python 3.x"，可以选择卸载
4. 然后按照上面的步骤安装正式的Python

## 安装项目依赖

进入项目目录后，执行以下命令安装依赖：

```bash
# 进入项目目录
cd D:\ai-coder\cn-data-validator

# 升级pip（推荐）
python -m pip install --upgrade pip

# 安装所有依赖
python -m pip install -r requirements.txt

# 或单独安装特定GUI版本的依赖
# CustomTkinter版本
python -m pip install customtkinter

# PySimpleGUI版本
python -m pip install PySimpleGUI

# PyQt6版本
python -m pip install PyQt6
```

## 选择运行版本

### 1. 命令行版本（无GUI依赖）
```bash
python validator_cli.py
```

### 2. CustomTkinter GUI版本（推荐）
```bash
python validator.py
```

### 3. PySimpleGUI GUI版本
```bash
python validator_psg.py
```

### 4. PyQt6 GUI版本
```bash
python validator_qt.py
```

## 常见问题

### 问题1：pip不是内部或外部命令
**解决方案**：确保在安装Python时勾选了"Add Python to PATH"，或手动将Python添加到系统PATH环境变量。

### 问题2：安装依赖时出现权限错误
**解决方案**：
```bash
python -m pip install --user -r requirements.txt
```

### 问题3：Windows Store打开
**解决方案**：这说明系统使用了Windows Store的Python重定向。需要安装正式的Python版本。

### 问题4：GUI程序无法启动
**解决方案**：某些GUI库可能需要额外的系统依赖。建议先尝试命令行版本确保基础功能正常。

## 项目说明

这是一个网络数据包校验工具，支持：
- ZIP文件
- TAR.GZ文件
- TAR文件
- XLSX文件

工具会递归扫描指定目录，识别合法和非法的文件格式，并生成校验报告。

## 开发环境建议

- Python 3.9+
- Windows 10/11
- 建议使用虚拟环境（可选）

创建虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```
