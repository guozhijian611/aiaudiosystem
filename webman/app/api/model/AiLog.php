<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\model;

use plugin\saiadmin\basic\BaseNormalModel;

/**
 * 日志记录模型
 */
class AiLog extends BaseNormalModel
{
    /**
     * 数据表主键
     * @var string
     */
    protected $pk = 'id';

    /**
     * 数据库表名称
     * @var string
     */
    protected $table = 'ai_log';

    /**
     * 创建时间 搜索
     */
    public function searchCreateTimeAttr($query, $value)
    {
        $query->whereTime('create_time', 'between', $value);
    }

}
