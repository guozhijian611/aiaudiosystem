<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\controller;

use plugin\saiadmin\basic\BaseController;
use app\api\logic\TaskInfoLogic;
use app\api\validate\TaskInfoValidate;
use support\Request;
use support\Response;

/**
 * 任务详情控制器
 */
class TaskInfoController extends BaseController
{
    /**
     * 构造函数
     */
    public function __construct()
    {
        $this->logic = new TaskInfoLogic();
        $this->validate = new TaskInfoValidate;
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
            ['tid', ''],
            ['filename', ''],
            ['type', ''],
            ['is_extract', ''],
            ['is_clear', ''],
            ['fast_status', ''],
            ['transcribe_status', ''],
            ['effective_voice', ''],
            ['total_voice', ''],
            ['language', ''],
        ]);
        $query = $this->logic->search($where);
        $data = $this->logic->getList($query);
        return $this->success($data);
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
            ['tid', ''],
            ['filename', ''],
            ['type', ''],
            ['is_extract', ''],
            ['is_clear', ''],
            ['fast_status', ''],
            ['transcribe_status', ''],
            ['effective_voice', ''],
            ['total_voice', ''],
            ['language', ''],
        ]);
        return $this->logic->export($where);
    }

}
