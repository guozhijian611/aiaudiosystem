#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
转写示例脚本
简单的转写功能演示
"""

import os
import sys
import json

# 添加项目路径
sys.path.append(os.path.dirname(__file__))
from src.transcriber import WhisperDiarizationTranscriber
from logger import logger

def example_transcribe():
    """转写示例"""
    
    # 示例音频文件路径（请替换为实际的音频文件）
    audio_file = "example_audio.wav"  # 请替换为实际的音频文件路径
    
    # 检查音频文件是否存在
    if not os.path.exists(audio_file):
        logger.error(f"示例音频文件不存在: {audio_file}")
        logger.info("请将音频文件放在当前目录，并修改 audio_file 变量")
        return
    
    try:
        # 初始化转写器
        logger.info("初始化转写器...")
        transcriber = WhisperDiarizationTranscriber()
        
        # 执行转写
        logger.info("开始转写...")
        result = transcriber.transcribe_audio(audio_file)
        
        # 显示结果
        logger.info("转写完成！")
        logger.info(f"文本: {result['text']}")
        logger.info(f"语言: {result['language']}")
        logger.info(f"段落数: {len(result.get('segments', []))}")
        logger.info(f"说话人数: {len(result.get('speakers', {}))}")
        
        # 保存结果
        output_file = "transcribe_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {output_file}")
        
    except Exception as e:
        logger.error(f"转写失败: {e}")

if __name__ == "__main__":
    example_transcribe() 