<?php

namespace app\model;

use support\think\Model;

/**
 * ai_task_info 
 * @property integer $id ID(主键)
 * @property integer $tid 任务ID
 * @property string $filename 原始文件名
 * @property string $size 文件大小
 * @property integer $type 文件类型 1-语音 2-视频
 * @property string $url 原始文件 URL
 * @property string $voice_url 提取音频后的 URL
 * @property string $clear_url 降噪后的 URL
 * @property integer $is_extract 是否提取音频
 * @property integer $is_clear 是否降噪
 * @property integer $fast_status 是否快速识别
 * @property integer $transcribe_status 是否转写
 * @property string $effective_voice 有效语音时长
 * @property string $total_voice 音频总时长
 * @property string $language 语言类型
 * @property mixed $text_info 转写内容
 * @property string $error_msg 任务错误信息
 * @property integer $retry_count 失败重试次数
 * @property integer $step 当前处理阶段
 * @property string $create_time 创建时间
 * @property string $update_time 更新时间
 * @property string $delete_time 删除时间
 */
class TaskInfo extends Model
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
    protected $table = 'ai_task_info';

    /**
     * The primary key associated with the table.
     *
     * @var string
     */
    protected $pk = 'id';

    
}
