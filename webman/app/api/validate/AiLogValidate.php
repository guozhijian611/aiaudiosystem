<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\validate;

use think\Validate;

/**
 * 日志记录验证器
 */
class AiLogValidate extends Validate
{
    /**
     * 定义验证规则
     */
    protected $rule =   [
        'task_id' => 'require',
        'task_type' => 'require',
    ];

    /**
     * 定义错误信息
     */
    protected $message  =   [
        'task_id' => '任务详情ID必须填写',
        'task_type' => '任务类型必须填写',
    ];

    /**
     * 定义场景
     */
    protected $scene = [
        'save' => [
            'task_id',
            'task_type',
        ],
        'update' => [
            'task_id',
            'task_type',
        ],
    ];

}
