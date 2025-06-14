#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows PyTorch GPU修复脚本
专门用于在Windows上修复PyTorch GPU支持问题
"""

import os
import sys
import subprocess
import platform

def check_system():
    """检查系统信息"""
    print("=" * 60)
    print("1. 系统信息检查")
    print("=" * 60)
    
    system_info = {
        'system': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'conda_env': os.environ.get('CONDA_DEFAULT_ENV', 'None')
    }
    
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    return system_info['system'].lower() == 'windows'

def check_cuda_installation():
    """检查CUDA安装"""
    print("\n" + "=" * 60)
    print("2. CUDA安装检查")
    print("=" * 60)
    
    try:
        # 检查nvidia-smi命令
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("✓ NVIDIA驱动已安装")
            print("NVIDIA-SMI输出:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print("✗ nvidia-smi命令失败")
            return False
    except FileNotFoundError:
        print("✗ nvidia-smi命令未找到，请安装NVIDIA驱动")
        return False
    except Exception as e:
        print(f"✗ CUDA检查失败: {e}")
        return False

def get_cuda_version():
    """获取CUDA版本"""
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            output = result.stdout
            # 解析CUDA版本
            for line in output.split('\n'):
                if 'release' in line.lower():
                    version = line.split('release')[1].split(',')[0].strip()
                    print(f"✓ CUDA版本: {version}")
                    return version
        else:
            print("⚠ nvcc命令不可用，可能只安装了运行时")
            return "unknown"
    except:
        print("⚠ 无法获取CUDA版本")
        return "unknown"

def uninstall_current_pytorch():
    """卸载当前的PyTorch"""
    print("\n" + "=" * 60)
    print("3. 卸载当前PyTorch")
    print("=" * 60)
    
    packages_to_remove = [
        'torch',
        'torchaudio',
        'torchvision'
    ]
    
    for package in packages_to_remove:
        try:
            print(f"卸载 {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'uninstall', package, '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ {package} 卸载成功")
            else:
                print(f"⚠ {package} 卸载失败或未安装: {result.stderr}")
        except Exception as e:
            print(f"✗ {package} 卸载异常: {e}")

def install_pytorch_gpu():
    """安装GPU版本的PyTorch"""
    print("\n" + "=" * 60)
    print("4. 安装GPU版本PyTorch")
    print("=" * 60)
    
    # 提供多个CUDA版本选项
    cuda_options = {
        '1': ('cu118', 'CUDA 11.8'),
        '2': ('cu121', 'CUDA 12.1'),
        '3': ('cu124', 'CUDA 12.4'),
        '4': ('cpu', 'CPU版本（无GPU加速）')
    }
    
    print("请选择CUDA版本:")
    for key, (version, desc) in cuda_options.items():
        print(f"  {key}. {desc}")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice in cuda_options:
        cuda_version, desc = cuda_options[choice]
        print(f"选择了: {desc}")
        
        if cuda_version == 'cpu':
            install_cmd = [
                sys.executable, '-m', 'pip', 'install', 
                'torch', 'torchaudio', '--index-url', 
                'https://download.pytorch.org/whl/cpu'
            ]
        else:
            install_cmd = [
                sys.executable, '-m', 'pip', 'install', 
                'torch', 'torchaudio', '--index-url', 
                f'https://download.pytorch.org/whl/{cuda_version}'
            ]
        
        print(f"执行安装命令: {' '.join(install_cmd)}")
        
        try:
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ PyTorch安装成功")
                return True
            else:
                print(f"✗ PyTorch安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ PyTorch安装异常: {e}")
            return False
    else:
        print("无效选择")
        return False

def test_pytorch_gpu():
    """测试PyTorch GPU支持"""
    print("\n" + "=" * 60)
    print("5. 测试PyTorch GPU支持")
    print("=" * 60)
    
    try:
        import torch
        print(f"✓ PyTorch版本: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        print(f"CUDA可用: {cuda_available}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"✓ GPU设备数量: {device_count}")
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_props = torch.cuda.get_device_properties(i)
                memory_total = device_props.total_memory / 1024**3
                print(f"  GPU {i}: {device_name}")
                print(f"    总内存: {memory_total:.1f}GB")
                print(f"    计算能力: {device_props.major}.{device_props.minor}")
            
            # 测试GPU计算
            print("\n测试GPU计算...")
            x = torch.randn(1000, 1000, device='cuda')
            y = torch.randn(1000, 1000, device='cuda')
            z = torch.matmul(x, y)
            print("✓ GPU矩阵运算测试通过")
            
            return True
        else:
            print("✗ CUDA不可用")
            return False
            
    except ImportError:
        print("✗ PyTorch导入失败")
        return False
    except Exception as e:
        print(f"✗ PyTorch测试失败: {e}")
        return False

def test_faster_whisper():
    """测试faster-whisper GPU支持"""
    print("\n" + "=" * 60)
    print("6. 测试faster-whisper GPU支持")
    print("=" * 60)
    
    try:
        from faster_whisper import WhisperModel
        print("✓ faster-whisper导入成功")
        
        # 测试GPU模型创建
        try:
            print("测试创建GPU模型...")
            model = WhisperModel("tiny", device="cuda", compute_type="float16")
            print("✓ GPU模型创建成功 (float16)")
            del model
            
            model = WhisperModel("tiny", device="cuda", compute_type="float32")
            print("✓ GPU模型创建成功 (float32)")
            del model
            
            return True
            
        except Exception as e:
            print(f"✗ GPU模型创建失败: {e}")
            
            # 尝试CPU模型
            try:
                print("尝试CPU模型...")
                model = WhisperModel("tiny", device="cpu", compute_type="float32")
                print("✓ CPU模型创建成功")
                del model
                return False  # GPU失败但CPU成功
            except Exception as e2:
                print(f"✗ CPU模型也失败: {e2}")
                return False
                
    except ImportError as e:
        print(f"✗ faster-whisper导入失败: {e}")
        return False

def update_environment_config():
    """更新环境配置"""
    print("\n" + "=" * 60)
    print("7. 更新环境配置")
    print("=" * 60)
    
    try:
        # 检查.env文件
        env_file = ".env"
        config_updates = []
        
        # 根据GPU测试结果推荐配置
        import torch
        if torch.cuda.is_available():
            device_props = torch.cuda.get_device_properties(0)
            if device_props.major >= 7:  # Volta及以上架构
                recommended_config = {
                    'WHISPER_DEVICE': 'cuda',
                    'WHISPER_COMPUTE_TYPE': 'float16'
                }
                print("✓ 检测到支持float16的GPU，推荐使用GPU + float16")
            else:
                recommended_config = {
                    'WHISPER_DEVICE': 'cuda', 
                    'WHISPER_COMPUTE_TYPE': 'float32'
                }
                print("⚠ GPU不支持高效float16，推荐使用GPU + float32")
        else:
            recommended_config = {
                'WHISPER_DEVICE': 'cpu',
                'WHISPER_COMPUTE_TYPE': 'float32'
            }
            print("⚠ GPU不可用，推荐使用CPU + float32")
        
        print("\n推荐的环境变量:")
        for key, value in recommended_config.items():
            print(f"  {key}={value}")
        
        # 询问是否更新配置文件
        if os.path.exists(env_file):
            update = input(f"\n是否更新 {env_file} 配置文件? (y/N): ").lower().strip()
            if update == 'y':
                # 读取现有配置
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 更新配置
                for key, value in recommended_config.items():
                    if f"{key}=" in content:
                        # 替换现有配置
                        import re
                        pattern = f"^{key}=.*$"
                        replacement = f"{key}={value}"
                        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                    else:
                        # 添加新配置
                        content += f"\n{key}={value}"
                
                # 写回文件
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ 配置文件已更新")
                return True
        else:
            create = input(f"\n是否创建 {env_file} 配置文件? (y/N): ").lower().strip()
            if create == 'y':
                config_content = "# Translate Node 配置\n"
                for key, value in recommended_config.items():
                    config_content += f"{key}={value}\n"
                
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                
                print(f"✓ 配置文件已创建")
                return True
        
        print("跳过配置文件更新")
        return True
        
    except Exception as e:
        print(f"✗ 配置更新失败: {e}")
        return False

def main():
    """主函数"""
    print("Windows PyTorch GPU修复工具")
    print("=" * 60)
    
    # 检查系统
    is_windows = check_system()
    if not is_windows:
        print("⚠ 此脚本专为Windows设计")
        return
    
    # 检查CUDA
    cuda_installed = check_cuda_installation()
    if cuda_installed:
        get_cuda_version()
    else:
        print("⚠ 建议先安装NVIDIA驱动和CUDA工具包")
        proceed = input("是否继续安装CPU版本的PyTorch? (y/N): ").lower().strip()
        if proceed != 'y':
            return
    
    # 卸载当前PyTorch
    uninstall_current_pytorch()
    
    # 安装新的PyTorch
    pytorch_installed = install_pytorch_gpu()
    if not pytorch_installed:
        print("✗ PyTorch安装失败")
        return
    
    # 测试PyTorch
    pytorch_gpu_ok = test_pytorch_gpu()
    
    # 测试faster-whisper
    faster_whisper_ok = test_faster_whisper()
    
    # 更新配置
    config_ok = update_environment_config()
    
    # 总结
    print("\n" + "=" * 60)
    print("修复总结")
    print("=" * 60)
    print(f"CUDA驱动: {'✓' if cuda_installed else '✗'}")
    print(f"PyTorch GPU: {'✓' if pytorch_gpu_ok else '✗'}")
    print(f"Faster-Whisper: {'✓' if faster_whisper_ok else '✗'}")
    print(f"配置更新: {'✓' if config_ok else '✗'}")
    
    if pytorch_gpu_ok and faster_whisper_ok:
        print("\n🎉 GPU支持修复完成！")
        print("\n下一步:")
        print("1. 重启translate_node服务")
        print("2. 运行 python test_gpu_support.py 验证结果")
    elif pytorch_installed:
        print("\n⚠️ PyTorch已安装但GPU支持可能有问题")
        print("建议检查NVIDIA驱动和CUDA版本兼容性")
    else:
        print("\n❌ 修复失败，请检查错误信息")

if __name__ == "__main__":
    main() 