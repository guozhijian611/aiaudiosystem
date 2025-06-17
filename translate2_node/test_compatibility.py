#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
兼容性测试脚本
测试新版本 NeMo 和 huggingface_hub 的兼容性
"""

import sys
import os

def test_imports():
    """测试模块导入"""
    print("=" * 60)
    print("    兼容性测试")
    print("=" * 60)
    
    # 测试基础模块
    modules = [
        ("torch", "PyTorch"),
        ("whisper", "Whisper"),
        ("faster_whisper", "Faster Whisper"),
        ("transformers", "Transformers"),
        ("huggingface_hub", "Huggingface Hub"),
    ]
    
    print("基础模块测试:")
    for module, name in modules:
        try:
            imported_module = __import__(module)
            version = getattr(imported_module, '__version__', 'unknown')
            print(f"✓ {name}: {version}")
        except ImportError as e:
            print(f"✗ {name}: 导入失败 - {e}")
    
    # 测试 NeMo
    print("\nNeMo 模块测试:")
    try:
        import nemo
        print(f"✓ NeMo: {nemo.__version__}")
        
        # 测试 NeuralDiarizer
        try:
            from nemo.collections.asr.models.msdd_models import NeuralDiarizer
            print("✓ NeuralDiarizer: 可用")
        except ImportError as e:
            print(f"⚠ NeuralDiarizer: 不可用 - {e}")
            
            # 测试 ClusteringDiarizer
            try:
                from nemo.collections.asr.models import ClusteringDiarizer
                print("✓ ClusteringDiarizer: 可用")
            except ImportError as e:
                print(f"⚠ ClusteringDiarizer: 不可用 - {e}")
                
    except ImportError as e:
        print(f"✗ NeMo: 导入失败 - {e}")
    
    # 测试 Whisper-Diarization 脚本
    print("\nWhisper-Diarization 脚本测试:")
    diarize_script = os.path.join("whisper-diarization", "diarize.py")
    if os.path.exists(diarize_script):
        print("✓ diarize.py: 存在")
        
        # 测试脚本语法
        try:
            with open(diarize_script, 'r', encoding='utf-8') as f:
                content = f.read()
                compile(content, diarize_script, 'exec')
            print("✓ diarize.py: 语法正确")
        except SyntaxError as e:
            print(f"✗ diarize.py: 语法错误 - {e}")
    else:
        print("✗ diarize.py: 不存在")
    
    print("\n" + "=" * 60)
    print("兼容性测试完成")
    print("=" * 60)

def test_transcriber():
    """测试转写器"""
    print("\n转写器测试:")
    try:
        from src.transcriber import WhisperDiarizationTranscriber
        print("✓ 转写器导入成功")
        
        # 初始化转写器
        try:
            transcriber = WhisperDiarizationTranscriber()
            print("✓ 转写器初始化成功")
            
            # 检查模型类型
            if transcriber.model == "script_mode":
                print("✓ 使用脚本模式")
            else:
                print("✓ 使用基础 Whisper 模式")
                
        except Exception as e:
            print(f"✗ 转写器初始化失败: {e}")
            
    except ImportError as e:
        print(f"✗ 转写器导入失败: {e}")

if __name__ == "__main__":
    test_imports()
    test_transcriber() 