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
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from logger import logger
import re

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
        self.use_script_mode = False
        self._init_device()
        self._init_whisper_diarization()
        self._init_model()
        
        logger.info(f"Whisper-Diarization 转写器初始化完成")
        logger.info(f"设备: {self.device}")
        logger.info(f"模型: {self.config.WHISPER_MODEL}")
        logger.info(f"说话人分离: {self.config.ENABLE_DIARIZATION}")
        logger.info(f"VAD启用: {self.config.ENABLE_VAD}")
        logger.info(f"TitaNet启用: {self.config.ENABLE_TITANET}")
        logger.info(f"脚本模式: {self.use_script_mode}")
    
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
                # 尝试直接导入 whisper-diarization 模块
                logger.info("尝试直接导入 whisper-diarization 模块")
                self.use_script_mode = False
                self._init_whisper_diarization_module()
            else:
                # 回退到基础 Whisper 实现
                logger.info("使用基础 Whisper 实现")
                self.use_script_mode = False
                self._init_fallback_model()
                
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            logger.info("尝试使用基础 Whisper 实现")
            self.use_script_mode = False
            self._init_fallback_model()
    
    def _init_fallback_model(self):
        """初始化基础 Whisper 模型"""
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
    
    def _init_whisper_diarization_module(self):
        """初始化 whisper-diarization 模块"""
        try:
            # 在导入前修复 Windows 兼容性问题
            self._apply_windows_compatibility_fix()
            
            # 添加 whisper-diarization 路径到 Python 路径
            sys.path.insert(0, self.whisper_diarization_path)
            
            # 尝试导入必要的模块（基于 Jupyter Notebook 教程）
            import faster_whisper
            from nemo.collections.asr.models.msdd_models import NeuralDiarizer
            from deepmultilingualpunctuation import PunctuationModel
            from ctc_forced_aligner import (
                load_alignment_model,
                generate_emissions,
                preprocess_text,
                get_alignments,
                get_spans,
                postprocess_results,
            )
            # 导入 helpers 模块
            from helpers import (
                create_config,
                get_words_speaker_mapping,
                get_realigned_ws_mapping_with_punctuation,
                get_sentences_speaker_mapping,
                langs_to_iso,
                punct_model_langs,
                find_numeral_symbol_tokens,
            )
            
            logger.info("成功导入 whisper-diarization 相关模块")
            
            # 标记为可用
            self.diarization_available = True
            
            # 同时初始化基础 Whisper 模型
            self._init_fallback_model()
            
            logger.info("whisper-diarization 功能初始化成功")
            
        except ImportError as e:
            logger.error(f"无法导入 whisper-diarization 模块: {e}")
            raise Exception("whisper-diarization 模块导入失败，无法使用高级功能")
        except Exception as e:
            logger.error(f"whisper-diarization 模块初始化失败: {e}")
            raise Exception(f"whisper-diarization 模块初始化失败: {e}")
    
    def _apply_windows_compatibility_fix(self):
        """应用 Windows 兼容性修复"""
        try:
            # 修复 signal.SIGKILL 问题
            import signal
            if not hasattr(signal, 'SIGKILL'):
                signal.SIGKILL = 9  # Windows 使用 9 作为终止信号
                logger.info("已修复 Windows signal.SIGKILL 兼容性问题")
            
            # 修复其他可能的 Windows 兼容性问题
            if platform.system() == 'Windows':
                # 确保环境变量正确设置
                os.environ['PYTHONPATH'] = os.pathsep.join([
                    os.environ.get('PYTHONPATH', ''),
                    self.whisper_diarization_path
                ]).strip(os.pathsep)
                
                logger.info("已应用 Windows 兼容性修复")
        except Exception as e:
            logger.warning(f"Windows 兼容性修复失败: {e}")
    
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
            
            # 执行转写 - 必须使用高级功能
            if hasattr(self, 'diarization_available') and self.config.ENABLE_DIARIZATION:
                result = self._transcribe_with_diarization_module(audio_path, timeout)
            else:
                raise Exception("高级功能不可用，无法进行转写")
            
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
                'diarization_enabled': hasattr(self, 'diarization_available') and self.config.ENABLE_DIARIZATION,
                'vad_enabled': self.config.ENABLE_VAD,
                'titanet_enabled': self.config.ENABLE_TITANET,
                'whisper_diarization_available': hasattr(self, 'diarization_available')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"音频转写失败: {e}")
            raise
    
    def _transcribe_with_diarization_module(self, audio_path: str, timeout: int = None) -> Dict:
        """使用 whisper-diarization 功能进行转写（基于官方 Jupyter Notebook）"""
        try:
            # 检查 HF_TOKEN
            if self.config.ENABLE_DIARIZATION and not self.config.HF_TOKEN:
                raise Exception("未配置 HF_TOKEN，说话人分离功能无法使用")
            
            # 设置 HF_TOKEN
            os.environ["HF_TOKEN"] = self.config.HF_TOKEN
            
            logger.info("使用 whisper-diarization 功能进行转写...")
            
            # 导入必要的模块
            import faster_whisper
            import torchaudio
            from nemo.collections.asr.models.msdd_models import NeuralDiarizer
            from deepmultilingualpunctuation import PunctuationModel
            from ctc_forced_aligner import (
                load_alignment_model,
                generate_emissions,
                preprocess_text,
                get_alignments,
                get_spans,
                postprocess_results,
            )
            from helpers import (
                create_config,
                get_words_speaker_mapping,
                get_realigned_ws_mapping_with_punctuation,
                get_sentences_speaker_mapping,
                langs_to_iso,
                punct_model_langs,
                find_numeral_symbol_tokens,
            )
            
            # 设置参数
            mtypes = {"cpu": "int8", "cuda": "float16"}
            
            # 处理语言参数
            language = self.config.WHISPER_LANGUAGE
            if language and language.lower() in ['auto', 'none', 'null', '']:
                language = None  # 让 Whisper 自动检测语言
            
            # 1. 音频预处理（人声分离）
            if self.config.ENABLE_VAD:
                # 使用 demucs 分离人声
                return_code = os.system(
                    f'python -m demucs.separate -n htdemucs --two-stems=vocals "{audio_path}" -o temp_outputs --device "{self.device}"'
                )
                
                if return_code != 0:
                    logger.warning("音频分离失败，使用原始音频")
                    vocal_target = audio_path
                else:
                    vocal_target = os.path.join(
                        "temp_outputs",
                        "htdemucs",
                        os.path.splitext(os.path.basename(audio_path))[0],
                        "vocals.wav",
                    )
            else:
                vocal_target = audio_path
            
            # 2. Whisper 转写
            logger.info("开始 Whisper 转写...")
            whisper_model = faster_whisper.WhisperModel(
                self.config.WHISPER_MODEL, 
                device=self.device, 
                compute_type=mtypes[self.device]
            )
            whisper_pipeline = faster_whisper.BatchedInferencePipeline(whisper_model)
            audio_waveform = faster_whisper.decode_audio(vocal_target)
            
            suppress_tokens = (
                find_numeral_symbol_tokens(whisper_model.hf_tokenizer)
                if hasattr(self.config, 'SUPPRESS_NUMERALS') and self.config.SUPPRESS_NUMERALS
                else [-1]
            )
            
            if self.config.WHISPER_BATCH_SIZE > 0:
                transcript_segments, info = whisper_pipeline.transcribe(
                    audio_waveform,
                    language,
                    suppress_tokens=suppress_tokens,
                    batch_size=self.config.WHISPER_BATCH_SIZE,
                )
            else:
                transcript_segments, info = whisper_model.transcribe(
                    audio_waveform,
                    language,
                    suppress_tokens=suppress_tokens,
                    vad_filter=True,
                )
            
            full_transcript = "".join(segment.text for segment in transcript_segments)
            
            # 清理内存
            del whisper_model, whisper_pipeline
            torch.cuda.empty_cache()
            
            # 3. 强制对齐
            logger.info("开始强制对齐...")
            alignment_model, alignment_tokenizer = load_alignment_model(
                self.device,
                dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            emissions, stride = generate_emissions(
                alignment_model,
                torch.from_numpy(audio_waveform)
                .to(alignment_model.dtype)
                .to(alignment_model.device),
                batch_size=self.config.WHISPER_BATCH_SIZE,
            )
            
            del alignment_model
            torch.cuda.empty_cache()
            
            tokens_starred, text_starred = preprocess_text(
                full_transcript,
                romanize=True,
                language=langs_to_iso.get(info.language, info.language),
            )
            
            segments, scores, blank_token = get_alignments(
                emissions,
                tokens_starred,
                alignment_tokenizer,
            )
            
            spans = get_spans(tokens_starred, segments, blank_token)
            word_timestamps = postprocess_results(text_starred, spans, stride, scores)
            
            # 4. 说话人分离
            logger.info("开始说话人分离...")
            # 转换音频为单声道
            ROOT = os.getcwd()
            temp_path = os.path.join(ROOT, "temp_outputs")
            os.makedirs(temp_path, exist_ok=True)
            torchaudio.save(
                os.path.join(temp_path, "mono_file.wav"),
                torch.from_numpy(audio_waveform).unsqueeze(0).float(),
                16000,
                channels_first=True,
            )
            
            # 初始化 NeMo MSDD 说话人分离模型
            msdd_model = NeuralDiarizer(cfg=create_config(temp_path)).to(self.device)
            msdd_model.diarize()
            
            del msdd_model
            torch.cuda.empty_cache()
            
            # 5. 读取说话人时间戳
            speaker_ts = []
            rttm_file = os.path.join(temp_path, "pred_rttms", "mono_file.rttm")
            with open(rttm_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line_list = line.split(" ")
                    s = int(float(line_list[5]) * 1000)
                    e = s + int(float(line_list[8]) * 1000)
                    speaker_ts.append([s, e, int(line_list[11].split("_")[-1])])
            
            # 6. 生成词级说话人映射
            wsm = get_words_speaker_mapping(word_timestamps, speaker_ts, "start")
            
            # 7. 标点符号恢复
            if info.language in punct_model_langs:
                logger.info("恢复标点符号...")
                punct_model = PunctuationModel(model="kredor/punctuate-all")
                words_list = list(map(lambda x: x["word"], wsm))
                labled_words = punct_model.predict(words_list, chunk_size=230)
                
                ending_puncts = ".?!"
                model_puncts = ".,;:!?"
                is_acronym = lambda x: re.fullmatch(r"\b(?:[a-zA-Z]\.){2,}", x)
                
                for word_dict, labeled_tuple in zip(wsm, labled_words):
                    word = word_dict["word"]
                    if (
                        word
                        and labeled_tuple[1] in ending_puncts
                        and (word[-1] not in model_puncts or is_acronym(word))
                    ):
                        word += labeled_tuple[1]
                        if word.endswith(".."):
                            word = word.rstrip(".")
                        word_dict["word"] = word
            else:
                logger.warning(f"语言 {info.language} 不支持标点符号恢复")
            
            # 8. 重新对齐和生成句子级说话人映射
            wsm = get_realigned_ws_mapping_with_punctuation(wsm)
            ssm = get_sentences_speaker_mapping(wsm, speaker_ts)
            
            # 9. 格式化结果
            return self._format_diarization_result_from_ssm(ssm, info)
            
        except Exception as e:
            logger.error(f"whisper-diarization 转写失败: {e}")
            raise Exception(f"高级功能转写失败: {e}")
    
    def _format_diarization_result_from_ssm(self, ssm, info) -> Dict:
        """从句子级说话人映射格式化结果"""
        result = {
            'text': '',
            'language': info.language,
            'segments': [],
            'speakers': {},
            'summary': {
                'total_duration': 0,
                'total_segments': 0,
                'total_speakers': 0
            }
        }
        
        # 处理段落
        for i, (speaker, sentence) in enumerate(ssm):
            segment = {
                'id': i,
                'start': sentence['start_time'] / 1000.0,  # 转换为秒
                'end': sentence['end_time'] / 1000.0,
                'text': sentence['text'].strip(),
                'speaker': f'SPEAKER_{speaker:02d}',
                'confidence': 1.0
            }
            result['segments'].append(segment)
            
            # 收集说话人信息
            speaker_key = f'SPEAKER_{speaker:02d}'
            if speaker_key not in result['speakers']:
                result['speakers'][speaker_key] = speaker_key
        
        # 更新摘要信息
        if result['segments']:
            result['text'] = ' '.join(seg['text'] for seg in result['segments'])
            result['summary']['total_duration'] = max(
                seg['end'] for seg in result['segments']
            )
            result['summary']['total_segments'] = len(result['segments'])
            result['summary']['total_speakers'] = len(result['speakers'])
        
        return result
    
    def _transcribe_with_whisper(self, audio_path: str, timeout: int = None) -> Dict:
        """使用基础 Whisper 进行转写"""
        try:
            # 执行转写
            logger.info("使用基础 Whisper 进行转写...")
            
            # 处理语言参数
            language = self.config.WHISPER_LANGUAGE
            if language and language.lower() in ['auto', 'none', 'null', '']:
                language = None  # 让 Whisper 自动检测语言
            
            result = self.model.transcribe(
                audio_path,
                language=language,
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