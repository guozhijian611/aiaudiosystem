#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPU支持修复脚本
检查并修复translate_node的GPU支持问题
"""

import os
import sys
import subprocess
import platform

def check_conda_environment():
    """检查conda环境"""
    print("=" * 50)
    print("1. 检查Conda环境")
    print("=" * 50)
    
    try:
        # 检查是否在conda环境中
        conda_env = os.environ.get('CONDA_DEFAULT_ENV')
        if conda_env:
            print(f"✓ 当前Conda环境: {conda_env}")
        else:
            print("⚠ 未检测到Conda环境")
            return False
        
        # 检查Python版本
        python_version = sys.version
        print(f"✓ Python版本: {python_version}")
        
        return True
        
    except Exception as e:
        print(f"✗ Conda环境检查失败: {e}")
        return False

def check_pytorch_installation():
    """检查PyTorch安装"""
    print("\n" + "=" * 50)
    print("2. 检查PyTorch安装")
    print("=" * 50)
    
    try:
        import torch
        print(f"✓ PyTorch版本: {torch.__version__}")
        
        # 检查CUDA支持
        cuda_available = torch.cuda.is_available()
        print(f"CUDA可用: {cuda_available}")
        
        if cuda_available:
            cuda_version = torch.version.cuda
            print(f"✓ CUDA版本: {cuda_version}")
            
            device_count = torch.cuda.device_count()
            print(f"✓ GPU设备数量: {device_count}")
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                print(f"  GPU {i}: {device_name}")
        
        return cuda_available
        
    except ImportError:
        print("✗ PyTorch未安装")
        return False
    except Exception as e:
        print(f"✗ PyTorch检查失败: {e}")
        return False

def fix_pytorch_installation():
    """修复PyTorch安装"""
    print("\n" + "=" * 50)
    print("3. 修复PyTorch安装")
    print("=" * 50)
    
    try:
        # 检查系统类型
        system = platform.system().lower()
        print(f"检测到系统: {system}")
        
        if system == "windows":
            # Windows系统的修复命令
            commands = [
                # 卸载现有的PyTorch
                "pip uninstall torch torchaudio torchvision -y",
                # 安装CUDA版本的PyTorch
                "pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121"
            ]
        else:
            # Linux/macOS系统的修复命令
            commands = [
                # 卸载现有的PyTorch
                "pip uninstall torch torchaudio torchvision -y",
                # 安装CUDA版本的PyTorch
                "pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121"
            ]
        
        print("将执行以下修复命令:")
        for cmd in commands:
            print(f"  {cmd}")
        
        confirm = input("\n是否执行修复? (y/N): ").lower().strip()
        if confirm == 'y':
            for cmd in commands:
                print(f"\n执行: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✓ 命令执行成功")
                else:
                    print(f"✗ 命令执行失败: {result.stderr}")
                    return False
            
            print("\n✓ PyTorch修复完成，请重新运行诊断脚本验证")
            return True
        else:
            print("跳过PyTorch修复")
            return False
            
    except Exception as e:
        print(f"✗ PyTorch修复失败: {e}")
        return False

def check_dependencies():
    """检查其他依赖"""
    print("\n" + "=" * 50)
    print("4. 检查其他依赖")
    print("=" * 50)
    
    dependencies = [
        'ctranslate2',
        'faster-whisper',
        'transformers',
        'librosa',
        'numpy',
        'pandas'
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} - 未安装")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n缺少依赖: {', '.join(missing_deps)}")
        return False
    else:
        print("\n✓ 所有依赖都已安装")
        return True

def fix_dependencies():
    """修复依赖"""
    print("\n" + "=" * 50)
    print("5. 修复依赖")
    print("=" * 50)
    
    try:
        # 使用environment.yml重新安装环境
        env_file = "environment.yml"
        if os.path.exists(env_file):
            print(f"找到环境文件: {env_file}")
            
            commands = [
                "conda env update -f environment.yml",
                "pip install -r requirements.txt" if os.path.exists("requirements.txt") else None
            ]
            
            commands = [cmd for cmd in commands if cmd]  # 过滤None
            
            print("将执行以下修复命令:")
            for cmd in commands:
                print(f"  {cmd}")
            
            confirm = input("\n是否执行依赖修复? (y/N): ").lower().strip()
            if confirm == 'y':
                for cmd in commands:
                    print(f"\n执行: {cmd}")
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✓ 命令执行成功")
                    else:
                        print(f"✗ 命令执行失败: {result.stderr}")
                
                print("\n✓ 依赖修复完成")
                return True
            else:
                print("跳过依赖修复")
                return False
        else:
            print(f"✗ 未找到环境文件: {env_file}")
            return False
            
    except Exception as e:
        print(f"✗ 依赖修复失败: {e}")
        return False

def update_config():
    """更新配置"""
    print("\n" + "=" * 50)
    print("6. 更新配置")
    print("=" * 50)
    
    try:
        # 检查.env文件
        env_file = ".env"
        if os.path.exists(env_file):
            print(f"找到配置文件: {env_file}")
            
            # 读取现有配置
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否需要更新配置
            updates = []
            
            if 'WHISPER_COMPUTE_TYPE=float16' in content:
                updates.append(('WHISPER_COMPUTE_TYPE=float16', 'WHISPER_COMPUTE_TYPE=auto'))
            
            if updates:
                print("建议的配置更新:")
                for old, new in updates:
                    print(f"  {old} -> {new}")
                
                confirm = input("\n是否更新配置? (y/N): ").lower().strip()
                if confirm == 'y':
                    for old, new in updates:
                        content = content.replace(old, new)
                    
                    # 写回文件
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("✓ 配置更新完成")
                    return True
                else:
                    print("跳过配置更新")
                    return False
            else:
                print("✓ 配置无需更新")
                return True
        else:
            print("未找到.env配置文件，创建推荐配置...")
            
            # 创建推荐配置
            recommended_config = """# Translate Node 配置
WHISPER_MODEL=large-v3
WHISPER_LANGUAGE=auto
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=auto
WHISPER_BATCH_SIZE=16

# 启用功能
ENABLE_ALIGNMENT=true
ENABLE_DIARIZATION=false

# 处理限制
MAX_AUDIO_DURATION=3600
PROCESSING_TIMEOUT=7200
"""
            
            confirm = input("是否创建推荐配置文件? (y/N): ").lower().strip()
            if confirm == 'y':
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(recommended_config)
                print(f"✓ 已创建配置文件: {env_file}")
                return True
            else:
                print("跳过配置文件创建")
                return False
            
    except Exception as e:
        print(f"✗ 配置更新失败: {e}")
        return False

def main():
    """主函数"""
    print("Translate Node GPU支持修复工具")
    print("=" * 50)
    
    # 检查步骤
    conda_ok = check_conda_environment()
    pytorch_ok = check_pytorch_installation()
    deps_ok = check_dependencies()
    
    # 修复步骤
    if not pytorch_ok:
        print("\n检测到PyTorch问题，开始修复...")
        pytorch_ok = fix_pytorch_installation()
    
    if not deps_ok:
        print("\n检测到依赖问题，开始修复...")
        deps_ok = fix_dependencies()
    
    # 更新配置
    config_ok = update_config()
    
    # 总结
    print("\n" + "=" * 50)
    print("修复总结")
    print("=" * 50)
    print(f"Conda环境: {'✓' if conda_ok else '✗'}")
    print(f"PyTorch: {'✓' if pytorch_ok else '✗'}")
    print(f"依赖库: {'✓' if deps_ok else '✗'}")
    print(f"配置文件: {'✓' if config_ok else '✗'}")
    
    if all([conda_ok, pytorch_ok, deps_ok, config_ok]):
        print("\n🎉 修复完成！建议重启translate_node服务")
        print("\n下一步:")
        print("1. 重启translate_node服务")
        print("2. 运行 python test_gpu_support.py 验证修复结果")
    else:
        print("\n⚠️  部分问题未解决，请检查上述失败项目")
        print("\n手动修复建议:")
        if not conda_ok:
            print("- 确保在正确的conda环境中运行")
        if not pytorch_ok:
            print("- 手动重新安装PyTorch: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121")
        if not deps_ok:
            print("- 手动安装依赖: conda env update -f environment.yml")

if __name__ == "__main__":
    main() 