<?php

namespace app\controller;

use support\Request;
use support\Response;
use app\api\model\Task;
use app\api\model\TaskInfo;
use plugin\saiadmin\basic\BaseController;
use plugin\saiadmin\app\logic\system\SystemAttachmentLogic;
use Exception;

class TaskController extends BaseController
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
     * 获取用户任务列表
     */
    public function taskList(Request $request)
    {
        $uid = $request->user['id'];
        $page = $request->post('page', 1); // 页码，默认第1页
        $limit = $request->post('limit', 10); // 每页数量，默认10条

        $task = new Task();
        try {
            $result = $task->where('uid', $uid)->order('id', 'desc')->paginate([
                'list_rows' => $limit,
                'page' => $page
            ]);

            $currentPage = $result->currentPage();
            $lastPage = $result->lastPage();

            return jsons(200, '获取任务列表成功', [
                'list' => $result->items(),
                'total' => $result->total(),
                'current_page' => $currentPage,
                'per_page' => $result->listRows(),
                'last_page' => $lastPage,
                'has_more' => $currentPage < $lastPage  // 修复：当前页小于最后一页时才有更多数据
            ]);
        } catch (Exception $e) {
            // 使用 getMessage() 获取具体错误信息
            return jsons(400, '获取任务列表失败：' . $e->getMessage());
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
        if ($task->status == 5) return jsons(400, '任务已暂停，无法上传文件');

        // 只有空任务(1)和已检测(2)状态可以上传文件  
        if (!in_array($task->status, [1, 2])) return jsons(400, '当前任务状态不允许上传文件');

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
                        'is_extract' => 2, // 默认未提取
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

}
