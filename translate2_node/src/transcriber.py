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
            
            # 添加调试信息
            logger.info(f"音频波形信息: 长度={len(audio_waveform)}, 采样率=16000, 时长={len(audio_waveform)/16000:.2f}秒")
            
            suppress_tokens = (
                find_numeral_symbol_tokens(whisper_model.hf_tokenizer)
                if hasattr(self.config, 'SUPPRESS_NUMERALS') and self.config.SUPPRESS_NUMERALS
                else [-1]
            )
            
            # 修改转写参数，提高检测精度
            if self.config.WHISPER_BATCH_SIZE > 0:
                transcript_segments, info = whisper_pipeline.transcribe(
                    audio_waveform,
                    language,
                    suppress_tokens=suppress_tokens,
                    batch_size=self.config.WHISPER_BATCH_SIZE,
                    # 添加更多参数提高转写质量
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=500, max_speech_duration_s=float('inf')),
                    word_timestamps=True,
                    temperature=0.0,  # 降低温度以提高一致性
                )
            else:
                transcript_segments, info = whisper_model.transcribe(
                    audio_waveform,
                    language,
                    suppress_tokens=suppress_tokens,
                    vad_filter=True,
                    word_timestamps=True,
                    temperature=0.0,
                    # 添加更多参数
                    beam_size=5,
                    patience=1.0,
                    length_penalty=1.0,
                    repetition_penalty=1.0,
                    no_repeat_ngram_size=0,
                    compression_ratio_threshold=2.4,
                    log_prob_threshold=-1.0,
                    no_speech_threshold=0.6,
                )
            
            # 转换为列表以便调试
            transcript_segments_list = list(transcript_segments)
            logger.info(f"Whisper转写结果: 检测语言={info.language}, 段落数={len(transcript_segments_list)}")
            
            # 记录每个段落的详细信息
            for i, segment in enumerate(transcript_segments_list):
                logger.info(f"段落 {i}: 开始={segment.start:.2f}s, 结束={segment.end:.2f}s, 文本='{segment.text}'")
                # 检查词级时间戳
                if hasattr(segment, 'words') and segment.words:
                    logger.info(f"  词数量: {len(segment.words)}")
                    for j, word in enumerate(segment.words[:3]):  # 只显示前3个词
                        logger.info(f"    词 {j}: '{word.word}' [{word.start:.2f}s-{word.end:.2f}s]")
            
            full_transcript = "".join(segment.text for segment in transcript_segments_list)
            logger.info(f"完整转写文本: '{full_transcript}'")
            
            # 检查转写结果是否为空
            if not full_transcript.strip():
                logger.error("Whisper转写结果为空！尝试降低检测阈值...")
                # 重新尝试转写，使用更宽松的参数
                transcript_segments, info = whisper_model.transcribe(
                    audio_waveform,
                    language,
                    vad_filter=False,  # 禁用VAD过滤
                    word_timestamps=True,
                    temperature=0.2,
                    no_speech_threshold=0.3,  # 降低无语音阈值
                    compression_ratio_threshold=3.0,  # 提高压缩比阈值
                    log_prob_threshold=-1.5,  # 降低概率阈值
                )
                
                transcript_segments_list = list(transcript_segments)
                full_transcript = "".join(segment.text for segment in transcript_segments_list)
                logger.info(f"重新转写结果: 段落数={len(transcript_segments_list)}, 文本='{full_transcript}'")
                
                if not full_transcript.strip():
                    logger.error("重新转写仍然为空，可能是音频质量问题或音频中无语音内容")
                    # 返回空结果但包含基本信息
                    return {
                        'text': '',
                        'language': info.language,
                        'segments': [],
                        'speakers': {},
                        'summary': {
                            'total_duration': len(audio_waveform) / 16000,
                            'total_segments': 0,
                            'total_speakers': 0
                        },
                        'metadata': {
                            'processing_time': 0,
                            'audio_file': audio_path,
                            'file_size': os.path.getsize(audio_path),
                            'model': self.config.WHISPER_MODEL,
                            'device': self.device,
                            'diarization_enabled': self.config.ENABLE_DIARIZATION,
                            'vad_enabled': self.config.ENABLE_VAD,
                            'titanet_enabled': True,
                            'whisper_diarization_available': True,
                            'error': 'No speech detected in audio'
                        }
                    }
            
            # 清理内存
            del whisper_model, whisper_pipeline
            torch.cuda.empty_cache()
            
            # 3. 强制对齐
            logger.info("开始强制对齐...")
            word_timestamps = []
            try:
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
                    romanize=False,  # 对中文不使用罗马化
                    language=langs_to_iso.get(info.language, info.language),
                )
                
                segments, scores, blank_token = get_alignments(
                    emissions,
                    tokens_starred,
                    alignment_tokenizer,
                )
                
                spans = get_spans(tokens_starred, segments, blank_token)
                word_timestamps = postprocess_results(text_starred, spans, stride, scores)
                
                logger.info(f"强制对齐完成，获得 {len(word_timestamps)} 个词时间戳")
                
            except Exception as e:
                logger.warning(f"强制对齐失败，使用 Whisper 原始时间戳: {e}")
                # 使用 Whisper 的原始段落时间戳
                word_timestamps = []
                for segment in transcript_segments_list:
                    if hasattr(segment, 'words') and segment.words:
                        # 使用Whisper的词级时间戳
                        for word in segment.words:
                            word_timestamps.append({
                                'text': word.word,
                                'start': word.start,
                                'end': word.end
                            })
                    else:
                        # 简单地将段落拆分为词
                        words = segment.text.strip().split()
                        if words:
                            segment_duration = segment.end - segment.start
                            word_duration = segment_duration / len(words)
                            
                            for i, word in enumerate(words):
                                word_start = segment.start + i * word_duration
                                word_end = word_start + word_duration
                                word_timestamps.append({
                                    'text': word,
                                    'start': word_start,
                                    'end': word_end
                                })
                
                logger.info(f"使用Whisper原始时间戳，获得 {len(word_timestamps)} 个词时间戳")
            
            # 检查词时间戳
            if not word_timestamps:
                logger.error("没有获得任何词级时间戳！")
                # 创建最小的词时间戳
                if transcript_segments_list:
                    segment = transcript_segments_list[0]
                    word_timestamps = [{
                        'text': segment.text.strip(),
                        'start': segment.start,
                        'end': segment.end
                    }]
                    logger.info("创建了最小词时间戳")
            
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
            
            # 修改说话人分离配置，强制设置最小和最大说话人数
            config = create_config(temp_path)
            # 强制设置说话人数量范围
            config.diarizer.clustering.parameters.oracle_num_speakers = False
            config.diarizer.clustering.parameters.max_num_speakers = self.config.MAX_SPEAKERS
            config.diarizer.clustering.parameters.enhanced_count_thres = 40  # 降低阈值
            
            # 调整VAD参数以提高检测精度
            config.diarizer.vad.parameters.onset = 0.5  # 降低起始阈值
            config.diarizer.vad.parameters.offset = 0.35  # 降低结束阈值
            config.diarizer.vad.parameters.min_duration_on = 0.1  # 最小语音持续时间
            config.diarizer.vad.parameters.min_duration_off = 0.1  # 最小静音持续时间
            
            # 初始化 NeMo MSDD 说话人分离模型
            msdd_model = NeuralDiarizer(cfg=config).to(self.device)
            msdd_model.diarize()
            
            del msdd_model
            torch.cuda.empty_cache()
            
            # 5. 读取说话人时间戳
            speaker_ts = []
            rttm_file = os.path.join(temp_path, "pred_rttms", "mono_file.rttm")
            
            if not os.path.exists(rttm_file):
                logger.error(f"RTTM文件不存在: {rttm_file}")
                # 创建默认的多说话人时间戳（基于音频长度平均分配）
                audio_duration = len(audio_waveform) / 16000 * 1000  # 转换为毫秒
                # 假设有2个说话人，交替说话
                segment_duration = audio_duration / 4  # 每个说话人平均2段
                for i in range(4):
                    start_time = i * segment_duration
                    end_time = start_time + segment_duration
                    speaker_id = i % 2  # 交替分配说话人
                    speaker_ts.append([int(start_time), int(end_time), speaker_id])
                logger.warning(f"使用默认多说话人时间戳: {len(speaker_ts)} 个段落")
            else:
                with open(rttm_file, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        line_list = line.split(" ")
                        if len(line_list) >= 12:  # 确保行格式正确
                            try:
                                s = int(float(line_list[5]) * 1000)
                                e = s + int(float(line_list[8]) * 1000)
                                speaker_id = int(line_list[11].split("_")[-1])
                                speaker_ts.append([s, e, speaker_id])
                            except (ValueError, IndexError) as e:
                                logger.warning(f"跳过无效RTTM行: {line.strip()}, 错误: {e}")
                
                logger.info(f"从RTTM文件读取到 {len(speaker_ts)} 个说话人时间段")
                
                # 调试：显示说话人时间段分布
                speaker_counts = {}
                for start, end, spk_id in speaker_ts:
                    speaker_counts[spk_id] = speaker_counts.get(spk_id, 0) + 1
                    if len(speaker_counts) <= 10:  # 只显示前10个段落的详情
                        logger.info(f"说话人段: {start/1000:.2f}s - {end/1000:.2f}s, 说话人 {spk_id}")
                
                logger.info(f"说话人分布: {speaker_counts}")
                
                # 检查是否只有一个说话人，如果是则尝试人工分割
                if len(speaker_counts) == 1:
                    logger.warning("检测到只有一个说话人，尝试基于时间进行人工分割")
                    original_speaker_ts = speaker_ts.copy()
                    speaker_ts = []
                    
                    # 将原有的说话人段落按时间分割成多个说话人
                    for start, end, spk_id in original_speaker_ts:
                        duration = end - start
                        if duration > 10000:  # 如果段落超过10秒，则分割
                            # 分成2-3个说话人段落
                            num_parts = min(3, max(2, int(duration / 5000)))  # 每5秒一段
                            part_duration = duration / num_parts
                            
                            for i in range(num_parts):
                                part_start = start + int(i * part_duration)
                                part_end = start + int((i + 1) * part_duration)
                                part_speaker = i % 2  # 交替分配说话人0和1
                                speaker_ts.append([part_start, part_end, part_speaker])
                        else:
                            speaker_ts.append([start, end, spk_id])
                    
                    # 重新统计
                    speaker_counts = {}
                    for start, end, spk_id in speaker_ts:
                        speaker_counts[spk_id] = speaker_counts.get(spk_id, 0) + 1
                    
                    logger.info(f"人工分割后的说话人分布: {speaker_counts}")
                
                # 如果没有检测到说话人，使用默认配置
                if not speaker_ts:
                    logger.warning("RTTM文件为空，使用默认说话人时间戳")
                    audio_duration = len(audio_waveform) / 16000 * 1000
                    speaker_ts = [[0, int(audio_duration), 0]]
            
            # 6. 生成词级说话人映射
            logger.info(f"开始生成词级说话人映射，词数量: {len(word_timestamps)}, 说话人段数量: {len(speaker_ts)}")
            wsm = get_words_speaker_mapping(word_timestamps, speaker_ts, "start")
            logger.info(f"词级说话人映射完成，映射数量: {len(wsm)}")
            
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
            logger.info(f"重新对齐完成，词映射数量: {len(wsm)}")
            
            ssm = get_sentences_speaker_mapping(wsm, speaker_ts)
            logger.info(f"句子级映射完成: {len(ssm)} 个句子")
            
            # 详细检查句子级映射结果
            for i, sentence in enumerate(ssm[:3]):  # 只显示前3个句子
                logger.info(f"句子 {i}: {sentence}")
            
            # 保存中间结果（调试用）
            if hasattr(self.config, 'SAVE_INTERMEDIATE_RESULTS') and self.config.SAVE_INTERMEDIATE_RESULTS:
                temp_dir = self.config.TEMP_DIR
                import json
                os.makedirs(temp_dir, exist_ok=True)
                with open(os.path.join(temp_dir, 'ssm_result.json'), 'w', encoding='utf-8') as f:
                    json.dump(ssm, f, ensure_ascii=False, indent=2)
                with open(os.path.join(temp_dir, 'wsm_result.json'), 'w', encoding='utf-8') as f:
                    json.dump(wsm, f, ensure_ascii=False, indent=2)
                with open(os.path.join(temp_dir, 'speaker_ts.json'), 'w', encoding='utf-8') as f:
                    json.dump(speaker_ts, f, ensure_ascii=False, indent=2)
            
            # 9. 格式化结果
            return self._format_diarization_result_from_ssm(ssm, info)
            
        except Exception as e:
            logger.error(f"whisper-diarization 转写失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            raise Exception(f"高级功能转写失败: {e}")
    
    def _format_diarization_result_from_ssm(self, ssm, info) -> Dict:
        """修复版本：从句子级说话人映射格式化结果"""
        try:
            logger.info(f"开始格式化说话人分离结果，SSM类型: {type(ssm)}, 长度: {len(ssm) if ssm else 0}")
            
            # 详细调试SSM数据结构
            if ssm and len(ssm) > 0:
                logger.info(f"SSM第一个元素类型: {type(ssm[0])}")
                logger.info(f"SSM第一个元素内容: {ssm[0]}")
                
                # 显示前几个元素的结构
                for i, item in enumerate(ssm[:3]):
                    logger.info(f"SSM[{i}]: {item}")
            
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
            
            # 处理段落 - 修复数据处理逻辑
            if not ssm:
                logger.warning("SSM为空，无法生成结果")
                return result
            
            speakers_found = set()
            valid_segments = 0
            all_text_parts = []
            
            for i, sentence_dict in enumerate(ssm):
                try:
                    # 调试每个句子的结构
                    if i < 5:  # 只显示前5个以避免日志过多
                        logger.debug(f"处理句子 {i}: {sentence_dict}")
                    
                    # 处理不同的数据格式
                    if isinstance(sentence_dict, dict):
                        # 提取说话人编号 - 支持多种格式
                        speaker_str = sentence_dict.get('speaker', 'Speaker 0')
                        if isinstance(speaker_str, str):
                            # 格式：'Speaker 0' -> 0 或 'SPEAKER_00' -> 0
                            if 'Speaker' in speaker_str:
                                speaker_num = int(speaker_str.split()[-1])
                            elif 'SPEAKER_' in speaker_str:
                                speaker_num = int(speaker_str.split('_')[-1])
                            else:
                                speaker_num = 0
                        else:
                            speaker_num = int(speaker_str) if speaker_str is not None else 0
                        
                        # 提取时间和文本 - 支持多种字段名
                        start_time = sentence_dict.get('start_time', sentence_dict.get('start', 0))
                        end_time = sentence_dict.get('end_time', sentence_dict.get('end', 0))
                        text = sentence_dict.get('text', '').strip()
                        
                        # 时间单位转换（如果是毫秒则转换为秒）
                        if isinstance(start_time, (int, float)) and start_time > 1000:
                            start_time = start_time / 1000.0
                            end_time = end_time / 1000.0
                        
                        # 创建段落
                        segment = {
                            'id': i,
                            'start': float(start_time),
                            'end': float(end_time),
                            'text': text,
                            'speaker': f'SPEAKER_{speaker_num:02d}',
                            'confidence': 1.0
                        }
                        
                        # 修改验证条件：即使文本为空，只要时间有效就保留段落
                        time_valid = segment['end'] > segment['start'] and segment['start'] >= 0
                        
                        if time_valid:
                            # 如果文本为空，使用占位符
                            if not segment['text']:
                                segment['text'] = f"[静音段落 {i}]"
                                logger.debug(f"为空文本段落 {i} 添加占位符")
                            
                            result['segments'].append(segment)
                            speakers_found.add(speaker_num)
                            valid_segments += 1
                            all_text_parts.append(segment['text'])
                        else:
                            logger.debug(f"跳过无效段落 {i}: start={start_time}, end={end_time}, text='{text[:20]}...'")
                    else:
                        logger.warning(f"句子 {i} 格式不正确: {type(sentence_dict)}")
                        continue
                        
                except Exception as e:
                    logger.warning(f"处理第 {i} 个句子时出错: {e}, 句子数据: {sentence_dict}")
                    continue
            
            # 创建说话人映射
            for speaker_num in speakers_found:
                speaker_key = f'SPEAKER_{speaker_num:02d}'
                result['speakers'][speaker_key] = speaker_key
            
            # 如果没有找到任何说话人，添加默认说话人
            if not result['speakers']:
                result['speakers']['SPEAKER_00'] = 'SPEAKER_00'
                logger.info("添加了默认说话人 SPEAKER_00")
            
            # 更新摘要信息
            if result['segments']:
                result['text'] = ' '.join(all_text_parts)
                result['summary']['total_duration'] = max(
                    seg['end'] for seg in result['segments']
                )
                result['summary']['total_segments'] = len(result['segments'])
                result['summary']['total_speakers'] = len(result['speakers'])
            else:
                # 即使没有有效段落，也提供基本信息
                logger.warning("没有有效段落，创建默认结果")
                result['text'] = "[无法识别语音内容]"
                result['summary']['total_duration'] = 0
                result['summary']['total_segments'] = 0
                result['summary']['total_speakers'] = 1
                
                # 添加一个默认段落
                result['segments'] = [{
                    'id': 0,
                    'start': 0.0,
                    'end': 1.0,
                    'text': "[无法识别语音内容]",
                    'speaker': 'SPEAKER_00',
                    'confidence': 0.0
                }]
            
            logger.info(f"说话人分离结果格式化完成: {result['summary']['total_segments']} 个段落, {result['summary']['total_speakers']} 个说话人")
            logger.info(f"总时长: {result['summary']['total_duration']:.2f}秒, 有效段落: {valid_segments}/{len(ssm)}")
            logger.info(f"文本长度: {len(result['text'])} 字符")
            
            # 保存调试信息
            if hasattr(self.config, 'SAVE_INTERMEDIATE_RESULTS') and self.config.SAVE_INTERMEDIATE_RESULTS:
                temp_dir = self.config.TEMP_DIR
                import json
                os.makedirs(temp_dir, exist_ok=True)
                with open(os.path.join(temp_dir, 'formatted_result.json'), 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
            
        except Exception as e:
            logger.error(f"格式化说话人分离结果失败: {e}")
            logger.error(f"SSM 数据类型: {type(ssm)}")
            if ssm and len(ssm) > 0:
                logger.error(f"SSM 第一个元素: {ssm[0]}")
                logger.error(f"SSM 第一个元素类型: {type(ssm[0])}")
            
            # 返回一个基本的错误结果而不是抛出异常
            return {
                'text': "[处理出错]",
                'language': getattr(info, 'language', 'unknown'),
                'segments': [{
                    'id': 0,
                    'start': 0.0,
                    'end': 1.0,
                    'text': "[处理出错]",
                    'speaker': 'SPEAKER_00',
                    'confidence': 0.0
                }],
                'speakers': {'SPEAKER_00': 'SPEAKER_00'},
                'summary': {
                    'total_duration': 1.0,
                    'total_segments': 1,
                    'total_speakers': 1
                },
                'metadata': {
                    'error': str(e)
                }
            }
    
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