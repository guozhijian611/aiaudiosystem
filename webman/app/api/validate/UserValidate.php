<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\validate;

use think\Validate;

/**
 * 用户管理验证器
 */
class UserValidate extends Validate
{
    /**
     * 定义验证规则
     */
    protected $rule =   [
        'username' => 'require',
        'password' => 'require',
        'nickname' => 'require',
        'role' => 'require',
    ];

    /**
     * 定义错误信息
     */
    protected $message  =   [
        'username' => '用户名必须填写',
        'password' => '密码必须填写',
        'nickname' => '昵称必须填写',
        'role' => '角色必须填写',
    ];

    /**
     * 定义场景
     */
    protected $scene = [
        'save' => [
            'username',
            'password',
            'nickname',
            'role',
        ],
        'update' => [
            'username',
            'password',
            'nickname',
            'role',
        ],
    ];

}
