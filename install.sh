#!/bin/bash

# 统计图制作系统安装脚本

REINSTALL=false
SKIP_CLONE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--reinstall)
            REINSTALL=true
            shift
            ;;
        -s|--skip-clone)
            SKIP_CLONE=true
            shift
            ;;
        *)
            echo "未知选项: $1"
            exit 1
            ;;
    esac
done

PROJECT_URL="https://github.com/shumaoyong-lele/chart/"
VENV_PATH=".venv"
VENV_PYTHON="$VENV_PATH/bin/python"
VENV_PIP="$VENV_PATH/bin/pip"
PACKAGES=("matplotlib" "squarify" "flask" "sqlalchemy" "psycopg2-binary")

echo ""
echo "========================================"
echo "    统计图制作系统安装脚本"
echo "========================================"
echo ""

if [ "$REINSTALL" = true ]; then
    echo -e "\033[36m[INFO]\033[0m 重新安装模式..."
    if [ -d "$VENV_PATH" ]; then
        echo -e "\033[36m[INFO]\033[0m 正在删除旧虚拟环境..."
        rm -rf "$VENV_PATH"
        echo -e "\033[32m[OK]\033[0m 虚拟环境已删除"
    fi
fi

echo -e "\033[36m[INFO]\033[0m 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "\033[32m[OK]\033[0m 检测到 $PYTHON_VERSION"
else
    echo -e "\033[31m[ERROR]\033[0m 未检测到 Python，请先安装 Python"
    exit 1
fi

echo -e "\033[36m[INFO]\033[0m 检查 Git 环境..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "\033[32m[OK]\033[0m 检测到 $GIT_VERSION"
else
    echo -e "\033[31m[ERROR]\033[0m 未检测到 Git，请先安装 Git"
    exit 1
fi

if [ "$SKIP_CLONE" = false ]; then
    echo -e "\033[36m[INFO]\033[0m 检查项目文件..."
    if [ -f "main.py" ] || [ -d ".git" ]; then
        echo -e "\033[33m[WARN]\033[0m 项目文件已存在，跳过克隆"
    else
        echo -e "\033[36m[INFO]\033[0m 克隆项目: $PROJECT_URL"
        git clone "$PROJECT_URL" .
        if [ $? -ne 0 ]; then
            echo -e "\033[31m[ERROR]\033[0m 项目克隆失败"
            exit 1
        fi
        echo -e "\033[32m[OK]\033[0m 项目克隆成功"
    fi
else
    echo -e "\033[33m[WARN]\033[0m 跳过克隆步骤"
fi

echo -e "\033[36m[INFO]\033[0m 创建虚拟环境 $VENV_PATH..."
if [ -d "$VENV_PATH" ]; then
    echo -e "\033[33m[WARN]\033[0m 虚拟环境已存在，跳过创建"
else
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo -e "\033[31m[ERROR]\033[0m 虚拟环境创建失败"
        exit 1
    fi
    echo -e "\033[32m[OK]\033[0m 虚拟环境创建成功"
fi

echo -e "\033[36m[INFO]\033[0m 安装 Python 包..."
FAILED_PACKAGES=()
for package in "${PACKAGES[@]}"; do
    echo -e "\033[36m[INFO]\033[0m 安装 $package..."
    "$VENV_PIP" install "$package" -q
    if [ $? -eq 0 ]; then
        echo -e "\033[32m[OK]\033[0m $package 安装成功"
    else
        echo -e "\033[31m[ERROR]\033[0m $package 安装失败"
        FAILED_PACKAGES+=("$package")
    fi
done

echo -e "\033[36m[INFO]\033[0m 验证安装..."
ALL_INSTALLED=true
for package in "${PACKAGES[@]}"; do
    if "$VENV_PIP" show "$package" &> /dev/null; then
        echo -e "\033[32m[OK]\033[0m $package 已安装"
    else
        echo -e "\033[31m[ERROR]\033[0m $package 未安装"
        ALL_INSTALLED=false
    fi
done

echo ""
if [ "$ALL_INSTALLED" = true ]; then
    echo "========================================"
    echo -e "    \033[32m安装完成！\033[0m"
    echo "========================================"
    echo ""
    echo "项目地址: $PROJECT_URL"
    echo ""
    echo "启动程序:"
    echo -e "  \033[32m$VENV_PATH/bin/python main.py\033[0m"
    echo ""
else
    echo -e "\033[31m[ERROR]\033[0m 安装过程中存在问题，请检查错误信息"
    exit 1
fi