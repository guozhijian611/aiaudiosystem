#!/bin/bash

# Translate2 Node 安装脚本

set -e

echo "================================================="
echo "        Translate2 Node 安装脚本"
echo "================================================="

# 检查操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    echo "不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "检测到操作系统: $OS"

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "错误: Conda 未安装"
    echo "请先安装 Conda: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✓ Conda 已安装"

# 检查 git 是否安装
if ! command -v git &> /dev/null; then
    echo "错误: Git 未安装"
    echo "请先安装 Git"
    exit 1
fi

echo "✓ Git 已安装"

# 检查 FFmpeg 是否安装
if ! command -v ffmpeg &> /dev/null; then
    echo "警告: FFmpeg 未安装"
    echo "请安装 FFmpeg:"
    if [[ "$OS" == "linux" ]]; then
        echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
        echo "  CentOS/RHEL: sudo yum install ffmpeg"
    elif [[ "$OS" == "macos" ]]; then
        echo "  macOS: brew install ffmpeg"
    elif [[ "$OS" == "windows" ]]; then
        echo "  Windows: 下载 https://ffmpeg.org/download.html"
    fi
    echo "安装完成后重新运行此脚本"
    exit 1
fi

echo "✓ FFmpeg 已安装"

# 创建环境配置文件
if [ ! -f ".env" ]; then
    echo "创建环境配置文件..."
    cp .env.example .env
    echo "⚠ 请编辑 .env 文件，特别是设置 HF_TOKEN"
    echo "  然后重新运行此脚本"
    exit 1
fi

echo "✓ 环境配置文件已存在"

# 创建 conda 环境
echo "创建 conda 环境..."
if conda env list | grep -q "whisper-diarization"; then
    echo "✓ conda 环境已存在"
else
    conda env create -f environment.yml
    echo "✓ conda 环境创建成功"
fi

# 激活环境
echo "激活 conda 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate whisper-diarization

# 安装 Whisper-Diarization
if [ ! -d "whisper-diarization" ]; then
    echo "安装 Whisper-Diarization..."
    git clone https://github.com/guillaumekln/whisper-diarization.git
    cd whisper-diarization
    pip install -e .
    cd ..
    echo "✓ Whisper-Diarization 安装成功"
else
    echo "✓ Whisper-Diarization 目录已存在"
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs temp work models
echo "✓ 目录创建完成"

# 安装 Python 依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt
echo "✓ Python 依赖安装完成"

# 设置权限
echo "设置脚本权限..."
chmod +x start.sh
chmod +x test.py
echo "✓ 权限设置完成"

echo ""
echo "================================================="
echo "安装完成！"
echo "================================================="
echo ""
echo "下一步操作："
echo "1. 编辑 .env 文件，设置 HF_TOKEN 和其他配置"
echo "2. 运行测试: python test.py"
echo "3. 启动服务: python main.py"
echo "4. 或者使用启动脚本: ./start.sh"
echo ""
echo "重要提醒："
echo "- 确保设置了有效的 HF_TOKEN（用于说话人分离）"
echo "- 确保 RabbitMQ 服务正在运行"
echo "- 确保后端 API 服务正在运行"
echo "" 