<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\model;

use plugin\saiadmin\basic\BaseModel;

/**
 * 任务管理模型
 */
/**
 * ai_task 任务表
 * @property integer $id id(主键)
 * @property integer $uid 用户 id
 * @property string $number 任务编号
 * @property string $name 任务昵称
 * @property integer $status 状态 1.空任务 2.已检测 3.已转写 4.处理中 5.暂停中
 * @property string $create_time 创建时间
 * @property string $update_time 更新时间
 * @property string $delete_time 删除时间
 */
class Task extends BaseModel
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
    protected $table = 'ai_task';

    /**
     * 任务昵称 搜索
     */
    public function searchNameAttr($query, $value)
    {
        $query->where('name', 'like', '%'.$value.'%');
    }

}
