#!/bin/bash

# Quick Node 启动脚本

echo "=========================================="
echo "启动 Quick Node - 快速识别节点"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 检查依赖文件
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到 requirements.txt"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件，使用默认配置"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "已复制 .env.example 到 .env"
    fi
fi

# 创建必要的目录
mkdir -p temp work logs

# 检查并安装依赖
echo "检查Python依赖..."
if [ -f "environment.yml" ] && command -v conda &> /dev/null; then
    echo "检测到conda环境，使用environment.yml安装依赖..."
    conda env update -f environment.yml
    echo "安装Quick Node特有依赖..."
    pip3 install -r requirements.txt
else
    echo "使用pip安装完整依赖..."
    pip3 install -r requirements-full.txt
fi

# 安装本地FunASR
if [ -d "FunASR" ] && [ -f "FunASR/setup.py" ]; then
    echo "安装本地FunASR..."
    cd FunASR
    pip3 install -e .
    cd ..
    echo "本地FunASR安装完成"
else
    echo "警告: 未找到本地FunASR目录，请确保FunASR目录存在"
fi

# 启动服务
echo "启动 Quick Node 服务..."
python3 run.py 