# Python3 命令设置指南

## ✅ 已创建解决方案

我已经为你创建了 `python3.cmd` 文件，现在可以在CMD中使用 `python3` 命令了！

## 🚀 使用方法

### 方式1：在CMD中使用 (推荐)

**直接使用**:
```cmd
python3 script.py
python3 --version
python3 -m pip list
```

**测试是否工作**:
```cmd
python3 --version
```

应该看到：`Python 3.13.0`

### 方式2：在PowerShell中使用

如果你使用PowerShell，运行：
```powershell
function python3 { & "D:\Applications\python3.13.0\python.exe" $args }
```

### 方式3：使用批处理文件 (最简单)

**直接双击**以下文件：
- `run_gui_qt.bat` - PyQt6 GUI版本（推荐）
- `run_cli.bat` - 命令行版本
- `run_gui_psg.bat` - PySimpleGUI版本

这些文件已经配置了正确的Python路径，无需设置别名。

## 📝 已创建的文件

1. **python3.cmd** - CMD别名文件
2. **python3_alias.cmd** - 别名配置文件
3. **test_python3.cmd** - 测试脚本

## 🧪 测试

**运行测试脚本**:
```cmd
test_python3.cmd
```

**手动测试**:
```cmd
python3 --version
```

**测试模块导入**:
```cmd
python3 -c "from utils.file_scanner import FileScanner; print('OK')"
```

## 🎯 立即开始使用

### 启动网络数据包校验工具

**方式A：使用python3命令**
```cmd
cd D:\ai-coder\cn-data-validator
python3 validator_qt.py
```

**方式B：使用批处理文件（推荐）**
```
双击 run_gui_qt.bat
```

**方式C：使用完整Python路径**
```cmd
cd D:\ai-coder\cn-data-validator
"D:\Applications\python3.13.0\python.exe" validator_qt.py
```

## 🔧 技术细节

### CMD别名原理

在Windows CMD中，别名通过创建与命令同名的`.cmd`文件实现：

```
python3.cmd 调用 → "D:\Applications\python3.13.0\python.exe"
```

### PowerShell别名原理

在PowerShell中，使用函数：
```powershell
function python3 { & "D:\Applications\python3.13.0\python.exe" $args }
```

### 为什么Set-Alias失败

`Set-Alias` 是PowerShell命令，不适用于Windows CMD：
- CMD (命令提示符) - 使用 .cmd 文件创建别名
- PowerShell - 使用 function 或 Set-Alias

## 📊 当前状态

- ✅ **python3.cmd** 已创建并测试成功
- ✅ **Python 3.13.0** 可以通过 `python3` 命令调用
- ✅ **所有导入问题已修复**
- ✅ **代码已推送到GitHub**

## 🎉 现在可以使用

**CMD中**:
```cmd
python3 validator_qt.py
python3 validator_cli.py
python3 test_simple.py
```

**双击文件**:
```
run_gui_qt.bat (推荐)
```

---

**Python3命令现在可以在CMD中正常使用了！** 🎉

试试运行：`python3 --version`
