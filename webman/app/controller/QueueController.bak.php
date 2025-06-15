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
 * 
 * =============================================================================
 * MQ消息数据结构说明 (新版本 - 传递完整TaskInfo数据)
 * =============================================================================
 * 
 * 📋 消息统一格式：
 * {
 *   "task_info": {
 *     "id": 123,                    // TaskInfo主键ID
 *     "tid": 45,                    // 关联的Task ID
 *     "filename": "test.mp4",       // 原始文件名
 *     "url": "http://...",          // 原始文件URL
 *     "voice_url": "http://...",    // 提取音频后的URL
 *     "clear_url": "http://...",    // 降噪后的URL
 *     "type": 2,                    // 文件类型：1=音频，2=视频
 *     "is_extract": 1,              // 是否已提取：1=是，2=否
 *     "is_clear": 1,                // 是否已降噪：1=是，2=否
 *     "fast_status": 1,             // 快速识别状态：1=已完成，2=未完成
 *     "transcribe_status": 1,       // 转写状态：1=已完成，2=未完成
 *     "step": 3,                    // 当前处理步骤
 *     "error_msg": "",              // 错误信息
 *     "retry_count": 0,             // 重试次数
 *     // ... 其他字段
 *   },
 *   "task_flow": 1,                 // 任务流程：1=快速识别，2=完整转写（仅extract时有）
 *   "processing_type": "extract"    // 处理类型标识
 * }
 * 
 * 🎯 各节点使用的URL字段：
 * 
 * 1️⃣ cut_node (音频提取节点)：
 *    - 使用：task_info.url (原始文件URL)
 *    - 处理：从视频中提取音频
 *    - 回调：更新voice_url字段
 * 
 * 2️⃣ clear_node (音频降噪节点)：
 *    - 使用：task_info.voice_url (提取后的音频URL)
 *    - 注意：如果是音频文件，voice_url = url
 *    - 处理：对音频进行降噪处理
 *    - 回调：更新clear_url字段
 * 
 * 3️⃣ quick_node (快速识别节点)：
 *    - 使用：task_info.clear_url (降噪后的音频URL)
 *    - 处理：快速语音识别
 *    - 回调：更新fast_status=1
 * 
 * 4️⃣ translate_node (文本转写节点)：
 *    - 使用：task_info.clear_url (降噪后的音频URL)
 *    - 处理：完整文本转写
 *    - 回调：更新transcribe_status=1，text_info等字段
 * 
 * 🔄 工作流程：
 * 原始文件(url) → 音频提取(voice_url) → 音频降噪(clear_url) → 识别/转写
 * 
 * 💡 优势：
 * - 减少节点的数据库查询
 * - 提供完整的上下文信息
 * - 支持复杂的业务逻辑判断
 * - 便于节点进行状态验证和错误处理
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
     * 队列数据格式（传递完整TaskInfo数据）：
     * {
     *   'task_info': {
     *     'id': 任务详情ID,
     *     'tid': 任务ID,
     *     'filename': '原始文件名',
     *     'url': '原始文件URL',    // cut_node使用此URL
     *     'voice_url': '',        // 待更新
     *     'clear_url': '',        // 待更新
     *     'type': 文件类型,
     *     'step': 当前步骤,
     *     // ... 其他完整字段
     *   }
     * }
     * 
     * @param mixed $taskInfoItem 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - url: 原始文件URL（cut_node将使用此URL）
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
            // 传递完整的TaskInfo数据，包含所有字段信息
            $publishData = [
                'task_info' => $taskInfoItem->toArray(), // 完整的TaskInfo数据
                'task_flow' => $taskFlow, // 任务流程类型
                'processing_type' => 'extract', // 处理类型标识
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
            // 音频文件无需提取，直接进入降噪流程
            // 设置voice_url为原始URL（音频文件本身）
            if (empty($taskInfoItem->voice_url)) {
                $taskInfoItem->voice_url = $taskInfoItem->url;
                $taskInfoItem->step = QueueConstants::STEP_EXTRACT_COMPLETED;
                $taskInfoItem->save();
            }
            
            // 直接推送到音频降噪队列
            try {
                $this->pushToAudioClearQueue($taskInfoItem);
                return true;
            } catch (\Exception $e) {
                //记录错误信息到数据库
                $taskInfoItem->error_msg = $e->getMessage();
                $taskInfoItem->retry_count = $taskInfoItem->retry_count + 1;
                $taskInfoItem->step = QueueConstants::STEP_FAILED;
                $taskInfoItem->save();
                
                return $e->getMessage();
            }
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

            // 记录回调详细信息用于调试
            error_log("回调处理开始 - 任务ID: {$taskId}, 类型: {$taskType}, 状态: {$status}");
            if (!empty($data)) {
                error_log("回调数据结构: " . json_encode(array_keys($data), JSON_UNESCAPED_UNICODE));
            }

            if ($status === 'success') {
                $this->handleTaskSuccess($taskInfo, $taskType, $data);
            } else {
                $this->handleTaskFailed($taskInfo, $taskType, $message);
            }

            return jsons(200, '回调处理成功');
        } catch (\Exception $e) {
            // 记录详细的错误信息
            error_log("回调处理异常 - 任务ID: {$taskId}, 错误: " . $e->getMessage());
            error_log("错误堆栈: " . $e->getTraceAsString());
            return jsons(400, '回调处理失败：' . $e->getMessage());
        }
    }

    /**
     * 处理任务成功回调 - 根据新工作流程的核心状态处理器
     * 
     * 功能说明：
     * 1. 根据不同的任务类型执行相应的成功处理逻辑
     * 2. 更新任务状态和相关数据字段
     * 3. 先保存字段更新，再触发工作流程的下一个步骤
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
        // 清空错误信息
        $taskInfo->error_msg = '';
        
        try {
            switch ($taskType) {
                case QueueConstants::TASK_TYPE_EXTRACT:
                    // 音频提取完成 - 更新字段并保存
                    $taskInfo->is_extract = QueueConstants::STATUS_YES;
                    $taskInfo->voice_url = $data['voice_url'] ?? '';
                    $taskInfo->step = QueueConstants::STEP_EXTRACT_COMPLETED;
                    $taskInfo->save(); // 先保存字段更新
                    
                    // 自动推送到音频降噪队列
                    $this->pushToAudioClearQueue($taskInfo);
                    break;
                    
                case QueueConstants::TASK_TYPE_CONVERT:
                    // 音频降噪完成 - 更新字段并保存
                    $taskInfo->is_clear = QueueConstants::STATUS_YES;
                    $taskInfo->clear_url = $data['clear_url'] ?? '';
                    $taskInfo->step = QueueConstants::STEP_CLEAR_COMPLETED;
                    $taskInfo->save(); // 先保存字段更新
                    
                    // 根据用户选择的流程进行下一步
                    $this->processNextStepAfterClear($taskInfo);
                    break;
                    
                case QueueConstants::TASK_TYPE_FAST_RECOGNITION:
                    // 快速识别完成 - 更新字段并保存
                    $taskInfo->fast_status = QueueConstants::STATUS_YES;
                    $taskInfo->effective_voice = $data['effective_voice'] ?? '';
                    $taskInfo->total_voice = $data['total_voice'] ?? '';
                    $taskInfo->step = QueueConstants::STEP_FAST_COMPLETED;
                    $taskInfo->save(); // 保存字段更新
                    
                    // 检查是否应该自动继续转写（完整流程）
                    $this->checkAndContinueToTranscribe($taskInfo);
                    break;
                    
                case QueueConstants::TASK_TYPE_TEXT_CONVERT:
                    error_log("处理文本转写回调 - 任务ID: {$taskInfo->id}");
                    
                    // 文本转写完成 - 更新字段并保存
                    $taskInfo->transcribe_status = QueueConstants::STATUS_YES;
                    
                    // 安全处理text_info字段
                    try {
                        $textInfo = $data['text_info'] ?? '';
                        if (is_array($textInfo) || is_object($textInfo)) {
                            // 如果是数组或对象，序列化为JSON字符串
                            $jsonString = json_encode($textInfo, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
                            if ($jsonString === false) {
                                error_log("JSON编码失败: " . json_last_error_msg());
                                $taskInfo->text_info = '{"error": "JSON编码失败"}';
                            } else {
                                $taskInfo->text_info = $jsonString;
                                error_log("text_info已成功序列化，长度: " . strlen($jsonString));
                            }
                        } else {
                            // 如果是字符串，直接保存
                            $taskInfo->text_info = (string)$textInfo;
                            error_log("text_info保存为字符串，长度: " . strlen($textInfo));
                        }
                    } catch (\Exception $e) {
                        error_log("处理text_info时出错: " . $e->getMessage());
                        $taskInfo->text_info = '{"error": "处理text_info时出错: ' . $e->getMessage() . '"}';
                    }
                    
                    // 安全处理其他字段
                    $taskInfo->effective_voice = isset($data['effective_voice']) ? (string)$data['effective_voice'] : '';
                    $taskInfo->total_voice = isset($data['total_voice']) ? (string)$data['total_voice'] : '';
                    $taskInfo->language = isset($data['language']) ? (string)$data['language'] : '';
                    $taskInfo->step = QueueConstants::STEP_ALL_COMPLETED;
                    
                    error_log("准备保存任务信息到数据库");
                    $taskInfo->save(); // 保存字段更新
                    error_log("任务信息已成功保存到数据库");
                    
                    // 任务完成，无需后续操作
                    break;
            }
        } catch (\Exception $e) {
            error_log("handleTaskSuccess异常 - 任务ID: {$taskInfo->id}, 类型: {$taskType}, 错误: " . $e->getMessage());
            error_log("错误堆栈: " . $e->getTraceAsString());
            throw $e; // 重新抛出异常
        }
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
     * 2. 重新从数据库查询最新的TaskInfo数据，确保数据完整性
     * 3. 将提取后的音频文件推送到降噪处理队列
     * 4. 更新任务状态为"正在音频降噪"
     * 5. 提供完整的异常处理机制
     * 
     * 队列数据包含完整TaskInfo信息：
     * - clear_node将使用voice_url（提取后的音频URL）进行降噪处理
     * - 如果是音频文件，voice_url就是原始url
     * - 如果是视频文件，voice_url是提取后的音频文件URL
     * 
     * 状态流转：
     * STEP_EXTRACT_COMPLETED(2) → STEP_CLEARING(3)
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - voice_url: 提取后的音频文件URL（clear_node使用）
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
        try {
            // 重新从数据库查询最新的TaskInfo数据，确保获取最新状态
            $latestTaskInfo = TaskInfo::find($taskInfo->id);
            if (!$latestTaskInfo) {
                throw new \Exception('任务详情不存在：' . $taskInfo->id);
            }
            
            // 传递最新的完整TaskInfo数据
            $publishData = [
                'task_info' => $latestTaskInfo->toArray(), // 最新的完整TaskInfo数据
                'processing_type' => 'clear', // 处理类型标识
            ];

            $rabbitMQ = new RabbitMQ();
            $rabbitMQ->publishMessage(QueueConstants::QUEUE_AUDIO_CLEAR, $publishData);
            
            // 更新任务状态为正在降噪
            $latestTaskInfo->step = QueueConstants::STEP_CLEARING;
            $latestTaskInfo->save();
            
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

        // 尝试从多个来源获取任务流程类型
        $taskFlow = $this->getTaskFlowType($task, $taskInfo);
        
        if ($taskFlow === QueueConstants::TASK_FLOW_FAST) {
            // 快速识别流程
            $this->pushToFastRecognitionQueue($taskInfo);
        } else {
            // 完整转写流程，直接跳到转写
            $this->pushToTranscribeQueue($taskInfo);
        }
    }

    /**
     * 获取任务流程类型 - 从多个来源智能判断用户选择的流程
     * 
     * 功能说明：
     * 1. 从多个数据源获取任务流程类型
     * 2. 提供灵活的流程类型判断策略
     * 3. 支持向后兼容和渐进式升级
     * 4. 为不同的业务场景提供适配能力
     * 
     * 判断优先级：
     * 1. 任务表中的task_flow字段（如果存在）
     * 2. 任务名称中的关键词识别
     * 3. 任务创建时间的默认策略
     * 4. 系统全局默认配置
     * 
     * @param mixed $task 任务对象（Task模型实例）
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     * 
     * @return int 任务流程类型
     *   - QueueConstants::TASK_FLOW_FAST: 快速识别流程
     *   - QueueConstants::TASK_FLOW_FULL: 完整转写流程
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function getTaskFlowType($task, $taskInfo)
    {
        // 策略1: 检查任务表中的task_flow字段
        if (isset($task->task_flow) && !empty($task->task_flow)) {
            return $task->task_flow;
        }

        // 策略2: 从任务名称推断流程类型
        if (!empty($task->name)) {
            $taskName = strtolower($task->name);
            // 检查是否包含完整转写的关键词
            $fullFlowKeywords = ['完整', '全量', '详细', 'full', 'complete', 'detail'];
            foreach ($fullFlowKeywords as $keyword) {
                if (strpos($taskName, $keyword) !== false) {
                    return QueueConstants::TASK_FLOW_FULL;
                }
            }
        }

        // 策略3: 根据任务创建时间的默认策略
        // 例如：新创建的任务默认使用完整流程，老任务保持快速流程
        // 这里可以根据实际业务需求调整
        
        // 策略4: 系统默认配置
        // 当前默认为快速流程，保持向后兼容
        return QueueConstants::TASK_FLOW_FAST;
    }

    /**
     * 推送到快速识别队列 - 快速识别流程的核心处理方法
     * 
     * 功能说明：
     * 1. 音频降噪完成后，快速识别流程的处理方法
     * 2. 重新从数据库查询最新的TaskInfo数据，确保数据完整性
     * 3. 将降噪后的音频文件推送到快速识别队列
     * 4. 更新任务状态为"正在快速识别"
     * 5. 提供完整的异常处理和错误记录
     * 
     * 业务价值：
     * - 快速获得语音识别结果，满足用户的即时需求
     * - 相比完整转写，处理速度更快，资源消耗更少
     * - 为用户提供预览功能，决定是否继续完整转写
     * 
     * 队列数据包含完整TaskInfo信息：
     * - quick_node将使用clear_url（降噪后的音频URL）进行快速识别
     * 
     * 状态流转：
     * STEP_CLEAR_COMPLETED(4) → STEP_FAST_RECOGNIZING(5)
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - clear_url: 降噪后的音频文件URL（quick_node使用）
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
        try {
            // 重新从数据库查询最新的TaskInfo数据，确保获取最新状态
            $latestTaskInfo = TaskInfo::find($taskInfo->id);
            if (!$latestTaskInfo) {
                throw new \Exception('任务详情不存在：' . $taskInfo->id);
            }
            
            // 传递最新的完整TaskInfo数据
            $publishData = [
                'task_info' => $latestTaskInfo->toArray(), // 最新的完整TaskInfo数据
                'processing_type' => 'fast_recognition', // 处理类型标识
            ];

            $rabbitMQ = new RabbitMQ();
            $rabbitMQ->publishMessage(QueueConstants::QUEUE_FAST_PROCESS, $publishData);
            
            // 更新任务状态为正在快速识别
            $latestTaskInfo->step = QueueConstants::STEP_FAST_RECOGNIZING;
            $latestTaskInfo->save();
            
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
     * 1. 重新从数据库查询最新的TaskInfo数据，确保数据完整性
     * 2. 将降噪后的音频文件推送到文本转写队列
     * 3. 支持两种调用场景：完整流程直接转写、快速识别后继续转写
     * 4. 更新任务状态为"正在文本转写"
     * 5. 提供完整的异常处理和错误记录
     * 
     * 队列数据包含完整TaskInfo信息：
     * - translate_node将使用clear_url（降噪后的音频URL）进行文本转写
     * 
     * 状态流转：
     * STEP_TRANSCRIBING(7) → STEP_ALL_COMPLETED(8)
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - id: 任务详情ID
     *   - clear_url: 降噪后的音频文件URL（translate_node使用）
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
        try {
            // 重新从数据库查询最新的TaskInfo数据，确保获取最新状态
            $latestTaskInfo = TaskInfo::find($taskInfo->id);
            if (!$latestTaskInfo) {
                throw new \Exception('任务详情不存在：' . $taskInfo->id);
            }
            
            // 传递最新的完整TaskInfo数据
            $publishData = [
                'task_info' => $latestTaskInfo->toArray(), // 最新的完整TaskInfo数据
                'processing_type' => 'transcribe', // 处理类型标识
            ];

            $rabbitMQ = new RabbitMQ();
            $rabbitMQ->publishMessage(QueueConstants::QUEUE_TRANSCRIBE, $publishData);
            
            // 更新任务状态为正在转写
            $latestTaskInfo->step = QueueConstants::STEP_TRANSCRIBING;
            $latestTaskInfo->save();
            
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

    /**
     * 检查并自动继续转写 - 快速识别完成后的智能流程判断
     * 
     * 功能说明：
     * 1. 快速识别完成后，判断是否应该自动继续转写
     * 2. 支持多种判断策略，实现智能化的流程控制
     * 3. 为完整流程用户提供无缝的处理体验
     * 4. 保持快速流程用户的选择权
     * 
     * 判断策略（按优先级）：
     * 1. 检查任务表中的task_flow字段（如果存在）
     * 2. 检查TaskInfo中的处理类型标识
     * 3. 根据任务创建时的参数判断
     * 4. 默认策略：等待用户选择
     * 
     * 自动继续条件：
     * - 用户选择了完整转写流程（TASK_FLOW_FULL）
     * - 或者任务标记为自动转写
     * - 或者满足其他预设的自动化条件
     * 
     * 状态流转：
     * STEP_FAST_COMPLETED(6) → STEP_TRANSCRIBING(7) [自动]
     * STEP_FAST_COMPLETED(6) → 等待用户选择 [手动]
     * 
     * @param mixed $taskInfo 任务详情对象（TaskInfo模型实例）
     *   - tid: 关联的任务ID
     *   - 其他字段用于判断流程类型
     * 
     * @return void
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    private function checkAndContinueToTranscribe($taskInfo)
    {
        try {
            // 获取关联的任务信息
            $task = Task::find($taskInfo->tid);
            if (!$task) {
                // 任务不存在，默认等待用户选择
                return;
            }

            // 策略1: 检查任务表中的task_flow字段（如果存在）
            if (isset($task->task_flow)) {
                $taskFlow = $task->task_flow;
            } else {
                // 策略2: 从任务名称或其他字段推断流程类型
                // 这里可以根据实际业务需求添加判断逻辑
                // 例如：检查任务名称是否包含"完整"、"全量"等关键词
                // 或者检查任务的其他标识字段
                
                // 策略3: 检查任务创建时的默认行为
                // 可以根据用户的历史偏好或系统配置来判断
                
                // 当前默认策略：等待用户选择（保持原有行为）
                $taskFlow = QueueConstants::TASK_FLOW_FAST;
            }

            // 根据流程类型决定是否自动继续
            if ($taskFlow === QueueConstants::TASK_FLOW_FULL) {
                // 完整流程：自动推送到转写队列
                $this->pushToTranscribeQueue($taskInfo);
            } else {
                // 快速流程：等待用户选择，无需额外操作
                // 用户可以通过 continueToTranscribe 接口手动继续
            }

        } catch (\Exception $e) {
            // 发生异常时，默认等待用户选择，不影响主流程
            // 可以记录日志用于后续分析
            error_log("checkAndContinueToTranscribe failed: " . $e->getMessage());
        }
    }

    /**
     * 单独推送任务到指定队列 - 支持独立的任务类型处理
     * 
     * 功能说明：
     * 1. 支持4种任务类型的独立推送，不依赖工作流程
     * 2. 可以跳过前置步骤，直接处理特定类型的任务
     * 3. 适用于重新处理、手动干预、测试等场景
     * 4. 保持与原有工作流程的兼容性
     * 
     * 支持的任务类型：
     * - TASK_TYPE_EXTRACT(1): 音频提取
     * - TASK_TYPE_CONVERT(2): 音频降噪  
     * - TASK_TYPE_FAST_RECOGNITION(3): 快速识别
     * - TASK_TYPE_TEXT_CONVERT(4): 文本转写
     * 
     * 使用场景：
     * - 重新处理失败的任务
     * - 跳过某些步骤直接处理
     * - 测试特定的处理节点
     * - 手动干预和调试
     * 
     * @param Request $request 请求对象
     * @param int $request->task_id 任务详情ID（必须）
     * @param int $request->task_type 任务类型（必须）1-4
     * @param bool $request->force 是否强制推送（可选），忽略状态检查
     * 
     * @return array JSON响应
     *   成功：{'code': 200, 'msg': '任务推送成功', 'data': {'queue': '队列名称'}}
     *   失败：{'code': 400, 'msg': '错误信息', 'data': null}
     * 
     * @since 1.0.0
     * @author 系统管理员
     */
    public function pushSingleTask(Request $request)
    {
        $taskId = $request->input('task_id');
        $taskType = $request->input('task_type');
        $force = $request->input('force', false);

        // 参数验证
        if (empty($taskId) || empty($taskType)) {
            return jsons(400, '缺少必要参数：task_id 和 task_type');
        }

        if (!QueueConstants::isValidTaskType($taskType)) {
            return jsons(400, '无效的任务类型，支持的类型：1-4');
        }

        try {
            // 查找任务
            $taskInfo = TaskInfo::find($taskId);
            if (!$taskInfo) {
                return jsons(400, '任务不存在');
            }

            // 检查任务锁（除非强制推送）
            if (!$force && $this->isTaskLocked($taskId)) {
                return jsons(400, '任务正在处理中，如需强制推送请设置 force=true');
            }

            // 验证任务状态和前置条件
            $validationResult = $this->validateTaskForType($taskInfo, $taskType, $force);
            if ($validationResult !== true) {
                return jsons(400, $validationResult);
            }

            // 推送到对应队列
            $result = $this->pushToSpecificQueue($taskInfo, $taskType);
            
            if ($result['success']) {
                return jsons(200, '任务推送成功', [
                    'queue' => $result['queue'],
                    'task_id' => $taskId,
                    'task_type' => $taskType,
                    'step' => $taskInfo->step
                ]);
            } else {
                return jsons(400, $result['message']);
            }

        } catch (\Exception $e) {
            return jsons(400, '推送失败：' . $e->getMessage());
        }
    }

    /**
     * 验证任务是否满足指定类型的处理条件
     * 
     * @param mixed $taskInfo 任务详情对象
     * @param int $taskType 任务类型
     * @param bool $force 是否强制推送
     * @return true|string 验证通过返回true，否则返回错误信息
     */
    private function validateTaskForType($taskInfo, $taskType, $force)
    {
        if ($force) {
            return true; // 强制推送跳过所有验证
        }

        switch ($taskType) {
            case QueueConstants::TASK_TYPE_EXTRACT:
                // 音频提取：需要原始文件URL
                if (empty($taskInfo->url)) {
                    return '缺少原始文件URL，无法进行音频提取';
                }
                if ($taskInfo->is_extract == QueueConstants::STATUS_YES) {
                    return '音频已提取，无需重复处理';
                }
                break;

            case QueueConstants::TASK_TYPE_CONVERT:
                // 音频降噪：需要音频文件URL
                if (empty($taskInfo->voice_url)) {
                    return '缺少音频文件URL，请先完成音频提取';
                }
                if ($taskInfo->is_clear == QueueConstants::STATUS_YES) {
                    return '音频已降噪，无需重复处理';
                }
                break;

            case QueueConstants::TASK_TYPE_FAST_RECOGNITION:
                // 快速识别：需要降噪后的音频文件
                if (empty($taskInfo->clear_url)) {
                    return '缺少降噪音频文件URL，请先完成音频降噪';
                }
                if ($taskInfo->fast_status == QueueConstants::STATUS_YES) {
                    return '快速识别已完成，无需重复处理';
                }
                break;

            case QueueConstants::TASK_TYPE_TEXT_CONVERT:
                // 文本转写：需要降噪后的音频文件
                if (empty($taskInfo->clear_url)) {
                    return '缺少降噪音频文件URL，请先完成音频降噪';
                }
                if ($taskInfo->transcribe_status == QueueConstants::STATUS_YES) {
                    return '文本转写已完成，无需重复处理';
                }
                break;
        }

        return true;
    }

    /**
     * 推送任务到指定类型的队列
     * 
     * @param mixed $taskInfo 任务详情对象
     * @param int $taskType 任务类型
     * @return array 推送结果 ['success' => bool, 'queue' => string, 'message' => string]
     */
    private function pushToSpecificQueue($taskInfo, $taskType)
    {
        try {
            $rabbitMQ = new RabbitMQ();
            $publishData = [
                'task_info' => $taskInfo->toArray(),
                'processing_type' => $this->getProcessingTypeByTaskType($taskType),
                'manual_push' => true // 标记为手动推送
            ];

            switch ($taskType) {
                case QueueConstants::TASK_TYPE_EXTRACT:
                    $rabbitMQ->publishMessage(QueueConstants::QUEUE_VOICE_EXTRACT, $publishData);
                    $taskInfo->step = QueueConstants::STEP_EXTRACTING;
                    $queueName = QueueConstants::QUEUE_VOICE_EXTRACT;
                    break;

                case QueueConstants::TASK_TYPE_CONVERT:
                    $rabbitMQ->publishMessage(QueueConstants::QUEUE_AUDIO_CLEAR, $publishData);
                    $taskInfo->step = QueueConstants::STEP_CLEARING;
                    $queueName = QueueConstants::QUEUE_AUDIO_CLEAR;
                    break;

                case QueueConstants::TASK_TYPE_FAST_RECOGNITION:
                    $rabbitMQ->publishMessage(QueueConstants::QUEUE_FAST_PROCESS, $publishData);
                    $taskInfo->step = QueueConstants::STEP_FAST_RECOGNIZING;
                    $queueName = QueueConstants::QUEUE_FAST_PROCESS;
                    break;

                case QueueConstants::TASK_TYPE_TEXT_CONVERT:
                    $rabbitMQ->publishMessage(QueueConstants::QUEUE_TRANSCRIBE, $publishData);
                    $taskInfo->step = QueueConstants::STEP_TRANSCRIBING;
                    $queueName = QueueConstants::QUEUE_TRANSCRIBE;
                    break;

                default:
                    return ['success' => false, 'message' => '不支持的任务类型'];
            }

            // 更新任务状态
            $taskInfo->error_msg = ''; // 清空错误信息
            $taskInfo->save();

            return [
                'success' => true,
                'queue' => $queueName,
                'message' => '推送成功'
            ];

        } catch (\Exception $e) {
            // 记录错误
            $taskInfo->error_msg = $e->getMessage();
            $taskInfo->retry_count += 1;
            $taskInfo->step = QueueConstants::STEP_FAILED;
            $taskInfo->save();

            return [
                'success' => false,
                'message' => '推送失败：' . $e->getMessage()
            ];
        }
    }

    /**
     * 根据任务类型获取处理类型标识
     * 
     * @param int $taskType 任务类型
     * @return string 处理类型标识
     */
    private function getProcessingTypeByTaskType($taskType)
    {
        $typeMap = [
            QueueConstants::TASK_TYPE_EXTRACT => 'extract',
            QueueConstants::TASK_TYPE_CONVERT => 'clear',
            QueueConstants::TASK_TYPE_FAST_RECOGNITION => 'fast_recognition',
            QueueConstants::TASK_TYPE_TEXT_CONVERT => 'transcribe'
        ];

        return $typeMap[$taskType] ?? 'unknown';
    }

    /**
     * 批量推送任务 - 支持批量处理多个任务
     * 
     * 功能说明：
     * 1. 支持批量推送多个任务到同一类型的队列
     * 2. 提供批量操作的事务性处理
     * 3. 详细的成功/失败统计信息
     * 4. 适用于批量重新处理、批量测试等场景
     * 
     * @param Request $request 请求对象
     * @param array $request->task_ids 任务ID数组（必须）
     * @param int $request->task_type 任务类型（必须）
     * @param bool $request->force 是否强制推送（可选）
     * @param bool $request->continue_on_error 遇到错误是否继续（可选）
     * 
     * @return array JSON响应
     */
    public function pushBatchTasks(Request $request)
    {
        $taskIds = $request->input('task_ids', []);
        $taskType = $request->input('task_type');
        $force = $request->input('force', false);
        $continueOnError = $request->input('continue_on_error', true);

        // 参数验证
        if (empty($taskIds) || !is_array($taskIds)) {
            return jsons(400, 'task_ids 必须是非空数组');
        }

        if (!QueueConstants::isValidTaskType($taskType)) {
            return jsons(400, '无效的任务类型');
        }

        $results = [
            'total' => count($taskIds),
            'success' => 0,
            'failed' => 0,
            'details' => []
        ];

        foreach ($taskIds as $taskId) {
            try {
                $taskInfo = TaskInfo::find($taskId);
                if (!$taskInfo) {
                    $results['details'][] = [
                        'task_id' => $taskId,
                        'status' => 'failed',
                        'message' => '任务不存在'
                    ];
                    $results['failed']++;
                    continue;
                }

                // 验证和推送
                $validationResult = $this->validateTaskForType($taskInfo, $taskType, $force);
                if ($validationResult !== true) {
                    $results['details'][] = [
                        'task_id' => $taskId,
                        'status' => 'failed',
                        'message' => $validationResult
                    ];
                    $results['failed']++;
                    
                    if (!$continueOnError) {
                        break;
                    }
                    continue;
                }

                $pushResult = $this->pushToSpecificQueue($taskInfo, $taskType);
                if ($pushResult['success']) {
                    $results['details'][] = [
                        'task_id' => $taskId,
                        'status' => 'success',
                        'queue' => $pushResult['queue']
                    ];
                    $results['success']++;
                } else {
                    $results['details'][] = [
                        'task_id' => $taskId,
                        'status' => 'failed',
                        'message' => $pushResult['message']
                    ];
                    $results['failed']++;
                    
                    if (!$continueOnError) {
                        break;
                    }
                }

            } catch (\Exception $e) {
                $results['details'][] = [
                    'task_id' => $taskId,
                    'status' => 'failed',
                    'message' => $e->getMessage()
                ];
                $results['failed']++;
                
                if (!$continueOnError) {
                    break;
                }
            }
        }

        $message = "批量推送完成：成功 {$results['success']} 个，失败 {$results['failed']} 个";
        $code = $results['failed'] > 0 ? 207 : 200; // 207 表示部分成功

        return jsons($code, $message, $results);
    }
}
