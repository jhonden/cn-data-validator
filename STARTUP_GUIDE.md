# 启动脚本使用指南

本指南介绍如何使用提供的启动脚本来快速启动 Network Package Validator 的 PyQt6 图形界面版本。

## 📁 文件说明

- `startup.sh` - Linux/macOS 启动脚本
- `startup.bat` - Windows 启动脚本

## 🚀 使用方法

### Linux/macOS 系统

1. **直接运行**（推荐）：
   ```bash
   ./startup.sh
   ```

2. **或者使用 bash**：
   ```bash
   bash startup.sh
   ```

### Windows 系统

1. **双击运行**：
   - 直接双击 `startup.bat` 文件

2. **或者命令行运行**：
   ```cmd
   startup.bat
   ```

## ✨ 脚本功能

### 启动前检查
- ✅ 检查 Python 是否安装
- ✅ 显示 Python 版本信息
- ✅ 检查核心依赖（PyQt6）
- ✅ 检查可选依赖（openpyxl, PyYAML）

### 依赖说明
- **必需依赖**：PyQt6
- **可选依赖**：openpyxl（Excel处理）、PyYAML（配置文件）
- 如果缺少可选依赖，程序会显示警告但仍能启动

## 📋 系统要求

### 通用要求
- Python 3.9 或更高版本
- 至少 100MB 可用内存

### 系统特定要求

#### Linux
- Python 3.x
- GTK+ 库（PyQt6 依赖）

#### macOS
- Python 3.x
- Quartz 库（系统自带）

#### Windows
- Python 3.x
- Visual C++ Redistributable（PyQt6 可能需要）

## 🔧 故障排除

### 常见问题

1. **Python 未安装**
   - 错误信息：`python3 not found` 或 `Python not found`
   - 解决方案：安装 Python 3.9+

2. **PyQt6 未安装**
   - 错误信息：`PyQt6 not installed`
   - 解决方案：
     ```bash
     pip3 install PyQt6  # Linux/macOS
     pip install PyQt6    # Windows
     ```

3. **权限问题（Linux/macOS）**
   - 错误信息：`Permission denied`
   - 解决方案：`chmod +x startup.sh`

4. **编码问题（Windows）**
   - 如果显示乱码，确保系统支持 UTF-8 编码

### 手动安装依赖

如果自动检查失败，可以手动安装：

```bash
# 安装所有依赖
pip3 install PyQt6 openpyxl PyYAML  # Linux/macOS
pip install PyQt6 openpyxl PyYAML    # Windows
```

## 🎯 高级用法

### 环境变量

可以通过环境变量自定义行为：

```bash
# 设置 Python 路径
export PYTHONPATH=/path/to/python-modules
./startup.sh

# 设置日志级别
export PYTHONLOGLEVEL=DEBUG
./startup.sh
```

### 后台运行

Linux/macOS 后台运行：
```bash
nohup ./startup.sh > app.log 2>&1 &
```

Windows 后台运行（使用 PowerShell）：
```powershell
Start-Process -FilePath "cmd.exe" -ArgumentList "/c startup.bat"
```

## 📝 日志

程序运行日志会显示在控制台中。如果需要保存日志：
- Linux/macOS：重定向到文件 `./startup.sh > logfile.txt 2>&1`
- Windows：重定向到文件 `startup.bat > logfile.txt 2>&1`

## 🆘 获取帮助

如果遇到问题：
1. 检查 Python 版本是否满足要求
2. 确保所有依赖都已安装
3. 查看 `CLAUDE.md` 了解项目详细信息
4. 查看 `docs/` 目录下的其他文档

---

**提示**：首次运行前建议先运行测试脚本 `python3 tests/unit/test_simple.py` 验证环境。