#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VAD分析测试脚本
"""

import sys
import os
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.vad_analyzer import VADAnalyzer
from loguru import logger

def test_vad_analyzer():
    """测试VAD分析器"""
    try:
        logger.info("开始测试VAD分析器...")
        
        # 初始化分析器
        analyzer = VADAnalyzer()
        
        # 获取模型信息
        model_info = analyzer.get_model_info()
        logger.info(f"模型信息: {json.dumps(model_info, indent=2, ensure_ascii=False)}")
        
        # 测试音频文件路径（需要提供实际的音频文件）
        test_audio_path = "./test_audio.wav"  # 请替换为实际的音频文件路径
        
        if os.path.exists(test_audio_path):
            logger.info(f"开始分析测试音频: {test_audio_path}")
            
            # 进行VAD分析
            result = analyzer.analyze_audio(test_audio_path)
            
            # 输出结果
            logger.info("VAD分析结果:")
            logger.info(f"总时长: {result['total_duration']:.2f}秒")
            logger.info(f"有效语音时长: {result['effective_duration']:.2f}秒")
            logger.info(f"静音时长: {result['silence_duration']:.2f}秒")
            logger.info(f"语音占比: {result['speech_ratio']:.2%}")
            logger.info(f"语音段落数: {result['speech_segments_count']}")
            
            # 输出详细的语音段落信息
            if result['speech_segments']:
                logger.info("语音段落详情:")
                for i, segment in enumerate(result['speech_segments'][:5]):  # 只显示前5个段落
                    logger.info(f"  段落{i+1}: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s (时长: {segment['duration']:.2f}s)")
                
                if len(result['speech_segments']) > 5:
                    logger.info(f"  ... 还有 {len(result['speech_segments']) - 5} 个段落")
            
            logger.info("VAD分析测试完成！")
            
        else:
            logger.warning(f"测试音频文件不存在: {test_audio_path}")
            logger.info("请将音频文件放置在项目根目录下，命名为 test_audio.wav")
            
    except Exception as e:
        logger.error(f"VAD分析测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vad_analyzer() 