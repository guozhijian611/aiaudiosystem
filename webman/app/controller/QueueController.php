<?php

namespace app\controller;

use support\Request;
use app\api\model\TaskInfo;
use app\api\model\AiLog;
use app\service\RabbitMQ;
use app\constants\QueueConstants;
use app\api\model\Task;

/**
 * 队列控制器（统一入口 action 2=clear, 3=quick, 4=transcribe）
 */
class QueueController
{
    /**
     * 统一入口方法，支持传 task_id（批量/单个）或 taskinfo_id（批量/单个）
     * action: 2=clear，3=quick，4=transcribe
     */
    public function queueAction(Request $request)
    {
        $taskinfoIds = (array)$request->input('taskinfo_id', []);
        $taskIds = (array)$request->input('task_id', []);
        $action = (int)$request->input('action');
        $results = [];
        $affectedTaskIds = []; // 记录受影响的任务ID
        
        if (!empty($taskinfoIds)) {
            foreach ($taskinfoIds as $tid) {
                $taskInfo = TaskInfo::find($tid);
                if ($taskInfo) {
                    $affectedTaskIds[] = $taskInfo->tid;
                }
                $results[] = $this->processSingleTaskInfo($taskInfo, $action);
            }
        } elseif (!empty($taskIds)) {
            foreach ($taskIds as $taskId) {
                $affectedTaskIds[] = $taskId;
                $taskInfos = TaskInfo::where('tid', $taskId)->select();
                foreach ($taskInfos as $taskInfo) {
                    $results[] = $this->processSingleTaskInfo($taskInfo, $action);
                }
            }
        } else {
            return jsons(400, '请传入 taskinfo_id 或 task_id');
        }
        
        // 统计信息
        $total = count($results);
        $success = 0;
        $failed = 0;
        foreach ($results as $item) {
            if ($item['status'] === 'success') {
                $success++;
            } else {
                $failed++;
            }
        }
        
        // 🔥 更新受影响的任务状态
        $affectedTaskIds = array_unique($affectedTaskIds);
        foreach ($affectedTaskIds as $taskId) {
            $this->updateTaskStatus($taskId);
        }
        
        $stat = [
            'total' => $total,
            'success' => $success,
            'failed' => $failed
        ];
        return jsons(200, '推送完成', [
            'stat' => $stat,
            'results' => $results
        ]);
    }

    /**
     * 单个子文件的推送逻辑抽象
     */
    private function processSingleTaskInfo($taskInfo, $action)
    {
        if (!$taskInfo) {
            return ['id' => null, 'status' => 'failed', 'msg' => '子文件不存在'];
        }
                $rabbitMQ = new RabbitMQ();
        try {
            switch ($action) {
                case 2: // clear
                    if ($taskInfo->is_clear == QueueConstants::STATUS_YES || $taskInfo->step == QueueConstants::STEP_CLEARING) {
                        return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '已降噪或正在降噪，请勿重复提交'];
                    }
                    $rabbitMQ->publishMessage(QueueConstants::QUEUE_AUDIO_CLEAR, [
                        'task_info' => $taskInfo->toArray()
                    ]);
                    $taskInfo->step = QueueConstants::STEP_CLEARING;
                    $taskInfo->save();
                    return ['id' => $taskInfo->id, 'status' => 'success', 'msg' => '已推送到降噪队列'];
                case 3: // quick
                    if ($taskInfo->fast_status == QueueConstants::STATUS_YES || $taskInfo->step == QueueConstants::STEP_FAST_RECOGNIZING) {
                        return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '已识别或正在识别，请勿重复提交'];
                    }
                    $rabbitMQ->publishMessage(QueueConstants::QUEUE_FAST_PROCESS, [
                        'task_info' => $taskInfo->toArray()
                    ]);
                    $taskInfo->step = QueueConstants::STEP_FAST_RECOGNIZING;
                    $taskInfo->save();
                    return ['id' => $taskInfo->id, 'status' => 'success', 'msg' => '已推送到快速识别队列'];
                case 4: // transcribe
                    // 1. 正在转写中，禁止重复提交
                    if ($taskInfo->step == QueueConstants::STEP_TRANSCRIBING) {
                        return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '正在转写，请勿重复提交'];
                    }
                    
                    // 2. 已转写完成的文件，根据降噪状态判断是否允许重新转写
                    if ($taskInfo->transcribe_status == QueueConstants::STATUS_YES) {
                        // 如果是已降噪文件且已完成转写，不允许重复提交
                        if ($taskInfo->is_clear == QueueConstants::STATUS_YES && $taskInfo->step == QueueConstants::STEP_ALL_COMPLETED) {
                            return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '已降噪文件已完成转写，请勿重复提交'];
                        }
                        // 如果是未降噪文件且已完成转写，检查当前是否已降噪
                        if ($taskInfo->is_clear == QueueConstants::STATUS_NO && $taskInfo->step == QueueConstants::STEP_UNCLEAR_TRANSCRIBE) {
                            return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '未降噪文件已完成转写，请勿重复提交'];
                        }
                        // 如果是未降噪转写过的文件，但现在已降噪，允许重新转写（降噪后音质更好）
                    }
                   
                    $rabbitMQ->publishMessage(QueueConstants::QUEUE_TRANSCRIBE, [
                        'task_info' => $taskInfo->toArray()
                    ]);
                    $taskInfo->step = QueueConstants::STEP_TRANSCRIBING;
                    $taskInfo->save();
                    return ['id' => $taskInfo->id, 'status' => 'success', 'msg' => '已推送到转写队列'];
                default:
                    return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '未知操作类型'];
            }
        } catch (\Exception $e) {
            return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => $e->getMessage()];
        }
    }

    /**
     * 处理队列任务回调 - 各节点worker处理完后回调
     * 根据task_type和status更新对应字段和step
     */
    public function handleTaskCallback(Request $request)
    {
        $taskId = $request->input('task_id');
        $taskType = $request->input('task_type');
        $status = $request->input('status');
        $message = $request->input('message', '');
        $data = $request->input('data', []);


        if (empty($taskId) || empty($taskType) || empty($status)) {
            return jsons(400, '缺少必要参数');
        }
        $aiLog = new AiLog();
        $aiLog->task_id = $taskId;
        $aiLog->task_type = $taskType;
        $aiLog->status = $status;
        $aiLog->message = $message;
        $aiLog->log = json_encode($data, JSON_UNESCAPED_UNICODE);
        $aiLog->save();
            $taskInfo = TaskInfo::find($taskId);
            if (!$taskInfo) {
                return jsons(400, '任务不存在');
            }
            if ($status === 'success') {
            switch ($taskType) {
                case QueueConstants::TASK_TYPE_EXTRACT:
                    $taskInfo->is_extract = QueueConstants::STATUS_YES;
                    $taskInfo->voice_url = $data['voice_url'] ?? '';
                    $taskInfo->total_voice = $data['duration'] ?? '';
                    $taskInfo->step = QueueConstants::STEP_EXTRACT_COMPLETED;
                    break;
                case QueueConstants::TASK_TYPE_CONVERT:
                    $taskInfo->is_clear = QueueConstants::STATUS_YES;
                    $taskInfo->clear_url = $data['clear_url'] ?? '';
                    $taskInfo->step = QueueConstants::STEP_CLEAR_COMPLETED;
                    break;
                case QueueConstants::TASK_TYPE_FAST_RECOGNITION:
                    $taskInfo->fast_status = QueueConstants::STATUS_YES;
                    $taskInfo->effective_voice = $data['effective_voice'] ?? '';
                    $taskInfo->step = QueueConstants::STEP_FAST_COMPLETED;
                    break;
                case QueueConstants::TASK_TYPE_TEXT_CONVERT:
                    $taskInfo->transcribe_status = QueueConstants::STATUS_YES;
                    $taskInfo->language = $data['language'] ?? '';
                    $taskInfo->text_info = isset($data['text_info']) ? json_encode($data['text_info'], JSON_UNESCAPED_UNICODE) : '';
                    if ($taskInfo->is_clear == QueueConstants::STATUS_YES) {
                        $taskInfo->step = QueueConstants::STEP_ALL_COMPLETED;
                            } else {
                        $taskInfo->step = 11; // 未降噪转写
                    }
                    break;
            }
            $taskInfo->error_msg = '';
        } else {
        $taskInfo->error_msg = $message;
        $taskInfo->retry_count += 1;
        $taskInfo->step = QueueConstants::STEP_FAILED;
        }

            $taskInfo->save();
            
            // 🔥 新增：更新任务表的状态
            $this->updateTaskStatus($taskInfo->tid);
            
        return jsons(200, '回调处理成功');
    }

    /**
     * 根据任务子项的完成情况更新主任务状态
     * 
     * @param int $taskId 任务ID
     * @return void
     */
    private function updateTaskStatus($taskId)
    {
        try {
            // 获取任务的所有子项
            $taskInfos = TaskInfo::where('tid', $taskId)->select();
            if (!$taskInfos || $taskInfos->isEmpty()) {
                return;
            }

            $totalFiles = $taskInfos->count();
            $detectedFiles = 0; // 已检测文件数（fast_status=1）
            $transcribedFiles = 0; // 已转写文件数（transcribe_status=1）
            $processingFiles = 0; // 正在处理的文件数
            
            // 正在处理或等待处理的步骤（除了已完成、失败、暂停状态外的所有状态）
            $processingSteps = [
                QueueConstants::STEP_UPLOADED,           // 0 - 文件已上传，等待处理
                QueueConstants::STEP_EXTRACTING,         // 1 - 正在提取音频
                QueueConstants::STEP_EXTRACT_COMPLETED,  // 2 - 音频提取完成，等待降噪
                QueueConstants::STEP_CLEARING,           // 3 - 正在音频降噪
                QueueConstants::STEP_CLEAR_COMPLETED,    // 4 - 音频降噪完成，等待下一步处理
                QueueConstants::STEP_FAST_RECOGNIZING,   // 5 - 正在快速识别
                QueueConstants::STEP_FAST_COMPLETED,     // 6 - 快速识别完成，等待用户选择是否转写
                QueueConstants::STEP_TRANSCRIBING        // 7 - 正在文本转写
            ];
            
            foreach ($taskInfos as $taskInfo) {
                if ($taskInfo->fast_status == QueueConstants::STATUS_YES) {
                    $detectedFiles++;
                }
                if ($taskInfo->transcribe_status == QueueConstants::STATUS_YES) {
                    $transcribedFiles++;
                }
                if (in_array($taskInfo->step, $processingSteps)) {
                    $processingFiles++;
                }
            }

            // 根据完成情况确定任务状态
            $newStatus = QueueConstants::TASK_STATUS_EMPTY; // 默认空任务状态
            
            if ($processingFiles > 0) {
                // 有文件正在处理中或等待处理
                $newStatus = QueueConstants::TASK_STATUS_PROCESSING; // 处理中
            } elseif ($transcribedFiles == $totalFiles) {
                // 所有文件都已转写完成
                $newStatus = QueueConstants::TASK_STATUS_CONVERTED; // 已转写
            } elseif ($detectedFiles == $totalFiles) {
                // 所有文件都已检测完成但未全部转写
                $newStatus = QueueConstants::TASK_STATUS_CHECKED; // 已检测
            } elseif ($detectedFiles > 0 || $transcribedFiles > 0) {
                // 部分文件已处理
                $newStatus = QueueConstants::TASK_STATUS_CHECKED; // 已检测
            } else {
                // 所有文件都还没有开始处理
                $newStatus = QueueConstants::TASK_STATUS_EMPTY; // 空任务
            }

            // 更新任务状态
            $task = Task::find($taskId);
            if ($task && $task->status != $newStatus) {
                $task->status = $newStatus;
                $task->save();
                
                error_log("任务状态已更新 - 任务ID: {$taskId}, 旧状态: {$task->status}, 新状态: {$newStatus}, 总文件: {$totalFiles}, 已检测: {$detectedFiles}, 已转写: {$transcribedFiles}, 处理中: {$processingFiles}");
            }
            
        } catch (\Exception $e) {
            error_log("更新任务状态失败 - 任务ID: {$taskId}, 错误: " . $e->getMessage());
        }
    }

    /**
     * 上传接口（节点处理结果文件上传）
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
