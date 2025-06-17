#!/bin/bash

# Translate2 Node 启动脚本

set -e

echo "================================================="
echo "        Translate2 Node 启动脚本"
echo "================================================="

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "错误: Conda 未安装，请先安装 Conda"
    exit 1
fi

# 检查环境配置文件
if [ ! -f ".env" ]; then
    echo "创建环境配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置相关参数，然后重新运行此脚本"
    echo "主要配置项："
    echo "  - HF_TOKEN: Hugging Face Token（必需）"
    echo "  - RABBITMQ_HOST: RabbitMQ 服务器地址"
    echo "  - API_BASE_URL: 后端 API 地址"
    exit 1
fi

# 检查 conda 环境是否存在
if ! conda env list | grep -q "whisper-diarization"; then
    echo "创建 conda 环境..."
    conda env create -f environment.yml
fi

# 激活环境
echo "激活 conda 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate whisper-diarization

# 检查 Whisper-Diarization 是否安装
if [ ! -d "whisper-diarization" ]; then
    echo "安装 Whisper-Diarization..."
    git clone https://github.com/guillaumekln/whisper-diarization.git
    cd whisper-diarization
    pip install -e .
    cd ..
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs temp work models

# 启动服务
echo "启动 Translate2 Node 服务..."
python main.py 