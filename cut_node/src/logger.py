"""
日志管理模块
提供统一的日志记录功能
"""

import logging
import sys
from datetime import datetime
from config import Config

def setup_logger():
    """设置日志记录器"""
    
    # 创建日志记录器
    logger = logging.getLogger('cut_node')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    try:
        file_handler = logging.FileHandler(f'/app/logs/cut_node_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except:
        # 如果无法创建文件日志，只使用控制台日志
        pass
    
    return logger

# 全局日志记录器
logger = setup_logger() 