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
    QUEUE_NAME = os.getenv('QUEUE_NAME', 'voice_clear_queue')
    
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
    
    # 音频清理配置
    CLEAR_MODEL = os.getenv('CLEAR_MODEL', 'FRCRN_SE_16K')  # 默认使用FRCRN模型
    CLEAR_TASK = os.getenv('CLEAR_TASK', 'speech_enhancement')  # 语音增强任务
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'wav')  # 输出格式
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', 16000))  # 采样率
    
    # 处理限制配置
    MAX_AUDIO_DURATION = int(os.getenv('MAX_AUDIO_DURATION', 1800))  # 最大音频时长（秒），默认30分钟
    PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', 3600))  # 处理超时（秒），默认1小时
    CHUNK_DURATION = int(os.getenv('CHUNK_DURATION', 300))  # 分块处理时长（秒），默认5分钟
    
    # ClearVoice模型路径配置
    CLEARVOICE_PATH = os.getenv('CLEARVOICE_PATH', './ClearerVoice-Studio/clearvoice')
    
    @property
    def upload_url(self):
        """获取上传接口完整URL"""
        return f"{self.API_BASE_URL}{self.API_UPLOAD_ENDPOINT}"
    
    @property
    def callback_url(self):
        """获取回调接口完整URL"""
        return f"{self.API_BASE_URL}{self.API_CALLBACK_ENDPOINT}"
    
    def __str__(self):
        """配置信息字符串表示"""
        return f"""Clear Node 配置信息:
        RabbitMQ: {self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}
        队列名称: {self.QUEUE_NAME}
        API地址: {self.API_BASE_URL}
        工作目录: {self.WORK_DIR}
        临时目录: {self.TEMP_DIR}
        清理模型: {self.CLEAR_MODEL}
        清理任务: {self.CLEAR_TASK}
        输出格式: {self.OUTPUT_FORMAT}
        采样率: {self.SAMPLE_RATE}
        """