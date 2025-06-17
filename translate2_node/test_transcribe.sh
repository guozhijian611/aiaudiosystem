#!/bin/bash

# Translate2 Node 转写测试脚本

echo "================================================"
echo "    Translate2 Node 转写测试脚本"
echo "================================================"

# 检查参数
if [ $# -eq 0 ]; then
    echo "使用方法: ./test_transcribe.sh <音频文件路径>"
    echo "示例: ./test_transcribe.sh test.wav"
    echo "示例: ./test_transcribe.sh /path/to/audio.mp3"
    exit 1
fi

AUDIO_FILE="$1"

# 检查文件是否存在
if [ ! -f "$AUDIO_FILE" ]; then
    echo "错误: 音频文件不存在 - $AUDIO_FILE"
    exit 1
fi

echo "音频文件: $AUDIO_FILE"

# 创建输出目录
mkdir -p output

# 生成输出文件名
BASE_NAME=$(basename "$AUDIO_FILE" | sed 's/\.[^.]*$//')
OUTPUT_FILE="output/${BASE_NAME}_transcribe.json"

echo "输出文件: $OUTPUT_FILE"
echo

# 执行转写测试
echo "开始转写测试..."
python test_local_transcribe.py "$AUDIO_FILE" -o "$OUTPUT_FILE" -v

if [ $? -eq 0 ]; then
    echo
    echo "================================================"
    echo "转写测试成功完成！"
    echo "================================================"
    echo "结果文件:"
    echo "  JSON: $OUTPUT_FILE"
    echo "  SRT: ${OUTPUT_FILE%.json}.srt"
    echo
    
    # 检查是否有图形界面
    if command -v xdg-open >/dev/null 2>&1; then
        echo "是否打开结果文件？(y/N)"
        read -r OPEN_RESULT
        if [[ $OPEN_RESULT =~ ^[Yy]$ ]]; then
            xdg-open "$OUTPUT_FILE" 2>/dev/null &
            xdg-open "${OUTPUT_FILE%.json}.srt" 2>/dev/null &
        fi
    elif command -v open >/dev/null 2>&1; then
        echo "是否打开结果文件？(y/N)"
        read -r OPEN_RESULT
        if [[ $OPEN_RESULT =~ ^[Yy]$ ]]; then
            open "$OUTPUT_FILE" 2>/dev/null &
            open "${OUTPUT_FILE%.json}.srt" 2>/dev/null &
        fi
    fi
else
    echo
    echo "================================================"
    echo "转写测试失败！"
    echo "================================================"
fi 