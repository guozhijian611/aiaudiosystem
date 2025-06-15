<?php

namespace app\constants;

/**
 * 队列系统常量定义类
 * 
 * 包含队列系统中使用的所有常量定义，包括：
 * - 队列名称
 * - 任务步骤状态
 * - 任务表状态
 * - 任务类型
 * - 任务流程类型
 * - 文件类型
 * - 是否状态值
 * 
 * @package app\constants
 * @author 系统管理员
 * @since 1.0.0
 */
class QueueConstants
{
    // ==================== 队列名称常量 ====================

    /**
     * 语音提取任务队列名称
     * @const string
     */
    const QUEUE_VOICE_EXTRACT = 'voice_extract_queue';

    /**
     * 音频降噪任务队列名称
     * @const string
     */
    const QUEUE_AUDIO_CLEAR = 'audio_clear_queue';

    /**
     * 快速识别任务队列名称
     * @const string
     */
    const QUEUE_FAST_PROCESS = 'fast_process_queue';

    /**
     * 文本转写任务队列名称
     * @const string
     */
    const QUEUE_TRANSCRIBE = 'transcribe_queue';

    // ==================== 任务步骤状态常量 ====================

    /**
     * 文件已上传，等待处理
     * @const int
     */
    const STEP_UPLOADED = 0;

    /**
     * 正在提取音频
     * @const int
     */
    const STEP_EXTRACTING = 1;

    /**
     * 音频提取完成，等待降噪
     * @const int
     */
    const STEP_EXTRACT_COMPLETED = 2;

    /**
     * 正在音频降噪
     * @const int
     */
    const STEP_CLEARING = 3;

    /**
     * 音频降噪完成，等待下一步处理
     * @const int
     */
    const STEP_CLEAR_COMPLETED = 4;

    /**
     * 正在快速识别
     * @const int
     */
    const STEP_FAST_RECOGNIZING = 5;

    /**
     * 快速识别完成，等待用户选择是否转写
     * @const int
     */
    const STEP_FAST_COMPLETED = 6;

    /**
     * 正在文本转写
     * @const int
     */
    const STEP_TRANSCRIBING = 7;

    /**
     * 所有处理完成
     * @const int
     */
    const STEP_ALL_COMPLETED = 8;

    /**
     * 处理失败
     * @const int
     */
    const STEP_FAILED = 9;

    /**
     * 任务暂停
     * @const int
     */
    const STEP_PAUSED = 10;

    /**
     * 未降噪转写
     * @const int
     */
    const STEP_UNCLEAR_TRANSCRIBE = 11;
    // ==================== 任务表状态常量 ====================

    /**
     * 空任务状态
     * @const int
     */
    const TASK_STATUS_EMPTY = 1;

    /**
     * 已检测状态
     * @const int
     */
    const TASK_STATUS_CHECKED = 2;

    /**
     * 已转写状态
     * @const int
     */
    const TASK_STATUS_CONVERTED = 3;

    /**
     * 处理中状态
     * @const int
     */
    const TASK_STATUS_PROCESSING = 4;

    /**
     * 已暂停状态
     * @const int
     */
    const TASK_STATUS_PAUSED = 5;

    // ==================== 任务类型常量 ====================

    /**
     * 提取音频任务类型
     * @const int
     */
    const TASK_TYPE_EXTRACT = 1;

    /**
     * 语音降噪任务类型
     * @const int
     */
    const TASK_TYPE_CONVERT = 2;

    /**
     * 快速识别任务类型
     * @const int
     */
    const TASK_TYPE_FAST_RECOGNITION = 3;

    /**
     * 文本转写任务类型
     * @const int
     */
    const TASK_TYPE_TEXT_CONVERT = 4;

    // ==================== 任务流程类型常量 ====================

    /**
     * 快速识别流程：提取音频+语音降噪+快速识别
     * @const int
     */
    const TASK_FLOW_FAST = 1;

    /**
     * 完整流程：提取音频+语音降噪+文本转写
     * @const int
     */
    const TASK_FLOW_FULL = 2;

    // ==================== 文件类型常量 ====================

    /**
     * 音频文件类型
     * @const int
     */
    const TASK_FILE_TYPE_AUDIO = 1;

    /**
     * 视频文件类型
     * @const int
     */
    const TASK_FILE_TYPE_VIDEO = 2;

    // ==================== 是否状态常量 ====================

    /**
     * 是状态值
     * @const int
     */
    const STATUS_YES = 1;

    /**
     * 否状态值
     * @const int
     */
    const STATUS_NO = 2;

    // ==================== 辅助方法 ====================

    /**
     * 获取所有队列名称
     * @return array
     */
    public static function getAllQueues(): array
    {
        return [
            self::QUEUE_VOICE_EXTRACT,
            self::QUEUE_AUDIO_CLEAR,
            self::QUEUE_FAST_PROCESS,
            self::QUEUE_TRANSCRIBE,
        ];
    }

    /**
     * 获取所有步骤状态
     * @return array
     */
    public static function getAllSteps(): array
    {
        return [
            self::STEP_UPLOADED,
            self::STEP_EXTRACTING,
            self::STEP_EXTRACT_COMPLETED,
            self::STEP_CLEARING,
            self::STEP_CLEAR_COMPLETED,
            self::STEP_FAST_RECOGNIZING,
            self::STEP_FAST_COMPLETED,
            self::STEP_TRANSCRIBING,
            self::STEP_ALL_COMPLETED,
            self::STEP_FAILED,
            self::STEP_PAUSED,
        ];
    }

    /**
     * 获取正在处理中的步骤状态
     * @return array
     */
    public static function getProcessingSteps(): array
    {
        return [
            self::STEP_EXTRACTING,
            self::STEP_CLEARING,
            self::STEP_FAST_RECOGNIZING,
            self::STEP_TRANSCRIBING,
        ];
    }

    /**
     * 获取步骤状态的中文描述
     * @param int $step
     * @return string
     */
    public static function getStepDescription(int $step): string
    {
        $descriptions = [
            self::STEP_UPLOADED => '文件已上传，等待处理',
            self::STEP_EXTRACTING => '正在提取音频',
            self::STEP_EXTRACT_COMPLETED => '音频提取完成，等待降噪',
            self::STEP_CLEARING => '正在音频降噪',
            self::STEP_CLEAR_COMPLETED => '音频降噪完成，等待下一步处理',
            self::STEP_FAST_RECOGNIZING => '正在快速识别',
            self::STEP_FAST_COMPLETED => '快速识别完成，等待用户选择是否转写',
            self::STEP_TRANSCRIBING => '正在文本转写',
            self::STEP_ALL_COMPLETED => '所有处理完成',
            self::STEP_FAILED => '处理失败',
            self::STEP_PAUSED => '任务暂停',
            self::STEP_UNCLEAR_TRANSCRIBE => '未降噪转写',
        ];

        return $descriptions[$step] ?? '未知状态';
    }

    /**
     * 检查步骤是否为处理中状态
     * @param int $step
     * @return bool
     */
    public static function isProcessingStep(int $step): bool
    {
        return in_array($step, self::getProcessingSteps());
    }

    /**
     * 检查任务流程类型是否有效
     * @param int $flow
     * @return bool
     */
    public static function isValidTaskFlow(int $flow): bool
    {
        return in_array($flow, [self::TASK_FLOW_FAST, self::TASK_FLOW_FULL]);
    }

    /**
     * 检查任务类型是否有效
     * @param int $type
     * @return bool
     */
    public static function isValidTaskType(int $type): bool
    {
        return in_array($type, [
            self::TASK_TYPE_EXTRACT,
            self::TASK_TYPE_CONVERT,
            self::TASK_TYPE_FAST_RECOGNITION,
            self::TASK_TYPE_TEXT_CONVERT,
        ]);
    }
} 