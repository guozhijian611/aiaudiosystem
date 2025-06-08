"""
配置管理模块
负责加载和管理所有配置项
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # RabbitMQ配置
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_VIRTUAL_HOST = os.getenv('RABBITMQ_VIRTUAL_HOST', '/')
    
    # 队列名称
    QUEUE_NAME = os.getenv('QUEUE_NAME', 'voice_extract_queue')
    
    # 后端API配置
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8787')
    API_UPLOAD_ENDPOINT = os.getenv('API_UPLOAD_ENDPOINT', '/queue/upload')
    API_CALLBACK_ENDPOINT = os.getenv('API_CALLBACK_ENDPOINT', '/queue/callback')
    
    # 工作目录配置
    # 在本地开发时使用当前目录下的文件夹，在Docker中使用/app路径
    default_work_dir = './work' if not os.path.exists('/app') else '/app/work'
    default_temp_dir = './temp' if not os.path.exists('/app') else '/app/temp'
    WORK_DIR = os.getenv('WORK_DIR', default_work_dir)
    TEMP_DIR = os.getenv('TEMP_DIR', default_temp_dir)
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # FFmpeg配置
    FFMPEG_THREADS = int(os.getenv('FFMPEG_THREADS', 4))
    AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'mp3')
    AUDIO_BITRATE = os.getenv('AUDIO_BITRATE', '128k')
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', 44100))
    
    @property
    def upload_url(self):
        """获取上传接口完整URL"""
        return f"{self.API_BASE_URL}{self.API_UPLOAD_ENDPOINT}"
    
    @property
    def callback_url(self):
        """获取回调接口完整URL"""
        return f"{self.API_BASE_URL}{self.API_CALLBACK_ENDPOINT}"
    
    def ensure_directories(self):
        """确保工作目录存在"""
        os.makedirs(self.WORK_DIR, exist_ok=True)
        os.makedirs(self.TEMP_DIR, exist_ok=True) 