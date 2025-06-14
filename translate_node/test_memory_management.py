#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内存管理测试脚本
测试音频拆分和动态内存管理功能
"""

import os
import sys
import time
import tempfile
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(__file__))
from src.transcriber import WhisperXTranscriber
from logger import logger

def create_test_audio(duration_seconds: int, sample_rate: int = 16000) -> str:
    """创建测试音频文件"""
    try:
        # 生成测试音频数据（白噪声）
        samples = int(duration_seconds * sample_rate)
        audio_data = np.random.normal(0, 0.1, samples).astype(np.float32)
        
        # 保存为临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # 使用soundfile保存
        try:
            import soundfile as sf
            sf.write(temp_path, audio_data, sample_rate)
        except ImportError:
            # 如果没有soundfile，使用scipy
            from scipy.io import wavfile
            # 转换为16位整数
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wavfile.write(temp_path, sample_rate, audio_int16)
        
        logger.info(f"创建测试音频: {temp_path}, 时长: {duration_seconds}秒")
        return temp_path
        
    except Exception as e:
        logger.error(f"创建测试音频失败: {e}")
        raise

def test_memory_monitoring():
    """测试内存监控功能"""
    print("=" * 60)
    print("1. 测试内存监控功能")
    print("=" * 60)
    
    try:
        transcriber = WhisperXTranscriber()
        
        # 测试内存使用情况获取
        memory_info = transcriber._get_memory_usage()
        print(f"内存信息: {memory_info}")
        
        # 测试GPU内存清理
        transcriber._clear_gpu_memory()
        print("GPU内存清理完成")
        
        return True
        
    except Exception as e:
        print(f"内存监控测试失败: {e}")
        return False

def test_batch_size_optimization():
    """测试批处理大小优化"""
    print("\n" + "=" * 60)
    print("2. 测试批处理大小优化")
    print("=" * 60)
    
    try:
        transcriber = WhisperXTranscriber()
        
        # 测试不同设备和音频长度的批处理大小
        test_cases = [
            ('cpu', 300),    # 5分钟音频，CPU
            ('cpu', 1800),   # 30分钟音频，CPU
            ('cuda', 300),   # 5分钟音频，GPU
            ('cuda', 1800),  # 30分钟音频，GPU
        ]
        
        for device, duration in test_cases:
            batch_size = transcriber._get_optimal_batch_size(device, duration)
            print(f"设备: {device}, 音频时长: {duration}s, 推荐批处理: {batch_size}")
        
        return True
        
    except Exception as e:
        print(f"批处理大小优化测试失败: {e}")
        return False

def test_audio_splitting_decision():
    """测试音频拆分决策"""
    print("\n" + "=" * 60)
    print("3. 测试音频拆分决策")
    print("=" * 60)
    
    try:
        transcriber = WhisperXTranscriber()
        
        # 模拟不同的内存情况
        test_cases = [
            (300, 'cuda', {'type': 'GPU', 'free': 4.0}),    # 短音频，充足内存
            (1800, 'cuda', {'type': 'GPU', 'free': 4.0}),   # 长音频，充足内存
            (600, 'cuda', {'type': 'GPU', 'free': 1.0}),    # 中等音频，内存不足
            (3600, 'cpu', {'type': 'CPU', 'free': 8.0}),    # 超长音频，CPU
        ]
        
        for duration, device, memory_info in test_cases:
            should_split = transcriber._should_split_audio(duration, device, memory_info)
            print(f"音频: {duration}s, 设备: {device}, 内存: {memory_info['free']:.1f}GB, 是否拆分: {should_split}")
        
        return True
        
    except Exception as e:
        print(f"音频拆分决策测试失败: {e}")
        return False

def test_small_audio_transcription():
    """测试小音频转写"""
    print("\n" + "=" * 60)
    print("4. 测试小音频转写（整体处理）")
    print("=" * 60)
    
    test_audio_path = None
    try:
        # 创建5分钟测试音频
        test_audio_path = create_test_audio(300)  # 5分钟
        
        transcriber = WhisperXTranscriber()
        
        # 测试转写
        start_time = time.time()
        result = transcriber.transcribe_audio(test_audio_path, timeout=600)
        end_time = time.time()
        
        print(f"转写完成:")
        print(f"- 处理时间: {end_time - start_time:.1f}秒")
        print(f"- 文本长度: {len(result.get('text', ''))}字符")
        print(f"- 段落数: {result.get('segments_count', 0)}")
        print(f"- 检测语言: {result.get('language', 'unknown')}")
        print(f"- 有效语音: {result.get('effective_voice', 0):.1f}秒")
        
        return True
        
    except Exception as e:
        print(f"小音频转写测试失败: {e}")
        return False
        
    finally:
        # 清理测试文件
        if test_audio_path and os.path.exists(test_audio_path):
            os.unlink(test_audio_path)

def test_large_audio_transcription():
    """测试大音频转写（分块处理）"""
    print("\n" + "=" * 60)
    print("5. 测试大音频转写（分块处理）")
    print("=" * 60)
    
    test_audio_path = None
    try:
        # 创建35分钟测试音频（强制分块）
        test_audio_path = create_test_audio(2100)  # 35分钟
        
        transcriber = WhisperXTranscriber()
        
        # 测试转写
        start_time = time.time()
        result = transcriber.transcribe_audio(test_audio_path, timeout=1800)
        end_time = time.time()
        
        print(f"分块转写完成:")
        print(f"- 处理时间: {end_time - start_time:.1f}秒")
        print(f"- 文本长度: {len(result.get('text', ''))}字符")
        print(f"- 段落数: {result.get('segments_count', 0)}")
        print(f"- 检测语言: {result.get('language', 'unknown')}")
        print(f"- 有效语音: {result.get('effective_voice', 0):.1f}秒")
        
        return True
        
    except Exception as e:
        print(f"大音频转写测试失败: {e}")
        return False
        
    finally:
        # 清理测试文件
        if test_audio_path and os.path.exists(test_audio_path):
            os.unlink(test_audio_path)

def test_memory_fallback():
    """测试内存不足时的回退机制"""
    print("\n" + "=" * 60)
    print("6. 测试内存回退机制")
    print("=" * 60)
    
    test_audio_path = None
    try:
        # 创建中等长度测试音频
        test_audio_path = create_test_audio(600)  # 10分钟
        
        transcriber = WhisperXTranscriber()
        
        # 模拟内存不足的情况（通过设置很小的批处理大小）
        original_batch_size = transcriber.config.WHISPER_BATCH_SIZE
        transcriber.config.WHISPER_BATCH_SIZE = 1  # 设置很小的批处理
        
        print(f"使用小批处理大小 {transcriber.config.WHISPER_BATCH_SIZE} 测试回退机制")
        
        start_time = time.time()
        result = transcriber.transcribe_audio(test_audio_path, timeout=900)
        end_time = time.time()
        
        print(f"回退机制测试完成:")
        print(f"- 处理时间: {end_time - start_time:.1f}秒")
        print(f"- 文本长度: {len(result.get('text', ''))}字符")
        print(f"- 段落数: {result.get('segments_count', 0)}")
        
        # 恢复原始批处理大小
        transcriber.config.WHISPER_BATCH_SIZE = original_batch_size
        
        return True
        
    except Exception as e:
        print(f"内存回退机制测试失败: {e}")
        return False
        
    finally:
        # 清理测试文件
        if test_audio_path and os.path.exists(test_audio_path):
            os.unlink(test_audio_path)

def main():
    """主函数"""
    print("内存管理和音频拆分测试工具")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("内存监控", test_memory_monitoring),
        ("批处理优化", test_batch_size_optimization),
        ("拆分决策", test_audio_splitting_decision),
        ("小音频转写", test_small_audio_transcription),
        ("大音频转写", test_large_audio_transcription),
        ("内存回退", test_memory_fallback),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n开始测试: {test_name}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"测试 {test_name} 出现异常: {e}")
            results[test_name] = False
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {test_name}")
    
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        print(f"\n🎉 所有测试通过! ({passed}/{total})")
    else:
        print(f"\n⚠️  部分测试失败 ({passed}/{total})")
    
    print("\n建议:")
    if not results.get("内存监控", False):
        print("- 检查PyTorch和GPU驱动安装")
    if not results.get("小音频转写", False):
        print("- 检查WhisperX模型和依赖")
    if not results.get("大音频转写", False):
        print("- 可能需要更多内存或调整分块大小")

if __name__ == "__main__":
    main() 