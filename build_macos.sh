#!/bin/bash

echo "============================================================"
echo "           网络数据包校验工具 - macOS/Linux 打包脚本"
echo "============================================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.6+"
    exit 1
fi

echo "[信息] Python 版本:"
python3 --version
echo ""

# 检查 pip 是否安装
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未检测到 pip3"
    exit 1
fi

# 检查并安装 PyInstaller
if ! python3 -m pyinstaller --version &> /dev/null; then
    echo "[信息] 正在安装 PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[错误] PyInstaller 安装失败"
        exit 1
    fi
    echo "[成功] PyInstaller 安装完成"
    echo ""
fi

# 检查并安装 PyQt6
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "[信息] 正在安装 PyQt6..."
    pip3 install PyQt6
    if [ $? -ne 0 ]; then
        echo "[错误] PyQt6 安装失败"
        exit 1
    fi
    echo "[成功] PyQt6 安装完成"
    echo ""
fi

echo "[信息] 开始打包 PyQt6 版本..."
echo ""

# 打包 PyQt6 版本
pyinstaller --onefile --windowed --name="网络数据包校验工具" validator_qt.py
if [ $? -ne 0 ]; then
    echo "[错误] 打包失败"
    exit 1
fi

echo ""
echo "============================================================"
echo "                      打包完成！"
echo "============================================================"
echo ""
echo "生成的文件位于: dist/网络数据包校验工具"
echo ""
echo "说明:"
echo "  - 这是一个独立的可执行文件"
echo "  - 用户可以直接运行，无需安装 Python"
echo "  - macOS: 可以分发给 macOS 用户"
echo ""

# 询问是否也打包命令行版本
read -p "是否同时打包命令行版本？(y/n): " pack_cli
if [ "$pack_cli" = "y" ] || [ "$pack_cli" = "Y" ]; then
    echo ""
    echo "[信息] 打包命令行版本..."
    pyinstaller --onefile --name="网络数据包校验工具-CLI" validator_cli.py
    echo ""
    echo "生成的文件: dist/网络数据包校验工具-CLI"
fi

echo ""
echo "============================================================"
echo "打包文件位置: $(pwd)/dist"
echo "============================================================"
echo ""

# 打开 dist 目录 (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open dist
fi
