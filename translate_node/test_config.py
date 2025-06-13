#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置测试脚本
用于验证translate_node的配置和依赖是否正常
"""

import os
import sys
import traceback

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, current_dir)

def test_config():
    """测试配置加载"""
    try:
        from config import Config
        config = Config()
        print("✅ 配置加载成功")
        print(f"   队列名称: {config.QUEUE_NAME}")
        print(f"   RabbitMQ: {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
        print(f"   API地址: {config.API_BASE_URL}")
        print(f"   Whisper模型: {config.WHISPER_MODEL}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    dependencies = [
        ("pika", "RabbitMQ客户端"),
        ("requests", "HTTP客户端"),
        ("python-dotenv", "环境变量"),
        ("loguru", "日志库"),
        ("psutil", "系统监控"),
    ]
    
    all_ok = True
    for package, desc in dependencies:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {desc} ({package}) - 已安装")
        except ImportError:
            print(f"❌ {desc} ({package}) - 未安装")
            all_ok = False
    
    return all_ok

def test_whisperx_dependencies():
    """测试WhisperX相关依赖"""
    dependencies = [
        ("torch", "PyTorch"),
        ("torchaudio", "PyTorch音频"),
        ("transformers", "Transformers"),
        ("numpy", "NumPy"),
        ("librosa", "音频处理"),
    ]
    
    all_ok = True
    for package, desc in dependencies:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {desc} ({package}) - 版本: {version}")
        except ImportError:
            print(f"❌ {desc} ({package}) - 未安装")
            all_ok = False
    
    return all_ok

def test_device_detection():
    """测试设备检测"""
    try:
        import torch
        print(f"✅ PyTorch版本: {torch.__version__}")
        
        # 检测CUDA
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
            print(f"✅ CUDA可用 - 设备数: {device_count}, 主GPU: {device_name}")
        else:
            print("ℹ️  CUDA不可用")
        
        # 检测MPS
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ MPS可用 (Apple Silicon)")
        else:
            print("ℹ️  MPS不可用")
        
        return True
    except Exception as e:
        print(f"❌ 设备检测失败: {e}")
        return False

def test_directories():
    """测试目录结构"""
    dirs = ['work', 'temp', 'logs', 'models', 'src']
    all_ok = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录缺失: {dir_name}")
            all_ok = False
    
    return all_ok

def test_logger():
    """测试日志系统"""
    try:
        from src.logger import logger
        logger.info("日志系统测试")
        print("✅ 日志系统正常")
        return True
    except Exception as e:
        print(f"❌ 日志系统失败: {e}")
        return False

def test_api_client():
    """测试API客户端"""
    try:
        from src.api_client import APIClient
        client = APIClient()
        print("✅ API客户端初始化成功")
        print(f"   上传URL: {client.config.upload_url}")
        print(f"   回调URL: {client.config.callback_url}")
        return True
    except Exception as e:
        print(f"❌ API客户端失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Translate Node 配置测试")
    print("=" * 50)
    
    tests = [
        ("配置系统", test_config),
        ("基础依赖", test_dependencies),
        ("WhisperX依赖", test_whisperx_dependencies),
        ("设备检测", test_device_detection),
        ("目录结构", test_directories),
        ("日志系统", test_logger),
        ("API客户端", test_api_client),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            print(traceback.format_exc())
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统配置正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 