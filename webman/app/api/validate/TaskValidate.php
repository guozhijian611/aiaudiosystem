<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\validate;

use think\Validate;

/**
 * 任务管理验证器
 */
class TaskValidate extends Validate
{
    /**
     * 定义验证规则
     */
    protected $rule =   [
        'uid' => 'require',
        'number' => 'require',
        'name' => 'require',
        'status' => 'require',
    ];

    /**
     * 定义错误信息
     */
    protected $message  =   [
        'uid' => '用户 id必须填写',
        'number' => '任务编号必须填写',
        'name' => '任务昵称必须填写',
        'status' => '状态必须填写',
    ];

    /**
     * 定义场景
     */
    protected $scene = [
        'save' => [
            'uid',
            'number',
            'name',
            'status',
        ],
        'update' => [
            'uid',
            'number',
            'name',
            'status',
        ],
    ];

}
