<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\controller;

use plugin\saiadmin\basic\BaseController;
use app\api\logic\AiLogLogic;
use app\api\validate\AiLogValidate;
use support\Request;
use support\Response;

/**
 * 日志记录控制器
 */
class AiLogController extends BaseController
{
    /**
     * 构造函数
     */
    public function __construct()
    {
        $this->logic = new AiLogLogic();
        $this->validate = new AiLogValidate;
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
            ['task_id', ''],
            ['log', ''],
            ['task_type', ''],
            ['status', ''],
            ['create_time', ''],
        ]);
        $query = $this->logic->search($where);
        $data = $this->logic->getList($query);
        return $this->success($data);
    }

}
