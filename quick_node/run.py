#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速识别节点启动脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.queue_consumer import main

if __name__ == "__main__":
    main() 