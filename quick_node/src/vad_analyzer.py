#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import librosa
import numpy as np
from pathlib import Path
from loguru import logger
from funasr import AutoModel
import sys
import os

# 添加本地FunASR路径
current_dir = os.path.dirname(__file__)
funasr_path = os.path.join(os.path.dirname(current_dir), 'FunASR')
if os.path.exists(funasr_path):
    sys.path.insert(0, funasr_path)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

class VADAnalyzer:
    """语音活动检测分析器 - 基于FunASR的VAD模型"""
    
    def __init__(self):
        """初始化VAD分析器"""
        self.config = Config()
        self.vad_model = None
        self._init_vad_model()
    
    def _init_vad_model(self):
        """初始化VAD模型"""
        try:
            logger.info("正在初始化FunASR VAD模型...")
            
            # 检查是否存在本地模型
            local_model_path = None
            possible_local_paths = [
                os.path.join(self.config.MODEL_CACHE_DIR, 'speech_fsmn_vad_zh-cn-16k-common-pytorch'),
                os.path.join(self.config.MODEL_CACHE_DIR, 'iic', 'speech_fsmn_vad_zh-cn-16k-common-pytorch'),
                './models/speech_fsmn_vad_zh-cn-16k-common-pytorch',
                './models/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch',
                # 兼容其他可能的本地路径
                '/root/.cache/modelscope/hub/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch',
                '/home/.cache/modelscope/hub/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch',
            ]
            
            # 查找本地模型
            for path in possible_local_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    # 检查是否包含模型文件
                    model_files = [f for f in os.listdir(path) if f.endswith(('.bin', '.pt', '.pth', '.onnx'))]
                    config_files = [f for f in os.listdir(path) if f in ['config.yaml', 'config.json', 'configuration.json']]
                    
                    if model_files and config_files:
                        local_model_path = path
                        logger.info(f"发现本地VAD模型: {local_model_path}")
                        break
            
            # 根据是否找到本地模型来配置模型参数
            if local_model_path and (self.config.OFFLINE_MODE or self.config.DISABLE_UPDATE):
                # 使用本地模型
                logger.info(f"使用本地VAD模型: {local_model_path}")
                self.vad_model = AutoModel(
                    model=local_model_path,
                    disable_update=True,
                    trust_remote_code=True
                )
            else:
                # 使用远程模型（在线模式）
                logger.info(f"使用远程VAD模型: {self.config.VAD_MODEL}")
                self.vad_model = AutoModel(
                    model=self.config.VAD_MODEL,
                    model_revision=self.config.VAD_MODEL_REVISION,
                    cache_dir=self.config.MODEL_CACHE_DIR,
                    disable_update=self.config.DISABLE_UPDATE,
                    trust_remote_code=True
                )
            
            logger.info(f"VAD模型初始化成功 - 模型: {self.config.VAD_MODEL}")
            
        except Exception as e:
            logger.error(f"VAD模型初始化失败: {e}")
            # 尝试使用备用方案
            logger.info("尝试使用备用VAD配置...")
            try:
                # 尝试使用流式VAD模型作为备用
                self.vad_model = AutoModel(
                    model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                    disable_update=True,
                    trust_remote_code=True
                )
                logger.info("使用备用VAD模型成功")
            except Exception as e2:
                logger.error(f"备用VAD模型也失败: {e2}")
                raise Exception(f"VAD模型初始化失败: 主模型错误={e}, 备用模型错误={e2}")
    
    def analyze_audio(self, audio_path: str) -> dict:
        """
        分析音频文件的语音活动
        
        Args:
            audio_path (str): 音频文件路径
            
        Returns:
            dict: 分析结果
            {
                'total_duration': float,      # 音频总时长(秒)
                'effective_duration': float,  # 有效语音时长(秒)
                'silence_duration': float,    # 静音时长(秒)
                'speech_ratio': float,        # 语音占比(0-1)
                'speech_segments': list,      # 语音段落信息
                'file_info': dict            # 文件基本信息
            }
        """
        try:
            # 验证文件存在
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_path}")
            
            logger.info(f"开始分析音频: {audio_path}")
            
            # 获取音频基本信息
            file_info = self._get_audio_info(audio_path)
            total_duration = file_info['duration']
            
            logger.info(f"音频基本信息: 时长={total_duration:.2f}秒, 采样率={file_info['sample_rate']}Hz")
            
            # 使用VAD模型进行语音活动检测
            vad_result = self.vad_model.generate(
                input=audio_path,
                batch_size_s=300  # VAD模型使用batch_size_s参数，单位为秒
            )
            
            # 解析VAD结果
            analysis_result = self._parse_vad_result(vad_result, total_duration, file_info)
            
            logger.info(f"VAD分析完成: 总时长={analysis_result['total_duration']:.2f}秒, "
                       f"有效语音={analysis_result['effective_duration']:.2f}秒, "
                       f"语音占比={analysis_result['speech_ratio']:.2%}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"音频分析失败: {e}")
            raise
    
    def _get_audio_info(self, audio_path: str) -> dict:
        """获取音频文件基本信息"""
        try:
            # 使用librosa获取音频信息
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            file_size = os.path.getsize(audio_path)
            
            return {
                'file_path': audio_path,
                'file_name': os.path.basename(audio_path),
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'duration': duration,
                'sample_rate': sr,
                'channels': 1 if len(y.shape) == 1 else y.shape[0],
                'samples': len(y)
            }
            
        except Exception as e:
            logger.error(f"获取音频信息失败: {e}")
            raise
    
    def _parse_vad_result(self, vad_result, total_duration: float, file_info: dict) -> dict:
        """解析VAD检测结果"""
        try:
            speech_segments = []
            effective_duration = 0.0
            
            # 解析VAD结果中的语音段落
            if vad_result and len(vad_result) > 0:
                # FunASR VAD结果格式: [{'key': 'filename', 'value': [[start_ms, end_ms], ...]}]
                for result_item in vad_result:
                    # 检查新格式：'value' 键包含时间戳列表
                    if 'value' in result_item:
                        timestamps = result_item['value']
                        for timestamp in timestamps:
                            if len(timestamp) >= 2:
                                start_ms, end_ms = timestamp[0], timestamp[1]
                                start_sec = start_ms / 1000.0
                                end_sec = end_ms / 1000.0
                                duration_sec = end_sec - start_sec
                                
                                # 添加语音段落信息
                                speech_segments.append({
                                    'start_time': start_sec,
                                    'end_time': end_sec,
                                    'duration': duration_sec,
                                    'start_ms': start_ms,
                                    'end_ms': end_ms
                                })
                                
                                effective_duration += duration_sec
                    # 兼容旧格式：'timestamp' 键
                    elif 'timestamp' in result_item:
                        timestamps = result_item['timestamp']
                        for timestamp in timestamps:
                            if len(timestamp) >= 2:
                                start_ms, end_ms = timestamp[0], timestamp[1]
                                start_sec = start_ms / 1000.0
                                end_sec = end_ms / 1000.0
                                duration_sec = end_sec - start_sec
                                
                                # 添加语音段落信息
                                speech_segments.append({
                                    'start_time': start_sec,
                                    'end_time': end_sec,
                                    'duration': duration_sec,
                                    'start_ms': start_ms,
                                    'end_ms': end_ms
                                })
                                
                                effective_duration += duration_sec
            
            # 计算统计信息
            silence_duration = max(0, total_duration - effective_duration)
            speech_ratio = effective_duration / total_duration if total_duration > 0 else 0
            
            return {
                'total_duration': round(total_duration, 2),
                'effective_duration': round(effective_duration, 2),
                'silence_duration': round(silence_duration, 2),
                'speech_ratio': round(speech_ratio, 4),
                'speech_segments_count': len(speech_segments),
                'speech_segments': speech_segments,
                'file_info': file_info
            }
            
        except Exception as e:
            logger.error(f"解析VAD结果失败: {e}")
            # 返回基本信息，避免完全失败
            return {
                'total_duration': round(total_duration, 2),
                'effective_duration': 0.0,
                'silence_duration': round(total_duration, 2),
                'speech_ratio': 0.0,
                'speech_segments_count': 0,
                'speech_segments': [],
                'file_info': file_info,
                'error': str(e)
            }
    
    def batch_analyze(self, audio_files: list) -> list:
        """批量分析音频文件"""
        results = []
        
        for audio_file in audio_files:
            try:
                result = self.analyze_audio(audio_file)
                result['status'] = 'success'
                results.append(result)
                
            except Exception as e:
                logger.error(f"分析文件失败 {audio_file}: {e}")
                results.append({
                    'file_path': audio_file,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'model_name': self.config.VAD_MODEL,
            'model_revision': self.config.VAD_MODEL_REVISION,
            'max_end_silence_time': self.config.VAD_MAX_END_SILENCE_TIME,
            'max_start_silence_time': self.config.VAD_MAX_START_SILENCE_TIME,
            'min_speech_duration': self.config.VAD_MIN_SPEECH_DURATION,
        } 