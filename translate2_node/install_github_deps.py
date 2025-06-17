#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安装 GitHub 依赖脚本
"""

import subprocess
import sys

def install_github_deps():
    """安装 GitHub 依赖"""
    print("=" * 60)
    print("    安装 GitHub 依赖")
    print("=" * 60)
    
    # GitHub 依赖列表
    github_deps = [
        ("https://github.com/MahmoudAshraf97/demucs.git", "Demucs"),
        ("https://github.com/oliverguhr/deepmultilingualpunctuation.git", "Deep Multilingual Punctuation"),
        ("https://github.com/MahmoudAshraf97/ctc-forced-aligner.git", "CTC Forced Aligner"),
    ]
    
    success_count = 0
    total_count = len(github_deps)
    
    for repo_url, name in github_deps:
        print(f"\n安装 {name}...")
        try:
            cmd = [sys.executable, "-m", "pip", "install", f"git+{repo_url}"]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ {name} 安装成功")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"✗ {name} 安装失败: {e}")
            print(f"  命令: {' '.join(cmd)}")
    
    print(f"\n" + "=" * 60)
    print(f"GitHub 依赖安装完成: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✓ 所有 GitHub 依赖安装成功！")
        print("\n现在可以运行转写测试:")
        print("  python test_local_transcribe.py your_audio.wav")
    else:
        print("⚠ 部分依赖安装失败")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 确保 Git 已安装")
        print("3. 手动安装失败的包")
    
    print("=" * 60)

def test_imports():
    """测试导入"""
    print("\n测试 GitHub 依赖导入...")
    
    test_modules = [
        ("demucs", "Demucs"),
        ("deepmultilingualpunctuation", "Deep Multilingual Punctuation"),
        ("ctc_forced_aligner", "CTC Forced Aligner"),
    ]
    
    success_count = 0
    for module, name in test_modules:
        try:
            __import__(module)
            print(f"✓ {name}: 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"✗ {name}: 导入失败 - {e}")
    
    print(f"\n导入测试: {success_count}/{len(test_modules)}")
    return success_count == len(test_modules)

if __name__ == "__main__":
    install_github_deps()
    test_imports() 