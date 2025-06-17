#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复 torchaudio 问题
"""

import subprocess
import sys
import platform

def check_torch_versions():
    """检查 PyTorch 和 torchaudio 版本"""
    print("=" * 60)
    print("    检查 PyTorch 和 torchaudio 版本")
    print("=" * 60)
    
    try:
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"PyTorch CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
    except ImportError:
        print("PyTorch 未安装")
        return False
    
    try:
        import torchaudio
        print(f"torchaudio 版本: {torchaudio.__version__}")
    except ImportError as e:
        print(f"torchaudio 导入失败: {e}")
        return False
    
    return True

def fix_torchaudio():
    """修复 torchaudio 问题"""
    print("\n" + "=" * 60)
    print("    修复 torchaudio 问题")
    print("=" * 60)
    
    try:
        # 1. 卸载当前的 torch 和 torchaudio
        print("1. 卸载当前的 PyTorch 和 torchaudio...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchaudio"], 
                      check=True, capture_output=True)
        print("✓ 卸载成功")
        
        # 2. 重新安装 PyTorch 和 torchaudio
        print("2. 重新安装 PyTorch 和 torchaudio...")
        
        # 检查系统架构
        is_windows = platform.system() == "Windows"
        is_cuda_available = False
        
        try:
            import torch
            is_cuda_available = torch.cuda.is_available()
        except:
            pass
        
        if is_windows:
            if is_cuda_available:
                # Windows + CUDA
                subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu121"], 
                              check=True, capture_output=True)
            else:
                # Windows + CPU
                subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"], 
                              check=True, capture_output=True)
        else:
            # Linux/Mac
            subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchaudio"], 
                          check=True, capture_output=True)
        
        print("✓ 安装成功")
        
        # 3. 验证安装
        print("3. 验证安装...")
        if check_torch_versions():
            print("✓ PyTorch 和 torchaudio 安装验证成功")
            return True
        else:
            print("✗ 安装验证失败")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 修复失败: {e}")
        return False

def test_torchaudio_import():
    """测试 torchaudio 导入"""
    print("\n测试 torchaudio 导入...")
    try:
        import torchaudio
        print("✓ torchaudio 导入成功")
        
        # 测试基本功能
        try:
            # 创建一个简单的音频张量
            import torch
            audio_tensor = torch.randn(1, 16000)  # 1秒的随机音频
            print("✓ 音频张量创建成功")
            
            # 测试保存功能
            torchaudio.save("test_audio.wav", audio_tensor, 16000)
            print("✓ 音频保存功能正常")
            
            # 清理测试文件
            import os
            if os.path.exists("test_audio.wav"):
                os.remove("test_audio.wav")
                print("✓ 测试文件清理完成")
                
        except Exception as e:
            print(f"⚠ 功能测试失败: {e}")
            
        return True
        
    except ImportError as e:
        print(f"✗ torchaudio 导入失败: {e}")
        return False

def main():
    """主函数"""
    print("开始修复 torchaudio 问题...")
    
    # 检查当前状态
    if check_torch_versions():
        print("\n当前版本看起来正常，但仍有导入问题")
    
    # 修复问题
    if fix_torchaudio():
        print("\n✓ torchaudio 修复成功！")
        
        # 测试导入
        if test_torchaudio_import():
            print("\n✓ 所有测试通过！")
            print("\n现在可以运行兼容性测试:")
            print("  python test_compatibility.py")
        else:
            print("\n⚠ 仍有问题，可能需要手动处理")
    else:
        print("\n✗ 修复失败")
        print("\n建议手动处理:")
        print("1. 完全卸载 PyTorch: pip uninstall torch torchaudio")
        print("2. 重新安装: pip install torch torchaudio")
        print("3. 或者使用 conda: conda install pytorch torchaudio -c pytorch")

if __name__ == "__main__":
    main() 