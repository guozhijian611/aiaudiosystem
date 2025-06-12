#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("测试配置加载")
    print("=" * 60)
    
    # 显示原始环境变量
    print("原始环境变量:")
    env_vars = ['DISABLE_UPDATE', 'VAD_MODEL', 'VAD_MODEL_REVISION']
    for var in env_vars:
        value = os.getenv(var)
        print(f"  {var} = {repr(value)}")
    
    print("\n" + "-" * 40)
    
    # 加载配置
    try:
        from config import Config
        
        print("配置类加载后:")
        print(f"  Config.DISABLE_UPDATE = {repr(Config.DISABLE_UPDATE)} (类型: {type(Config.DISABLE_UPDATE)})")
        print(f"  Config.VAD_MODEL = {repr(Config.VAD_MODEL)}")
        print(f"  Config.VAD_MODEL_REVISION = {repr(Config.VAD_MODEL_REVISION)}")
        
        # 测试布尔值解析
        print(f"\n布尔值解析测试:")
        test_values = ['true', 'True', 'TRUE', 'false', 'False', 'FALSE', '1', '0', None]
        for val in test_values:
            parsed = str(val).lower() == 'true' if val else False
            print(f"  '{val}' -> {parsed}")
            
    except Exception as e:
        print(f"配置加载失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_config() 