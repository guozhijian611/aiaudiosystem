#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Whisper-Diarization 依赖安装脚本
自动安装所有必需的依赖包
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def install_dependencies():
    """安装所有依赖"""
    print("=" * 60)
    print("    Whisper-Diarization 依赖安装脚本")
    print("=" * 60)
    
    # 基础依赖
    dependencies = [
        ("pip install pika requests python-dotenv psutil loguru", "安装基础依赖"),
        ("pip install torch torchaudio", "安装 PyTorch"),
        ("pip install transformers datasets accelerate", "安装 Transformers"),
        ("pip install pyannote-audio pyannote-core", "安装说话人分离"),
        ("pip install soundfile resampy librosa", "安装音频处理"),
        ("pip install numpy pandas scipy scikit-learn", "安装科学计算"),
        ("pip install openai-whisper", "安装 Whisper"),
        ("pip install wget nltk", "安装工具包"),
        ("pip install faster-whisper>=1.1.0", "安装 Faster Whisper"),
        ("pip install nemo_toolkit[asr]==2.0.0rc0", "安装 NeMo 工具包"),
    ]
    
    # GitHub 依赖
    github_deps = [
        ("pip install git+https://github.com/MahmoudAshraf97/demucs.git", "安装 Demucs"),
        ("pip install git+https://github.com/oliverguhr/deepmultilingualpunctuation.git", "安装标点符号模型"),
        ("pip install git+https://github.com/MahmoudAshraf97/ctc-forced-aligner.git", "安装 CTC 对齐器"),
    ]
    
    success_count = 0
    total_count = len(dependencies) + len(github_deps)
    
    # 安装基础依赖
    for cmd, desc in dependencies:
        if run_command(cmd, desc):
            success_count += 1
    
    print("\n" + "=" * 40)
    print("正在安装 GitHub 依赖（可能需要较长时间）...")
    print("=" * 40)
    
    # 安装 GitHub 依赖
    for cmd, desc in github_deps:
        if run_command(cmd, desc):
            success_count += 1
    
    # 显示结果
    print("\n" + "=" * 60)
    print(f"安装完成: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✓ 所有依赖安装成功！")
        print("\n现在可以运行转写测试:")
        print("  python test_local_transcribe.py your_audio.wav")
        print("  python example_transcribe.py")
    else:
        print("⚠ 部分依赖安装失败，请检查错误信息")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 确保 Python 版本 >= 3.9")
        print("3. 尝试单独安装失败的包")
    
    print("=" * 60)

def test_imports():
    """测试关键模块是否可以导入"""
    print("\n正在测试模块导入...")
    
    test_modules = [
        ("torch", "PyTorch"),
        ("whisper", "Whisper"),
        ("faster_whisper", "Faster Whisper"),
        ("nemo", "NeMo"),
        ("ctc_forced_aligner", "CTC Forced Aligner"),
        ("deepmultilingualpunctuation", "标点符号模型"),
    ]
    
    success_count = 0
    for module, name in test_modules:
        try:
            __import__(module)
            print(f"✓ {name} 导入成功")
            success_count += 1
        except ImportError:
            print(f"✗ {name} 导入失败")
    
    print(f"\n模块测试: {success_count}/{len(test_modules)}")
    return success_count == len(test_modules)

if __name__ == "__main__":
    install_dependencies()
    test_imports() 