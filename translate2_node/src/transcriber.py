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
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from logger import logger

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

class WhisperDiarizationTranscriber:
    """Whisper-Diarization 转写器类"""
    
    def __init__(self):
        """初始化转写器"""
        self.config = Config()
        self.model = None
        self.device = None
        self.whisper_diarization_path = None
        self._init_device()
        self._init_whisper_diarization()
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
    
    def _init_whisper_diarization(self):
        """初始化 Whisper-Diarization 路径"""
        # 检查 Whisper-Diarization 目录
        whisper_diarization_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'whisper-diarization')
        if os.path.exists(whisper_diarization_path):
            self.whisper_diarization_path = whisper_diarization_path
            logger.info(f"找到 Whisper-Diarization 目录: {whisper_diarization_path}")
            
            # 检查 diarize.py 是否存在
            diarize_script = os.path.join(whisper_diarization_path, 'diarize.py')
            if os.path.exists(diarize_script):
                logger.info("找到 diarize.py 脚本")
            else:
                logger.warning("未找到 diarize.py 脚本")
                self.whisper_diarization_path = None
        else:
            logger.warning("未找到 Whisper-Diarization 目录")
            self.whisper_diarization_path = None
    
    def _init_model(self):
        """初始化模型"""
        try:
            if self.whisper_diarization_path and self.config.ENABLE_DIARIZATION:
                # 使用 Whisper-Diarization 脚本
                logger.info("Whisper-Diarization 脚本可用，将使用脚本模式")
                self.model = "script_mode"
            else:
                # 回退到基础 Whisper 实现
                logger.info("使用基础 Whisper 实现")
                self._init_fallback_model()
                
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            logger.info("尝试使用基础 Whisper 实现")
            self._init_fallback_model()
    
    def _init_fallback_model(self):
        """初始化回退模型（基础 Whisper）"""
        try:
            import whisper
            logger.info(f"正在加载基础 Whisper 模型: {self.config.WHISPER_MODEL}")
            self.model = whisper.load_model(self.config.WHISPER_MODEL, device=self.device)
            logger.info("基础 Whisper 模型加载成功")
        except ImportError:
            logger.error("whisper 模块未安装，请运行: pip install openai-whisper")
            raise
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
            if self.model == "script_mode" and self.config.ENABLE_DIARIZATION:
                result = self._transcribe_with_diarization_script(audio_path)
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
                'diarization_enabled': self.config.ENABLE_DIARIZATION and self.model == "script_mode",
                'vad_enabled': self.config.ENABLE_VAD,
                'titanet_enabled': self.config.ENABLE_TITANET,
                'whisper_diarization_available': self.model == "script_mode"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"音频转写失败: {e}")
            raise
    
    def _transcribe_with_diarization_script(self, audio_path: str) -> Dict:
        """使用 Whisper-Diarization 脚本进行转写"""
        try:
            # 检查 HF_TOKEN
            if self.config.ENABLE_DIARIZATION and not self.config.HF_TOKEN:
                logger.warning("未配置 HF_TOKEN，说话人分离功能将被禁用")
                # 使用基础 Whisper 模式
                return self._transcribe_with_whisper(audio_path)
            
            # 构建命令
            diarize_script = os.path.join(self.whisper_diarization_path, 'diarize.py')
            cmd = [
                sys.executable,
                diarize_script,
                '-a', audio_path,
                '--whisper-model', self.config.WHISPER_MODEL,
                '--device', self.device,
                '--batch-size', str(self.config.WHISPER_BATCH_SIZE)
            ]
            
            # 添加语言参数
            if self.config.WHISPER_LANGUAGE:
                cmd.extend(['--language', self.config.WHISPER_LANGUAGE])
            
            # 添加其他参数
            if not self.config.ENABLE_VAD:
                cmd.append('--no-stem')
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行脚本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.whisper_diarization_path,
                timeout=timeout or 3600  # 默认1小时超时
            )
            
            if result.returncode != 0:
                logger.error(f"Whisper-Diarization 脚本执行失败: {result.stderr}")
                raise Exception(f"脚本执行失败: {result.stderr}")
            
            # 解析输出
            return self._parse_diarization_output(result.stdout, audio_path)
            
        except subprocess.TimeoutExpired:
            logger.error("Whisper-Diarization 脚本执行超时")
            raise Exception("转写超时")
        except Exception as e:
            logger.error(f"Whisper-Diarization 脚本转写失败: {e}")
            raise
    
    def _parse_diarization_output(self, output: str, audio_path: str) -> Dict:
        """解析 Whisper-Diarization 脚本输出"""
        try:
            # 查找生成的 SRT 文件
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            srt_file = os.path.join(self.whisper_diarization_path, f"{base_name}.srt")
            
            if not os.path.exists(srt_file):
                logger.warning(f"未找到 SRT 文件: {srt_file}")
                # 尝试从输出中解析
                return self._parse_output_text(output)
            
            # 解析 SRT 文件
            return self._parse_srt_file(srt_file)
            
        except Exception as e:
            logger.error(f"解析 Whisper-Diarization 输出失败: {e}")
            raise
    
    def _parse_srt_file(self, srt_file: str) -> Dict:
        """解析 SRT 文件"""
        try:
            segments = []
            current_segment = {}
            speaker_mapping = {}
            current_speaker_id = 0
            
            with open(srt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.isdigit():  # 段落编号
                    if current_segment:
                        segments.append(current_segment)
                    
                    current_segment = {'id': int(line)}
                    i += 1
                    
                    # 时间戳行
                    if i < len(lines):
                        time_line = lines[i].strip()
                        start_time, end_time = self._parse_timestamp(time_line)
                        current_segment['start'] = start_time
                        current_segment['end'] = end_time
                        i += 1
                    
                    # 文本行
                    text_lines = []
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i].strip())
                        i += 1
                    
                    if text_lines:
                        text = ' '.join(text_lines)
                        # 提取说话人信息
                        speaker, clean_text = self._extract_speaker(text)
                        
                        # 说话人编号归一化
                        if speaker not in speaker_mapping:
                            speaker_mapping[speaker] = f"SPEAKER_{current_speaker_id:02d}"
                            current_speaker_id += 1
                        
                        current_segment['text'] = clean_text
                        current_segment['speaker'] = speaker_mapping[speaker]
                        current_segment['confidence'] = 1.0  # SRT 没有置信度信息
                
                i += 1
            
            # 添加最后一个段落
            if current_segment:
                segments.append(current_segment)
            
            # 构建结果
            result = {
                'text': ' '.join(seg['text'] for seg in segments),
                'language': 'unknown',  # SRT 没有语言信息
                'segments': segments,
                'speakers': speaker_mapping,
                'summary': {
                    'total_duration': max(seg['end'] for seg in segments) if segments else 0,
                    'total_segments': len(segments),
                    'total_speakers': len(speaker_mapping)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析 SRT 文件失败: {e}")
            raise
    
    def _parse_timestamp(self, time_line: str) -> Tuple[float, float]:
        """解析时间戳"""
        try:
            # 格式: 00:00:00,000 --> 00:00:00,000
            parts = time_line.split(' --> ')
            start_str = parts[0].replace(',', '.')
            end_str = parts[1].replace(',', '.')
            
            start_time = self._time_to_seconds(start_str)
            end_time = self._time_to_seconds(end_str)
            
            return start_time, end_time
        except Exception as e:
            logger.error(f"解析时间戳失败: {e}")
            return 0.0, 0.0
    
    def _time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数"""
        try:
            # 格式: HH:MM:SS.mmm
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            
            return hours * 3600 + minutes * 60 + seconds
        except Exception as e:
            logger.error(f"时间转换失败: {e}")
            return 0.0
    
    def _extract_speaker(self, text: str) -> Tuple[str, str]:
        """从文本中提取说话人信息"""
        try:
            # 常见的说话人格式: [Speaker 1], (Speaker 1), Speaker 1:, 等
            import re
            
            # 匹配各种说话人格式
            patterns = [
                r'\[([^\]]+)\]:?\s*(.*)',  # [Speaker 1]: text
                r'\(([^)]+)\):?\s*(.*)',   # (Speaker 1): text
                r'^([^:]+):\s*(.*)',       # Speaker 1: text
                r'^([A-Za-z\s]+\d+)\s*(.*)'  # Speaker 1 text
            ]
            
            for pattern in patterns:
                match = re.match(pattern, text.strip())
                if match:
                    speaker = match.group(1).strip()
                    clean_text = match.group(2).strip()
                    return speaker, clean_text
            
            # 如果没有匹配到，返回默认说话人
            return 'SPEAKER_UNKNOWN', text
            
        except Exception as e:
            logger.error(f"提取说话人信息失败: {e}")
            return 'SPEAKER_UNKNOWN', text
    
    def _parse_output_text(self, output: str) -> Dict:
        """从脚本输出中解析文本"""
        try:
            # 简单的文本解析，作为兜底方案
            lines = output.split('\n')
            text_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith('('):
                    text_lines.append(line)
            
            text = ' '.join(text_lines)
            
            return {
                'text': text,
                'language': 'unknown',
                'segments': [{
                    'id': 0,
                    'start': 0.0,
                    'end': 0.0,
                    'text': text,
                    'speaker': 'SPEAKER_00',
                    'confidence': 1.0
                }],
                'speakers': {'SPEAKER_00': 'SPEAKER_00'},
                'summary': {
                    'total_duration': 0.0,
                    'total_segments': 1,
                    'total_speakers': 1
                }
            }
            
        except Exception as e:
            logger.error(f"解析输出文本失败: {e}")
            raise
    
    def _transcribe_with_whisper(self, audio_path: str) -> Dict:
        """使用基础 Whisper 进行转写"""
        try:
            # 执行转写
            logger.info("使用基础 Whisper 进行转写...")
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