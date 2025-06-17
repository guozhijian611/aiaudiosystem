#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translate2 Node 主程序
基于Whisper-Diarization的音频转文本服务（加强版）
"""

import os
import sys

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from src.queue_consumer import main

if __name__ == "__main__":
    main() 