#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows PyTorch 修复脚本
专门解决 Windows 下的 PyTorch 和 torchaudio 问题
"""

import subprocess
import sys
import platform

def fix_windows_torch():
    """修复 Windows 下的 PyTorch 问题"""
    print("=" * 60)
    print("    Windows PyTorch 修复脚本")
    print("=" * 60)
    
    if platform.system() != "Windows":
        print("此脚本仅适用于 Windows 系统")
        return False
    
    try:
        # 1. 完全卸载 PyTorch 相关包
        print("1. 卸载所有 PyTorch 相关包...")
        packages_to_remove = [
            "torch", "torchaudio", "torchvision", "pytorch", "pytorch-cuda"
        ]
        
        for package in packages_to_remove:
            try:
                subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package], 
                              check=True, capture_output=True)
                print(f"✓ 卸载 {package} 成功")
            except subprocess.CalledProcessError:
                print(f"⚠ {package} 未安装或卸载失败")
        
        # 2. 清理 pip 缓存
        print("\n2. 清理 pip 缓存...")
        subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], 
                      check=True, capture_output=True)
        print("✓ 缓存清理完成")
        
        # 3. 重新安装 PyTorch CPU 版本（更稳定）
        print("\n3. 安装 PyTorch CPU 版本...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "torch", "torchaudio", "torchvision",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ], check=True, capture_output=True)
        print("✓ PyTorch CPU 版本安装成功")
        
        # 4. 验证安装
        print("\n4. 验证安装...")
        try:
            import torch
            import torchaudio
            print(f"✓ PyTorch 版本: {torch.__version__}")
            print(f"✓ torchaudio 版本: {torchaudio.__version__}")
            print(f"✓ CUDA 可用: {torch.cuda.is_available()}")
            
            # 测试基本功能
            audio_tensor = torch.randn(1, 16000)
            torchaudio.save("test.wav", audio_tensor, 16000)
            import os
            if os.path.exists("test.wav"):
                os.remove("test.wav")
            print("✓ 功能测试通过")
            
            return True
            
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 修复失败: {e}")
        return False

def main():
    """主函数"""
    print("开始修复 Windows PyTorch 问题...")
    
    if fix_windows_torch():
        print("\n" + "=" * 60)
        print("✓ Windows PyTorch 修复成功！")
        print("现在可以运行兼容性测试:")
        print("  python test_compatibility.py")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 修复失败")
        print("建议手动处理:")
        print("1. 使用 conda 重新创建环境")
        print("2. 或者手动下载 PyTorch wheel 文件安装")
        print("=" * 60)

if __name__ == "__main__":
    main() 