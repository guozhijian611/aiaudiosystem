<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: your name
// +----------------------------------------------------------------------
namespace app\api\model;

use plugin\saiadmin\basic\BaseModel;

/**
 * 用户管理模型
 */
class User extends BaseModel
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
    protected $table = 'ai_user';

    /**
     * 用户名 搜索
     */
    public function searchUsernameAttr($query, $value)
    {
        $query->where('username', 'like', '%'.$value.'%');
    }

    /**
     * 昵称 搜索
     */
    public function searchNicknameAttr($query, $value)
    {
        $query->where('nickname', 'like', '%'.$value.'%');
    }

}
