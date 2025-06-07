<?php

namespace app\controller;

use support\Request;
use app\api\model\TaskInfo;
use app\api\model\Task;
use app\service\RabbitMQ;

/**
 * 队列控制器
 * 用于处理队列任务，和接受任务回调
 */
class QueueController
{
    /**
     * 定义task_info表step状态常量
     */
    const STATUS_NULL = 0; //空任务
    const STATUS_WAIT_EXTRACT = 1; //等待提取音频
    const STATUS_WAIT_CONVERT = 2; //等待语音降噪
    const STATUS_WAIT_FAST_RECOGNITION = 3; //等待快速识别
    const STATUS_WAIT_TEXT_CONVERT = 4; //等待文本转写
    const STATUS_CONVERT_COMPLETED = 5; //转写完成
    const STATUS_PROCESSING = 6; //处理中

    /**
     * 定义task表status状态常量
     */
    const TASK_STATUS_EMPTY = 1; //空任务
    const TASK_STATUS_CHECKED = 2; //已检测
    const TASK_STATUS_CONVERTED = 3; //已转写
    const TASK_STATUS_PROCESSING = 4; //处理中
    const TASK_STATUS_PAUSED = 5; //已暂停

    /**
     * 定义任务类型常量
     */
    const TASK_TYPE_EXTRACT = 1; //提取音频
    const TASK_TYPE_CONVERT = 2; //语音降噪
    const TASK_TYPE_FAST_RECOGNITION = 3; //快速识别
    const TASK_TYPE_TEXT_CONVERT = 4; //文本转写

    /**
     * 用户提交的任务流类型常量
     */
    const TASK_FLOW_FAST = 1; //快速识别流程:提取音频+语音降噪+快速识别
    const TASK_FLOW_FULL = 2; //完整流程:提取音频+语音降噪+文本转写

    /**
     * 任务文件类型常量
     */
    const TASK_FILE_TYPE_AUDIO = 1; //音频
    const TASK_FILE_TYPE_VIDEO = 2; //视频


    /**
     * 将任务提交到队列
     */
    public function pushTaskToQueue(Request $request)
    {
        //需要任务id 和 任务类型
        $taskId = $request->input('task_id');
        $taskFlow = $request->input('task_flow');
        //判断流程是否存在
        if (!in_array($taskFlow, [self::TASK_FLOW_FAST, self::TASK_FLOW_FULL])) {
            return jsons(400, '任务流程不存在');
        }
        //判断任务是否存在
        $task = Task::find($taskId);
        if (!$task) {
            return jsons(400, '任务不存在');
        }
        //选择所有任务阶段为 0的任务
        $taskInfo = TaskInfo::where('tid', $taskId)->where('step', self::STATUS_NULL)->select();
        if ($taskInfo->isEmpty()) {
            return jsons(400, '待处理任务不存在');
        }
        try {
            //遍历任务
            foreach ($taskInfo as $item) {
                //直接调用音频提取方法
                $result = $this->pushTaskToQueueByVideo($item);
                if ($result !== true) {
                    return jsons(400, $result);
                }
                
            }
        } catch (\Exception $e) {
            return jsons(400, $e->getMessage());
        }


    }

    /**
     * 音频提取方法
     * 如果是视频，那么就先推送到提取音频队列,音频不处理
     * 传参是任务详情
     */
    private function pushTaskToQueueByVideo($taskInfoItem)
    {
        //判断任务文件是否已经提取
        //是 =1 否 =2
        if ($taskInfoItem->is_extract == 2) {
            $publishData = [
                'task_id' => $taskInfoItem->id,
                'task_url' => $taskInfoItem->url,
            ];
            //推送到提取音频队列
            try {
                $rabbitMQ = new RabbitMQ();
                $rabbitMQ->publishMessage('extract_audio', $publishData);
                return true;
            } catch (\Exception $e) {
                return $e->getMessage();
            }
        } else if ($taskInfoItem->is_extract == 1) {
            return true;
        }
        return false;
    }

    /**
     * 测试接口
     */
    public function test(Request $request)
    {
        $taskId = $request->input('task_id');
        $task = Task::find($taskId);
        if (!$task) {
            return jsons(400, '任务不存在');
        }
    }
}
