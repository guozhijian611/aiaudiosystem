"""
音频清理模块
使用 ClearVoice 进行音频降噪和增强处理
"""

import os
import sys
from pathlib import Path
from config import Config
from logger import logger

class AudioCleaner:
    """音频清理器"""
    
    def __init__(self):
        self.config = Config()
        self.clear_voice = None
        self._init_clearvoice()
        
    def _init_clearvoice(self):
        """初始化ClearVoice模块"""
        try:
            # 添加ClearVoice路径到系统路径
            clearvoice_path = os.path.abspath(self.config.CLEARVOICE_PATH)
            if clearvoice_path not in sys.path:
                sys.path.insert(0, clearvoice_path)
            
            # 导入ClearVoice
            from clearvoice import ClearVoice
            
            # 初始化ClearVoice实例
            self.clear_voice = ClearVoice(
                task=self.config.CLEAR_TASK,
                model_names=[self.config.CLEAR_MODEL]
            )
            
            logger.info(f"ClearVoice初始化成功 - 模型: {self.config.CLEAR_MODEL}, 任务: {self.config.CLEAR_TASK}")
            
        except Exception as e:
            logger.error(f"ClearVoice初始化失败: {e}")
            raise
    
    def clean_audio(self, input_path: str, output_path: str = None, timeout: int = 3600) -> str:
        """
        清理音频文件
        
        Args:
            input_path (str): 输入音频文件路径
            output_path (str, optional): 输出音频文件路径
            timeout (int): 处理超时时间（秒），默认1小时
            
        Returns:
            str: 清理后的音频文件路径
            
        Raises:
            Exception: 清理失败时抛出异常
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"音频处理超时（超过{timeout}秒）")
        
        try:
            # 验证输入文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"音频文件不存在: {input_path}")
            
            # 生成输出文件路径
            if output_path is None:
                input_name = Path(input_path).stem
                output_path = os.path.join(
                    self.config.WORK_DIR, 
                    f"{input_name}_cleaned.{self.config.OUTPUT_FORMAT}"
                )
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"开始清理音频: {input_path} -> {output_path}")
            logger.info(f"设置处理超时: {timeout}秒")
            
            # 获取音频信息用于估算处理时间
            audio_info = self.get_audio_info(input_path)
            duration = audio_info.get('duration', 0)
            file_size_mb = audio_info.get('file_size_mb', 0)
            
            # 估算处理时间（经验值：约为音频时长的0.1-0.3倍）
            estimated_time = duration * 0.2  # 估算20%的处理时间
            logger.info(f"音频时长: {duration:.1f}秒 ({duration/60:.1f}分钟)")
            logger.info(f"文件大小: {file_size_mb:.1f}MB")
            logger.info(f"预估处理时间: {estimated_time:.1f}秒 ({estimated_time/60:.1f}分钟)")
            logger.info("注意: ClearVoice处理过程中不显示进度，请耐心等待...")
            
            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            try:
                # 使用ClearVoice处理音频
                logger.info("正在调用ClearVoice模型进行音频降噪...")
                logger.info("提示: 大文件处理可能需要较长时间，如果长时间无响应可能是内存不足")
                
                output_wav = self.clear_voice(input_path=input_path, online_write=False)
                
                # 记录处理时间
                process_time = time.time() - start_time
                logger.info(f"ClearVoice处理完成，实际耗时: {process_time:.1f}秒 ({process_time/60:.1f}分钟)")
                
            finally:
                # 取消超时信号
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            
            # 写入输出文件
            self.clear_voice.write(output_wav, output_path=output_path)
            
            # 验证输出文件是否创建成功
            if not os.path.exists(output_path):
                raise Exception("音频清理失败，输出文件未创建")
            
            # 检查文件大小
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception("音频清理失败，输出文件为空")
            
            logger.info(f"音频清理成功: {output_path} (大小: {self._format_size(file_size)})")
            return output_path
            
        except Exception as e:
            logger.error(f"音频清理失败: {str(e)}")
            # 清理可能存在的不完整文件
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logger.info(f"已清理不完整文件: {output_path}")
                except:
                    pass
            raise
    
    def batch_clean_audio(self, input_dir: str, output_dir: str) -> list:
        """
        批量清理音频文件
        
        Args:
            input_dir (str): 输入目录路径
            output_dir (str): 输出目录路径
            
        Returns:
            list: 成功处理的文件列表
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 支持的音频格式
            audio_extensions = {'.wav', '.mp3', '.flac', '.aac', '.ogg', '.aiff'}
            
            # 获取所有音频文件
            audio_files = []
            for file_path in Path(input_dir).rglob('*'):
                if file_path.suffix.lower() in audio_extensions:
                    audio_files.append(file_path)
            
            logger.info(f"找到 {len(audio_files)} 个音频文件待处理")
            
            # 批量处理
            processed_files = []
            for i, input_file in enumerate(audio_files, 1):
                try:
                    # 生成输出文件路径
                    relative_path = input_file.relative_to(input_dir)
                    output_file = Path(output_dir) / relative_path.with_suffix(f'.{self.config.OUTPUT_FORMAT}')
                    
                    logger.info(f"处理进度: {i}/{len(audio_files)} - {input_file.name}")
                    
                    # 清理音频
                    result_path = self.clean_audio(str(input_file), str(output_file))
                    processed_files.append(result_path)
                    
                except Exception as e:
                    logger.error(f"处理文件失败 {input_file}: {e}")
                    continue
            
            logger.info(f"批量处理完成，成功处理 {len(processed_files)} 个文件")
            return processed_files
            
        except Exception as e:
            logger.error(f"批量清理失败: {e}")
            raise
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        获取音频文件信息
        
        Args:
            audio_path (str): 音频文件路径
            
        Returns:
            dict: 音频信息
        """
        try:
            import librosa
            
            # 加载音频文件
            y, sr = librosa.load(audio_path, sr=None)
            
            # 计算时长
            duration = len(y) / sr
            
            # 获取文件大小
            file_size = os.path.getsize(audio_path)
            
            return {
                'file_path': audio_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'duration': round(duration, 2),
                'sample_rate': sr,
                'channels': 1 if len(y.shape) == 1 else y.shape[0],
                'samples': len(y)
            }
            
        except Exception as e:
            logger.error(f"获取音频信息失败: {e}")
            return {}
    
    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes (int): 字节大小
            
        Returns:
            str: 格式化后的大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def clean_audio_with_chunking(self, input_path: str, output_path: str = None, chunk_duration: int = None) -> str:
        """
        分块处理大音频文件
        
        Args:
            input_path (str): 输入音频文件路径
            output_path (str, optional): 输出音频文件路径
            chunk_duration (int, optional): 分块时长（秒）
            
        Returns:
            str: 清理后的音频文件路径
        """
        try:
            import librosa
            import soundfile as sf
            
            if chunk_duration is None:
                chunk_duration = self.config.CHUNK_DURATION
                
            logger.info(f"开始分块处理音频: 分块时长={chunk_duration}秒")
            
            # 加载音频文件
            y, sr = librosa.load(input_path, sr=None)
            total_duration = len(y) / sr
            chunk_samples = chunk_duration * sr
            
            logger.info(f"音频总时长: {total_duration:.2f}秒, 分块大小: {chunk_duration}秒")
            
            # 生成输出路径
            if output_path is None:
                input_name = Path(input_path).stem
                output_path = os.path.join(
                    self.config.WORK_DIR, 
                    f"{input_name}_cleaned.{self.config.OUTPUT_FORMAT}"
                )
            
                         # 分块处理
            import numpy as np
            processed_chunks = []
            chunk_count = int(np.ceil(len(y) / chunk_samples))
            
            for i in range(chunk_count):
                start_idx = i * chunk_samples
                end_idx = min((i + 1) * chunk_samples, len(y))
                chunk_data = y[start_idx:end_idx]
                
                # 保存临时块文件
                chunk_temp_path = f"{input_path}_chunk_{i}.wav"
                sf.write(chunk_temp_path, chunk_data, sr)
                
                # 处理块文件
                chunk_output_path = f"{output_path}_chunk_{i}.wav"
                logger.info(f"处理分块 {i+1}/{chunk_count}")
                
                cleaned_chunk_path = self.clean_audio(chunk_temp_path, chunk_output_path)
                
                # 加载处理后的块
                cleaned_chunk, _ = librosa.load(cleaned_chunk_path, sr=sr)
                processed_chunks.append(cleaned_chunk)
                
                # 清理临时文件
                try:
                    os.remove(chunk_temp_path)
                    os.remove(cleaned_chunk_path)
                except:
                    pass
            
            # 合并所有处理后的块
            final_audio = np.concatenate(processed_chunks)
            
            # 保存最终结果
            sf.write(output_path, final_audio, sr)
            
            logger.info(f"分块处理完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"分块处理失败: {e}")
            raise

    def cleanup_temp_files(self, temp_dir: str = None):
        """
        清理临时文件
        
        Args:
            temp_dir (str, optional): 临时目录路径
        """
        try:
            if temp_dir is None:
                temp_dir = self.config.TEMP_DIR
            
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                logger.info(f"已清理临时目录: {temp_dir}")
                
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")