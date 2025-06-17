#!/bin/bash

# Translate2 Node 安装脚本

set -e

echo "================================================="
echo "    Translate2 Node 安装脚本"
echo "================================================="

# 检查当前目录
if [ ! -f "main.py" ]; then
    echo "错误: 请在 translate2_node 目录下运行此脚本"
    exit 1
fi

# 检查 conda 环境
if ! conda env list | grep -q "whisper-diarization"; then
    echo "创建 conda 环境..."
    conda env create -f environment.yml
fi

# 激活环境
echo "激活 conda 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate whisper-diarization

# 安装基础依赖
echo "安装基础依赖..."
pip install -r requirements.txt

# 安装 Whisper-Diarization 专用依赖
echo "安装 Whisper-Diarization 专用依赖..."
pip install wget
pip install nemo_toolkit[asr]==2.0.0rc0
pip install nltk
pip install faster-whisper>=1.1.0

# 安装 GitHub 依赖
echo "安装 GitHub 依赖..."
pip install git+https://github.com/MahmoudAshraf97/demucs.git
pip install git+https://github.com/oliverguhr/deepmultilingualpunctuation.git
pip install git+https://github.com/MahmoudAshraf97/ctc-forced-aligner.git

# 修复 huggingface_hub 版本兼容性问题
echo "修复 huggingface_hub 版本兼容性问题..."
python fix_huggingface_hub.py

# 检查 Whisper-Diarization 目录
if [ ! -d "whisper-diarization" ]; then
    echo "克隆 Whisper-Diarization 仓库..."
    git clone https://github.com/guillaumekln/whisper-diarization.git
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p work
mkdir -p temp
mkdir -p logs
mkdir -p models
mkdir -p output

# 复制配置文件
if [ ! -f ".env" ]; then
    echo "复制配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置您的设置"
fi

# 测试安装
echo "测试安装..."
python -c "
import sys
try:
    import torch
    print('✓ PyTorch 安装成功')
except ImportError:
    print('✗ PyTorch 安装失败')

try:
    import whisper
    print('✓ Whisper 安装成功')
except ImportError:
    print('✗ Whisper 安装失败')

try:
    import faster_whisper
    print('✓ Faster Whisper 安装成功')
except ImportError:
    print('✗ Faster Whisper 安装失败')

try:
    import nemo
    print('✓ NeMo 安装成功')
except ImportError:
    print('✗ NeMo 安装失败')

try:
    import ctc_forced_aligner
    print('✓ CTC Forced Aligner 安装成功')
except ImportError:
    print('✗ CTC Forced Aligner 安装失败')

try:
    import deepmultilingualpunctuation
    print('✓ 标点符号模型 安装成功')
except ImportError:
    print('✗ 标点符号模型 安装失败')
"

echo ""
echo "================================================="
echo "安装完成！"
echo "================================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件配置您的设置"
echo "2. 运行测试: python test.py"
echo "3. 测试转写: python test_local_transcribe.py your_audio.wav"
echo "4. 启动服务: python main.py"
echo "" 