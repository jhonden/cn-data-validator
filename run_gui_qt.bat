@echo off
chcp 65001 >nul
set PYTHON_PATH=D:\Applications\python3.13.0
set SCRIPTS_PATH=D:\Applications\python3.13.0\Scripts
set PATH=%PYTHON_PATH%;%SCRIPTS_PATH%;%PATH%
echo 启动网络数据包校验工具 (PyQt6版本)...
"%PYTHON_PATH%\python.exe" validator_qt.py
if %errorlevel% neq 0 (
    echo 程序运行失败，按任意键退出...
    pause
)
