#!/usr/bin/env python3
"""
Clear Node 测试脚本
用于测试音频清理功能
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from logger import logger
from audio_cleaner import AudioCleaner
from api_client import APIClient

def test_config():
    """测试配置加载"""
    logger.info("=== 测试配置加载 ===")
    try:
        config = Config()
        logger.info(f"配置加载成功:\n{config}")
        return True
    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        return False

def test_clearvoice_import():
    """测试ClearVoice导入"""
    logger.info("=== 测试ClearVoice导入 ===")
    try:
        config = Config()
        clearvoice_path = os.path.abspath(config.CLEARVOICE_PATH)
        
        if not os.path.exists(clearvoice_path):
            logger.error(f"ClearVoice路径不存在: {clearvoice_path}")
            return False
        
        # 添加路径
        if clearvoice_path not in sys.path:
            sys.path.insert(0, clearvoice_path)
        
        # 尝试导入
        from clearvoice import ClearVoice
        logger.info("ClearVoice导入成功")
        
        # 尝试初始化
        clear_voice = ClearVoice(
            task=config.CLEAR_TASK,
            model_names=[config.CLEAR_MODEL]
        )
        logger.info(f"ClearVoice初始化成功 - 模型: {config.CLEAR_MODEL}")
        return True
        
    except Exception as e:
        logger.error(f"ClearVoice测试失败: {e}")
        return False

def test_audio_cleaner():
    """测试音频清理器"""
    logger.info("=== 测试音频清理器 ===")
    try:
        cleaner = AudioCleaner()
        logger.info("音频清理器初始化成功")
        return True
    except Exception as e:
        logger.error(f"音频清理器测试失败: {e}")
        return False

def test_api_client():
    """测试API客户端"""
    logger.info("=== 测试API客户端 ===")
    try:
        client = APIClient()
        logger.info("API客户端初始化成功")
        
        # 测试健康检查（可能会失败，这是正常的）
        try:
            health = client.health_check()
            logger.info(f"API健康检查: {'正常' if health else '失败'}")
        except:
            logger.info("API健康检查失败（这是正常的，如果后端未启动）")
        
        return True
    except Exception as e:
        logger.error(f"API客户端测试失败: {e}")
        return False

def test_audio_processing():
    """测试音频处理（如果有测试音频文件）"""
    logger.info("=== 测试音频处理 ===")
    try:
        # 查找测试音频文件
        test_audio_paths = [
            "ClearerVoice-Studio/clearvoice/samples/input.wav",
            "ClearerVoice-Studio/clearvoice/samples/speech1.wav",
            "test_audio.wav"
        ]
        
        test_file = None
        for path in test_audio_paths:
            if os.path.exists(path):
                test_file = path
                break
        
        if not test_file:
            logger.info("未找到测试音频文件，跳过音频处理测试")
            return True
        
        logger.info(f"使用测试文件: {test_file}")
        
        # 初始化音频清理器
        cleaner = AudioCleaner()
        
        # 获取音频信息
        audio_info = cleaner.get_audio_info(test_file)
        logger.info(f"音频信息: {audio_info}")
        
        # 创建输出目录
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 执行音频清理
        output_file = os.path.join(output_dir, "test_cleaned.wav")
        logger.info(f"开始音频清理: {test_file} -> {output_file}")
        
        start_time = time.time()
        result_path = cleaner.clean_audio(test_file, output_file)
        processing_time = time.time() - start_time
        
        logger.info(f"音频清理完成: {result_path}")
        logger.info(f"处理时间: {processing_time:.2f}秒")
        
        # 获取输出音频信息
        output_info = cleaner.get_audio_info(result_path)
        logger.info(f"输出音频信息: {output_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"音频处理测试失败: {e}")
        return False

def test_directories():
    """测试目录创建"""
    logger.info("=== 测试目录创建 ===")
    try:
        config = Config()
        
        # 创建必要目录
        directories = [config.WORK_DIR, config.TEMP_DIR, "logs", "test_output"]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if os.path.exists(directory):
                logger.info(f"目录创建成功: {directory}")
            else:
                logger.error(f"目录创建失败: {directory}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"目录创建测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始Clear Node测试")
    logger.info("=" * 50)
    
    tests = [
        ("配置加载", test_config),
        ("目录创建", test_directories),
        ("ClearVoice导入", test_clearvoice_import),
        ("音频清理器", test_audio_cleaner),
        ("API客户端", test_api_client),
        ("音频处理", test_audio_processing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n开始测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"测试结果: {test_name} - {'通过' if result else '失败'}")
        except Exception as e:
            logger.error(f"测试异常: {test_name} - {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    logger.info("\n" + "=" * 50)
    logger.info("测试总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！Clear Node准备就绪")
        return True
    else:
        logger.error(f"❌ {total - passed} 个测试失败，请检查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)