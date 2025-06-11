<?php

namespace app\controller;

use support\Request;
use app\api\model\User;
use app\exception\ApiException;

class AdminController
{
    /**
     * 构造函数鉴权
     */
    public function __construct()
    {
        // 获取当前请求对象
        $request = request();
        
        // 判断是否是管理员 1为管理员 2为普通用户
        if (!isset($request->user['role']) || $request->user['role'] != 1) {
            // 使用自定义异常返回 JSON 响应
            throw new ApiException('您没有权限', 403);
        }
    }

    /**
     * 更新用户状态
     */
    public function updateUserStatus(Request $request)
    {
        $uid = $request->post('uid');
        $status = $request->post('status');
      
        // 判断参数是否符合规则
        if (empty($uid) || empty($status)) {
            return jsons(400, '参数为空');
        }
        
        // 判断状态是否为1正常或2禁用
        if ($status != 1 && $status != 2) {
            return jsons(400, '状态值错误');
        }
        
        // 判断用户是否存在
        $user = User::where('id', $uid)->find();
        if (!$user) {
            return jsons(400, '用户不存在');
        }
        
        // 更新用户状态
        $user->status = $status;
        $user->save();
        return jsons(200, '更新成功');
    }
    /**
     * 删除用户
     */
    public function deleteUser(Request $request)
    {
        $uid = $request->post('uid');
        //判断参数
        if (empty($uid)) {
            return jsons(400, '参数为空');
        }
        //不能删除自己
        if ($uid == $request->user['id']) {
            return jsons(400, '不能删除自己');
        }
        //判断用户是否存在
        $user = User::where('id', $uid)->find();
        if (!$user) {
            return jsons(400, '用户不存在');
        }
        
        // 软删除用户 - 使用 ThinkORM 的软删除功能
        try {
            $user->delete();
            return jsons(200, '删除成功');
        } catch (\Exception $e) {
            throw new ApiException('删除失败', 500);
        }
    }

    /**
     * 获取用户列表，支持分页、搜索、排序、字段筛选
     */
    public function getUserList(Request $request)
    {
        $page = (int)$request->post('page', 1);
        $limit = (int)$request->post('limit', 10);
        $search = $request->post('search', ''); // 搜索关键词
        $role = $request->post('role', ''); // 角色筛选
        $status = $request->post('status', ''); // 状态筛选
        $order_field = $request->post('order_field', 'create_time'); // 排序字段
        $order_type = $request->post('order_type', 'desc'); // 排序方式
        $fields = $request->post('fields', 'id,username,nickname,role,status,create_time'); // 查询字段
        
        // 参数验证
        if ($page < 1) {
            $page = 1;
        }
        if ($limit < 1 || $limit > 100) {
            $limit = 10;
        }
        
        // 验证排序字段
        $allowed_order_fields = ['id', 'username', 'nickname', 'role', 'status', 'create_time'];
        if (!in_array($order_field, $allowed_order_fields)) {
            $order_field = 'create_time';
        }
        
        // 验证排序方式
        $order_type = in_array(strtolower($order_type), ['asc', 'desc']) ? strtolower($order_type) : 'desc';
        
        try {
            // 构建查询
            $query = User::field($fields);
            
            // 搜索条件
            if (!empty($search)) {
                $query->where(function($query) use ($search) {
                    $query->whereLike('username', '%' . $search . '%')
                          ->whereOr('nickname', 'like', '%' . $search . '%');
                });
            }
            
            // 角色筛选
            if ($role !== '') {
                $query->where('role', $role);
            }
            
            // 状态筛选
            if ($status !== '') {
                $query->where('status', $status);
            }
            
            // 排除已删除的用户（如果有软删除字段）
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
            
            return jsons(200, '获取成功', [
                'list' => $result->items(),
                'total' => $result->total(),
                'current_page' => $currentPage,
                'per_page' => $result->listRows(),
                'last_page' => $lastPage,
                'has_more' => $currentPage < $lastPage,
                'search_params' => [
                    'search' => $search,
                    'role' => $role,
                    'status' => $status,
                    'order_field' => $order_field,
                    'order_type' => $order_type
                ]
            ]);
        } catch (\Exception $e) {
            return jsons(500, '获取用户列表失败', $e->getMessage());
        }
    }

    /**
     * 获取所有任务，支持分页、搜索、排序、字段筛选
     * 管理员可以查看所有用户的任务
     */
    public function getTaskList(Request $request)
    {
        $page = (int)$request->post('page', 1);
        $limit = (int)$request->post('limit', 10);
        $search = $request->post('search', '');
        $uid = $request->post('uid', ''); // 用户ID筛选
        $status = $request->post('status', ''); // 状态筛选
        $start_time = $request->post('start_time', ''); // 开始时间
        $end_time = $request->post('end_time', ''); // 结束时间
        $order_field = $request->post('order_field', 'create_time');
        $order_type = $request->post('order_type', 'desc');
        $fields = $request->post('fields', 'id,uid,name,number,status,create_time,update_time');

        // 参数验证
        if ($page < 1) {
            $page = 1;
        }
        if ($limit < 1 || $limit > 100) {
            $limit = 10;
        }
        
        // 验证排序字段
        $allowed_order_fields = ['id', 'uid', 'name', 'number', 'status', 'create_time', 'update_time'];
        if (!in_array($order_field, $allowed_order_fields)) {
            $order_field = 'create_time';
        }
        
        // 验证排序方式
        $order_type = in_array(strtolower($order_type), ['asc', 'desc']) ? strtolower($order_type) : 'desc';
        
        // 验证状态值
        if ($status !== '' && !in_array($status, [1, 2, 3, 4, 5])) {
            $status = '';
        }
        
        try {
            // 构建查询 - 管理员可以查看所有任务
            $query = \app\api\model\Task::field($fields);
            
            // 搜索条件 - 支持任务名称、任务编号和用户ID搜索
            if (!empty($search)) {
                $query->where(function($query) use ($search) {
                    $query->whereLike('name', '%' . $search . '%')
                          ->whereOr('number', 'like', '%' . $search . '%')
                          ->whereOr('uid', 'like', '%' . $search . '%');
                });
            }
            
            // 用户ID筛选
            if ($uid !== '') {
                $query->where('uid', $uid);
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
            
            return jsons(200, '获取任务列表成功', [
                'list' => $result->items(),
                'total' => $result->total(),
                'current_page' => $currentPage,
                'per_page' => $result->listRows(),
                'last_page' => $lastPage,
                'has_more' => $currentPage < $lastPage,
                'search_params' => [
                    'search' => $search,
                    'uid' => $uid,
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
                        ['value' => 'uid', 'label' => '用户ID'],
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
                ],
                // 统计信息
                'statistics' => [
                    'total_tasks' => $result->total(),
                    'status_counts' => $this->getTaskStatusCounts()
                ]
            ]);
        } catch (\Exception $e) {
            return jsons(500, '获取任务列表失败', $e->getMessage());
        }
    }
    
    /**
     * 获取任务状态统计
     * 私有方法，用于getTaskList中的统计信息
     */
    private function getTaskStatusCounts()
    {
        try {
            $counts = \app\api\model\Task::whereNull('delete_time')
                ->field('status, count(*) as count')
                ->group('status')
                ->select()
                ->toArray();
            
            $statusMap = [
                1 => 'empty_tasks',
                2 => 'detected_tasks', 
                3 => 'transcribed_tasks',
                4 => 'processing_tasks',
                5 => 'paused_tasks'
            ];
            
            $result = [];
            foreach ($counts as $item) {
                $statusKey = $statusMap[$item['status']] ?? 'unknown_status';
                $result[$statusKey] = (int)$item['count'];
            }
            
            return $result;
        } catch (\Exception $e) {
            return [];
        }
    }
}
