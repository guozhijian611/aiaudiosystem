#!/usr/bin/env python3
"""
Cut Node 主程序
音频提取节点，用于从视频文件中提取音频
"""

import signal
import sys
from logger import logger
from queue_consumer import QueueConsumer

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"接收到信号 {signum}，正在退出...")
    sys.exit(0)

def main():
    """主函数"""
    logger.info("Cut Node 启动中...")
    logger.info("=" * 50)
    logger.info("音频提取节点 v1.0.0")
    logger.info("功能: 从视频文件中提取音频")
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
    
    logger.info("Cut Node 已停止")

if __name__ == "__main__":
    main() 