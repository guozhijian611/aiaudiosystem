<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\validate;

use think\Validate;

/**
 * 任务详情验证器
 */
class TaskInfoValidate extends Validate
{
    /**
     * 定义验证规则
     */
    protected $rule =   [
        'tid' => 'require',
        'type' => 'require',
        'is_extract' => 'require',
        'is_clear' => 'require',
        'fast_status' => 'require',
        'transcribe_status' => 'require',
        'retry_count' => 'require',
    ];

    /**
     * 定义错误信息
     */
    protected $message  =   [
        'tid' => '任务ID必须填写',
        'type' => '文件类型必须填写',
        'is_extract' => '是否提取音频必须填写',
        'is_clear' => '是否降噪必须填写',
        'fast_status' => '是否快速识别必须填写',
        'transcribe_status' => '是否转写必须填写',
        'retry_count' => '失败重试次数必须填写',
    ];

    /**
     * 定义场景
     */
    protected $scene = [
        'save' => [
            'tid',
            'type',
            'is_extract',
            'is_clear',
            'fast_status',
            'transcribe_status',
            'retry_count',
        ],
        'update' => [
            'tid',
            'type',
            'is_extract',
            'is_clear',
            'fast_status',
            'transcribe_status',
            'retry_count',
        ],
    ];

}
