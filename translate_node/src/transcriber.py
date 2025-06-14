#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import signal
import platform
import threading
import concurrent.futures
from pathlib import Path
from logger import logger

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

class WhisperXTranscriber:
    """WhisperX文本转写器 - 基于WhisperX的音频转文本功能"""
    
    def __init__(self):
        """初始化转写器"""
        self.config = Config()
        self.model = None
        self.align_model = None
        self.diarize_model = None
        self._init_whisperx()
    
    def _init_whisperx(self):
        """初始化WhisperX模型"""
        try:
            logger.info("正在初始化WhisperX转写模型...")
            
            # 添加WhisperX路径到系统路径
            whisperx_path = os.path.abspath(self.config.WHISPERX_PATH)
            if whisperx_path not in sys.path:
                sys.path.insert(0, whisperx_path)
            
            # 检测计算设备
            device_info = self._detect_compute_device()
            logger.info(f"计算设备检测: {device_info}")
            
            # 导入WhisperX
            import whisperx
            
            # 确定设备
            device = self._get_device()
            logger.info(f"使用计算设备: {device}")
            
            # 智能选择计算类型
            compute_type = self._get_optimal_compute_type(device)
            logger.info(f"选择计算类型: {compute_type}")
            
            # 初始化转写模型
            logger.info(f"正在加载Whisper模型: {self.config.WHISPER_MODEL}")
            self.model = whisperx.load_model(
                self.config.WHISPER_MODEL, 
                device, 
                compute_type=compute_type,
                language=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else None
            )
            
            # 初始化对齐模型
            if self.config.ENABLE_ALIGNMENT:
                logger.info(f"正在加载对齐模型: {self.config.ALIGNMENT_MODEL}")
                self.align_model, self.align_metadata = whisperx.load_align_model(
                    language_code=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else 'en',
                    device=device,
                    model_name=self.config.ALIGNMENT_MODEL
                )
            
            # 初始化说话人分离模型
            if self.config.ENABLE_DIARIZATION and self.config.HF_TOKEN:
                logger.info(f"正在加载说话人分离模型: {self.config.DIARIZATION_MODEL}")
                self.diarize_model = whisperx.DiarizationPipeline(
                    use_auth_token=self.config.HF_TOKEN,
                    device=device
                )
            
            # 获取模型实际使用的设备
            actual_device = self._get_model_device()
            
            logger.info(f"WhisperX初始化成功")
            logger.info(f"转写模型: {self.config.WHISPER_MODEL}")
            logger.info(f"计算精度: {compute_type}")
            logger.info(f"语言设置: {self.config.WHISPER_LANGUAGE}")
            logger.info(f"对齐模型: {'启用' if self.config.ENABLE_ALIGNMENT else '禁用'}")
            logger.info(f"说话人分离: {'启用' if self.config.ENABLE_DIARIZATION else '禁用'}")
            logger.info(f"模型运行设备: {actual_device}")
            
        except Exception as e:
            logger.error(f"WhisperX初始化失败: {e}")
            raise
    
    def _detect_compute_device(self) -> str:
        """检测可用的计算设备"""
        try:
            import torch
            
            # 检测CUDA
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                cuda_version = torch.version.cuda
                return f"GPU可用 - 设备数量: {gpu_count}, 主GPU: {gpu_name}, CUDA版本: {cuda_version}"
            
            # 检测MPS (Apple Silicon)
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "MPS可用 - Apple Silicon GPU加速"
            
            # CPU only
            else:
                cpu_count = torch.get_num_threads()
                return f"仅CPU可用 - 线程数: {cpu_count}"
                
        except ImportError:
            return "PyTorch未安装，无法检测设备"
        except Exception as e:
            return f"设备检测失败: {str(e)}"
    
    def _get_device(self) -> str:
        """获取要使用的设备"""
        if self.config.WHISPER_DEVICE != 'auto':
            return self.config.WHISPER_DEVICE
        
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        except:
            return "cpu"
    
    def _get_model_device(self) -> str:
        """获取模型实际使用的设备"""
        try:
            import torch
            
            if torch.cuda.is_available():
                current_device = torch.cuda.current_device()
                device_name = torch.cuda.get_device_name(current_device)
                return f"CUDA设备: cuda:{current_device} ({device_name})"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "设备: MPS (Apple Silicon)"
            else:
                return "设备: CPU"
                
        except Exception as e:
            return f"无法获取设备信息: {str(e)}"
    
    def _get_current_device_usage(self) -> str:
        """获取当前设备使用情况"""
        try:
            import torch
            
            if torch.cuda.is_available():
                device_id = torch.cuda.current_device()
                device_name = torch.cuda.get_device_name(device_id)
                
                # 获取GPU内存使用情况
                memory_allocated = torch.cuda.memory_allocated(device_id) / 1024**3  # GB
                memory_total = torch.cuda.get_device_properties(device_id).total_memory / 1024**3  # GB
                
                return f"GPU cuda:{device_id} ({device_name}) - 内存: {memory_allocated:.1f}GB/{memory_total:.1f}GB"
                
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "MPS (Apple Silicon GPU)"
                
            else:
                # CPU使用情况
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                memory_used = memory_info.used / 1024**3  # GB
                memory_total = memory_info.total / 1024**3  # GB
                
                return f"CPU - 使用率: {cpu_percent:.1f}%, 内存: {memory_used:.1f}GB/{memory_total:.1f}GB"
                
        except ImportError as e:
            return f"缺少依赖库: {str(e)}"
        except Exception as e:
            return f"获取设备使用情况失败: {str(e)}"
    
    def transcribe_audio(self, audio_path: str, timeout: int = 7200) -> dict:
        """
        转写音频文件
        
        Args:
            audio_path (str): 音频文件路径
            timeout (int): 处理超时时间（秒），默认2小时
            
        Returns:
            dict: 转写结果
        """
        try:
            # 验证文件存在
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_path}")
            
            logger.info(f"开始转写音频: {audio_path}")
            
            # 获取音频基本信息
            file_info = self._get_audio_info(audio_path)
            total_duration = file_info['duration']
            
            logger.info(f"音频基本信息: 时长={total_duration:.2f}秒 ({total_duration/60:.1f}分钟), "
                       f"大小={file_info['file_size_mb']:.1f}MB")
            
            # 估算处理时间
            estimated_time = total_duration * 0.3  # 估算30%的处理时间
            logger.info(f"预估处理时间: {estimated_time:.1f}秒 ({estimated_time/60:.1f}分钟)")
            
            # 显示当前设备使用情况
            current_device = self._get_current_device_usage()
            logger.info(f"当前计算设备: {current_device}")
            
            # 设置超时处理
            start_time = time.time()
            result = self._transcribe_with_timeout(audio_path, timeout)
            
            # 记录处理时间
            process_time = time.time() - start_time
            logger.info(f"转写处理完成，实际耗时: {process_time:.1f}秒 ({process_time/60:.1f}分钟)")
            
            # 显示处理完成后的设备状态
            final_device = self._get_current_device_usage()
            logger.info(f"处理完成后设备状态: {final_device}")
            
            # 组合完整结果
            transcribe_result = {
                'text': result.get('text', ''),
                'language': result.get('language', 'unknown'),
                'segments': result.get('segments', []),
                'segments_count': len(result.get('segments', [])),
                'confidence_avg': result.get('confidence_avg', 0),
                'word_count': len(result.get('text', '').split()),
                'speakers': result.get('speakers', []),
                'effective_voice': result.get('effective_voice', total_duration),
                'total_voice': total_duration,
                'processing_time': process_time,
                'file_info': file_info
            }
            
            logger.info(f"转写完成: 文本长度={len(transcribe_result['text'])}字符, "
                       f"段落数={transcribe_result['segments_count']}, "
                       f"语言={transcribe_result['language']}")
            
            return transcribe_result
            
        except Exception as e:
            logger.error(f"音频转写失败: {e}")
            raise
    
    def _transcribe_with_timeout(self, audio_path: str, timeout: int) -> dict:
        """带超时的转写处理"""
        # 检查是否为Windows系统
        is_windows = platform.system().lower() == 'windows'
        
        if is_windows or not hasattr(signal, 'SIGALRM'):
            # Windows系统使用线程池
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._do_transcribe, audio_path)
                try:
                    return future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"音频转写超时（超过{timeout}秒）")
        else:
            # Unix/Linux系统使用信号
            def timeout_handler(signum, frame):
                raise TimeoutError(f"音频转写超时（超过{timeout}秒）")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            try:
                return self._do_transcribe(audio_path)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
    
    def _do_transcribe(self, audio_path: str) -> dict:
        """执行实际的转写处理"""
        import whisperx
        
        logger.info("正在进行音频转写...")
        
        # 加载音频
        audio = whisperx.load_audio(audio_path)
        
        # Step 1: 转写
        logger.info("Step 1: 执行语音识别...")
        result = self.model.transcribe(
            audio, 
            batch_size=self.config.WHISPER_BATCH_SIZE,
            language=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else None
        )
        
        # 提取文本和语言
        text = ' '.join([segment['text'] for segment in result['segments']])
        language = result.get('language', 'unknown')
        
        logger.info(f"识别语言: {language}")
        logger.info(f"转写文本长度: {len(text)}字符")
        
        # Step 2: 语言对齐（可选）
        if self.config.ENABLE_ALIGNMENT and self.align_model:
            logger.info("Step 2: 执行语言对齐...")
            result = whisperx.align(
                result['segments'], 
                self.align_model, 
                self.align_metadata, 
                audio, 
                self._get_device()
            )
        
        # Step 3: 说话人分离（可选）
        speakers = []
        if self.config.ENABLE_DIARIZATION and self.diarize_model:
            logger.info("Step 3: 执行说话人分离...")
            diarize_segments = self.diarize_model(
                audio,
                min_speakers=self.config.MIN_SPEAKERS,
                max_speakers=self.config.MAX_SPEAKERS
            )
            result = whisperx.assign_word_speakers(diarize_segments, result)
            
            # 提取说话人信息
            speakers = list(set([segment.get('speaker', 'UNKNOWN') 
                               for segment in result['segments'] 
                               if segment.get('speaker')]))
        
        # 计算平均置信度
        confidences = []
        for segment in result['segments']:
            if 'words' in segment:
                for word in segment['words']:
                    if 'score' in word:
                        confidences.append(word['score'])
            elif 'score' in segment:
                confidences.append(segment['score'])
        
        confidence_avg = sum(confidences) / len(confidences) if confidences else 0
        
        # 计算有效语音时长
        effective_voice = 0
        for segment in result['segments']:
            if 'start' in segment and 'end' in segment:
                effective_voice += segment['end'] - segment['start']
        
        return {
            'text': text,
            'language': language,
            'segments': result['segments'],
            'confidence_avg': confidence_avg,
            'speakers': speakers,
            'effective_voice': effective_voice
        }
    
    def _get_audio_info(self, audio_path: str) -> dict:
        """获取音频文件基本信息"""
        try:
            # 使用librosa获取音频信息
            import librosa
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
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'whisper_model': self.config.WHISPER_MODEL,
            'language': self.config.WHISPER_LANGUAGE,
            'device': self._get_device(),
            'batch_size': self.config.WHISPER_BATCH_SIZE,
            'compute_type': self.config.WHISPER_COMPUTE_TYPE,
            'alignment_enabled': self.config.ENABLE_ALIGNMENT,
            'diarization_enabled': self.config.ENABLE_DIARIZATION,
            'alignment_model': self.config.ALIGNMENT_MODEL if self.config.ENABLE_ALIGNMENT else None,
            'diarization_model': self.config.DIARIZATION_MODEL if self.config.ENABLE_DIARIZATION else None
        }
    
    def _get_optimal_compute_type(self, device: str) -> str:
        """智能选择最优计算类型"""
        try:
            # 如果配置明确指定了计算类型且不是auto，先尝试使用配置的类型
            if self.config.WHISPER_COMPUTE_TYPE != 'auto':
                config_compute_type = self.config.WHISPER_COMPUTE_TYPE
                
                # 测试配置的计算类型是否可用
                if self._test_compute_type(device, config_compute_type):
                    logger.info(f"使用配置的计算类型: {config_compute_type}")
                    return config_compute_type
                else:
                    logger.warning(f"配置的计算类型 {config_compute_type} 不支持，将自动选择")
            
            # 自动选择最优计算类型
            if device == 'cpu':
                logger.info("CPU设备，使用 float32")
                return 'float32'
            
            # GPU设备，按优先级测试
            compute_types = ['float16', 'float32', 'int8']
            
            for compute_type in compute_types:
                if self._test_compute_type(device, compute_type):
                    logger.info(f"自动选择计算类型: {compute_type}")
                    return compute_type
            
            # 如果都不支持，回退到float32
            logger.warning("所有计算类型测试失败，回退到 float32")
            return 'float32'
            
        except Exception as e:
            logger.error(f"计算类型选择失败: {e}，使用默认 float32")
            return 'float32'
    
    def _test_compute_type(self, device: str, compute_type: str) -> bool:
        """测试指定的计算类型是否支持"""
        try:
            logger.info(f"测试计算类型: {compute_type} (设备: {device})")
            
            # 导入必要的库
            from faster_whisper import WhisperModel
            
            # 尝试创建一个小模型来测试
            test_model = WhisperModel(
                "tiny",  # 使用最小的模型进行测试
                device=device,
                compute_type=compute_type
            )
            
            # 如果创建成功，清理模型并返回True
            del test_model
            logger.info(f"计算类型 {compute_type} 测试通过")
            return True
            
        except ValueError as e:
            if "float16 compute type" in str(e):
                logger.warning(f"计算类型 {compute_type} 不支持: {e}")
            else:
                logger.warning(f"计算类型 {compute_type} 测试失败: {e}")
            return False
        except Exception as e:
            logger.warning(f"计算类型 {compute_type} 测试异常: {e}")
            return False 