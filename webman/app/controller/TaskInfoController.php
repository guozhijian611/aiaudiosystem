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

            return jsons(200, '获取任务信息成功', [
                'list' => $result->items(),
                'total' => $result->total(),
                'current_page' => $currentPage,
                'per_page' => $result->listRows(),
                'last_page' => $lastPage,
                'has_more' => $currentPage < $lastPage  // 修复：当前页小于最后一页时才有更多数据
            ]);
        } catch (\Exception $e) {
            // 使用 getMessage() 获取具体错误信息
            return jsons(400, '获取任务信息失败：' . $e->getMessage());
        }
   }
}
