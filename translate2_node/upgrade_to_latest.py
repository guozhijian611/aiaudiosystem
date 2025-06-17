#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
升级到最新版本 - 解决 huggingface_hub 兼容性问题
"""

import subprocess
import sys

def upgrade_to_latest():
    """升级到最新版本"""
    print("=" * 60)
    print("    升级到最新版本解决兼容性问题")
    print("=" * 60)
    
    try:
        # 1. 升级 huggingface_hub 到最新版本
        print("1. 升级 huggingface_hub 到最新版本...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "huggingface_hub"], 
                      check=True, capture_output=True)
        print("✓ huggingface_hub 升级成功")
        
        # 2. 升级 NeMo 到最新版本
        print("2. 升级 NeMo 到最新版本...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "nemo_toolkit[asr]"], 
                      check=True, capture_output=True)
        print("✓ NeMo 升级成功")
        
        # 3. 升级其他相关包
        print("3. 升级其他相关包...")
        packages = [
            "transformers",
            "datasets", 
            "accelerate",
            "torch",
            "torchaudio"
        ]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], 
                              check=True, capture_output=True)
                print(f"✓ {package} 升级成功")
            except subprocess.CalledProcessError:
                print(f"⚠ {package} 升级失败，继续...")
        
        # 4. 测试导入
        print("4. 测试模块导入...")
        try:
            import nemo
            print(f"✓ NeMo 版本: {nemo.__version__}")
            
            # 测试关键模块
            try:
                from nemo.collections.asr.models.msdd_models import NeuralDiarizer
                print("✓ NeuralDiarizer 导入成功")
            except ImportError as e:
                print(f"⚠ NeuralDiarizer 导入失败: {e}")
                print("尝试使用替代方案...")
                
                # 检查是否有其他说话人分离模块
                try:
                    from nemo.collections.asr.models import ClusteringDiarizer
                    print("✓ ClusteringDiarizer 可用")
                except ImportError:
                    print("⚠ 未找到可用的说话人分离模块")
            
            # 测试 huggingface_hub
            import huggingface_hub
            print(f"✓ huggingface_hub 版本: {huggingface_hub.__version__}")
            
            print("\n" + "=" * 60)
            print("升级完成！")
            print("注意：如果说话人分离模块不可用，将使用基础 Whisper 模式")
            print("现在可以运行转写测试:")
            print("  python test_local_transcribe.py your_audio.wav")
            print("  python example_transcribe.py")
            print("=" * 60)
            
            return True
            
        except ImportError as e:
            print(f"✗ 模块导入测试失败: {e}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 升级失败: {e}")
        return False

def check_versions():
    """检查当前版本"""
    print("\n当前版本信息:")
    try:
        import nemo
        print(f"NeMo: {nemo.__version__}")
    except ImportError:
        print("NeMo: 未安装")
    
    try:
        import huggingface_hub
        print(f"huggingface_hub: {huggingface_hub.__version__}")
    except ImportError:
        print("huggingface_hub: 未安装")
    
    try:
        import transformers
        print(f"transformers: {transformers.__version__}")
    except ImportError:
        print("transformers: 未安装")

if __name__ == "__main__":
    check_versions()
    upgrade_to_latest() 