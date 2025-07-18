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
use app\api\model\User;
use plugin\saiadmin\service\OpenSpoutWriter;

/**
 * 用户管理逻辑层
 */
class UserLogic extends BaseLogic
{
    /**
     * 构造函数
     */
    public function __construct()
    {
        $this->model = new User();
    }

    /**
     * 导出数据
     */
    public function export($where = [])
    {
        $option = [
            ['field' => 'username', 'title' => '用户名', 'width' => 15],
            ['field' => 'password', 'title' => '密码', 'width' => 15],
            ['field' => 'nickname', 'title' => '昵称', 'width' => 15],
            ['field' => 'role', 'title' => '角色', 'width' => 15],
            ['field' => 'status', 'title' => '状态', 'width' => 15],
        ];
        $filter = [
            'role' => dictDataList('user_type'),
        ]; // 过滤器
        $query = $this->search($where)->field(array_column($option, 'field'));
        $data = $this->getAll($query);
        $file_name = '用户管理.xlsx';
        $writer = new OpenSpoutWriter($file_name);
        $writer->setWidth(array_column($option, 'width'));
        $writer->setHeader(array_column($option, 'title'));
        $writer->setData($data, null, $filter);
        $file_path = $writer->returnFile();
        return response()->download($file_path, urlencode($file_name));
    }

}
