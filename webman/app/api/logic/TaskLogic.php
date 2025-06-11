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
use app\api\model\Task;
use plugin\saiadmin\service\OpenSpoutWriter;

/**
 * 任务管理逻辑层
 */
class TaskLogic extends BaseLogic
{
    /**
     * 构造函数
     */
    public function __construct()
    {
        $this->model = new Task();
    }

    /**
     * 导出数据
     */
    public function export($where = [])
    {
        $option = [
            ['field' => 'uid', 'title' => '用户 id', 'width' => 15],
            ['field' => 'number', 'title' => '任务编号', 'width' => 15],
            ['field' => 'name', 'title' => '任务昵称', 'width' => 15],
            ['field' => 'status', 'title' => '状态', 'width' => 15],
        ];
        $filter = [
            'status' => dictDataList('task_type'),
        ]; // 过滤器
        $query = $this->search($where)->field(array_column($option, 'field'));
        $data = $this->getAll($query);
        $file_name = '任务管理.xlsx';
        $writer = new OpenSpoutWriter($file_name);
        $writer->setWidth(array_column($option, 'width'));
        $writer->setHeader(array_column($option, 'title'));
        $writer->setData($data, null, $filter);
        $file_path = $writer->returnFile();
        return response()->download($file_path, urlencode($file_name));
    }

}
