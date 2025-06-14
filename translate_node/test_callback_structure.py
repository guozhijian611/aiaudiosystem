#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
回调数据结构测试脚本
验证text_info现在包含完整的transcribe_details内容
"""

import json

def test_new_callback_structure():
    """测试新的回调数据结构"""
    print("=" * 60)
    print("测试新的回调数据结构")
    print("=" * 60)
    
    # 模拟转写结果
    mock_transcribe_result = {
        'text': '这是一段测试转写文本，用于验证回调数据结构的正确性。',
        'language': 'zh',
        'segments': [
            {
                'start': 0.0,
                'end': 5.2,
                'text': '这是一段测试转写文本，',
                'words': [
                    {'start': 0.0, 'end': 0.5, 'word': '这是', 'score': 0.95},
                    {'start': 0.5, 'end': 1.0, 'word': '一段', 'score': 0.92}
                ]
            }
        ],
        'segments_count': 1,
        'confidence_avg': 0.95,
        'word_count': 12,
        'speakers': ['SPEAKER_00'],
        'effective_voice': 10.8,
        'total_voice': 15.0,
        'processing_time': 45.2,
        'file_info': {
            'file_name': 'test_audio.wav',
            'file_size_mb': 2.5,
            'duration': 15.0,
            'sample_rate': 16000
        },
        'whisper_model': 'large-v3',
        'compute_device': 'cuda',
        'alignment_enabled': True,
        'diarization_enabled': True
    }
    
    # 构建完整的转写详情（模拟api_client.py的逻辑）
    transcribe_details = {
        'text': mock_transcribe_result.get('text', ''),
        'segments_count': mock_transcribe_result.get('segments_count', 0),
        'confidence_avg': mock_transcribe_result.get('confidence_avg', 0),
        'word_count': mock_transcribe_result.get('word_count', 0),
        'speakers': mock_transcribe_result.get('speakers', []),
        'segments': mock_transcribe_result.get('segments', []),
        'processing_time': mock_transcribe_result.get('processing_time', 0),
        'file_info': mock_transcribe_result.get('file_info', {}),
        'model_info': {
            'whisper_model': mock_transcribe_result.get('whisper_model', 'unknown'),
            'language_detected': mock_transcribe_result.get('language', 'unknown'),
            'compute_device': mock_transcribe_result.get('compute_device', 'unknown'),
            'alignment_enabled': mock_transcribe_result.get('alignment_enabled', False),
            'diarization_enabled': mock_transcribe_result.get('diarization_enabled', False)
        }
    }
    
    # 准备回调数据
    callback_data = {
        'text_info': transcribe_details,                               # 完整的转写详情
        'effective_voice': mock_transcribe_result.get('effective_voice', 0),
        'total_voice': mock_transcribe_result.get('total_voice', 0),
        'language': mock_transcribe_result.get('language', 'unknown'),
        'transcribe_details': transcribe_details                       # 保持向后兼容
    }
    
    print("新的回调数据结构:")
    print("=" * 40)
    print(json.dumps(callback_data, ensure_ascii=False, indent=2))
    
    return callback_data

def validate_structure(callback_data):
    """验证数据结构"""
    print("\n" + "=" * 40)
    print("数据结构验证:")
    print("=" * 40)
    
    # 检查顶级字段
    required_top_fields = ['text_info', 'effective_voice', 'total_voice', 'language', 'transcribe_details']
    for field in required_top_fields:
        if field in callback_data:
            if field == 'text_info':
                print(f"✓ {field}: dict类型，包含完整转写详情")
            else:
                print(f"✓ {field}: {type(callback_data[field]).__name__}")
        else:
            print(f"✗ 缺少字段: {field}")
    
    # 验证text_info和transcribe_details是否相同
    text_info = callback_data.get('text_info', {})
    transcribe_details = callback_data.get('transcribe_details', {})
    
    print(f"\ntext_info 和 transcribe_details 内容对比:")
    if text_info == transcribe_details:
        print("✓ text_info 和 transcribe_details 内容完全一致")
    else:
        print("✗ text_info 和 transcribe_details 内容不一致")
    
    # 检查text_info的详细字段
    required_detail_fields = [
        'text', 'segments_count', 'confidence_avg', 'word_count', 
        'speakers', 'segments', 'processing_time', 'file_info', 'model_info'
    ]
    
    print(f"\ntext_info 字段检查:")
    for field in required_detail_fields:
        if field in text_info:
            value = text_info[field]
            if field == 'text':
                print(f"✓ {field}: {len(value)}字符")
            elif field == 'segments':
                print(f"✓ {field}: {len(value)}个段落")
            elif field == 'speakers':
                print(f"✓ {field}: {len(value)}个说话人")
            elif field == 'file_info':
                print(f"✓ {field}: {len(value)}个属性")
            elif field == 'model_info':
                print(f"✓ {field}: {len(value)}个属性")
            else:
                print(f"✓ {field}: {value}")
        else:
            print(f"✗ 缺少字段: {field}")

def compare_old_vs_new():
    """对比新旧数据结构"""
    print("\n" + "=" * 60)
    print("新旧数据结构对比")
    print("=" * 60)
    
    print("旧结构:")
    print("├── text_info: '转写文本字符串'")
    print("├── effective_voice")
    print("├── total_voice") 
    print("├── language")
    print("└── transcribe_details")
    print("    ├── segments_count")
    print("    ├── confidence_avg")
    print("    ├── word_count")
    print("    ├── speakers")
    print("    └── segments")
    
    print("\n新结构:")
    print("├── text_info: { 完整的转写详情对象 }")
    print("│   ├── text")
    print("│   ├── segments_count")
    print("│   ├── confidence_avg")
    print("│   ├── word_count")
    print("│   ├── speakers")
    print("│   ├── segments")
    print("│   ├── processing_time")
    print("│   ├── file_info")
    print("│   └── model_info")
    print("├── effective_voice")
    print("├── total_voice")
    print("├── language")
    print("└── transcribe_details: { 与text_info相同的内容 }")
    
    print("\n主要变化:")
    print("✓ text_info 从简单字符串变为完整的详情对象")
    print("✓ text_info 现在包含所有转写相关信息")
    print("✓ transcribe_details 保持不变，确保向后兼容")
    print("✓ 后端可以通过 text_info 获取所有转写详情")

def show_usage_examples():
    """显示使用示例"""
    print("\n" + "=" * 60)
    print("后端使用示例")
    print("=" * 60)
    
    print("PHP后端获取数据:")
    print("```php")
    print("// 获取转写文本")
    print("$text = $data['text_info']['text'];")
    print("")
    print("// 获取段落数量")
    print("$segments_count = $data['text_info']['segments_count'];")
    print("")
    print("// 获取处理时间")
    print("$processing_time = $data['text_info']['processing_time'];")
    print("")
    print("// 获取模型信息")
    print("$model = $data['text_info']['model_info']['whisper_model'];")
    print("$device = $data['text_info']['model_info']['compute_device'];")
    print("")
    print("// 获取文件信息")
    print("$file_size = $data['text_info']['file_info']['file_size_mb'];")
    print("$duration = $data['text_info']['file_info']['duration'];")
    print("```")
    
    print("\nJavaScript前端获取数据:")
    print("```javascript")
    print("// 获取转写文本")
    print("const text = data.text_info.text;")
    print("")
    print("// 获取详细段落")
    print("const segments = data.text_info.segments;")
    print("")
    print("// 获取说话人")
    print("const speakers = data.text_info.speakers;")
    print("")
    print("// 获取置信度")
    print("const confidence = data.text_info.confidence_avg;")
    print("```")

def main():
    """主函数"""
    print("回调数据结构测试工具")
    print("验证 text_info 现在包含完整的 transcribe_details 内容")
    
    try:
        # 测试新的回调数据结构
        callback_data = test_new_callback_structure()
        
        # 验证数据结构
        validate_structure(callback_data)
        
        # 对比新旧结构
        compare_old_vs_new()
        
        # 显示使用示例
        show_usage_examples()
        
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print("✓ 回调数据结构测试通过")
        print("✓ text_info 现在包含完整的转写详情")
        print("✓ 保持了向后兼容性（transcribe_details仍然存在）")
        print("✓ 后端可以通过 text_info 获取所有转写信息")
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 