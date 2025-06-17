#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地文件转写测试脚本
用于测试 Whisper-Diarization 转写器的本地文件处理能力
"""

import os
import sys
import time
import argparse
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(__file__))
from src.transcriber import WhisperDiarizationTranscriber
from logger import logger

def test_local_transcribe(audio_file: str, output_file: str = None, timeout: int = 3600):
    """
    测试本地文件转写
    
    Args:
        audio_file (str): 音频文件路径
        output_file (str, optional): 输出文件路径
        timeout (int): 超时时间（秒）
    """
    try:
        # 检查音频文件是否存在
        if not os.path.exists(audio_file):
            logger.error(f"音频文件不存在: {audio_file}")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(audio_file)
        logger.info(f"音频文件: {audio_file}")
        logger.info(f"文件大小: {format_size(file_size)}")
        
        # 初始化转写器
        logger.info("正在初始化转写器...")
        transcriber = WhisperDiarizationTranscriber()
        
        # 执行转写
        logger.info("开始转写...")
        start_time = time.time()
        
        result = transcriber.transcribe_audio(audio_file, timeout=timeout)
        
        process_time = time.time() - start_time
        
        # 显示结果
        logger.info("=" * 60)
        logger.info("转写结果:")
        logger.info("=" * 60)
        
        # 基本信息
        logger.info(f"转写文本: {result['text']}")
        logger.info(f"检测语言: {result['language']}")
        logger.info(f"处理时间: {process_time:.1f}秒")
        
        # 段落信息
        segments = result.get('segments', [])
        logger.info(f"段落数量: {len(segments)}")
        
        if segments:
            logger.info("\n段落详情:")
            for i, segment in enumerate(segments[:5]):  # 只显示前5个段落
                logger.info(f"  段落 {i+1}: [{segment['start']:.1f}s - {segment['end']:.1f}s] "
                           f"[{segment['speaker']}] {segment['text']}")
            
            if len(segments) > 5:
                logger.info(f"  ... 还有 {len(segments) - 5} 个段落")
        
        # 说话人信息
        speakers = result.get('speakers', {})
        logger.info(f"\n说话人数量: {len(speakers)}")
        if speakers:
            logger.info("说话人映射:")
            for original, normalized in speakers.items():
                logger.info(f"  {original} -> {normalized}")
        
        # 摘要信息
        summary = result.get('summary', {})
        logger.info(f"\n摘要信息:")
        logger.info(f"  总时长: {summary.get('total_duration', 0):.1f}秒")
        logger.info(f"  总段落: {summary.get('total_segments', 0)}")
        logger.info(f"  说话人数: {summary.get('total_speakers', 0)}")
        
        # 元数据
        metadata = result.get('metadata', {})
        logger.info(f"\n元数据:")
        logger.info(f"  模型: {metadata.get('model', 'unknown')}")
        logger.info(f"  设备: {metadata.get('device', 'unknown')}")
        logger.info(f"  说话人分离: {metadata.get('diarization_enabled', False)}")
        logger.info(f"  VAD启用: {metadata.get('vad_enabled', False)}")
        logger.info(f"  TitaNet启用: {metadata.get('titanet_enabled', False)}")
        logger.info(f"  Whisper-Diarization可用: {metadata.get('whisper_diarization_available', False)}")
        
        # 保存结果到文件
        if output_file:
            save_result_to_file(result, output_file)
            logger.info(f"\n结果已保存到: {output_file}")
        
        logger.info("=" * 60)
        logger.info("转写测试完成！")
        
        return True
        
    except Exception as e:
        logger.error(f"转写测试失败: {e}")
        return False

def save_result_to_file(result: dict, output_file: str):
    """保存结果到文件"""
    try:
        # 创建输出目录
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存为JSON格式
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 同时保存为SRT格式
        srt_file = output_file.replace('.json', '.srt')
        save_as_srt(result, srt_file)
        
        logger.info(f"结果已保存为JSON: {output_file}")
        logger.info(f"结果已保存为SRT: {srt_file}")
        
    except Exception as e:
        logger.error(f"保存结果失败: {e}")

def save_as_srt(result: dict, srt_file: str):
    """保存为SRT格式"""
    try:
        segments = result.get('segments', [])
        
        with open(srt_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                # 段落编号
                f.write(f"{i}\n")
                
                # 时间戳
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])
                f.write(f"{start_time} --> {end_time}\n")
                
                # 文本（包含说话人信息）
                speaker = segment.get('speaker', 'SPEAKER_UNKNOWN')
                text = segment.get('text', '')
                f.write(f"[{speaker}] {text}\n\n")
        
    except Exception as e:
        logger.error(f"保存SRT文件失败: {e}")

def format_timestamp(seconds: float) -> str:
    """格式化时间戳为 SRT 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="本地文件转写测试")
    parser.add_argument("audio_file", help="音频文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径（JSON格式）")
    parser.add_argument("-t", "--timeout", type=int, default=3600, help="超时时间（秒）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # 如果没有指定输出文件，使用默认路径
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.audio_file))[0]
        args.output = f"output/{base_name}_transcribe.json"
    
    # 执行测试
    success = test_local_transcribe(args.audio_file, args.output, args.timeout)
    
    if success:
        logger.info("测试成功完成！")
        sys.exit(0)
    else:
        logger.error("测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main() 