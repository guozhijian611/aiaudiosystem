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
    
    def clean_audio(self, input_path: str, output_path: str = None) -> str:
        """
        清理音频文件
        
        Args:
            input_path (str): 输入音频文件路径
            output_path (str, optional): 输出音频文件路径
            
        Returns:
            str: 清理后的音频文件路径
            
        Raises:
            Exception: 清理失败时抛出异常
        """
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
            
            # 使用ClearVoice处理音频
            output_wav = self.clear_voice(input_path=input_path, online_write=False)
            
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