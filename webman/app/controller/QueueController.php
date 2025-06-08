<?php

namespace app\controller;

use support\Request;
use app\api\model\TaskInfo;
use app\api\model\Task;
use app\service\RabbitMQ;
use app\constants\QueueConstants;

/**
 * 队列控制器
 * 用于处理队列任务，和接受任务回调
 */
class QueueController
{


    /**
     * 将任务提交到队列 - 主要入口方法
     * 
     * 功能说明：
     * 1. 接收用户提交的任务请求，包含任务ID和流程类型
     * 2. 验证任务存在性和流程类型有效性
     * 3. 查找所有待处理的任务详情（step=0的任务）
     * 4. 遍历每个任务详情，调用音频提取方法开始处理流程
     * 5. 支持两种流程：快速识别流程和完整转写流程
     * 
     * 工作流程：
     * - 快速识别流程：音频提取 → 音频降噪 → 快速识别 → 等待用户选择是否转写
     * - 完整转写流程：音频提取 → 音频降噪 → 直接文本转写
     * 
     * @param Request $request 请求对象
     * @param int $request->task_id 任务ID（必须）
     * @param int $request->task_flow 任务流程类型（必须）1=快速识别，2=完整流程
     * 
     * @return array JSON响应
     *   成功：{'code': 200, 'msg': '任务提交成功', 'data': null}
     *   失败：{'code': 400, 'msg': '错误信息', 'data': null}
     * 
     * @throws \Exception 当数据库操作失败或RabbitMQ连接失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    public function pushTaskToQueue(Request $request)
    {
        //需要任务id 和 任务类型
        $taskId = $request->input('task_id');
        $taskFlow = $request->input('task_flow');
        //判断流程是否存在
        if (!in_array($taskFlow, [QueueConstants::TASK_FLOW_FAST, QueueConstants::TASK_FLOW_FULL])) {
            return jsons(400, '任务流程不存在');
        }
        //判断任务是否存在
        $task = Task::find($taskId);
        if (!$task) {
            return jsons(400, '任务不存在');
        }
        //选择所有任务阶段为 0的任务
        $taskInfo = TaskInfo::where('tid', $taskId)->where('step', QueueConstants::STEP_UPLOADED)->select();
        if ($taskInfo->isEmpty()) {
            return jsons(400, '待处理任务不存在');
        }
        try {
            //遍历任务
            foreach ($taskInfo as $item) {
                //直接调用音频提取方法
                $result = $this->pushTaskToQueueByVideo($item, $taskFlow);
                if ($result !== true) {
                    return jsons(400, $result);
                }
                
            }
            
            return jsons(200, '任务提交成功');
        } catch (\Exception $e) {
            return jsons(400, $e->getMessage());
        }


    }

    /**
     * 音频提取处理方法 - 任务处理流程的起始点
     * 
     * 功能说明：
     * 1. 检查任务是否已被锁定，防止重复提交
     * 2. 判断文件类型和提取状态，决定是否需要音频提取
     * 3. 对于视频文件（is_extract=2），推送到音频提取队列
     * 4. 对于音频文件（is_extract=1），直接返回成功
     * 5. 更新任务状态为"正在提取音频"
     * 6. 异常处理：记录错误信息和重试次数
     * 
     * 业务逻辑：
     * - 视频文件：需要先提取音频 → 推送到voice_extract_queue
     * - 音频文件：无需提取 → 直接进入下一步
     * 
     * 状态流转：
     * STEP_UPLOADED(0) → STEP_EXTRACTING(1)
     * 
     * 队列数据格式：
     * {
     *   'task_id': 任务详情ID,
     *   'task_url': 原始文件URL
     * }
     * 
     * @param mixed $taskInfoItem 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - url: 原始文件URL
     *   - is_extract: 是否已提取音频（1=是，2=否）
     * @param int $taskFlow 任务流程类型
     *   - TASK_FLOW_FAST(1): 快速识别流程
     *   - TASK_FLOW_FULL(2): 完整转写流程
     * 
     * @return true|string 成功返回true，失败返回错误信息字符串
     * 
     * @throws \Exception 当RabbitMQ推送失败或数据库操作失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function pushTaskToQueueByVideo($taskInfoItem, $taskFlow = QueueConstants::TASK_FLOW_FAST)
    {
        // 检查任务锁
        if ($this->isTaskLocked($taskInfoItem->id)) {
            return '任务正在处理中，请勿重复提交';
        }

        //判断任务文件是否已经提取
        //是 =1 否 =2
        if ($taskInfoItem->is_extract == QueueConstants::STATUS_NO) {
            $publishData = [
                'task_id' => $taskInfoItem->id,
                'task_url' => $taskInfoItem->url,
            ];
            //推送到提取音频队列
            try {
                $rabbitMQ = new RabbitMQ();
                $rabbitMQ->publishMessage(QueueConstants::QUEUE_VOICE_EXTRACT, $publishData);
                
                //更新任务状态为正在提取音频
                $taskInfoItem->step = QueueConstants::STEP_EXTRACTING;
                $taskInfoItem->save();
                
                return true;
            } catch (\Exception $e) {
                //记录错误信息到数据库
                $taskInfoItem->error_msg = $e->getMessage();
                $taskInfoItem->retry_count = $taskInfoItem->retry_count + 1;
                $taskInfoItem->save();
                
                return $e->getMessage();
            }
        } else if ($taskInfoItem->is_extract == QueueConstants::STATUS_YES) {
            return true;
        }
        return false;
    }

    /**
     * 测试接口 - 用于开发和调试阶段的批量任务处理
     * 
     * 功能说明：
     * 1. 查找所有状态为"已上传"（step=0）的任务详情
     * 2. 批量调用音频提取方法，使用快速识别流程
     * 3. 主要用于开发调试和批量测试场景
     * 4. 不需要用户指定任务ID，自动处理所有待处理任务
     * 
     * 使用场景：
     * - 开发环境测试
     * - 批量处理历史积累的任务
     * - 系统调试和问题排查
     * 
     * 注意事项：
     * - 生产环境使用需谨慎，会处理所有待处理任务
     * - 默认使用快速识别流程
     * - 不进行权限验证和用户身份检查
     * 
     * @param Request $request 请求对象（本方法中未使用具体参数）
     * 
     * @return array JSON响应
     *   成功：{'code': 200, 'msg': '测试成功', 'data': null}
     *   失败：{'code': 400, 'msg': '待处理任务不存在', 'data': null}
     * 
     * @since 1.0.0
     * @author 系统管理员
     * @deprecated 建议仅在开发环境使用
     */
    public function test(Request $request)
    {
        $taskInfo = TaskInfo::where('step', QueueConstants::STEP_UPLOADED)->select();
        if ($taskInfo->isEmpty()) {
            return jsons(400, '待处理任务不存在');
        }
        foreach ($taskInfo as $item) {
            $this->pushTaskToQueueByVideo($item, QueueConstants::TASK_FLOW_FAST);
        }
        return jsons(200, '测试成功');
    }

    /**
     * 处理队列任务回调 - 接收外部队列处理结果的核心方法
     * 
     * 功能说明：
     * 1. 接收外部队列系统（如Python脚本、AI服务）的处理结果回调
     * 2. 验证回调参数的完整性和有效性
     * 3. 根据处理状态（成功/失败）调用相应的处理方法
     * 4. 更新任务状态并触发下一步流程
     * 5. 提供统一的错误处理和日志记录
     * 
     * 支持的任务类型：
     * - TASK_TYPE_EXTRACT(1): 音频提取任务
     * - TASK_TYPE_CONVERT(2): 音频降噪任务  
     * - TASK_TYPE_FAST_RECOGNITION(3): 快速识别任务
     * - TASK_TYPE_TEXT_CONVERT(4): 文本转写任务
     * 
     * 回调数据流程：
     * 外部处理系统 → HTTP回调 → 本方法 → 状态更新 → 触发下一步
     * 
     * 状态处理逻辑：
     * - success: 调用handleTaskSuccess()更新状态并触发下一步
     * - failed: 调用handleTaskFailed()记录错误信息
     * 
     * @param Request $request 回调请求对象
     * @param int $request->task_id 任务详情ID（必须）
     * @param int $request->task_type 任务类型（必须）
     * @param string $request->status 处理状态（必须）'success'或'failed'
     * @param string $request->message 消息内容（可选，失败时的错误信息）
     * @param array $request->data 处理结果数据（可选，成功时的结果数据）
     *   - voice_url: 提取的音频文件URL
     *   - clear_url: 降噪后的音频文件URL
     *   - text_info: 转写的文本内容
     *   - effective_voice: 有效语音时长
     *   - total_voice: 音频总时长
     *   - language: 识别的语言类型
     * 
     * @return array JSON响应
     *   成功：{'code': 200, 'msg': '回调处理成功', 'data': null}
     *   失败：{'code': 400, 'msg': '错误信息', 'data': null}
     * 
     * @throws \Exception 当任务查找失败或状态更新失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    public function handleTaskCallback(Request $request)
    {
        $taskId = $request->input('task_id');
        $taskType = $request->input('task_type');
        $status = $request->input('status'); // success 或 failed
        $message = $request->input('message', '');
        $data = $request->input('data', []);

        if (empty($taskId) || empty($taskType) || empty($status)) {
            return jsons(400, '缺少必要参数');
        }

        try {
            $taskInfo = TaskInfo::find($taskId);
            if (!$taskInfo) {
                return jsons(400, '任务不存在');
            }

            if ($status === 'success') {
                $this->handleTaskSuccess($taskInfo, $taskType, $data);
            } else {
                $this->handleTaskFailed($taskInfo, $taskType, $message);
            }

            return jsons(200, '回调处理成功');
        } catch (\Exception $e) {
            return jsons(400, '回调处理失败：' . $e->getMessage());
        }
    }

    /**
     * 处理任务成功回调 - 根据新工作流程的核心状态处理器
     * 
     * 功能说明：
     * 1. 根据不同的任务类型执行相应的成功处理逻辑
     * 2. 更新任务状态和相关数据字段
     * 3. 自动触发工作流程的下一个步骤
     * 4. 清空错误信息，标记任务处理正常
     * 
     * 任务类型处理逻辑：
     * 
     * TASK_TYPE_EXTRACT(音频提取)：
     * - 更新is_extract=1（已提取）
     * - 保存voice_url（提取后的音频URL）
     * - 状态：STEP_EXTRACT_COMPLETED(2)
     * - 触发：自动推送到音频降噪队列
     * 
     * TASK_TYPE_CONVERT(音频降噪)：
     * - 更新is_clear=1（已降噪）
     * - 保存clear_url（降噪后的音频URL）
     * - 状态：STEP_CLEAR_COMPLETED(4)
     * - 触发：根据用户流程选择推送到快速识别或转写队列
     * 
     * TASK_TYPE_FAST_RECOGNITION(快速识别)：
     * - 更新fast_status=1（已快速识别）
     * - 状态：STEP_FAST_COMPLETED(6)
     * - 触发：等待用户选择是否继续转写
     * 
     * TASK_TYPE_TEXT_CONVERT(文本转写)：
     * - 更新transcribe_status=1（已转写）
     * - 保存text_info、effective_voice、total_voice、language
     * - 状态：STEP_ALL_COMPLETED(8)
     * - 触发：任务完成，无后续操作
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     * @param int $taskType 任务类型常量
     * @param array $data 处理结果数据
     *   - voice_url: 音频文件URL（音频提取完成时）
     *   - clear_url: 降噪音频URL（音频降噪完成时）
     *   - text_info: 转写文本内容（转写完成时）
     *   - effective_voice: 有效语音时长（转写完成时）
     *   - total_voice: 音频总时长（转写完成时）
     *   - language: 识别语言类型（转写完成时）
     * 
     * @return void
     * 
     * @throws \Exception 当数据库操作失败或队列推送失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function handleTaskSuccess($taskInfo, $taskType, $data)
    {
        switch ($taskType) {
            case QueueConstants::TASK_TYPE_EXTRACT:
                // 音频提取完成
                $taskInfo->is_extract = QueueConstants::STATUS_YES;
                $taskInfo->voice_url = $data['voice_url'] ?? '';
                $taskInfo->step = QueueConstants::STEP_EXTRACT_COMPLETED;
                // 自动推送到音频降噪队列
                $this->pushToAudioClearQueue($taskInfo);
                break;
                
            case QueueConstants::TASK_TYPE_CONVERT:
                // 音频降噪完成
                $taskInfo->is_clear = QueueConstants::STATUS_YES;
                $taskInfo->clear_url = $data['clear_url'] ?? '';
                $taskInfo->step = QueueConstants::STEP_CLEAR_COMPLETED;
                // 根据用户选择的流程进行下一步
                $this->processNextStepAfterClear($taskInfo);
                break;
                
            case QueueConstants::TASK_TYPE_FAST_RECOGNITION:
                // 快速识别完成
                $taskInfo->fast_status = QueueConstants::STATUS_YES;
                $taskInfo->step = QueueConstants::STEP_FAST_COMPLETED;
                // 等待用户选择是否进行转写
                break;
                
            case QueueConstants::TASK_TYPE_TEXT_CONVERT:
                // 文本转写完成
                $taskInfo->transcribe_status = QueueConstants::STATUS_YES;
                $taskInfo->text_info = $data['text_info'] ?? '';
                $taskInfo->effective_voice = $data['effective_voice'] ?? '';
                $taskInfo->total_voice = $data['total_voice'] ?? '';
                $taskInfo->language = $data['language'] ?? '';
                $taskInfo->step = QueueConstants::STEP_ALL_COMPLETED;
                break;
        }

        $taskInfo->error_msg = '';
        $taskInfo->save();
    }

    /**
     * 处理任务失败回调 - 统一的错误处理机制
     * 
     * 功能说明：
     * 1. 记录任务处理失败的错误信息
     * 2. 增加重试计数器，用于统计失败次数
     * 3. 更新任务状态为"处理失败"
     * 4. 为后续的重试机制或人工干预提供数据支持
     * 
     * 处理逻辑：
     * - 保存详细的错误信息到error_msg字段
     * - 自动递增retry_count重试计数
     * - 将状态设置为STEP_FAILED(9)
     * - 停止当前任务的自动流程处理
     * 
     * 后续处理建议：
     * - 可根据retry_count实现自动重试机制
     * - 可设置重试上限，超限后转人工处理
     * - 可根据error_msg分析失败原因和解决方案
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     * @param int $taskType 任务类型常量（用于区分不同类型的失败）
     * @param string $message 错误信息详情
     * 
     * @return void
     * 
     * @throws \Exception 当数据库操作失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function handleTaskFailed($taskInfo, $taskType, $message)
    {
        $taskInfo->error_msg = $message;
        $taskInfo->retry_count += 1;
        $taskInfo->step = QueueConstants::STEP_FAILED;
        $taskInfo->save();
    }

    /**
     * 推送到音频降噪队列 - 音频提取完成后的自动流程
     * 
     * 功能说明：
     * 1. 音频提取完成后自动调用，无需用户手动触发
     * 2. 将提取后的音频文件推送到降噪处理队列
     * 3. 更新任务状态为"正在音频降噪"
     * 4. 提供完整的异常处理机制
     * 
     * 队列数据包含：
     * - task_id: 任务详情ID，用于回调时定位任务
     * - task_url: 提取后的音频文件URL（voice_url）
     * 
     * 状态流转：
     * STEP_EXTRACT_COMPLETED(2) → STEP_CLEARING(3)
     * 
     * 错误处理：
     * - RabbitMQ连接失败：记录错误，状态设为FAILED
     * - 数据库更新失败：记录错误信息和重试次数
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - voice_url: 提取后的音频文件URL
     * 
     * @return void
     * 
     * @throws \Exception 当RabbitMQ推送失败或数据库操作失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function pushToAudioClearQueue($taskInfo)
    {
        $publishData = [
            'task_id' => $taskInfo->id,
            'task_url' => $taskInfo->voice_url, // 使用提取后的音频URL
        ];

        try {
            $rabbitMQ = new RabbitMQ();
            $rabbitMQ->publishMessage(QueueConstants::QUEUE_AUDIO_CLEAR, $publishData);
            
            // 更新任务状态为正在降噪
            $taskInfo->step = QueueConstants::STEP_CLEARING;
            $taskInfo->save();
            
        } catch (\Exception $e) {
            // 记录错误信息
            $taskInfo->error_msg = $e->getMessage();
            $taskInfo->retry_count += 1;
            $taskInfo->step = QueueConstants::STEP_FAILED;
            $taskInfo->save();
        }
    }

    /**
     * 音频降噪完成后的流程分发器 - 根据用户选择决定后续处理路径
     * 
     * 功能说明：
     * 1. 音频降噪完成后的关键决策点
     * 2. 根据用户最初选择的任务流程类型进行分发
     * 3. 支持快速识别流程和完整转写流程两种路径
     * 4. 实现工作流程的自动化分支处理
     * 
     * 流程分支逻辑：
     * 
     * 快速识别流程（TASK_FLOW_FAST）：
     * - 推送到快速识别队列
     * - 目标：快速获得识别结果
     * - 后续：等待用户选择是否继续转写
     * 
     * 完整转写流程（TASK_FLOW_FULL）：
     * - 直接推送到文本转写队列
     * - 目标：一次性完成完整的转写处理
     * - 后续：任务完成
     * 
     * 注意事项：
     * - 当前实现为临时逻辑，使用默认快速流程
     * - 生产环境需要从任务表中读取用户的真实选择
     * - 建议在Task表中添加task_flow字段存储用户选择
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - tid: 关联的任务ID，用于查询任务配置
     *   - clear_url: 降噪后的音频文件URL
     * 
     * @return void
     * 
     * @throws \Exception 当任务查询失败或队列推送失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     * @todo 实现从数据库读取用户实际选择的流程类型
     */
    private function processNextStepAfterClear($taskInfo)
    {
        // 获取任务信息，判断用户选择的流程
        $task = Task::find($taskInfo->tid);
        if (!$task) {
            return;
        }

        // 这里需要根据任务表中存储的流程类型来决定
        // 暂时先用默认逻辑，实际应该从任务表中获取用户的选择
        $taskFlow = QueueConstants::TASK_FLOW_FAST; // 临时设置，实际应从数据库读取
        
        if ($taskFlow === QueueConstants::TASK_FLOW_FAST) {
            // 快速识别流程
            $this->pushToFastRecognitionQueue($taskInfo);
        } else {
            // 完整转写流程，直接跳到转写
            $this->pushToTranscribeQueue($taskInfo);
        }
    }

    /**
     * 推送到快速识别队列 - 快速识别流程的核心处理方法
     * 
     * 功能说明：
     * 1. 音频降噪完成后，快速识别流程的处理方法
     * 2. 将降噪后的音频文件推送到快速识别队列
     * 3. 更新任务状态为"正在快速识别"
     * 4. 提供完整的异常处理和错误记录
     * 
     * 业务价值：
     * - 快速获得语音识别结果，满足用户的即时需求
     * - 相比完整转写，处理速度更快，资源消耗更少
     * - 为用户提供预览功能，决定是否继续完整转写
     * 
     * 队列数据包含：
     * - task_id: 任务详情ID，用于回调时定位任务
     * - task_url: 降噪后的音频文件URL（clear_url）
     * 
     * 状态流转：
     * STEP_CLEAR_COMPLETED(4) → STEP_FAST_RECOGNIZING(5)
     * 
     * 后续流程：
     * - 快速识别完成后状态变为STEP_FAST_COMPLETED(6)
     * - 等待用户选择是否继续转写
     * - 用户可调用continueToTranscribe()继续完整转写
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - clear_url: 降噪后的音频文件URL
     * 
     * @return void
     * 
     * @throws \Exception 当RabbitMQ推送失败或数据库操作失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function pushToFastRecognitionQueue($taskInfo)
    {
        $publishData = [
            'task_id' => $taskInfo->id,
            'task_url' => $taskInfo->clear_url, // 使用降噪后的音频URL
        ];

        try {
            $rabbitMQ = new RabbitMQ();
            $rabbitMQ->publishMessage(QueueConstants::QUEUE_FAST_PROCESS, $publishData);
            
            // 更新任务状态为正在快速识别
            $taskInfo->step = QueueConstants::STEP_FAST_RECOGNIZING;
            $taskInfo->save();
            
        } catch (\Exception $e) {
            $taskInfo->error_msg = $e->getMessage();
            $taskInfo->retry_count += 1;
            $taskInfo->step = QueueConstants::STEP_FAILED;
            $taskInfo->save();
        }
    }

    /**
     * 推送到文本转写队列 - 完整转写流程的最终处理方法
     * 
     * 功能说明：
     * 1. 将降噪后的音频文件推送到文本转写队列
     * 2. 支持两种调用场景：完整流程直接转写、快速识别后继续转写
     * 3. 更新任务状态为"正在文本转写"
     * 4. 提供完整的异常处理和错误记录
     * 
     * 调用场景：
     * 
     * 场景1 - 完整流程直接转写：
     * - 用户选择完整转写流程（TASK_FLOW_FULL）
     * - 音频降噪完成后直接调用此方法
     * - 状态流转：STEP_CLEAR_COMPLETED(4) → STEP_TRANSCRIBING(7)
     * 
     * 场景2 - 快速识别后继续转写：
     * - 用户先选择快速识别，后决定继续转写
     * - 通过continueToTranscribe()方法调用
     * - 状态流转：STEP_FAST_COMPLETED(6) → STEP_TRANSCRIBING(7)
     * 
     * 业务价值：
     * - 提供高质量的完整文本转写服务
     * - 包含更详细的语音识别信息（时长、语言等）
     * - 转写完成后任务流程结束
     * 
     * 队列数据包含：
     * - task_id: 任务详情ID，用于回调时定位任务
     * - task_url: 降噪后的音频文件URL（clear_url）
     * 
     * 状态流转：
     * STEP_TRANSCRIBING(7) → STEP_ALL_COMPLETED(8)
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - clear_url: 降噪后的音频文件URL
     * 
     * @return void
     * 
     * @throws \Exception 当RabbitMQ推送失败或数据库操作失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function pushToTranscribeQueue($taskInfo)
    {
        $publishData = [
            'task_id' => $taskInfo->id,
            'task_url' => $taskInfo->clear_url, // 使用降噪后的音频URL
        ];

        try {
            $rabbitMQ = new RabbitMQ();
            $rabbitMQ->publishMessage(QueueConstants::QUEUE_TRANSCRIBE, $publishData);
            
            // 更新任务状态为正在转写
            $taskInfo->step = QueueConstants::STEP_TRANSCRIBING;
            $taskInfo->save();
            
        } catch (\Exception $e) {
            $taskInfo->error_msg = $e->getMessage();
            $taskInfo->retry_count += 1;
            $taskInfo->step = QueueConstants::STEP_FAILED;
            $taskInfo->save();
        }
    }

    /**
     * 用户选择继续转写 - 快速识别完成后的用户主动操作
     * 
     * 功能说明：
     * 1. 提供给前端的用户操作接口
     * 2. 用户在快速识别完成后，可选择继续进行文本转写
     * 3. 验证任务状态的有效性，确保只有符合条件的任务才能继续
     * 4. 实现工作流程中的用户决策点
     * 
     * 业务场景：
     * - 用户选择了快速识别流程
     * - 快速识别已完成（step=6）
     * - 用户查看快速识别结果后，决定继续转写
     * - 前端调用此接口触发转写流程
     * 
     * 状态验证：
     * - 必须是STEP_FAST_COMPLETED(6)状态
     * - 任务必须存在且有效
     * - 不允许重复提交
     * 
     * 状态流转：
     * STEP_FAST_COMPLETED(6) → STEP_TRANSCRIBING(7)
     * 
     * 使用示例：
     * POST /queue/continueToTranscribe
     * {
     *   "task_id": 123
     * }
     * 
     * @param Request $request 请求对象
     * @param int $request->task_id 任务详情ID（必须）
     * 
     * @return array JSON响应
     *   成功：{'code': 200, 'msg': '已提交转写任务', 'data': null}
     *   失败：{'code': 400, 'msg': '错误信息', 'data': null}
     * 
     * @throws \Exception 当任务查询失败或队列推送失败时
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    public function continueToTranscribe(Request $request)
    {
        $taskId = $request->input('task_id');
        
        if (empty($taskId)) {
            return jsons(400, '任务ID不能为空');
        }

        try {
            $taskInfo = TaskInfo::find($taskId);
            if (!$taskInfo) {
                return jsons(400, '任务不存在');
            }

            // 检查任务状态是否为快速识别完成
            if ($taskInfo->step !== QueueConstants::STEP_FAST_COMPLETED) {
                return jsons(400, '任务状态不正确，无法继续转写');
            }

            // 推送到转写队列
            $this->pushToTranscribeQueue($taskInfo);
            
            return jsons(200, '已提交转写任务');
            
        } catch (\Exception $e) {
            return jsons(400, '提交转写任务失败：' . $e->getMessage());
        }
    }

    /**
     * 任务锁机制 - 防止重复提交和并发处理冲突
     * 
     * 功能说明：
     * 1. 检查指定任务是否正在处理中，防止重复提交
     * 2. 基于任务状态实现简单的锁机制
     * 3. 保护系统资源，避免同一任务的并发处理
     * 4. 提供数据一致性保障
     * 
     * 锁定条件：
     * - 任务状态为"正在处理"的几种状态时视为已锁定
     * - STEP_EXTRACTING(1): 正在提取音频
     * - STEP_CLEARING(3): 正在音频降噪  
     * - STEP_FAST_RECOGNIZING(5): 正在快速识别
     * - STEP_TRANSCRIBING(7): 正在文本转写
     * 
     * 实现方式：
     * - 当前使用数据库状态检查的简单实现
     * - 生产环境建议升级为Redis分布式锁
     * - 可添加锁超时机制，防止死锁
     * 
     * 使用场景：
     * - 任务提交前的重复检查
     * - 回调处理前的状态验证
     * - 用户操作的有效性判断
     * 
     * 升级建议：
     * - 使用Redis实现分布式锁
     * - 添加锁过期时间，防止进程异常导致的死锁
     * - 添加锁等待队列，支持任务排队
     * 
     * @param int $taskInfoId 任务详情ID
     * 
     * @return bool 返回true表示任务已锁定，false表示可以处理
     * 
     * @since 1.0.0
     * @author 系统管理员
     * @todo 升级为Redis分布式锁实现
     */
    private function isTaskLocked($taskInfoId)
    {
        // 这里可以使用Redis或数据库实现锁机制
        // 暂时使用简单的状态检查
        $taskInfo = TaskInfo::find($taskInfoId);
        if (!$taskInfo) {
            return false;
        }

        // 如果任务正在处理中，则认为已锁定
        $processingSteps = [
            QueueConstants::STEP_EXTRACTING,
            QueueConstants::STEP_CLEARING,
            QueueConstants::STEP_FAST_RECOGNIZING,
            QueueConstants::STEP_TRANSCRIBING
        ];

        return in_array($taskInfo->step, $processingSteps);
    }

    /**
     * 上传接口，用于节点处理成功后的文件上传，参考 TaskController 的 upload 接口，但是不存 taskinfo 表
     * 
     * 设计思路：职责分离
     * 1. 此接口只负责文件上传，验证文件并保存到服务器
     * 2. 返回文件URL等信息给节点
     * 3. 节点拿到文件信息后，调用 handleTaskCallback 接口进行业务处理
     * 
     * @param Request $request 请求对象，需要包含：
     *   - file: 上传的文件（必需）
     *   - task_type: 任务类型，用于文件验证（可选）
     * @return array JSON响应
     *   成功：{'code': 200, 'msg': '上传成功', 'data': {'url': '文件URL', 'filename': '原始文件名', ...}}
     *   失败：{'code': 400, 'msg': '错误信息', 'data': null}
     * 
     * @throws Exception 文件上传失败时抛出异常
     * @since 1.0.0
     * @author 系统管理员
     * 
     * @example
     * // 节点调用示例：
     * // 1. 先调用upload接口上传文件
     * // POST /queue/upload
     * // Content-Type: multipart/form-data
     * // file: [文件数据]
     * // task_type: 1 (可选，用于文件类型验证)
     * //
     * // 2. 获取到文件信息后，再调用回调接口
     * // POST /queue/callback
     * // {
     * //     "task_id": 123,
     * //     "task_type": 1,
     * //     "status": "success",
     * //     "data": {"voice_url": "上一步返回的URL"}
     * // }
     */
    public function upload(Request $request)
    {
        try {
            // 检查文件是否上传
            $files = $request->file();
            if (empty($files)) {
                return jsons(400, '请选择要上传的文件');
            }
            
            // 获取任务类型（可选参数，用于文件类型验证）
            $taskType = $request->post('task_type');
            
            // 只处理第一个文件（节点通常一次只上传一个处理结果文件）
            $file = reset($files);
            $fieldName = key($files);
            
            // 上传文件
            $result = $this->uploadFileForQueue($file, $taskType);
            
            return jsons(200, '文件上传成功', [
                'field_name' => $fieldName,
                'file_info' => $result
            ]);
            
        } catch (\Exception $e) {
            return jsons(400, '文件上传失败：' . $e->getMessage());
        }
    }
    
    /**
     * 队列专用文件上传方法
     * 
     * 与TaskController的uploadFileByField方法类似，但专门为队列节点设计：
     * 1. 支持队列处理结果文件的格式验证
     * 2. 不操作数据库，只返回文件信息
     * 3. 针对不同任务类型进行文件格式验证
     * 
     * @param mixed $file 上传的文件对象
     * @param int|null $taskType 任务类型，用于文件验证
     *   - QueueConstants::TASK_TYPE_EXTRACT: 音频提取（支持音频格式）
     *   - QueueConstants::TASK_TYPE_CONVERT: 音频降噪（支持音频格式）
     *   - QueueConstants::TASK_TYPE_FAST_RECOGNITION: 快速识别（支持文本格式）
     *   - QueueConstants::TASK_TYPE_TEXT_CONVERT: 文本转写（支持文本格式）
     * @return array 文件信息数组
     *   - storage_mode: 存储模式
     *   - origin_name: 原始文件名
     *   - object_name: 服务器文件名
     *   - hash: 文件哈希值
     *   - mime_type: MIME类型
     *   - storage_path: 存储路径
     *   - suffix: 文件扩展名
     *   - size_byte: 文件大小（字节）
     *   - size_info: 格式化的文件大小
     *   - url: 访问URL
     * 
     * @throws Exception 文件上传失败时抛出异常
     */
    private function uploadFileForQueue($file, $taskType = null)
    {
        // 获取上传配置
        $configLogic = new \plugin\saiadmin\app\logic\system\SystemConfigLogic();
        $uploadConfig = $configLogic->getGroup('upload_config');
        
        // 检查文件大小
        $file_size = $file->getSize();
        $maxSize = \plugin\saiadmin\utils\Arr::getConfigValue($uploadConfig, 'upload_size') ?? 104857600; // 默认100MB
        if ($file_size > $maxSize) {
            throw new \Exception('文件大小超过限制');
        }
        
        // 获取文件扩展名
        $ext = $file->getUploadExtension();
        
        // 根据任务类型验证文件格式
        $this->validateFileForTaskType($ext, $taskType);
        
        // 生成文件保存路径（使用queue子目录区分）
        $root = \plugin\saiadmin\utils\Arr::getConfigValue($uploadConfig, 'local_root') ?? 'public/storage/';
        $folder = 'queue/' . date('Ymd'); // 队列文件单独存放
        $fullDir = base_path() . DIRECTORY_SEPARATOR . $root . $folder . DIRECTORY_SEPARATOR;
        
        if (!is_dir($fullDir)) {
            mkdir($fullDir, 0777, true);
        }
        
        // 生成唯一文件名
        $hash = hash_file('sha1', $file->getRealPath());
        $objectName = $hash . '.' . $ext;
        $savePath = $fullDir . $objectName;
        
        // 移动文件
        $file->move($savePath);
        
        // 生成URL
        $domain = \plugin\saiadmin\utils\Arr::getConfigValue($uploadConfig, 'local_domain') ?? request()->host();
        $uri = \plugin\saiadmin\utils\Arr::getConfigValue($uploadConfig, 'local_uri') ?? '/storage/';
        $url = $domain . $uri . $folder . '/' . $objectName;
        
        // 构建返回数据
        $result = [
            'storage_mode' => 1,
            'origin_name' => $file->getUploadName(),
            'object_name' => $objectName,
            'hash' => $hash,
            'mime_type' => $file->getUploadMimeType(),
            'storage_path' => $root . $folder . '/' . $objectName,
            'suffix' => $ext,
            'size_byte' => $file_size,
            'size_info' => $this->formatBytes($file_size),
            'url' => $url
        ];
        
        // 保存到系统附件表（记录文件信息，便于管理）
        $attachment = new \plugin\saiadmin\app\model\system\SystemAttachment();
        $attachment->save($result);
        
        return $result;
    }
    
    /**
     * 根据任务类型验证文件格式
     * 
     * @param string $ext 文件扩展名
     * @param int|null $taskType 任务类型
     * @throws Exception 文件格式不符合要求时抛出异常
     */
    private function validateFileForTaskType($ext, $taskType)
    {
        // 如果没有指定任务类型，使用默认验证
        if ($taskType === null) {
            $allowedExtensions = ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'txt', 'json'];
            if (!in_array($ext, $allowedExtensions)) {
                throw new \Exception('不支持该格式的文件上传，支持的格式：' . implode(', ', $allowedExtensions));
            }
            return;
        }
        
        // 根据任务类型验证文件格式
        switch ($taskType) {
            case QueueConstants::TASK_TYPE_EXTRACT:
                // 音频提取结果：音频文件
                $audioExtensions = ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'opus'];
                if (!in_array($ext, $audioExtensions)) {
                    throw new \Exception('音频提取任务只支持音频文件格式：' . implode(', ', $audioExtensions));
                }
                break;
                
            case QueueConstants::TASK_TYPE_CONVERT:
                // 音频降噪结果：音频文件
                $audioExtensions = ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'opus'];
                if (!in_array($ext, $audioExtensions)) {
                    throw new \Exception('音频降噪任务只支持音频文件格式：' . implode(', ', $audioExtensions));
                }
                break;
                
            case QueueConstants::TASK_TYPE_FAST_RECOGNITION:
                // 快速识别结果：文本文件
                $textExtensions = ['txt', 'json'];
                if (!in_array($ext, $textExtensions)) {
                    throw new \Exception('快速识别任务只支持文本文件格式：' . implode(', ', $textExtensions));
                }
                break;
                
            case QueueConstants::TASK_TYPE_TEXT_CONVERT:
                // 文本转写结果：文本文件
                $textExtensions = ['txt', 'json'];
                if (!in_array($ext, $textExtensions)) {
                    throw new \Exception('文本转写任务只支持文本文件格式：' . implode(', ', $textExtensions));
                }
                break;
                
            default:
                throw new \Exception('未知的任务类型：' . $taskType);
        }
    }
    
    /**
     * 格式化文件大小
     * 
     * @param int $bytes 字节数
     * @return string 格式化后的文件大小
     */
    private function formatBytes($bytes)
    {
        $units = ['B', 'KB', 'MB', 'GB', 'TB'];
        $bytes = max($bytes, 0);
        $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
        $pow = min($pow, count($units) - 1);
        $bytes /= (1 << (10 * $pow));
        return round($bytes, 2) . ' ' . $units[$pow];
    }
}
