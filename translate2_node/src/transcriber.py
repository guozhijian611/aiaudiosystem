#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Whisper-Diarization 转写器模块
基于 Whisper-Diarization 的音频转文本服务，支持说话人分离
"""

import os
import sys
import json
import time
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from logger import logger

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

# 添加 Whisper-Diarization 路径
whisper_diarization_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'whisper-diarization')
if os.path.exists(whisper_diarization_path):
    sys.path.append(whisper_diarization_path)

try:
    from whisper_diarization import WhisperDiarization
except ImportError:
    logger.warning("Whisper-Diarization 模块未找到，将使用基础 Whisper 实现")
    WhisperDiarization = None

class WhisperDiarizationTranscriber:
    """Whisper-Diarization 转写器类"""
    
    def __init__(self):
        """初始化转写器"""
        self.config = Config()
        self.model = None
        self.device = None
        self._init_device()
        self._init_model()
        
        logger.info(f"Whisper-Diarization 转写器初始化完成")
        logger.info(f"设备: {self.device}")
        logger.info(f"模型: {self.config.WHISPER_MODEL}")
        logger.info(f"说话人分离: {self.config.ENABLE_DIARIZATION}")
        logger.info(f"VAD启用: {self.config.ENABLE_VAD}")
        logger.info(f"TitaNet启用: {self.config.ENABLE_TITANET}")
    
    def _init_device(self):
        """初始化设备"""
        if self.config.WHISPER_DEVICE == 'auto':
            if torch.cuda.is_available():
                self.device = 'cuda'
                logger.info(f"使用CUDA设备: {torch.cuda.get_device_name()}")
            elif torch.backends.mps.is_available():
                self.device = 'mps'
                logger.info("使用MPS设备")
            else:
                self.device = 'cpu'
                logger.info("使用CPU设备")
        else:
            self.device = self.config.WHISPER_DEVICE
    
    def _init_model(self):
        """初始化模型"""
        try:
            if WhisperDiarization is not None:
                # 使用 Whisper-Diarization
                self.model = WhisperDiarization(
                    model_name=self.config.WHISPER_MODEL,
                    device=self.device,
                    compute_type=self.config.WHISPER_COMPUTE_TYPE,
                    language=self.config.WHISPER_LANGUAGE,
                    batch_size=self.config.WHISPER_BATCH_SIZE,
                    diarization=self.config.ENABLE_DIARIZATION,
                    vad=self.config.ENABLE_VAD,
                    titanet=self.config.ENABLE_TITANET,
                    hf_token=self.config.HF_TOKEN,
                    min_speakers=self.config.MIN_SPEAKERS,
                    max_speakers=self.config.MAX_SPEAKERS,
                    vad_threshold=self.config.VAD_THRESHOLD,
                    vad_min_speech_duration=self.config.VAD_MIN_SPEECH_DURATION,
                    vad_max_speech_duration=self.config.VAD_MAX_SPEECH_DURATION,
                    titanet_model=self.config.TITANET_MODEL
                )
                logger.info("Whisper-Diarization 模型加载成功")
            else:
                # 回退到基础 Whisper 实现
                self._init_fallback_model()
                
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            logger.info("尝试使用基础 Whisper 实现")
            self._init_fallback_model()
    
    def _init_fallback_model(self):
        """初始化回退模型（基础 Whisper）"""
        try:
            import whisper
            self.model = whisper.load_model(self.config.WHISPER_MODEL, device=self.device)
            logger.info("基础 Whisper 模型加载成功")
        except Exception as e:
            logger.error(f"基础 Whisper 模型加载失败: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str, timeout: int = None) -> Dict:
        """
        转写音频文件
        
        Args:
            audio_path (str): 音频文件路径
            timeout (int, optional): 超时时间（秒）
            
        Returns:
            Dict: 转写结果
        """
        start_time = time.time()
        
        try:
            logger.info(f"开始转写音频: {audio_path}")
            
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                raise Exception(f"音频文件不存在: {audio_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                raise Exception("音频文件为空")
            
            logger.info(f"音频文件大小: {self._format_size(file_size)}")
            
            # 执行转写
            if WhisperDiarization is not None and self.model is not None:
                result = self._transcribe_with_diarization(audio_path)
            else:
                result = self._transcribe_with_whisper(audio_path)
            
            # 计算处理时间
            process_time = time.time() - start_time
            logger.info(f"转写完成，耗时: {process_time:.1f}秒")
            
            # 添加元数据
            result['metadata'] = {
                'processing_time': process_time,
                'audio_file': audio_path,
                'file_size': file_size,
                'model': self.config.WHISPER_MODEL,
                'device': self.device,
                'diarization_enabled': self.config.ENABLE_DIARIZATION,
                'vad_enabled': self.config.ENABLE_VAD,
                'titanet_enabled': self.config.ENABLE_TITANET
            }
            
            return result
            
        except Exception as e:
            logger.error(f"音频转写失败: {e}")
            raise
    
    def _transcribe_with_diarization(self, audio_path: str) -> Dict:
        """使用 Whisper-Diarization 进行转写"""
        try:
            # 检查 HF_TOKEN
            if self.config.ENABLE_DIARIZATION and not self.config.HF_TOKEN:
                logger.warning("未配置 HF_TOKEN，说话人分离功能将被禁用")
                # 临时禁用说话人分离
                self.model.diarization = False
            
            # 执行转写
            result = self.model.transcribe(
                audio_path,
                language=self.config.WHISPER_LANGUAGE,
                word_timestamps=self.config.INCLUDE_TIMESTAMPS,
                verbose=True
            )
            
            # 格式化结果
            return self._format_diarization_result(result)
            
        except Exception as e:
            logger.error(f"Whisper-Diarization 转写失败: {e}")
            raise
    
    def _transcribe_with_whisper(self, audio_path: str) -> Dict:
        """使用基础 Whisper 进行转写"""
        try:
            # 执行转写
            result = self.model.transcribe(
                audio_path,
                language=self.config.WHISPER_LANGUAGE,
                word_timestamps=self.config.INCLUDE_TIMESTAMPS,
                verbose=True
            )
            
            # 格式化结果
            return self._format_whisper_result(result)
            
        except Exception as e:
            logger.error(f"基础 Whisper 转写失败: {e}")
            raise
    
    def _format_diarization_result(self, result: Dict) -> Dict:
        """格式化 Whisper-Diarization 结果"""
        try:
            formatted_result = {
                'text': result.get('text', ''),
                'language': result.get('language', 'unknown'),
                'segments': [],
                'speakers': {},
                'summary': {
                    'total_duration': 0,
                    'total_segments': 0,
                    'total_speakers': 0
                }
            }
            
            # 处理段落
            segments = result.get('segments', [])
            speaker_mapping = {}
            current_speaker_id = 0
            
            for segment in segments:
                # 获取说话人信息
                speaker = segment.get('speaker', 'SPEAKER_UNKNOWN')
                
                # 说话人编号归一化
                if speaker not in speaker_mapping:
                    speaker_mapping[speaker] = f"SPEAKER_{current_speaker_id:02d}"
                    current_speaker_id += 1
                
                normalized_speaker = speaker_mapping[speaker]
                
                # 格式化段落
                formatted_segment = {
                    'id': segment.get('id', len(formatted_result['segments'])),
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': segment.get('text', ''),
                    'speaker': normalized_speaker,
                    'confidence': segment.get('confidence', 0.0)
                }
                
                # 添加词级时间戳
                if self.config.INCLUDE_TIMESTAMPS and 'words' in segment:
                    formatted_segment['words'] = segment['words']
                
                formatted_result['segments'].append(formatted_segment)
            
            # 更新摘要信息
            if formatted_result['segments']:
                formatted_result['summary']['total_duration'] = max(
                    seg['end'] for seg in formatted_result['segments']
                )
                formatted_result['summary']['total_segments'] = len(formatted_result['segments'])
                formatted_result['summary']['total_speakers'] = len(speaker_mapping)
            
            # 添加说话人映射
            formatted_result['speakers'] = speaker_mapping
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"格式化 Whisper-Diarization 结果失败: {e}")
            raise
    
    def _format_whisper_result(self, result: Dict) -> Dict:
        """格式化基础 Whisper 结果"""
        try:
            formatted_result = {
                'text': result.get('text', ''),
                'language': result.get('language', 'unknown'),
                'segments': [],
                'speakers': {},
                'summary': {
                    'total_duration': 0,
                    'total_segments': 0,
                    'total_speakers': 1  # 基础 Whisper 只有一个说话人
                }
            }
            
            # 处理段落
            segments = result.get('segments', [])
            
            for i, segment in enumerate(segments):
                formatted_segment = {
                    'id': i,
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': segment.get('text', ''),
                    'speaker': 'SPEAKER_00',  # 基础 Whisper 只有一个说话人
                    'confidence': segment.get('confidence', 0.0)
                }
                
                # 添加词级时间戳
                if self.config.INCLUDE_TIMESTAMPS and 'words' in segment:
                    formatted_segment['words'] = segment['words']
                
                formatted_result['segments'].append(formatted_segment)
            
            # 更新摘要信息
            if formatted_result['segments']:
                formatted_result['summary']['total_duration'] = max(
                    seg['end'] for seg in formatted_result['segments']
                )
                formatted_result['summary']['total_segments'] = len(formatted_result['segments'])
            
            # 添加说话人映射
            formatted_result['speakers'] = {'SPEAKER_00': 'SPEAKER_00'}
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"格式化基础 Whisper 结果失败: {e}")
            raise
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}" 