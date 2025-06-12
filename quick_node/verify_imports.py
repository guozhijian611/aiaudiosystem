#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证所有文件的FunASR导入是否正常
"""

import sys
import os
import importlib.util

def test_file_import(file_path, description):
    """测试单个文件的导入"""
    print(f"\n测试 {description}: {file_path}")
    
    try:
        # 动态导入文件
        spec = importlib.util.spec_from_file_location("test_module", file_path)
        if spec is None:
            print(f"❌ 无法创建模块规范")
            return False
            
        module = importlib.util.module_from_spec(spec)
        
        # 执行导入（但不执行主代码）
        original_name = getattr(module, '__name__', None)
        module.__name__ = 'test_module'  # 避免执行 if __name__ == "__main__"
        
        spec.loader.exec_module(module)
        
        print(f"✅ 导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Quick Node FunASR 导入验证")
    print("=" * 60)
    
    # 添加本地FunASR路径
    current_dir = os.path.dirname(__file__)
    funasr_path = os.path.join(current_dir, 'FunASR')
    if os.path.exists(funasr_path):
        sys.path.insert(0, funasr_path)
        print(f"✅ 已添加本地FunASR路径: {funasr_path}")
    else:
        print(f"❌ 本地FunASR路径不存在: {funasr_path}")
        return
    
    # 添加src目录
    src_path = os.path.join(current_dir, 'src')
    sys.path.insert(0, src_path)
    
    # 测试文件列表
    test_files = [
        ("src/vad_analyzer.py", "VAD分析器"),
        ("src/api_client.py", "API客户端"),
        ("src/queue_consumer.py", "队列消费者"),
        ("config.py", "配置文件"),
    ]
    
    success_count = 0
    total_count = len(test_files)
    
    for file_path, description in test_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            if test_file_import(full_path, description):
                success_count += 1
        else:
            print(f"\n❌ 文件不存在: {file_path}")
    
    print("\n" + "=" * 60)
    print(f"验证结果: {success_count}/{total_count} 文件导入成功")
    
    if success_count == total_count:
        print("🎉 所有文件导入验证通过！")
    else:
        print("⚠️  部分文件导入失败，请检查依赖和路径设置")
    
    # 额外测试：直接导入FunASR
    print("\n" + "=" * 30)
    print("直接测试FunASR导入:")
    try:
        from funasr import AutoModel
        print("✅ FunASR.AutoModel 导入成功")
    except Exception as e:
        print(f"❌ FunASR.AutoModel 导入失败: {e}")

if __name__ == "__main__":
    main() 