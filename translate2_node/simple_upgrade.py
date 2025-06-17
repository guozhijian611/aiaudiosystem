#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化升级脚本
"""

import subprocess
import sys

def simple_upgrade():
    """简化升级"""
    print("=" * 60)
    print("    简化升级到最新版本")
    print("=" * 60)
    
    try:
        # 升级所有相关包
        packages = [
            "huggingface_hub",
            "nemo_toolkit[asr]",
            "transformers",
            "datasets",
            "accelerate"
        ]
        
        for package in packages:
            print(f"升级 {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], 
                              check=True, capture_output=True)
                print(f"✓ {package} 升级成功")
            except subprocess.CalledProcessError as e:
                print(f"⚠ {package} 升级失败: {e}")
        
        print("\n" + "=" * 60)
        print("升级完成！")
        print("现在运行兼容性测试:")
        print("  python test_compatibility.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"升级失败: {e}")

if __name__ == "__main__":
    simple_upgrade() 