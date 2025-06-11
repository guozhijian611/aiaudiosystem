"""
音频提取模块
使用 FFmpeg 从视频文件中提取音频
"""

import os
import subprocess
import ffmpeg
from pathlib import Path
from config import Config
from logger import logger

class AudioExtractor:
    """音频提取器"""
    
    def __init__(self):
        self.config = Config()
        
    def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """
        从视频文件中提取音频
        
        Args:
            video_path (str): 视频文件路径
            output_path (str, optional): 输出音频文件路径
            
        Returns:
            str: 提取的音频文件路径
            
        Raises:
            Exception: 提取失败时抛出异常
        """
        try:
            # 验证输入文件是否存在
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            # 生成输出文件路径
            if output_path is None:
                video_name = Path(video_path).stem
                output_path = os.path.join(
                    self.config.WORK_DIR, 
                    f"{video_name}_extracted.{self.config.AUDIO_FORMAT}"
                )
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"开始提取音频: {video_path} -> {output_path}")
            
            # 使用 ffmpeg-python 提取音频
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                acodec='mp3' if self.config.AUDIO_FORMAT == 'mp3' else 'libmp3lame',
                audio_bitrate=self.config.AUDIO_BITRATE,
                ar=self.config.AUDIO_SAMPLE_RATE,
                threads=self.config.FFMPEG_THREADS
            )
            
            # 执行转换，覆盖已存在的文件
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # 验证输出文件是否创建成功
            if not os.path.exists(output_path):
                raise Exception("音频提取失败，输出文件未创建")
            
            # 检查文件大小
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception("音频提取失败，输出文件为空")
            
            logger.info(f"音频提取成功: {output_path} (大小: {self._format_size(file_size)})")
            return output_path
            
        except Exception as e:
            logger.error(f"音频提取失败: {str(e)}")
            # 清理可能存在的不完整文件
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logger.info(f"已清理不完整的输出文件: {output_path}")
                except:
                    pass
            raise
    
    def extract_audio_with_fallback(self, video_path: str, output_path: str = None) -> str:
        """
        使用备用方案提取音频（直接调用 ffmpeg 命令）
        
        Args:
            video_path (str): 视频文件路径
            output_path (str, optional): 输出音频文件路径
            
        Returns:
            str: 提取的音频文件路径
        """
        try:
            return self.extract_audio(video_path, output_path)
        except Exception as e:
            logger.warning(f"ffmpeg-python 提取失败，尝试直接调用 ffmpeg: {e}")
            return self._extract_with_command(video_path, output_path)
    
    def _extract_with_command(self, video_path: str, output_path: str = None) -> str:
        """
        直接调用 ffmpeg 命令提取音频
        
        Args:
            video_path (str): 视频文件路径
            output_path (str, optional): 输出音频文件路径
            
        Returns:
            str: 提取的音频文件路径
        """
        # 生成输出文件路径
        if output_path is None:
            video_name = Path(video_path).stem
            output_path = os.path.join(
                self.config.WORK_DIR, 
                f"{video_name}_extracted.{self.config.AUDIO_FORMAT}"
            )
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 构建 ffmpeg 命令
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # 不包含视频
            '-acodec', 'libmp3lame' if self.config.AUDIO_FORMAT == 'mp3' else 'copy',
            '-ab', self.config.AUDIO_BITRATE,
            '-ar', str(self.config.AUDIO_SAMPLE_RATE),
            '-threads', str(self.config.FFMPEG_THREADS),
            '-y',  # 覆盖输出文件
            output_path
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg 命令执行失败: {result.stderr}")
            
            # 验证输出文件
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("音频提取失败，输出文件未创建或为空")
            
            file_size = os.path.getsize(output_path)
            logger.info(f"音频提取成功: {output_path} (大小: {self._format_size(file_size)})")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise Exception("音频提取超时")
        except Exception as e:
            # 清理可能存在的不完整文件
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            raise
    
    def get_video_info(self, video_path: str) -> dict:
        """
        获取视频文件信息
        
        Args:
            video_path (str): 视频文件路径
            
        Returns:
            dict: 视频信息
        """
        try:
            probe = ffmpeg.probe(video_path)
            
            # 查找音频流
            audio_streams = [
                stream for stream in probe['streams'] 
                if stream['codec_type'] == 'audio'
            ]
            
            # 查找视频流
            video_streams = [
                stream for stream in probe['streams'] 
                if stream['codec_type'] == 'video'
            ]
            
            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'size': int(probe['format'].get('size', 0)),
                'has_audio': len(audio_streams) > 0,
                'has_video': len(video_streams) > 0,
                'audio_streams': len(audio_streams),
                'video_streams': len(video_streams)
            }
            
            # 音频信息
            if audio_streams:
                audio_stream = audio_streams[0]
                info['audio_codec'] = audio_stream.get('codec_name', 'unknown')
                info['audio_bitrate'] = int(audio_stream.get('bit_rate', 0))
                info['sample_rate'] = int(audio_stream.get('sample_rate', 0))
            
            # 视频信息
            if video_streams:
                video_stream = video_streams[0]
                info['video_codec'] = video_stream.get('codec_name', 'unknown')
                info['width'] = int(video_stream.get('width', 0))
                info['height'] = int(video_stream.get('height', 0))
            
            return info
            
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return {}
    
    def validate_video_file(self, video_path: str) -> bool:
        """
        验证视频文件是否有效
        
        Args:
            video_path (str): 视频文件路径
            
        Returns:
            bool: 文件是否有效
        """
        try:
            info = self.get_video_info(video_path)
            return info.get('has_audio', False) or info.get('has_video', False)
        except:
            return False
    
    def validate_audio_file(self, audio_path: str) -> bool:
        """
        验证音频文件是否有效
        
        Args:
            audio_path (str): 音频文件路径
            
        Returns:
            bool: 文件是否有效
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                logger.error(f"音频文件不存在: {audio_path}")
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                logger.error(f"音频文件为空: {audio_path}")
                return False
            
            # 使用ffmpeg探测音频文件信息
            info = self.get_video_info(audio_path)  # get_video_info也可以处理音频文件
            
            # 验证是否包含音频流
            if not info.get('has_audio', False):
                logger.error(f"文件不包含音频流: {audio_path}")
                return False
            
            # 验证音频时长
            duration = info.get('duration', 0)
            if duration <= 0:
                logger.error(f"音频文件时长无效: {audio_path}, 时长: {duration}")
                return False
            
            logger.info(f"音频文件验证通过: {audio_path} - 时长: {duration:.2f}秒, 大小: {self._format_size(file_size)}")
            return True
            
        except Exception as e:
            logger.error(f"音频文件验证失败: {audio_path}, 错误: {e}")
            return False
    
    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes (int): 字节数
            
        Returns:
            str: 格式化后的大小
        """
        if size_bytes == 0:
            return "0B"
        
        units = ['B', 'KB', 'MB', 'GB']
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.2f}{units[i]}" 