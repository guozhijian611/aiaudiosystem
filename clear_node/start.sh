#!/bin/bash

# Clear Node 启动脚本

set -e

echo "======================================"
echo "Clear Node 启动脚本"
echo "音频清理节点 v1.0.0"
echo "======================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 检查环境配置文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "复制环境配置文件..."
        cp .env.example .env
        echo "请编辑 .env 文件配置相关参数"
    else
        echo "警告: 未找到环境配置文件"
    fi
fi

# 创建必要目录
echo "创建工作目录..."
mkdir -p work temp logs

# 检查ClearVoice是否存在
if [ ! -d "ClearerVoice-Studio" ]; then
    echo "警告: 未找到ClearerVoice-Studio目录"
    echo "请确保ClearerVoice-Studio项目已正确放置在当前目录下"
fi

# 设置环境变量
export PYTHONPATH="$(pwd)/src:$(pwd)/ClearerVoice-Studio/clearvoice:$PYTHONPATH"

echo "======================================"
echo "启动Clear Node..."
echo "======================================"

# 启动程序
python3 src/main.py