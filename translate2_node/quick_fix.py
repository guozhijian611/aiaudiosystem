#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速修复脚本 - 解决 huggingface_hub 版本兼容性问题
"""

import subprocess
import sys

def quick_fix():
    """快速修复"""
    print("=" * 60)
    print("    快速修复 huggingface_hub 版本问题")
    print("=" * 60)
    
    try:
        # 1. 卸载当前版本
        print("1. 卸载当前 huggingface_hub 版本...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "huggingface_hub"], 
                      check=True, capture_output=True)
        print("✓ 卸载成功")
        
        # 2. 安装兼容版本
        print("2. 安装兼容版本 huggingface_hub<0.20.0...")
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub<0.20.0"], 
                      check=True, capture_output=True)
        print("✓ 安装成功")
        
        # 3. 重新安装 NeMo
        print("3. 重新安装 NeMo...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "nemo_toolkit[asr]==2.0.0rc0"], 
                      check=True, capture_output=True)
        print("✓ NeMo 重新安装成功")
        
        # 4. 测试导入
        print("4. 测试模块导入...")
        try:
            import nemo
            from nemo.collections.asr.models.msdd_models import NeuralDiarizer
            print("✓ 所有模块导入成功！")
            
            print("\n" + "=" * 60)
            print("修复完成！现在可以运行转写测试:")
            print("  python test_local_transcribe.py your_audio.wav")
            print("  python example_transcribe.py")
            print("=" * 60)
            
            return True
            
        except ImportError as e:
            print(f"✗ 模块导入测试失败: {e}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 修复失败: {e}")
        return False

if __name__ == "__main__":
    quick_fix() 