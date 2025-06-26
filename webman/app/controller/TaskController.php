<?php

namespace app\controller;

use support\Request;
use support\Response;
use app\api\model\Task;
use app\api\model\TaskInfo;
use plugin\saiadmin\app\logic\system\SystemAttachmentLogic;
use Exception;

class TaskController
{
    /**
     * 创建任务
     */
    public function createTask(Request $request)
    {
        $uid = $request->user['id'];
        $name = $request->post('name'); //任务昵称

        //检查参数状态
        if (empty($name)) return jsons(400, '请填写任务名称');

        //该编号包括用户编号、日期、该用户该日期任务序号
        $today = date('Ymd');
        // 用户ID补0为6位
        $paddedUid = str_pad($uid, 6, '0', STR_PAD_LEFT);
        // 获取该用户今天的任务数量
        $todayTaskCount = Task::where('uid', $uid)
            ->where('number', 'like', $paddedUid . $today . '%')
            ->count();
        // 序号补零，确保是3位数
        $sequence = str_pad($todayTaskCount + 1, 3, '0', STR_PAD_LEFT);
        // 组合成最终的任务编号：用户ID（6位，不足补0） + 日期 + 序号
        $number = $paddedUid . $today . $sequence;

        $data = [
            'uid' => $uid,
            'number' => $number,
            'name' => $name,
            'status' => 1,
        ];

        try {
            $task = new Task();
            $task->save($data);
            return jsons(200, '任务创建成功', ['number' => $number]);
        } catch (\Exception $e) {
            // 使用 getMessage() 获取具体错误信息
            return jsons(400, '任务创建失败：' . $e->getMessage());
        }
    }

    /**
     * 获取用户任务列表 - 支持搜索、排序、筛选、分页
     * 
     * 参考AdminController::getUserList的参数构建方式进行优化
     * 
     * @param Request $request 请求对象，支持以下参数：
     * @param int $page 页码，默认第1页，最小值为1
     * @param int $limit 每页数量，默认10条，范围1-100
     * @param string $search 搜索关键词，支持任务名称和任务编号模糊搜索
     * @param string $order_field 排序字段，支持：id, name, number, status, create_time, update_time
     * @param string $order_type 排序方向：asc(升序) 或 desc(降序)，默认desc
     * @param int $status 状态筛选，可选值：1-空任务, 2-已检测, 3-已转写, 4-处理中, 5-暂停中
     * @param string $start_time 开始时间筛选，格式：Y-m-d
     * @param string $end_time 结束时间筛选，格式：Y-m-d
     * @param string $fields 查询字段，默认：id,number,name,status,create_time,update_time
     * 
     * @return Response 返回JSON格式的任务列表数据
     */
    public function taskList(Request $request)
    {
        $uid = $request->user['id'];
        
        // 获取所有查询参数
        $page = (int)$request->post('page', 1);
        $limit = (int)$request->post('limit', 10);
        $search = $request->post('search', '');
        $order_field = $request->post('order_field', 'create_time'); // 改为order_field统一命名
        $order_type = $request->post('order_type', 'desc'); // 改为order_type统一命名
        $status = $request->post('status', '');
        $start_time = $request->post('start_time', '');
        $end_time = $request->post('end_time', '');
        $fields = $request->post('fields', 'id,number,name,status,create_time,update_time');
        
        // 参数验证 - 参考AdminController的验证方式
        if ($page < 1) {
            $page = 1;
        }
        if ($limit < 1 || $limit > 100) {
            $limit = 10;
        }
        
        // 验证排序字段，防止SQL注入
        $allowed_order_fields = ['id', 'name', 'number', 'status', 'create_time', 'update_time'];
        if (!in_array($order_field, $allowed_order_fields)) {
            $order_field = 'create_time';
        }
        
        // 验证排序方向
        $order_type = in_array(strtolower($order_type), ['asc', 'desc']) ? strtolower($order_type) : 'desc';
        
        // 验证状态值
        if ($status !== '' && !in_array($status, [1, 2, 3, 4, 5])) {
            $status = '';
        }

        try {
            // 构建查询 - 增加字段筛选功能
            $query = Task::field($fields)->where('uid', $uid);

            // 搜索条件 - 参考AdminController的搜索方式
            if (!empty($search)) {
                $query->where(function($query) use ($search) {
                    $query->whereLike('name', '%' . $search . '%')
                          ->whereOr('number', 'like', '%' . $search . '%');
                });
            }

            // 状态筛选
            if ($status !== '') {
                $query->where('status', $status);
            }

            // 时间范围筛选
            if (!empty($start_time)) {
                $query->where('create_time', '>=', $start_time . ' 00:00:00');
            }
            if (!empty($end_time)) {
                $query->where('create_time', '<=', $end_time . ' 23:59:59');
            }
            
            // 排除已删除的任务（如果有软删除字段）
            $query->whereNull('delete_time');

            // 排序
            $query->order($order_field, $order_type);

            // 分页查询
            $result = $query->paginate([
                'list_rows' => $limit,
                'page' => $page
            ]);

            $currentPage = $result->currentPage();
            $lastPage = $result->lastPage();

            // 构建返回数据 - 参考AdminController的返回格式
            return jsons(200, '获取任务列表成功', [
                'list' => $result->items(),
                'total' => $result->total(),
                'current_page' => $currentPage,
                'per_page' => $result->listRows(),
                'last_page' => $lastPage,
                'has_more' => $currentPage < $lastPage,
                'search_params' => [
                    'search' => $search,
                    'status' => $status,
                    'start_time' => $start_time,
                    'end_time' => $end_time,
                    'order_field' => $order_field,
                    'order_type' => $order_type
                ],
                'filter_options' => [
                    'status_options' => [
                        ['value' => '', 'label' => '全部状态'],
                        ['value' => 1, 'label' => '空任务'],
                        ['value' => 2, 'label' => '已检测'],
                        ['value' => 3, 'label' => '已转写'],
                        ['value' => 4, 'label' => '处理中'],
                        ['value' => 5, 'label' => '暂停中']
                    ],
                    'sort_options' => [
                        ['value' => 'id', 'label' => 'ID'],
                        ['value' => 'name', 'label' => '任务名称'],
                        ['value' => 'number', 'label' => '任务编号'],
                        ['value' => 'status', 'label' => '任务状态'],
                        ['value' => 'create_time', 'label' => '创建时间'],
                        ['value' => 'update_time', 'label' => '更新时间']
                    ],
                    'order_types' => [
                        ['value' => 'desc', 'label' => '降序'],
                        ['value' => 'asc', 'label' => '升序']
                    ]
                ]
            ]);
        } catch (Exception $e) {
            // 返回更详细的错误信息
            return jsons(500, '获取任务列表失败', $e->getMessage());
        }
    }

    /**
     * 删除任务
     */
    public function deleteTask(Request $request)
    {
        $id = $request->post('id');

        if (empty($id)) {
            return jsons(400, '任务ID不能为空');
        }

        try {
            $task = Task::where('id', $id)->find();
            if (!$task) {
                return jsons(400, '任务不存在');
            }

            $task->delete();
            return jsons(200, '任务删除成功');
        } catch (Exception $e) {
            return jsons(400, '任务删除失败：' . $e->getMessage());
        }
    }

    /**
     * 更新任务
     */
    public function updateTask(Request $request)
    {
        $id = $request->post('id');
        $name = $request->post('name');
        $status = $request->post('status');

        if (empty($id)) return jsons(400, '任务ID不能为空');
        // if(empty($name)) return jsons(400,'任务名称不能为空');
        // if(empty($status)) return jsons(400,'任务状态不能为空');

        $task = Task::where('id', $id)->find();
        if (!$task) return jsons(400, '任务不存在');
        try {
            if (!empty($name)) $task->name = $name;
            if (!empty($status)) $task->status = $status;
            $task->save();
            return jsons(200, '任务更新成功');
        } catch (Exception $e) {
            return jsons(400, '任务更新失败：' . $e->getMessage());
        }
    }

    /**
     * 文件上传
     * @param Request $request
     * @return Response
     */
    public function upload(Request $request): Response
    {
        // 检查任务 ID  
        $taskId = $request->post('task_id');
        if (empty($taskId)) return jsons(400, '任务ID不能为空');

        // 检查任务是否存在  
        $task = Task::where('id', $taskId)->find();
        if (!$task) return jsons(400, '任务不存在');

        // 检查任务是否属于当前用户  
        if ($task->uid != $request->user['id']) return jsons(400, '任务不属于当前用户');

        // 检查任务状态是否允许上传文件  
        if ($task->status == 3) return jsons(400, '任务已转写完成，无法上传文件');
        if ($task->status == 4) return jsons(400, '任务处理中，无法上传文件');
        if ($task->status == 2) return jsons(400, '任务已检测，无法上传文件');

        // 只有空任务(1)和暂停中(5)状态可以上传文件  
        if (!in_array($task->status, [1, 5])) return jsons(400, '当前任务状态不允许上传文件');

        try {
            // 处理多字段文件上传，比如file,file2,file3
            $logic = new SystemAttachmentLogic();
            $uploadResults = [];
            $files = $request->file();
            
            // 如果没有文件上传
            if (empty($files)) {
                return jsons(400, '请选择要上传的文件');
            }
            
            // 遍历所有上传的文件字段
            foreach ($files as $fieldName => $file) {
                try {
                    // 直接使用指定字段的文件上传
                    $result = $this->uploadFileByField($fieldName, $file);
                    $uploadResults[$fieldName] = $result;
                    
                    // 根据 MIME 类型判断文件类型
                    $mimeType = $result['mime_type'] ?? '';
                    $fileType = 1; // 默认为语音
                    
                    // 判断文件类型：1-语音 2-视频
                    if (strpos($mimeType, 'video/') === 0) {
                        $fileType = 2; // 视频文件
                    } elseif (strpos($mimeType, 'audio/') === 0) {
                        $fileType = 1; // 音频文件
                    } else {
                        // 根据文件扩展名判断
                        $suffix = strtolower($result['suffix'] ?? '');
                        $videoExtensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', '3gp', 'mpg', 'mpeg'];
                        $audioExtensions = ['mp3', 'wav', 'aac', 'flac', 'ogg', 'wma', 'm4a', 'opus'];
                        
                        if (in_array($suffix, $videoExtensions)) {
                            $fileType = 2; // 视频文件
                        } elseif (in_array($suffix, $audioExtensions)) {
                            $fileType = 1; // 音频文件
                        }
                    }
                    
                    // 将文件信息保存到 TaskInfo 表
                    $taskInfo = new TaskInfo();
                    $taskInfoData = [
                        'tid' => $taskId,
                        'filename' => $result['origin_name'] ?? '',
                        'size' => $result['size_info'] ?? '',
                        'type' => $fileType, // 根据文件类型设置：1-语音 2-视频
                        'url' => $result['url'] ?? '',
                        'is_extract' =>$fileType, // 根据文件类型设置：1-语音 2-视频 默认未提取2，是视频没有提取
                        'is_clear' => 2, // 默认未清理
                        'fast_status' => 2, // 默认状态
                        'transcribe_status' => 2, // 默认转写状态
                        'retry_count' => 0,
                        'create_time' => date('Y-m-d H:i:s'),
                        'update_time' => date('Y-m-d H:i:s')
                    ];
                    
                    $taskInfo->save($taskInfoData);
                    
                    // 在返回结果中添加数据库记录ID
                    $uploadResults[$fieldName]['task_info_id'] = $taskInfo->id;
                    
                } catch (\Exception $e) {
                    return jsons(400, "文件字段 {$fieldName} 上传失败：" . $e->getMessage());
                }
            }
            //更新任务状态为暂停中(5)，表示有文件上传
            $task->status = 5;
            $task->save();
            
            return jsons(200, '文件上传成功', [
                'total_files' => count($uploadResults),
                'upload_results' => $uploadResults
            ]);
            
        } catch (\Exception $e) {
            return jsons(400, '多文件上传失败：' . $e->getMessage());
        }
    }

    /**
     * 上传指定字段的文件
     * @param string $fieldName
     * @param $file
     * @return array
     */
    private function uploadFileByField($fieldName, $file)
    {
        $configLogic = new \plugin\saiadmin\app\logic\system\SystemConfigLogic();
        $uploadConfig = $configLogic->getGroup('upload_config');
        
        // 检查文件大小
        $file_size = $file->getSize();
        $maxSize = \plugin\saiadmin\utils\Arr::getConfigValue($uploadConfig, 'upload_size') ?? 104857600; // 默认100MB
        if ($file_size > $maxSize) {
            throw new \Exception('文件大小超过限制');
        }

        // 检查文件类型
        $ext = $file->getUploadExtension();
        $allowFile = \plugin\saiadmin\utils\Arr::getConfigValue($uploadConfig, 'upload_allow_file') ?? 'mp3,mp4,wav,avi,mov,wmv,flv';
        $allowFileArray = explode(',', $allowFile);
        if (!in_array($ext, $allowFileArray)) {
            throw new \Exception('不支持该格式的文件上传');
        }

        // 生成文件保存路径
        $root = \plugin\saiadmin\utils\Arr::getConfigValue($uploadConfig, 'local_root') ?? 'public/storage/';
        $folder = date('Ymd');
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

        // 保存到系统附件表
        $attachment = new \plugin\saiadmin\app\model\system\SystemAttachment();
        $attachment->save($result);

        return $result;
    }

    /**
     * 格式化文件大小
     * @param int $bytes
     * @return string
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
     * 获取文件快速检测进度
     */
    public function getFileProgress(Request $request)
    {
        $taskId = $request->post('task_id');
        if (empty($taskId)) return jsons(400, '任务ID不能为空');

        $task = Task::where('id', $taskId)->find();
        if (!$task) return jsons(400, '任务不存在');
        $taskInfo = TaskInfo::where('tid', $taskId)->select();
        //需要返回文件总数量，文件大小，文件总时长，预计检测时间，检测进度
        $total = count($taskInfo);
        $size = 0;
        $total_voice = 0;
        $progress = 0;
        // 新增：size字符串转字节数
        $parseSizeToBytes = function($sizeStr) {
            if (preg_match('/([\\d.]+)\\s*(B|KB|MB|GB|TB)/i', $sizeStr, $matches)) {
                $num = (float)$matches[1];
                $unit = strtoupper($matches[2]);
                switch ($unit) {
                    case 'TB': $num *= 1024;
                    case 'GB': $num *= 1024;
                    case 'MB': $num *= 1024;
                    case 'KB': $num *= 1024;
                }
                return (int)$num;
            }
            return 0;
        };
        foreach ($taskInfo as $item) {
            $size += $parseSizeToBytes($item->size);
            $total_voice += floatval($item->total_voice);
            if ($item->fast_status == 1) { // 用 fast_status 判断进度
                $progress++;
            }
        }
        $progress_percent = $total > 0 ? ($progress / $total * 100) : 0;
        $progress_percent = round($progress_percent, 2);
        $size_info = round($size / 1024 / 1024, 2) . ' MB';
        $duration_info = gmdate("H:i:s", (int)$total_voice);
        $estimate_time = round($total_voice * 0.1);
        $estimate_time_info = gmdate("H:i:s", $estimate_time);
        return jsons(200, '获取文件检测进度成功', [
            'total' => $total, // 文件总数量
            'size' => $size, // 文件总大小(字节)
            'size_info' => $size_info, // 文件总大小(MB)
            'total_voice' => $total_voice, // 总时长(秒)
            'duration_info' => $duration_info, // 总时长(时:分:秒)
            'estimate_time' => $estimate_time, // 预计检测时间(秒)
            'estimate_time_info' => $estimate_time_info, // 预计检测时间(时:分:秒)
            'progress' => $progress_percent, // 检测进度百分比
            'status' => $task->status // 任务状态: 1-空任务, 2-已检测, 3-已转写, 4-处理中, 5-暂停中
        ]);
    }

    /**
     * 获取文件转写进度
     */
    public function getFileTranscriptionProgress(Request $request)
    {
        $taskId = $request->post('task_id');
        if (empty($taskId)) return jsons(400, '任务ID不能为空');

        $task = Task::where('id', $taskId)->find();
        if (!$task) return jsons(400, '任务不存在');
        $taskInfo = TaskInfo::where('tid', $taskId)->select();
        $total = count($taskInfo);
        $progress = 0;
        $total_voice = 0;
        // 统计文件总大小
        $parseSizeToBytes = function($sizeStr) {
            if (preg_match('/([\\d.]+)\\s*(B|KB|MB|GB|TB)/i', $sizeStr, $matches)) {
                $num = (float)$matches[1];
                $unit = strtoupper($matches[2]);
                switch ($unit) {
                    case 'TB': $num *= 1024;
                    case 'GB': $num *= 1024;
                    case 'MB': $num *= 1024;
                    case 'KB': $num *= 1024;
                }
                return (int)$num;
            }
            return 0;
        };
        $size = 0;
        foreach ($taskInfo as $item) {
            $size += $parseSizeToBytes($item->size);
            $total_voice += floatval($item->total_voice);
            if ($item->transcribe_status == 1) {
                $progress++;
            }
        }
        $size_info = round($size / 1024 / 1024, 2) . ' MB';
        $progress_percent = $total > 0 ? ($progress / $total * 100) : 0;
        $progress_percent = round($progress_percent, 2);
        $duration_info = gmdate("H:i:s", (int)$total_voice);
        $estimate_time = round($total_voice * 0.1); // 10%
        $estimate_time_info = gmdate("H:i:s", $estimate_time);
        return jsons(200, '获取文件转写进度成功', [
            'total' => $total, // 文件总数量
            'size' => $size, // 文件总大小(字节)
            'size_info' => $size_info, // 文件总大小(MB)
            'total_voice' => $total_voice, // 总时长(秒)
            'duration_info' => $duration_info, // 总时长(时:分:秒)
            'estimate_time' => $estimate_time, // 预计转写时间(秒)
            'estimate_time_info' => $estimate_time_info, // 预计转写时间(时:分:秒)
            'progress' => $progress_percent, // 转写进度百分比
            'status' => $task->status // 任务状态: 1-空任务, 2-已检测, 3-已转写, 4-处理中, 5-暂停中
        ]);
    }

    /**
     * 获取任务统计
     */
    public function getTaskStatistics(Request $request)
    {
        $taskId = $request->post('task_id');
        if (empty($taskId)) return jsons(400, '任务ID不能为空');

        $task = Task::where('id', $taskId)->find();
        if (!$task) return jsons(400, '任务不存在');
        //需要返回总文件数，有效文件数，已转写文件数，已降噪文件数量
        $taskInfo = TaskInfo::where('tid', $taskId)->select();
        $total = count($taskInfo);
        $valid = 0;
        $valid_duration = 0;
        $transcribed = 0;
        $cleared = 0;
        foreach ($taskInfo as $item) {
            if (!empty($item->effective_voice) && floatval($item->effective_voice) > 0) {
                $valid++;
                $valid_duration += floatval($item->effective_voice);
            }
            if ($item->transcribe_status == 1) {
                $transcribed++;
            }
            if ($item->is_clear == 1) {
                $cleared++;
            }
        }
        return jsons(200, '获取任务统计成功', [
            'total' => $total, // 总文件数
            'valid' => $valid, // 有效文件数
            // 'valid_duration' => $valid_duration, // 有效时长(秒)
            'transcribed' => $transcribed, // 已转写文件数
            'cleared' => $cleared, // 已降噪文件数量
            'create_time' => $task->create_time, // 创建时间
            'update_time' => $task->update_time // 更新时间
        ]);
    }

    /**
     * 获取任务子文件详细信息
     */
    public function getTaskFileDetail(Request $request)
    {
        $taskInfoId = $request->post('task_info_id');
        if (empty($taskInfoId)) return jsons(400, '任务子文件ID不能为空');

        $taskInfo = TaskInfo::where('id', $taskInfoId)->find();
        if (!$taskInfo) return jsons(400, '任务子文件不存在');

        return jsons(200, '获取任务子文件详细信息成功', $taskInfo); 
        
    }
}
