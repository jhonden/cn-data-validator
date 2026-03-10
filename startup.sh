#!/bin/bash

# Network Package Validator - PyQt6 GUI Startup Script
# 用于启动PyQt6版本的图形界面工具

# 设置脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印启动信息
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}  Network Package Validator${NC}"
echo -e "${GREEN}  PyQt6 GUI Version${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    echo "Please install Python 3.9 or later"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${YELLOW}Python version: $PYTHON_VERSION${NC}"

# 检查依赖
echo -e "${YELLOW}Checking dependencies...${NC}"

# 检查PyQt6
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo -e "${RED}Error: PyQt6 not installed${NC}"
    echo "Please install dependencies:"
    echo "  pip3 install PyQt6"
    exit 1
fi

# 检查其他依赖
DEPENDENCIES=("openpyxl" "PyYAML")
for dep in "${DEPENDENCIES[@]}"; do
    if ! python3 -c "import $dep" &> /dev/null; then
        echo -e "${YELLOW}Warning: $dep not installed${NC}"
        echo "Some features may not work properly"
    fi
done

echo -e "${GREEN}All dependencies check passed!${NC}"
echo ""

# 启动应用
echo -e "${YELLOW}Starting PyQt6 GUI...${NC}"
echo "Close this window to exit the application."
echo ""

# 启动主程序
python3 src/view/validator_qt.py

# 检查退出状态
if [ $? -ne 0 ]; then
    echo -e "${RED}Application exited with error${NC}"
    exit 1
fi

echo -e "${GREEN}Application closed normally${NC}"