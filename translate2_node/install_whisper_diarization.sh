#!/bin/bash

# Whisper-Diarization 安装脚本

set -e

echo "================================================="
echo "    Whisper-Diarization 安装脚本"
echo "================================================="

# 检查当前目录
if [ ! -f "main.py" ]; then
    echo "错误: 请在 translate2_node 目录下运行此脚本"
    exit 1
fi

# 检查 conda 环境
if ! conda env list | grep -q "whisper-diarization"; then
    echo "错误: 请先创建 conda 环境"
    echo "运行: conda env create -f environment.yml"
    exit 1
fi

# 激活环境
echo "激活 conda 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate whisper-diarization

# 安装基础依赖
echo "安装基础依赖..."
pip install openai-whisper>=20231117
pip install torch>=2.0.0 torchaudio>=2.0.0
pip install transformers>=4.48.0
pip install pyannote-audio>=3.3.2 pyannote-core>=5.0.0

# 检查 Whisper-Diarization 目录
if [ ! -d "whisper-diarization" ]; then
    echo "克隆 Whisper-Diarization 仓库..."
    git clone https://github.com/guillaumekln/whisper-diarization.git
fi

# 进入目录并安装
echo "安装 Whisper-Diarization..."
cd whisper-diarization

# 检查是否有 setup.py 或 pyproject.toml
if [ -f "setup.py" ]; then
    pip install -e .
elif [ -f "pyproject.toml" ]; then
    pip install -e .
else
    echo "警告: 未找到安装文件，尝试直接安装依赖..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
fi

cd ..

# 测试安装
echo "测试 Whisper-Diarization 安装..."
python -c "
import sys
sys.path.append('whisper-diarization')
try:
    from whisper_diarization import WhisperDiarization
    print('✓ Whisper-Diarization 安装成功')
except ImportError as e:
    print(f'✗ Whisper-Diarization 安装失败: {e}')
    sys.exit(1)
"

echo ""
echo "================================================="
echo "安装完成！"
echo "================================================="
echo ""
echo "现在可以运行测试: python test.py"
echo "或者启动服务: python main.py"
echo "" 