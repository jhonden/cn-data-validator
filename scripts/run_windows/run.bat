@echo off
chcp 65001 >nul
echo ================================================
echo       网络数据包校验工具 - 启动脚本
echo ================================================
echo.

REM 设置Python路径
set PYTHON_PATH=D:\Applications\python3.13.0
set SCRIPTS_PATH=D:\Applications\python3.13.0\Scripts

REM 添加到当前会话的PATH
set PATH=%PYTHON_PATH%;%SCRIPTS_PATH%;%PATH%

echo Python路径: %PYTHON_PATH%
echo 脚本路径: %SCRIPTS_PATH%
echo.

REM 检查Python是否可用
"%PYTHON_PATH%\python.exe" --version
if %errorlevel% neq 0 (
    echo [错误] Python未找到，请检查Python安装路径
    pause
    exit /b 1
)

echo.
echo 请选择要运行的版本:
echo 1. PyQt6 GUI版本 (推荐)
echo 2. 命令行版本
echo 3. 退出
echo.

set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 启动PyQt6 GUI版本...
    "%PYTHON_PATH%\python.exe" validator_qt.py
) else if "%choice%"=="2" (
    echo.
    echo 启动命令行版本...
    "%PYTHON_PATH%\python.exe" validator_cli.py
) else if "%choice%"=="5" (
    echo.
    echo 退出程序
    exit /b 0
) else (
    echo.
    echo [错误] 无效的选择
    pause
    exit /b 1
)

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序运行失败，错误代码: %errorlevel%
    pause
)
