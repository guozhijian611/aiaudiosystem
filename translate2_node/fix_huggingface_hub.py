#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复 huggingface_hub 版本兼容性问题
"""

import subprocess
import sys
import importlib

def check_huggingface_hub_version():
    """检查 huggingface_hub 版本"""
    try:
        import huggingface_hub
        version = huggingface_hub.__version__
        print(f"当前 huggingface_hub 版本: {version}")
        return version
    except ImportError:
        print("huggingface_hub 未安装")
        return None

def fix_huggingface_hub():
    """修复 huggingface_hub 版本问题"""
    print("=" * 60)
    print("    修复 huggingface_hub 版本兼容性问题")
    print("=" * 60)
    
    current_version = check_huggingface_hub_version()
    
    if current_version:
        # 检查版本是否过高
        version_parts = current_version.split('.')
        major_version = int(version_parts[0])
        
        if major_version >= 0:
            minor_version = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            if major_version > 0 or minor_version >= 20:
                print(f"检测到版本过高: {current_version}")
                print("正在降级到兼容版本...")
                
                try:
                    # 卸载当前版本
                    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "huggingface_hub"], 
                                 check=True, capture_output=True)
                    print("✓ 卸载当前版本成功")
                    
                    # 安装兼容版本
                    subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub<0.20.0"], 
                                 check=True, capture_output=True)
                    print("✓ 安装兼容版本成功")
                    
                    # 验证安装
                    new_version = check_huggingface_hub_version()
                    print(f"修复后版本: {new_version}")
                    
                    return True
                    
                except subprocess.CalledProcessError as e:
                    print(f"✗ 修复失败: {e}")
                    return False
            else:
                print(f"版本兼容: {current_version}")
                return True
        else:
            print(f"版本格式异常: {current_version}")
            return False
    else:
        print("安装 huggingface_hub...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub<0.20.0"], 
                         check=True, capture_output=True)
            print("✓ 安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 安装失败: {e}")
            return False

def test_nemo_import():
    """测试 NeMo 导入"""
    print("\n测试 NeMo 导入...")
    try:
        import nemo
        print("✓ NeMo 导入成功")
        
        # 测试关键模块
        try:
            from nemo.collections.asr.models.msdd_models import NeuralDiarizer
            print("✓ NeuralDiarizer 导入成功")
            return True
        except ImportError as e:
            print(f"✗ NeuralDiarizer 导入失败: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ NeMo 导入失败: {e}")
        return False

def main():
    """主函数"""
    print("开始修复 huggingface_hub 兼容性问题...")
    
    # 修复版本问题
    if fix_huggingface_hub():
        print("\n✓ huggingface_hub 版本修复成功")
        
        # 测试 NeMo 导入
        if test_nemo_import():
            print("\n✓ 所有问题已修复！")
            print("\n现在可以正常运行转写测试:")
            print("  python test_local_transcribe.py your_audio.wav")
        else:
            print("\n⚠ NeMo 导入仍有问题，可能需要重新安装 NeMo")
            print("建议运行: pip install --force-reinstall nemo_toolkit[asr]==2.0.0rc0")
    else:
        print("\n✗ 修复失败，请手动处理")
        print("建议:")
        print("1. 手动卸载 huggingface_hub: pip uninstall huggingface_hub")
        print("2. 安装兼容版本: pip install huggingface_hub<0.20.0")
        print("3. 重新安装 NeMo: pip install --force-reinstall nemo_toolkit[asr]==2.0.0rc0")

if __name__ == "__main__":
    main() 