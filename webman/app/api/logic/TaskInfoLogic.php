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
use app\api\model\TaskInfo;
use plugin\saiadmin\service\OpenSpoutWriter;

/**
 * 任务详情逻辑层
 */
class TaskInfoLogic extends BaseLogic
{
    /**
     * 构造函数
     */
    public function __construct()
    {
        $this->model = new TaskInfo();
    }

    /**
     * 导出数据
     */
    public function export($where = [])
    {
        $option = [
            ['field' => 'tid', 'title' => '任务ID', 'width' => 15],
            ['field' => 'filename', 'title' => '原始文件名', 'width' => 15],
            ['field' => 'size', 'title' => '文件大小', 'width' => 15],
            ['field' => 'type', 'title' => '文件类型', 'width' => 15],
            ['field' => 'url', 'title' => '原始文件 URL', 'width' => 15],
            ['field' => 'voice_url', 'title' => '提取音频后的 URL', 'width' => 15],
            ['field' => 'clear_url', 'title' => '降噪后的 URL', 'width' => 15],
            ['field' => 'is_extract', 'title' => '是否提取音频', 'width' => 15],
            ['field' => 'is_clear', 'title' => '是否降噪', 'width' => 15],
            ['field' => 'fast_status', 'title' => '是否快速识别', 'width' => 15],
            ['field' => 'transcribe_status', 'title' => '是否转写', 'width' => 15],
            ['field' => 'effective_voice', 'title' => '有效语音时长', 'width' => 15],
            ['field' => 'total_voice', 'title' => '音频总时长', 'width' => 15],
            ['field' => 'language', 'title' => '语言类型', 'width' => 15],
            ['field' => 'text_info', 'title' => '转写内容', 'width' => 15],
            ['field' => 'error_msg', 'title' => '任务错误信息', 'width' => 15],
            ['field' => 'retry_count', 'title' => '失败重试次数', 'width' => 15],
            ['field' => 'step', 'title' => '当前处理阶段', 'width' => 15],
        ];
        $filter = [
            'type' => dictDataList('file_type'),
            'is_extract' => dictDataList('yes_or_no'),
            'is_clear' => dictDataList('yes_or_no'),
            'fast_status' => dictDataList('yes_or_no'),
            'transcribe_status' => dictDataList('yes_or_no'),
            'step' => dictDataList('step_type'),
        ]; // 过滤器
        $query = $this->search($where)->field(array_column($option, 'field'));
        $data = $this->getAll($query);
        $file_name = '任务详情.xlsx';
        $writer = new OpenSpoutWriter($file_name);
        $writer->setWidth(array_column($option, 'width'));
        $writer->setHeader(array_column($option, 'title'));
        $writer->setData($data, null, $filter);
        $file_path = $writer->returnFile();
        return response()->download($file_path, urlencode($file_name));
    }

}
