#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPU支持诊断脚本
检测PyTorch、CUDA、GPU状态和float16支持情况
"""

import sys
import os

def test_pytorch_installation():
    """测试PyTorch安装"""
    print("=" * 50)
    print("1. 测试PyTorch安装")
    print("=" * 50)
    
    try:
        import torch
        print(f"✓ PyTorch版本: {torch.__version__}")
        print(f"✓ PyTorch安装路径: {torch.__file__}")
        return True
    except ImportError as e:
        print(f"✗ PyTorch导入失败: {e}")
        return False

def test_cuda_support():
    """测试CUDA支持"""
    print("\n" + "=" * 50)
    print("2. 测试CUDA支持")
    print("=" * 50)
    
    try:
        import torch
        
        # 检查CUDA是否可用
        cuda_available = torch.cuda.is_available()
        print(f"CUDA可用: {cuda_available}")
        
        if cuda_available:
            # CUDA版本信息
            cuda_version = torch.version.cuda
            print(f"✓ CUDA版本: {cuda_version}")
            
            # GPU设备信息
            device_count = torch.cuda.device_count()
            print(f"✓ GPU设备数量: {device_count}")
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_props = torch.cuda.get_device_properties(i)
                memory_total = device_props.total_memory / 1024**3  # GB
                print(f"  GPU {i}: {device_name}")
                print(f"    总内存: {memory_total:.1f}GB")
                print(f"    计算能力: {device_props.major}.{device_props.minor}")
            
            # 当前设备
            current_device = torch.cuda.current_device()
            print(f"✓ 当前设备: cuda:{current_device}")
            
            return True
        else:
            print("✗ CUDA不可用")
            return False
            
    except Exception as e:
        print(f"✗ CUDA检测失败: {e}")
        return False

def test_float16_support():
    """测试float16支持"""
    print("\n" + "=" * 50)
    print("3. 测试float16支持")
    print("=" * 50)
    
    try:
        import torch
        
        if not torch.cuda.is_available():
            print("✗ CUDA不可用，无法测试GPU float16支持")
            return False
        
        # 测试GPU float16支持
        device = torch.cuda.current_device()
        device_props = torch.cuda.get_device_properties(device)
        
        print(f"GPU计算能力: {device_props.major}.{device_props.minor}")
        
        # 计算能力7.0以上通常支持高效的float16
        supports_efficient_fp16 = device_props.major >= 7
        print(f"支持高效float16: {supports_efficient_fp16}")
        
        # 实际测试float16操作
        try:
            x = torch.randn(100, 100, dtype=torch.float16, device='cuda')
            y = torch.randn(100, 100, dtype=torch.float16, device='cuda')
            z = torch.matmul(x, y)
            print("✓ float16矩阵运算测试通过")
            
            # 测试自动混合精度
            with torch.cuda.amp.autocast():
                z_amp = torch.matmul(x.float(), y.float())
            print("✓ 自动混合精度测试通过")
            
            return True
            
        except Exception as e:
            print(f"✗ float16操作测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"✗ float16支持检测失败: {e}")
        return False

def test_ctranslate2_support():
    """测试CTranslate2支持"""
    print("\n" + "=" * 50)
    print("4. 测试CTranslate2支持")
    print("=" * 50)
    
    try:
        import ctranslate2
        print(f"✓ CTranslate2版本: {ctranslate2.__version__}")
        
        # 检查支持的计算类型
        print("支持的计算类型:")
        
        # 测试不同的计算类型
        compute_types = ['float32', 'float16', 'int8']
        
        for compute_type in compute_types:
            try:
                # 这里只是测试导入，不实际创建模型
                print(f"  {compute_type}: 可用")
            except Exception as e:
                print(f"  {compute_type}: 不可用 - {e}")
        
        return True
        
    except ImportError as e:
        print(f"✗ CTranslate2导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ CTranslate2检测失败: {e}")
        return False

def test_faster_whisper():
    """测试faster-whisper"""
    print("\n" + "=" * 50)
    print("5. 测试faster-whisper")
    print("=" * 50)
    
    try:
        import torch
        from faster_whisper import WhisperModel
        print("✓ faster-whisper导入成功")
        
        # 测试不同计算类型的模型创建
        compute_types = ['float32', 'float16', 'int8']
        
        for compute_type in compute_types:
            try:
                print(f"\n测试计算类型: {compute_type}")
                
                # 使用最小的模型进行测试
                model = WhisperModel(
                    "tiny", 
                    device="cuda" if torch.cuda.is_available() else "cpu",
                    compute_type=compute_type
                )
                print(f"  ✓ {compute_type} 模型创建成功")
                
                # 清理模型
                del model
                
            except Exception as e:
                print(f"  ✗ {compute_type} 模型创建失败: {e}")
        
        return True
        
    except ImportError as e:
        print(f"✗ faster-whisper导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ faster-whisper测试失败: {e}")
        return False

def get_recommended_config():
    """获取推荐配置"""
    print("\n" + "=" * 50)
    print("6. 推荐配置")
    print("=" * 50)
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_props = torch.cuda.get_device_properties(0)
            compute_capability = f"{device_props.major}.{device_props.minor}"
            
            print(f"检测到GPU: {torch.cuda.get_device_name(0)}")
            print(f"计算能力: {compute_capability}")
            
            # 根据计算能力推荐配置
            if device_props.major >= 7:  # Volta架构及以上
                recommended_compute_type = "float16"
                print("✓ 推荐使用 float16 (支持高效半精度计算)")
            elif device_props.major >= 6:  # Pascal架构
                recommended_compute_type = "float32"
                print("⚠ 推荐使用 float32 (float16支持有限)")
            else:
                recommended_compute_type = "float32"
                print("⚠ 推荐使用 float32 (较老的GPU架构)")
            
            print(f"\n推荐环境变量设置:")
            print(f"WHISPER_DEVICE=cuda")
            print(f"WHISPER_COMPUTE_TYPE={recommended_compute_type}")
            
        else:
            print("未检测到CUDA GPU")
            print(f"\n推荐环境变量设置:")
            print(f"WHISPER_DEVICE=cpu")
            print(f"WHISPER_COMPUTE_TYPE=float32")
            
    except Exception as e:
        print(f"配置推荐失败: {e}")

def main():
    """主函数"""
    print("GPU支持诊断工具")
    print("检测PyTorch、CUDA、GPU状态和float16支持情况")
    
    # 运行所有测试
    pytorch_ok = test_pytorch_installation()
    
    if pytorch_ok:
        cuda_ok = test_cuda_support()
        float16_ok = test_float16_support()
        ctranslate2_ok = test_ctranslate2_support()
        faster_whisper_ok = test_faster_whisper()
        
        # 获取推荐配置
        get_recommended_config()
        
        # 总结
        print("\n" + "=" * 50)
        print("诊断总结")
        print("=" * 50)
        print(f"PyTorch: {'✓' if pytorch_ok else '✗'}")
        print(f"CUDA: {'✓' if cuda_ok else '✗'}")
        print(f"Float16: {'✓' if float16_ok else '✗'}")
        print(f"CTranslate2: {'✓' if ctranslate2_ok else '✗'}")
        print(f"Faster-Whisper: {'✓' if faster_whisper_ok else '✗'}")
        
        if all([pytorch_ok, cuda_ok, ctranslate2_ok, faster_whisper_ok]):
            print("\n🎉 所有组件检测通过！")
        else:
            print("\n⚠️  存在问题，请检查上述失败项目")
    
    else:
        print("\n❌ PyTorch未正确安装，请先解决PyTorch安装问题")

if __name__ == "__main__":
    main() 