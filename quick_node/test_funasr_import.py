#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试本地FunASR导入
"""

import sys
import os

# 添加本地FunASR路径
current_dir = os.path.dirname(__file__)
funasr_path = os.path.join(current_dir, 'FunASR')

print(f"当前目录: {current_dir}")
print(f"FunASR路径: {funasr_path}")
print(f"FunASR目录存在: {os.path.exists(funasr_path)}")

if os.path.exists(funasr_path):
    sys.path.insert(0, funasr_path)
    print(f"已添加FunASR路径到sys.path")

print("\nPython路径:")
for i, path in enumerate(sys.path[:5]):  # 只显示前5个路径
    print(f"  {i}: {path}")

print("\n测试导入FunASR...")

try:
    from funasr import AutoModel
    print("✅ 成功导入 funasr.AutoModel")
    
    # 测试模型初始化（不实际加载模型）
    print("\n测试模型信息...")
    print("✅ FunASR导入测试成功！")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n可能的解决方案:")
    print("1. 确保FunASR目录存在且包含funasr包")
    print("2. 在FunASR目录下运行: pip install -e .")
    print("3. 检查FunASR/funasr/__init__.py文件是否存在")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")

print("\n检查FunASR目录结构...")
if os.path.exists(funasr_path):
    funasr_package_path = os.path.join(funasr_path, 'funasr')
    funasr_init_path = os.path.join(funasr_package_path, '__init__.py')
    
    print(f"funasr包目录存在: {os.path.exists(funasr_package_path)}")
    print(f"funasr/__init__.py存在: {os.path.exists(funasr_init_path)}")
    
    if os.path.exists(funasr_package_path):
        print("\nfunasr包内容:")
        try:
            files = os.listdir(funasr_package_path)[:10]  # 只显示前10个文件
            for file in files:
                print(f"  - {file}")
        except Exception as e:
            print(f"  无法列出文件: {e}")
else:
    print("FunASR目录不存在，请检查路径") 