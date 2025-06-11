#!/usr/bin/env python3
"""
Clear Node 主程序
音频清理节点，用于音频降噪和增强处理
"""

import os
import sys
import signal
from pathlib import Path

# 设置PYTHONPATH，确保能找到clearvoice模块
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent
clearvoice_path = project_root / "ClearerVoice-Studio" / "clearvoice"
src_path = current_dir

# 添加路径到sys.path
if str(clearvoice_path) not in sys.path:
    sys.path.insert(0, str(clearvoice_path))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 设置环境变量PYTHONPATH
os.environ['PYTHONPATH'] = f"{src_path}{os.pathsep}{clearvoice_path}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"

from logger import logger
from queue_consumer import QueueConsumer

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"接收到信号 {signum}，正在退出...")
    sys.exit(0)

def main():
    """主函数"""
    logger.info("Clear Node 启动中...")
    logger.info("=" * 50)
    logger.info("音频清理节点 v1.0.0")
    logger.info("功能: 音频降噪和增强处理")
    logger.info("=" * 50)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 创建并启动队列消费者
        consumer = QueueConsumer()
        
        # 运行消费者（支持自动重连）
        consumer.run_with_retry(
            max_retries=10,  # 最大重试10次
            retry_interval=15  # 重试间隔15秒
        )
        
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1)
    
    logger.info("Clear Node 已停止")

if __name__ == "__main__":
    main()