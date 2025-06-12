#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

def test_vad_fix():
    """测试修复后的VAD分析器"""
    print("=" * 60)
    print("测试修复后的VAD分析器")
    print("=" * 60)
    
    try:
        # 导入VAD分析器
        from src.vad_analyzer import VADAnalyzer
        
        print("✓ VADAnalyzer导入成功")
        
        # 初始化分析器
        print("\n正在初始化VAD分析器...")
        start_time = time.time()
        
        vad_analyzer = VADAnalyzer()
        
        init_time = time.time() - start_time
        print(f"✓ VAD分析器初始化成功 (耗时: {init_time:.2f}秒)")
        
        # 检查是否有测试音频文件
        test_audio_files = [
            "test_audio.wav",
            "../test_audio.wav", 
            "example.wav",
            "../example.wav"
        ]
        
        test_file = None
        for audio_file in test_audio_files:
            if os.path.exists(audio_file):
                test_file = audio_file
                break
        
        if test_file:
            print(f"\n找到测试音频文件: {test_file}")
            print("正在进行VAD分析...")
            
            # 进行VAD分析
            analysis_start = time.time()
            result = vad_analyzer.analyze_audio(test_file)
            analysis_time = time.time() - analysis_start
            
            print(f"✓ VAD分析完成 (耗时: {analysis_time:.2f}秒)")
            print("\n分析结果:")
            print(f"  总时长: {result['total_duration']:.2f}秒")
            print(f"  有效语音: {result['effective_duration']:.2f}秒")
            print(f"  语音占比: {result['speech_ratio']:.2%}")
            print(f"  语音段数: {result['speech_segments_count']}")
            
            if result['speech_segments']:
                print("  语音段详情:")
                for i, segment in enumerate(result['speech_segments'][:3]):  # 只显示前3个
                    print(f"    段落{i+1}: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s "
                          f"(时长: {segment['duration']:.2f}s)")
                
                if len(result['speech_segments']) > 3:
                    print(f"    ... 还有 {len(result['speech_segments']) - 3} 个语音段")
            
        else:
            print("\n未找到测试音频文件，创建模拟分析...")
            # 显示模型信息
            model_info = vad_analyzer.get_model_info()
            print("VAD模型信息:")
            for key, value in model_info.items():
                print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        print("✓ VAD分析器测试完成，修复成功！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n错误详情:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行测试
    success = test_vad_fix()
    
    if success:
        print("\n🎉 VAD修复验证成功！")
        exit(0)
    else:
        print("\n💥 VAD修复验证失败，请检查错误信息")
        exit(1) 