<?php

namespace app\controller;

use support\Request;
use app\api\model\TaskInfo;
class TaskInfoController
{
   /**
    * 获取任务信息,需要支持分页，搜索，排序
    * @param Request $request
    * @return Response
    */
   public function getTaskInfo(Request $request)
   {
        $taskId = $request->post('task_id');
        $page = $request->post('page', 1); // 页码，默认第1页
        $limit = $request->post('limit', 10); // 每页数量，默认10条
        $search = $request->post('search', '');
        $sort = $request->post('sort', 'id');
        $order = $request->post('order', 'desc');

        if (empty($taskId)) {
            return jsons(400, '任务ID不能为空');
        }

        $taskInfo = new TaskInfo();
        try {
            $query = $taskInfo->where('tid', $taskId);
            
            // 添加搜索功能
            if (!empty($search)) {
                $query->where('filename', 'like', '%' . $search . '%');
            }
            
            // 添加排序功能
            $query->order($sort, $order);
            
            // 分页查询
            $result = $query->paginate([
                'list_rows' => $limit,
                'page' => $page
            ]);

            $currentPage = $result->currentPage();
            $lastPage = $result->lastPage();

            // 重新构建查询来获取统计信息（不分页）
            $statsQuery = $taskInfo->where('tid', $taskId);
            if (!empty($search)) {
                $statsQuery->where('filename', 'like', '%' . $search . '%');
            }
            
            // 获取统计信息
            $allRecords = $statsQuery->select();
            $count = $allRecords->count();
            $total_voice = 0;
            $effective_voice = 0;
            $total_size_bytes = 0;
            
            foreach ($allRecords as $record) {
                if (!empty($record['total_voice']) && is_numeric($record['total_voice'])) {
                    $total_voice += floatval($record['total_voice']);
                }
                if (!empty($record['effective_voice']) && is_numeric($record['effective_voice'])) {
                    $effective_voice += floatval($record['effective_voice']);
                }
                
                // 解析文件大小并累加
                if (!empty($record['size'])) {
                    $size_bytes = $this->parseSizeToBytes($record['size']);
                    $total_size_bytes += $size_bytes;
                }
            }
            
            // 格式化总大小
            $total_size_formatted = $this->formatBytes($total_size_bytes);
           
            return jsons(200, '获取任务信息成功', [
                'list' => $result->items(),
                'total' => $result->total(),
                'current_page' => $currentPage,
                'per_page' => $result->listRows(),
                'last_page' => $lastPage,
                'has_more' => $currentPage < $lastPage,  // 修复：当前页小于最后一页时才有更多数据
                'statistics' => [
                    'count' => $count,
                    'total_size' => $total_size_formatted,
                    'total_size_bytes' => $total_size_bytes,
                    'all_total_voice' => $total_voice,
                    'all_effective_voice' => $effective_voice
                ]
            ]);
        } catch (\Exception $e) {
            // 使用 getMessage() 获取具体错误信息
            return jsons(400, '获取任务信息失败：' . $e->getMessage());
        }
   }

   /**
    * 解析文件大小字符串为字节数
    * @param string $sizeStr 文件大小字符串（如 "43.05 MB"）
    * @return int 字节数
    */
   private function parseSizeToBytes($sizeStr)
   {
       if (empty($sizeStr)) {
           return 0;
       }

       // 使用正则表达式匹配数字和单位
       if (preg_match('/(\d+\.?\d*)\s*(B|KB|MB|GB|TB)/i', $sizeStr, $matches)) {
           $size_value = floatval($matches[1]);
           $unit = strtoupper($matches[2]);
           
           // 根据单位转换为字节
           switch ($unit) {
               case 'B':
                   return $size_value;
               case 'KB':
                   return $size_value * 1024;
               case 'MB':
                   return $size_value * 1024 * 1024;
               case 'GB':
                   return $size_value * 1024 * 1024 * 1024;
               case 'TB':
                   return $size_value * 1024 * 1024 * 1024 * 1024;
               default:
                   return 0;
           }
       }
       
       return 0;
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
