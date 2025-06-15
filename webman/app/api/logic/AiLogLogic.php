<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\logic;

use plugin\saiadmin\basic\BaseLogic;
use plugin\saiadmin\exception\OperationException;
use plugin\saiadmin\utils\Helper;
use app\api\model\AiLog;

/**
 * 日志记录逻辑层
 */
class AiLogLogic extends BaseLogic
{
    /**
     * 构造函数
     */
    public function __construct()
    {
        $this->model = new AiLog();
    }

}
