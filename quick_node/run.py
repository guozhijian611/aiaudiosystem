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

from src.queue_consumer import main

if __name__ == "__main__":
    print("=" * 50)
    print("Quick Node - 快速识别节点启动")
    print("=" * 50)
    
  
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭服务...")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")
        import traceback
        traceback.print_exc() 