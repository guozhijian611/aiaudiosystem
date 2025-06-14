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
import numpy as np

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
                try:
                    logger.info(f"正在加载对齐模型: {self.config.ALIGNMENT_MODEL}")
                    self.align_model, self.align_metadata = whisperx.load_align_model(
                        language_code=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else 'en',
                        device=device,
                        model_name=self.config.ALIGNMENT_MODEL
                    )
                    logger.info("对齐模型加载成功")
                except Exception as e:
                    logger.warning(f"对齐模型加载失败: {e}")
                    logger.warning("将禁用对齐功能，继续使用其他功能")
                    self.align_model = None
            else:
                logger.info("对齐功能已禁用")
                self.align_model = None
            
            # 初始化说话人分离模型
            if self.config.ENABLE_DIARIZATION and self.config.HF_TOKEN:
                try:
                    logger.info(f"正在加载说话人分离模型: {self.config.DIARIZATION_MODEL}")
                    # 直接从diarize模块导入DiarizationPipeline
                    from whisperx.diarize import DiarizationPipeline
                    self.diarize_model = DiarizationPipeline(
                        model_name=self.config.DIARIZATION_MODEL,
                        use_auth_token=self.config.HF_TOKEN,
                        device=device
                    )
                    logger.info("说话人分离模型加载成功")
                except Exception as e:
                    logger.warning(f"说话人分离模型加载失败: {e}")
                    logger.warning("将禁用说话人分离功能，继续使用其他功能")
                    self.diarize_model = None
            else:
                if not self.config.ENABLE_DIARIZATION:
                    logger.info("说话人分离功能已禁用")
                elif not self.config.HF_TOKEN:
                    logger.warning("未配置HF_TOKEN，无法使用说话人分离功能")
                self.diarize_model = None
            
            # 获取模型实际使用的设备
            actual_device = self._get_model_device()
            
            logger.info(f"WhisperX初始化成功")
            logger.info(f"转写模型: {self.config.WHISPER_MODEL}")
            logger.info(f"计算精度: {compute_type}")
            logger.info(f"语言设置: {self.config.WHISPER_LANGUAGE}")
            logger.info(f"对齐模型: {'启用' if self.align_model else '禁用'}")
            logger.info(f"说话人分离: {'启用' if self.diarize_model else '禁用'}")
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
                try:
                    import psutil
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory_info = psutil.virtual_memory()
                    memory_used = memory_info.used / 1024**3  # GB
                    memory_total = memory_info.total / 1024**3  # GB
                    
                    return f"CPU - 使用率: {cpu_percent:.1f}%, 内存: {memory_used:.1f}GB/{memory_total:.1f}GB"
                except ImportError:
                    return "CPU - 无法获取详细信息（缺少psutil）"
                
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
                'file_info': file_info,
                # 添加模型和设备信息
                'whisper_model': self.config.WHISPER_MODEL,
                'compute_device': self._get_device(),
                'alignment_enabled': bool(self.align_model),
                'diarization_enabled': bool(self.diarize_model)
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
        
        # 获取音频信息
        file_info = self._get_audio_info(audio_path)
        audio_duration = file_info['duration']
        
        # 清理GPU内存
        self._clear_gpu_memory()
        
        # 检查内存使用情况
        memory_info = self._get_memory_usage()
        logger.info(f"转写前内存状态: {memory_info}")
        
        # 判断是否需要拆分音频
        device = self._get_device()
        should_split = self._should_split_audio(audio_duration, device, memory_info)
        
        if should_split:
            logger.info(f"音频时长 {audio_duration:.1f}秒，将进行分块处理")
            return self._transcribe_with_splitting(audio_path, whisperx)
        else:
            logger.info(f"音频时长 {audio_duration:.1f}秒，进行整体处理")
            return self._transcribe_whole_audio(audio_path, whisperx)
    
    def _should_split_audio(self, duration: float, device: str, memory_info: dict) -> bool:
        """判断是否需要拆分音频"""
        # 强制拆分的条件
        max_duration = self.config.MAX_AUDIO_DURATION
        if duration > max_duration:
            logger.info(f"音频超过最大时长限制 {max_duration}秒，强制拆分")
            return True
        
        # GPU内存不足时拆分
        if device == 'cuda' and memory_info.get('type') == 'GPU':
            free_memory = memory_info.get('free', 0)
            if free_memory < 2.0:  # 少于2GB空闲内存
                logger.info(f"GPU空闲内存不足 {free_memory:.1f}GB，建议拆分")
                return True
        
        # 长音频建议拆分
        if duration > 1800:  # 30分钟以上
            logger.info(f"音频较长 {duration/60:.1f}分钟，建议拆分处理")
            return True
        
        return False
    
    def _transcribe_whole_audio(self, audio_path: str, whisperx) -> dict:
        """整体转写音频"""
        try:
            # 加载音频
            audio = whisperx.load_audio(audio_path)
            
            # 获取设备和批处理大小
            device = self._get_device()
            file_info = self._get_audio_info(audio_path)
            batch_size = self._get_optimal_batch_size(device, file_info['duration'])
            
            logger.info(f"使用批处理大小: {batch_size}")
            
            # Step 1: 转写
            logger.info("Step 1: 执行语音识别...")
            result = self._transcribe_with_fallback(audio, batch_size)
            
            # 提取文本和语言
            text = ' '.join([segment['text'] for segment in result['segments']])
            language = result.get('language', 'unknown')
            
            logger.info(f"识别语言: {language}")
            logger.info(f"转写文本长度: {len(text)}字符")
            
            # Step 2: 语言对齐（可选）
            if self.align_model:
                try:
                    logger.info("Step 2: 执行语言对齐...")
                    result = whisperx.align(
                        result['segments'], 
                        self.align_model, 
                        self.align_metadata, 
                        audio, 
                        self._get_device()
                    )
                    logger.info("语言对齐完成")
                except Exception as e:
                    logger.warning(f"语言对齐失败: {e}")
                    logger.warning("跳过对齐步骤，继续处理")
            else:
                logger.info("Step 2: 跳过语言对齐（已禁用）")
            
            # Step 3: 说话人分离（可选）
            speakers = []
            if self.diarize_model:
                try:
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
                    logger.info(f"说话人分离完成，检测到 {len(speakers)} 个说话人")
                except Exception as e:
                    logger.warning(f"说话人分离失败: {e}")
                    logger.warning("跳过说话人分离步骤，继续处理")
            else:
                logger.info("Step 3: 跳过说话人分离（已禁用）")
            
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
            
        except Exception as e:
            logger.error(f"整体转写失败: {e}")
            raise
    
    def _transcribe_with_splitting(self, audio_path: str, whisperx) -> dict:
        """分块转写音频"""
        try:
            logger.info("开始分块转写处理...")
            
            # 加载完整音频获取基本信息
            audio = whisperx.load_audio(audio_path)
            file_info = self._get_audio_info(audio_path)
            total_duration = file_info['duration']
            
            # 计算分块大小
            chunk_duration = min(self.config.CHUNK_DURATION, 300)  # 最大5分钟一块
            chunk_samples = int(chunk_duration * file_info['sample_rate'])
            
            logger.info(f"音频总时长: {total_duration:.1f}秒")
            logger.info(f"分块大小: {chunk_duration}秒")
            
            # 分块处理
            all_segments = []
            all_speakers = set()
            total_effective_voice = 0
            confidences = []
            detected_language = 'unknown'
            
            num_chunks = int(np.ceil(len(audio) / chunk_samples))
            logger.info(f"总共分为 {num_chunks} 块")
            
            for i in range(num_chunks):
                start_sample = i * chunk_samples
                end_sample = min((i + 1) * chunk_samples, len(audio))
                chunk_audio = audio[start_sample:end_sample]
                
                chunk_start_time = start_sample / file_info['sample_rate']
                chunk_end_time = end_sample / file_info['sample_rate']
                
                logger.info(f"处理第 {i+1}/{num_chunks} 块 ({chunk_start_time:.1f}s - {chunk_end_time:.1f}s)")
                
                # 清理GPU内存
                self._clear_gpu_memory()
                
                try:
                    # 转写当前块
                    chunk_result = self._transcribe_chunk(chunk_audio, chunk_start_time, whisperx)
                    
                    # 合并结果
                    if chunk_result['segments']:
                        all_segments.extend(chunk_result['segments'])
                        total_effective_voice += chunk_result.get('effective_voice', 0)
                        
                        # 收集置信度
                        for segment in chunk_result['segments']:
                            if 'words' in segment:
                                for word in segment['words']:
                                    if 'score' in word:
                                        confidences.append(word['score'])
                            elif 'score' in segment:
                                confidences.append(segment['score'])
                        
                        # 收集说话人
                        chunk_speakers = chunk_result.get('speakers', [])
                        all_speakers.update(chunk_speakers)
                        
                        # 记录检测到的语言
                        if detected_language == 'unknown':
                            detected_language = chunk_result.get('language', 'unknown')
                    
                    logger.info(f"第 {i+1} 块处理完成，段落数: {len(chunk_result.get('segments', []))}")
                    
                except Exception as e:
                    logger.error(f"第 {i+1} 块处理失败: {e}")
                    # 继续处理下一块
                    continue
            
            # 合并所有文本
            full_text = ' '.join([segment['text'] for segment in all_segments])
            confidence_avg = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"分块转写完成:")
            logger.info(f"- 总段落数: {len(all_segments)}")
            logger.info(f"- 文本长度: {len(full_text)}字符")
            logger.info(f"- 检测语言: {detected_language}")
            logger.info(f"- 说话人数: {len(all_speakers)}")
            
            return {
                'text': full_text,
                'language': detected_language,
                'segments': all_segments,
                'confidence_avg': confidence_avg,
                'speakers': list(all_speakers),
                'effective_voice': total_effective_voice
            }
            
        except Exception as e:
            logger.error(f"分块转写失败: {e}")
            raise
    
    def _transcribe_chunk(self, chunk_audio, start_time_offset: float, whisperx) -> dict:
        """转写单个音频块"""
        try:
            # 获取设备和批处理大小
            device = self._get_device()
            chunk_duration = len(chunk_audio) / 16000  # 假设16kHz采样率
            batch_size = self._get_optimal_batch_size(device, chunk_duration)
            
            # 转写
            result = self._transcribe_with_fallback(chunk_audio, batch_size)
            
            # 调整时间戳
            for segment in result['segments']:
                if 'start' in segment:
                    segment['start'] += start_time_offset
                if 'end' in segment:
                    segment['end'] += start_time_offset
                
                # 调整词级时间戳
                if 'words' in segment:
                    for word in segment['words']:
                        if 'start' in word:
                            word['start'] += start_time_offset
                        if 'end' in word:
                            word['end'] += start_time_offset
            
            # 计算有效语音时长
            effective_voice = 0
            for segment in result['segments']:
                if 'start' in segment and 'end' in segment:
                    effective_voice += segment['end'] - segment['start']
            
            return {
                'segments': result['segments'],
                'language': result.get('language', 'unknown'),
                'effective_voice': effective_voice,
                'speakers': []  # 分块处理暂不支持说话人分离
            }
            
        except Exception as e:
            logger.error(f"音频块转写失败: {e}")
            return {
                'segments': [],
                'language': 'unknown',
                'effective_voice': 0,
                'speakers': []
            }
    
    def _transcribe_with_fallback(self, audio, batch_size: int) -> dict:
        """带回退机制的转写"""
        device = self._get_device()
        
        try:
            # 尝试使用当前设备和批处理大小
            logger.info(f"尝试转写: 设备={device}, 批处理={batch_size}")
            result = self.model.transcribe(
                audio, 
                batch_size=batch_size,
                language=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else None
            )
            return result
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.warning(f"GPU内存不足: {e}")
                
                # 尝试减小批处理大小
                if batch_size > 1:
                    new_batch_size = max(1, batch_size // 2)
                    logger.info(f"尝试减小批处理大小到 {new_batch_size}")
                    self._clear_gpu_memory()
                    
                    try:
                        result = self.model.transcribe(
                            audio, 
                            batch_size=new_batch_size,
                            language=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else None
                        )
                        return result
                    except RuntimeError as e2:
                        if "out of memory" in str(e2).lower():
                            logger.warning(f"减小批处理大小仍然内存不足: {e2}")
                        else:
                            raise e2
                
                # 如果是GPU，尝试切换到CPU
                if device == 'cuda':
                    logger.warning("GPU内存不足，尝试切换到CPU处理")
                    return self._fallback_to_cpu(audio)
                else:
                    raise e
            else:
                raise e
        except Exception as e:
            logger.error(f"转写过程中出现未知错误: {e}")
            raise e
    
    def _fallback_to_cpu(self, audio) -> dict:
        """回退到CPU处理"""
        try:
            logger.info("正在切换到CPU模式...")
            
            # 重新初始化CPU模型
            import whisperx
            cpu_model = whisperx.load_model(
                self.config.WHISPER_MODEL,
                device="cpu",
                compute_type="float32",
                language=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else None
            )
            
            # 使用较小的批处理大小
            cpu_batch_size = max(1, self.config.WHISPER_BATCH_SIZE // 4)
            logger.info(f"CPU模式批处理大小: {cpu_batch_size}")
            
            result = cpu_model.transcribe(
                audio,
                batch_size=cpu_batch_size,
                language=self.config.WHISPER_LANGUAGE if self.config.WHISPER_LANGUAGE != 'auto' else None
            )
            
            logger.info("CPU模式转写完成")
            return result
            
        except Exception as e:
            logger.error(f"CPU回退处理失败: {e}")
            raise e
    
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
            'alignment_enabled': bool(self.align_model),
            'diarization_enabled': bool(self.diarize_model),
            'alignment_model': self.config.ALIGNMENT_MODEL if self.align_model else None,
            'diarization_model': self.config.DIARIZATION_MODEL if self.diarize_model else None
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
    
    def _get_optimal_batch_size(self, device: str, audio_duration: float) -> int:
        """根据设备和音频长度智能选择批处理大小"""
        try:
            base_batch_size = self.config.WHISPER_BATCH_SIZE
            
            if device == 'cpu':
                # CPU设备，根据音频长度调整
                if audio_duration > 1800:  # 30分钟以上
                    return max(1, base_batch_size // 4)
                elif audio_duration > 600:  # 10分钟以上
                    return max(1, base_batch_size // 2)
                else:
                    return base_batch_size
            
            # GPU设备，检查显存
            import torch
            if torch.cuda.is_available():
                device_props = torch.cuda.get_device_properties(0)
                total_memory_gb = device_props.total_memory / 1024**3
                
                # 根据显存大小调整批处理
                if total_memory_gb < 4:  # 小于4GB显存
                    return max(1, base_batch_size // 8)
                elif total_memory_gb < 8:  # 小于8GB显存
                    return max(1, base_batch_size // 4)
                elif total_memory_gb < 12:  # 小于12GB显存
                    return max(1, base_batch_size // 2)
                else:
                    return base_batch_size
            
            return base_batch_size
            
        except Exception as e:
            logger.warning(f"批处理大小优化失败: {e}，使用默认值")
            return max(1, self.config.WHISPER_BATCH_SIZE // 2)
    
    def _clear_gpu_memory(self):
        """清理GPU内存"""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                logger.info("GPU内存已清理")
        except Exception as e:
            logger.warning(f"GPU内存清理失败: {e}")
    
    def _get_memory_usage(self) -> dict:
        """获取内存使用情况"""
        try:
            import torch
            
            if torch.cuda.is_available():
                device_id = torch.cuda.current_device()
                memory_allocated = torch.cuda.memory_allocated(device_id) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(device_id) / 1024**3
                memory_total = torch.cuda.get_device_properties(device_id).total_memory / 1024**3
                
                return {
                    'type': 'GPU',
                    'allocated': memory_allocated,
                    'reserved': memory_reserved,
                    'total': memory_total,
                    'free': memory_total - memory_reserved,
                    'usage_percent': (memory_reserved / memory_total) * 100
                }
            else:
                try:
                    import psutil
                    memory_info = psutil.virtual_memory()
                    return {
                        'type': 'CPU',
                        'used': memory_info.used / 1024**3,
                        'total': memory_info.total / 1024**3,
                        'free': memory_info.available / 1024**3,
                        'usage_percent': memory_info.percent
                    }
                except ImportError:
                    return {'type': 'Unknown', 'error': 'psutil not available'}
                    
        except Exception as e:
            return {'type': 'Error', 'error': str(e)}