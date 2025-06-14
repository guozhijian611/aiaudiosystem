#!/bin/bash

# Translate Node 环境安装脚本

echo "开始安装 Translate Node 环境..."

# 检查conda是否已安装
if ! command -v conda &> /dev/null; then
    echo "错误: conda 未安装，请先安装 Anaconda 或 Miniconda"
    exit 1
fi

# 创建conda环境
echo "正在创建conda环境..."
conda env create -f environment.yml

# 激活环境
echo "正在激活环境..."
source activate whisperx

# 安装额外的Python包
echo "正在安装额外的Python包..."
pip install -r requirements.txt

# 创建必要的目录
echo "正在创建工作目录..."
mkdir -p work temp logs models

# 复制环境变量文件模板
if [ ! -f .env ]; then
    echo "正在创建 .env 文件..."
    cp .env.example .env
    echo "请编辑 .env 文件以配置你的环境参数"
    echo "特别注意：如需说话人分离功能，请设置有效的 HF_TOKEN"
fi

echo "安装完成！"
echo ""
echo "使用方法:"
echo "1. 编辑 .env 文件配置参数"
echo "2. 激活环境: conda activate whisperx"
echo "3. 运行服务: python main.py"
echo ""
echo "Docker使用:"
echo "docker-compose up -d" 