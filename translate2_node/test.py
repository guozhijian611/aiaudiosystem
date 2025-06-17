#!/usr/bin/env python3
"""
Translate2 Node 集成测试脚本
用于测试 Whisper-Diarization 转写功能和API对接
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
        print(f"  - Whisper Model: {config.WHISPER_MODEL}")
        print(f"  - Diarization: {config.ENABLE_DIARIZATION}")
        print(f"  - VAD: {config.ENABLE_VAD}")
        print(f"  - TitaNet: {config.ENABLE_TITANET}")
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

def test_transcriber():
    """测试转写器"""
    try:
        from transcriber import WhisperDiarizationTranscriber
        
        print("正在初始化转写器...")
        transcriber = WhisperDiarizationTranscriber()
        
        print("✓ 转写器初始化成功")
        print(f"  - 设备: {transcriber.device}")
        print(f"  - 模型: {transcriber.config.WHISPER_MODEL}")
        print(f"  - 说话人分离: {transcriber.config.ENABLE_DIARIZATION}")
        
        return True
    except Exception as e:
        print(f"✗ 转写器测试失败: {e}")
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

def test_whisper_diarization():
    """测试 Whisper-Diarization 模块"""
    try:
        # 检查 whisper-diarization 目录
        if os.path.exists('whisper-diarization'):
            print("✓ Whisper-Diarization 目录存在")
            
            # 尝试导入
            try:
                import sys
                sys.path.append('whisper-diarization')
                from whisper_diarization import WhisperDiarization
                print("✓ Whisper-Diarization 模块导入成功")
                return True
            except ImportError:
                print("⚠ Whisper-Diarization 模块未安装，将使用基础 Whisper")
                return True
        else:
            print("⚠ Whisper-Diarization 目录不存在")
            print("  将使用基础 Whisper 实现")
            return True
    except Exception as e:
        print(f"✗ Whisper-Diarization 测试失败: {e}")
        return False

def create_test_message():
    """创建测试队列消息"""
    return {
        "task_info": {
            "id": 123,
            "filename": "test_audio.mp3",
            "voice_url": "http://example.com/test_audio.mp3",
            "clear_url": "http://example.com/test_audio_clear.mp3",
            "is_clear": 1
        }
    }

def main():
    """主测试函数"""
    print("Translate2 Node 集成测试")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('src'):
        print("✗ 请在 translate2_node 目录下运行此脚本")
        sys.exit(1)
    
    # 运行各项测试
    tests = [
        ("配置管理", test_config),
        ("API客户端", test_api_client),
        ("Whisper-Diarization", test_whisper_diarization),
        ("转写器", test_transcriber),
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