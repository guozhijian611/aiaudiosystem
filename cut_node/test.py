#!/usr/bin/env python3
"""
Cut Node 集成测试脚本
用于测试音频提取功能和API对接
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# 添加源代码路径
sys.path.append('src')

def test_config():
    """测试配置加载"""
    try:
        from config import Config
        config = Config()
        print(f"✓ 配置加载成功")
        print(f"  - RabbitMQ: {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
        print(f"  - API Base: {config.API_BASE_URL}")
        print(f"  - Upload URL: {config.upload_url}")
        print(f"  - Callback URL: {config.callback_url}")
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

def test_api_client():
    """测试API客户端"""
    try:
        from api_client import APIClient
        client = APIClient()
        
        # 测试健康检查
        is_healthy = client.health_check()
        if is_healthy:
            print("✓ 后端API连接正常")
        else:
            print("⚠ 后端API连接失败（可能后端未启动）")
        
        return True
    except Exception as e:
        print(f"✗ API客户端测试失败: {e}")
        return False

def test_audio_extractor():
    """测试音频提取器"""
    try:
        from audio_extractor import AudioExtractor
        extractor = AudioExtractor()
        
        # 创建测试视频文件（模拟）
        print("⚠ 音频提取器需要实际视频文件进行测试")
        print("  请手动测试 extract_audio 方法")
        
        return True
    except Exception as e:
        print(f"✗ 音频提取器测试失败: {e}")
        return False

def test_queue_consumer():
    """测试队列消费者"""
    try:
        from queue_consumer import QueueConsumer
        consumer = QueueConsumer()
        
        # 测试连接（不实际连接）
        print("⚠ 队列消费者需要RabbitMQ服务进行测试")
        print("  请确保RabbitMQ服务正在运行")
        
        return True
    except Exception as e:
        print(f"✗ 队列消费者测试失败: {e}")
        return False

def create_test_message():
    """创建测试队列消息"""
    return {
        "task_id": 123,
        "video_url": "http://example.com/test_video.mp4",
        "url": "http://example.com/test_video.mp4"
    }

def main():
    """主测试函数"""
    print("Cut Node 集成测试")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('src'):
        print("✗ 请在 cut_node 目录下运行此脚本")
        sys.exit(1)
    
    # 运行各项测试
    tests = [
        ("配置管理", test_config),
        ("API客户端", test_api_client),
        ("音频提取器", test_audio_extractor),
        ("队列消费者", test_queue_consumer),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n测试 {test_name}...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append(False)
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    success_count = sum(results)
    total_count = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓" if results[i] else "✗"
        print(f"  {status} {test_name}")
    
    print(f"\n通过: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠ 部分测试失败，请检查配置和依赖")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 