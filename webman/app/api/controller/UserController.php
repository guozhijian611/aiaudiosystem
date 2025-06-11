<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\controller;

use plugin\saiadmin\basic\BaseController;
use app\api\logic\UserLogic;
use app\api\validate\UserValidate;
use support\Request;
use support\Response;

/**
 * 用户管理控制器
 */
class UserController extends BaseController
{
    /**
     * 构造函数
     */
    public function __construct()
    {
        $this->logic = new UserLogic();
        $this->validate = new UserValidate;
        parent::__construct();
    }

    /**
     * 数据列表
     * @param Request $request
     * @return Response
     */
    public function index(Request $request): Response
    {
        $where = $request->more([
            ['id', ''],
            ['username', ''],
            ['mobile', ''],
            ['role', ''],
            ['status', ''],
        ]);
        $query = $this->logic->search($where);
        $data = $this->logic->getList($query);
        return $this->success($data);
    }

    /**
     * 修改状态
     * @param Request $request
     * @return Response
     */
    public function changeStatus(Request $request) : Response
    {
        $id = $request->input('id', '');
        $status = $request->input('status', 1);
        $model = $this->logic->findOrEmpty($id);
        if ($model->isEmpty()) {
            return $this->fail('未查找到信息');
        }
        $result = $model->save(['status' => $status]);
        if ($result) {
            $this->afterChange('changeStatus', $model);
            return $this->success('操作成功');
        } else {
            return $this->fail('操作失败');
        }
    }

    /**
     * 导出数据
     * @param Request $request
     * @return Response
     */
    public function export(Request $request) : Response
    {
        $where = $request->more([
            ['id', ''],
            ['username', ''],
            ['mobile', ''],
            ['role', ''],
            ['status', ''],
        ]);
        return $this->logic->export($where);
    }

    
    /**
     * save 创建用户重写
     */
    public function save(Request $request) : Response
    {
        $data = $request->all();
        //加密密码
        $data['password'] = password_hash($data['password'], PASSWORD_DEFAULT);
        $result = $this->logic->save($data);
        return $this->success($result);
    }
}
