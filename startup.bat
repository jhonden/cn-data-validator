@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

REM Network Package Validator - PyQt6 GUI Startup Script
REM 用于启动PyQt6版本的图形界面工具

echo ===========================================
echo   Network Package Validator
echo   PyQt6 GUI Version
echo ===========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.9 or later
    pause
    exit /b 1
)

REM 检查Python版本
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo.

REM 检查依赖
echo Checking dependencies...

REM 检查PyQt6
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Error: PyQt6 not installed
    echo Please install dependencies:
    echo   pip install PyQt6
    pause
    exit /b 1
)

REM 检查其他依赖
set MISSING_DEPS=0

python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Warning: openpyxl not installed
    echo Some features may not work properly
    set MISSING_DEPS=1
)

python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo Warning: PyYAML not installed
    echo Some features may not work properly
    set MISSING_DEPS=1
)

if %MISSING_DEPS% equ 0 (
    echo All dependencies check passed!
) else (
    echo Some dependencies are missing, but application will try to start...
)

echo.
echo Starting PyQt6 GUI...
echo Close this window to exit the application.
echo.

REM 启动主程序
python src/view/validator_qt.py

if errorlevel 1 (
    echo.
    echo Error: Application exited with error
    pause
    exit /b 1
)

echo.
echo Application closed normally
pause