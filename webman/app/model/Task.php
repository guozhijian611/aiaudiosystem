<?php

namespace app\model;

use support\think\Model;

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
class Task extends Model
{
    /**
     * The connection name for the model.
     *
     * @var string|null
     */
    protected $connection = 'mysql';
    
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'ai_task';

    /**
     * The primary key associated with the table.
     *
     * @var string
     */
    protected $pk = 'id';

    
}
