<?php

namespace app\controller;

use support\Request;
use app\api\model\TaskInfo;
use app\api\model\AiLog;
use app\service\RabbitMQ;
use app\constants\QueueConstants;

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
        if (!empty($taskinfoIds)) {
            foreach ($taskinfoIds as $tid) {
                $taskInfo = TaskInfo::find($tid);
                $results[] = $this->processSingleTaskInfo($taskInfo, $action);
            }
        } elseif (!empty($taskIds)) {
            foreach ($taskIds as $taskId) {
                $taskInfos = TaskInfo::where('tid', $taskId)->select();
                foreach ($taskInfos as $taskInfo) {
                    $results[] = $this->processSingleTaskInfo($taskInfo, $action);
                }
            }
        } else {
            return jsons(400, '请传入 taskinfo_id 或 task_id');
        }
        return jsons(200, '推送完成', $results);
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
                    if (!in_array($taskInfo->step, [QueueConstants::STEP_EXTRACT_COMPLETED, 11])) {
                        return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '当前状态不允许降噪'];
                    }
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
                    if (!in_array($taskInfo->step, [QueueConstants::STEP_CLEAR_COMPLETED, QueueConstants::STEP_EXTRACT_COMPLETED])) {
                        return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '当前状态不允许快速识别'];
                    }
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
                    if ($taskInfo->step == QueueConstants::STEP_EXTRACT_COMPLETED && $taskInfo->is_clear != QueueConstants::STATUS_YES) {
                        $taskInfo->step = 11; // 未降噪转写
                    }
                    if (!in_array($taskInfo->step, [QueueConstants::STEP_CLEAR_COMPLETED, QueueConstants::STEP_FAST_COMPLETED, 11])) {
                        return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '当前状态不允许转写'];
                    }
                    if ($taskInfo->transcribe_status == QueueConstants::STATUS_YES || $taskInfo->step == QueueConstants::STEP_TRANSCRIBING) {
                        return ['id' => $taskInfo->id, 'status' => 'failed', 'msg' => '已转写或正在转写，请勿重复提交'];
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
                    $taskInfo->text_info = $data['text_info'] ?? '';
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
        $aiLog = new AiLog();
        $aiLog->task_id = $taskId;
        $aiLog->task_type = $taskType;
        $aiLog->status = $status;
        $aiLog->message = $message;
        $aiLog->data = $data;
        $aiLog->save();
        $taskInfo->save();
        return jsons(200, '回调处理成功');
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
