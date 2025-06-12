#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VAD分析测试脚本
"""

import sys
import os
import json

# 添加本地FunASR路径
current_dir = os.path.dirname(__file__)
funasr_path = os.path.join(current_dir, 'FunASR')
if os.path.exists(funasr_path):
    sys.path.insert(0, funasr_path)
    print(f"已添加本地FunASR路径: {funasr_path}")

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(current_dir, 'src'))

from src.vad_analyzer import VADAnalyzer
from loguru import logger

def install_missing_deps():
    """安装缺失的依赖"""
    missing_deps = []
    
    try:
        import omegaconf
    except ImportError:
        missing_deps.append('omegaconf')
    
    try:
        import torch_complex
    except ImportError:
        missing_deps.append('torch_complex')
    
    try:
        import hydra
    except ImportError:
        missing_deps.append('hydra-core')
    
    if missing_deps:
        print(f"检测到缺失依赖: {', '.join(missing_deps)}")
        response = input("是否自动安装？(y/n): ")
        if response.lower() == 'y':
            import subprocess
            for dep in missing_deps:
                print(f"正在安装 {dep}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep])
            print("依赖安装完成！")
            return True
    return False

def test_vad_analyzer():
    """测试VAD分析器"""
    try:
        print("=" * 50)
        print("开始测试VAD分析器...")
        print("=" * 50)
        
        # 检查依赖
        print("检查依赖导入...")
        try:
            import torch
            print(f"✅ PyTorch版本: {torch.__version__}")
        except ImportError:
            print("❌ PyTorch未安装")
            return
            
        try:
            import omegaconf
            print("✅ omegaconf已安装")
        except ImportError:
            print("❌ omegaconf未安装")
            if install_missing_deps():
                import omegaconf
                print("✅ omegaconf安装成功")
            else:
                return
            
        try:
            import torch_complex
            print("✅ torch_complex已安装")
        except ImportError:
            print("❌ torch_complex未安装")
            if not install_missing_deps():
                return
        
        print("\n初始化VAD分析器...")
        
        # 初始化分析器
        analyzer = VADAnalyzer()
        
        # 获取模型信息
        model_info = analyzer.get_model_info()
        print(f"模型信息: {json.dumps(model_info, indent=2, ensure_ascii=False)}")
        
        # 测试音频文件路径（需要提供实际的音频文件）
        test_audio_paths = [
            "./test_audio.wav",
            "./test_audio.mp3", 
            "../clear_node/work/task_53/45ba15a1b88f958f4bf043e50d38361d47005540_cleared.wav"  # 使用clear_node的输出文件
        ]
        
        test_audio_path = None
        for path in test_audio_paths:
            if os.path.exists(path):
                test_audio_path = path
                break
        
        if test_audio_path:
            print(f"\n开始分析测试音频: {test_audio_path}")
            
            # 进行VAD分析
            result = analyzer.analyze_audio(test_audio_path)
            
            # 输出结果
            print("\n" + "=" * 30)
            print("VAD分析结果:")
            print("=" * 30)
            print(f"📁 文件路径: {test_audio_path}")
            print(f"⏱️  总时长: {result['total_duration']:.2f}秒")
            print(f"🎤 有效语音时长: {result['effective_duration']:.2f}秒")
            print(f"🔇 静音时长: {result['silence_duration']:.2f}秒")
            print(f"📊 语音占比: {result['speech_ratio']:.2%}")
            print(f"📝 语音段落数: {result['speech_segments_count']}")
            
            # 输出详细的语音段落信息
            if result['speech_segments']:
                print("\n语音段落详情:")
                for i, segment in enumerate(result['speech_segments'][:5]):  # 只显示前5个段落
                    print(f"  段落{i+1}: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s (时长: {segment['duration']:.2f}s)")
                
                if len(result['speech_segments']) > 5:
                    print(f"  ... 还有 {len(result['speech_segments']) - 5} 个段落")
            
            print("\n✅ VAD分析测试完成！")
            
            # 输出JSON格式的完整结果
            print("\n" + "=" * 30)
            print("完整分析结果 (JSON格式):")
            print("=" * 30)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print("\n❌ 未找到测试音频文件")
            print("请将音频文件放置在以下位置之一:")
            for path in test_audio_paths:
                print(f"  - {path}")
            print("\n或者修改 test_audio_paths 列表添加你的音频文件路径")
            
    except Exception as e:
        print(f"\n❌ VAD分析测试失败: {e}")
        print("\n错误详情:")
        import traceback
        traceback.print_exc()
        
        print("\n可能的解决方案:")
        print("1. 确保已安装所有依赖: pip install omegaconf torch_complex")
        print("2. 检查FunASR目录是否存在且完整")
        print("3. 确保音频文件路径正确且文件可读")
        print("4. 检查网络连接（首次运行需要下载模型）")

if __name__ == "__main__":
    print("Quick Node VAD 测试工具")
    print("=" * 50)
    print("1. 运行VAD分析测试")
    print("2. 只检查依赖")
    print("3. 安装缺失依赖")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    if choice == "1":
        test_vad_analyzer()
    elif choice == "2":
        print("\n检查依赖...")
        try:
            import torch
            print(f"✅ PyTorch: {torch.__version__}")
        except ImportError:
            print("❌ PyTorch未安装")
            
        try:
            import omegaconf
            print("✅ omegaconf已安装")
        except ImportError:
            print("❌ omegaconf未安装")
            
        try:
            import torch_complex
            print("✅ torch_complex已安装")
        except ImportError:
            print("❌ torch_complex未安装")
            
        try:
            from funasr import AutoModel
            print("✅ FunASR导入成功")
        except ImportError as e:
            print(f"❌ FunASR导入失败: {e}")
            
    elif choice == "3":
        install_missing_deps()
    else:
        print("无效选择，运行默认测试...")
        test_vad_analyzer() 