#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速识别节点启动脚本
"""

import sys
import os

# 添加本地FunASR路径
current_dir = os.path.dirname(__file__)
funasr_path = os.path.join(current_dir, 'FunASR')
if os.path.exists(funasr_path):
    sys.path.insert(0, funasr_path)
    print(f"已添加本地FunASR路径: {funasr_path}")

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(current_dir, 'src'))

def check_dependencies():
    """检查关键依赖"""
    missing_deps = []
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError:
        missing_deps.append('torch')
        print("❌ PyTorch未安装")
    
    try:
        import omegaconf
        print("✅ omegaconf已安装")
    except ImportError:
        missing_deps.append('omegaconf')
        print("❌ omegaconf未安装")
    
    try:
        import torch_complex
        print("✅ torch_complex已安装")
    except ImportError:
        missing_deps.append('torch_complex')
        print("❌ torch_complex未安装")
    
    try:
        from funasr import AutoModel
        print("✅ FunASR导入成功")
    except ImportError as e:
        print(f"❌ FunASR导入失败: {e}")
        missing_deps.append('funasr')
    
    if missing_deps:
        print(f"\n缺失依赖: {', '.join(missing_deps)}")
        print("请运行以下命令安装依赖:")
        if 'omegaconf' in missing_deps:
            print("  pip install omegaconf")
        if 'torch_complex' in missing_deps:
            print("  pip install torch_complex")
        if 'torch' in missing_deps:
            print("  pip install torch torchaudio")
        if 'funasr' in missing_deps:
            print("  cd FunASR && pip install -e .")
        return False
    
    return True

from src.queue_consumer import main

if __name__ == "__main__":
    print("=" * 50)
    print("Quick Node - 快速识别节点启动")
    print("=" * 50)
    
    print("检查依赖...")
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺失的依赖后重试")
        exit(1)
    
    print("\n✅ 依赖检查通过，启动服务...")
    print("=" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭服务...")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")
        import traceback
        traceback.print_exc() 