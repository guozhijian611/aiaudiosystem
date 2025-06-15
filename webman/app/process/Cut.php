<?php
namespace app\process;

use Workerman\Timer;
use app\api\model\TaskInfo;
use app\service\RabbitMQ;
use app\constants\QueueConstants;

class Cut
{
    // 启动时自动定时扫描
    public function onWorkerStart()
    {
        // 每10秒扫描一次
        Timer::add(10, function () {
            $this->scanAndPush();
        });
    }

    // 扫描并推送到cut队列
    protected function scanAndPush()
    {
        // 只查找step=0（已上传/未处理）的任务，避免重复推送
        $tasks = TaskInfo::where('step', QueueConstants::STEP_UPLOADED)
            ->select();

        if ($tasks->isEmpty()) {
            return;
        }

        foreach ($tasks as $task) {
            try {
                // 推送到cut队列（voice_extract_queue）
                $rabbitMQ = new RabbitMQ();
                $rabbitMQ->publishMessage(
                    QueueConstants::QUEUE_VOICE_EXTRACT,
                    [
                        'task_info' => $task->toArray()
                    ]
                );
                // 推送后立即将step设为1（正在提取音频），防止并发重复推送
                $task->step = QueueConstants::STEP_EXTRACTING;
                $task->save();
                echo "推送到cut队列成功: task_info_id={$task->id}\n";
            } catch (\Exception $e) {
                echo "推送cut队列失败: task_info_id={$task->id}, 错误: {$e->getMessage()}\n";
            }
        }
    }
}
