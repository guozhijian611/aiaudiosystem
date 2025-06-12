#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的VAD测试脚本
"""

import os
import sys

# 添加本地FunASR路径
current_dir = os.path.dirname(__file__)
funasr_path = os.path.join(current_dir, 'FunASR')
if os.path.exists(funasr_path):
    sys.path.insert(0, funasr_path)
    print(f"✅ 已添加本地FunASR路径: {funasr_path}")

# 添加src路径
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_vad_model():
    """测试VAD模型"""
    try:
        print("=" * 50)
        print("测试VAD模型")
        print("=" * 50)
        
        # 导入FunASR
        from funasr import AutoModel
        print("✅ FunASR导入成功")
        
        # 初始化模型
        print("初始化VAD模型...")
        vad_model = AutoModel(
            model="fsmn-vad",
            model_revision="v2.0.4",
            vad_model="fsmn-vad",
            vad_kwargs={
                "max_end_silence_time": 800,
                "max_start_silence_time": 3000,
                "min_speech_duration": 250,
            }
        )
        print("✅ VAD模型初始化成功")
        
        # 测试音频文件路径（需要用户提供）
        test_files = [
            "./temp/test.wav",
            "./temp/test.mp3",
            # 可以添加更多测试文件路径
        ]
        
        found_file = None
        for test_file in test_files:
            if os.path.exists(test_file):
                found_file = test_file
                break
        
        if not found_file:
            print("⚠️  没有找到测试音频文件")
            print("请将测试音频文件放在以下路径之一:")
            for path in test_files:
                print(f"  - {path}")
            return True
        
        print(f"找到测试文件: {found_file}")
        
        # 进行VAD分析
        print("开始VAD分析...")
        result = vad_model.generate(
            input=found_file,
            batch_size=1
        )
        
        print("✅ VAD分析完成")
        print(f"结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主函数"""
    success = test_vad_model()
    
    if success:
        print("\n🎉 VAD模型测试通过!")
    else:
        print("\n❌ VAD模型测试失败!")

if __name__ == "__main__":
    main() 