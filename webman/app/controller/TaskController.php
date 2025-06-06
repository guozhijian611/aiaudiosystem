<?php

namespace app\controller;

use support\Request;
use app\api\model\Task;
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
        if(empty($name)) return jsons(400,'请填写任务名称');
        
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
            return jsons(200,'任务创建成功',['number'=>$number]);
        } catch (\Exception $e) {
            // 使用 getMessage() 获取具体错误信息
            return jsons(400,'任务创建失败：' . $e->getMessage());
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
            
            return jsons(200,'获取任务列表成功',[
                'list' => $result->items(),
                'total' => $result->total(),
                'current_page' => $currentPage,
                'per_page' => $result->listRows(),
                'last_page' => $lastPage,
                'has_more' => $currentPage < $lastPage  // 修复：当前页小于最后一页时才有更多数据
            ]);
        } catch (Exception $e) {
            // 使用 getMessage() 获取具体错误信息
            return jsons(400,'获取任务列表失败：' . $e->getMessage());
        }
    }

    /**
     * 删除任务
     */
    public function deleteTask(Request $request)
    {
        $id = $request->post('id');
        
        if (empty($id)) {
            return jsons(400,'任务ID不能为空');
        }
        
        try {
            $task = Task::where('id', $id)->find();
            if (!$task) {
                return jsons(400,'任务不存在');
            }
            
            $task->delete();
            return jsons(200,'任务删除成功');
        } catch (Exception $e) {
            return jsons(400,'任务删除失败：' . $e->getMessage());
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

        if(empty($id)) return jsons(400,'任务ID不能为空');
        // if(empty($name)) return jsons(400,'任务名称不能为空');
        // if(empty($status)) return jsons(400,'任务状态不能为空');

        $task = Task::where('id', $id)->find();
        if(!$task) return jsons(400,'任务不存在');
        try{
            if(!empty($name)) $task->name = $name;
            if(!empty($status)) $task->status = $status;
            $task->save();
            return jsons(200,'任务更新成功');
        }catch(Exception $e){
            return jsons(400,'任务更新失败：' . $e->getMessage());
        }
    }
}
