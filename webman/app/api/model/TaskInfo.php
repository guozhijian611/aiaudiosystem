<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\model;

use plugin\saiadmin\basic\BaseModel;

/**
 * 任务详情模型
 */
class TaskInfo extends BaseModel
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
    protected $table = 'ai_task_info';

    /**
     * 原始文件名 搜索
     */
    public function searchFilenameAttr($query, $value)
    {
        $query->where('filename', 'like', '%'.$value.'%');
    }

}
