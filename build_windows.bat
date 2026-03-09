@echo off
REM 设置Python编码为UTF-8
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
echo ============================================================
echo              网络数据包校验工具 - Windows 打包脚本
echo ============================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.6+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python 版本:
python --version
echo.

REM 检查 PyInstaller 是否安装
python -m pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败
        pause
        exit /b 1
    )
    echo [成功] PyInstaller 安装完成
    echo.
)

REM 检查 PyQt6 是否安装
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装 PyQt6...
    pip install PyQt6
    if errorlevel 1 (
        echo [错误] PyQt6 安装失败
        pause
        exit /b 1
    )
    echo [成功] PyQt6 安装完成
    echo.
)

echo [信息] 开始打包 PyQt6 版本...
echo.

REM 打包 PyQt6 版本
pyinstaller --onefile --windowed --name="网络数据包校验工具" --icon=NONE --add-data "utils/static_mml_config.yaml;utils" --add-data "utils/scenario_config.yaml;utils" validator_qt.py
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ============================================================
echo                      打包完成！
echo ============================================================
echo.
echo 生成的文件位于: dist\网络数据包校验工具.exe
echo.
echo 说明:
echo   - 这是一个独立的可执行文件
echo   - 用户可以直接双击运行，无需安装 Python
echo   - 可以分发给任何 Windows 用户
echo.

REM 询问是否也打包命令行版本
set /p pack_cli="是否同时打包命令行版本？(Y/N): "
if /i "%pack_cli%"=="Y" (
    echo.
    echo [信息] 打包命令行版本...
    pyinstaller --onefile --name="网络数据包校验工具(CLI)" --add-data "utils/static_mml_config.yaml;utils" --add-data "utils/scenario_config.yaml;utils" validator_cli.py
    echo.
    echo 生成的文件: dist\网络数据包校验工具(CLI).exe
)

echo.
echo ============================================================
echo 打包文件位置: %CD%\dist
echo ============================================================
echo.

REM 打开 dist 目录
explorer dist

pause
