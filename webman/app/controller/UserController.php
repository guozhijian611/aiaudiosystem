<?php

namespace app\controller;

use support\Request;
use app\api\model\User;
use Tinywan\Jwt\JwtToken;

class UserController
{
    public function login(Request $request)
    {
        $username = $request->post('username');
        $password = $request->post('password');
        if (empty($username) || empty($password)) {
            return jsons(400, '参数错误');
        }
        $user = User::where('username', $username)->find();
        if (!$user) {
            return jsons(400, '用户名不存在');
        }
        if (!password_verify($password, $user->password)) {
            return jsons(400, '密码错误');
        }
        if ($user->status == 2) {
            return jsons(400, '用户已禁用');
        }
        $userinfo = [
            'id' => $user->id,
            'username' => $user->username,
            'nickname' => $user->nickname,
            'role' => $user->role,
            // 'status' => $user->status,
            // 'create_time' => $user->create_time,
            'update_time' => $user->update_time,
        ];
        //更新登录时间
        $user->update_time = date('Y-m-d H:i:s',time());
        $user->save();
        $token = JwtToken::generateToken($userinfo);
        return jsons(200, '登录成功', ['userinfo' => $userinfo, 'data' => $token]);
    }

    public function register(Request $request)
    {
        $username = $request->post('username');
        $password = $request->post('password');
        if (empty($username) || empty($password)) {
            return jsons(400, '参数错误');
        }
        $user = User::where('username', $username)->find();
        if ($user) {
            return jsons(400, '用户名已存在');
        }
        try {
            $user = new User();
            $user->username = $username;
            $user->password = password_hash($password, PASSWORD_DEFAULT);
            $user->save();
        }catch (\Exception $e) {
            return jsons(500, '创建失败', ['data' => $e->getMessage()]);
        }
        return jsons(200, '创建成功');
    }
    
    public function logout(Request $request)
    {
        return jsons(200, '退出成功');
    }

    //更新密码
    public function updatePassword(Request $request)
    {
        $uid = $request->user['id'];
        $oldPassword = $request->post('oldPassword');
        $newPassword = $request->post('newPassword');
        if (empty($oldPassword) || empty($newPassword)) {
            return jsons(400, '参数不能为空');
        }
        if ($oldPassword == $newPassword) {
            return jsons(400, '新旧密码不能相同');
        }
        $user = User::where('id', $uid)->find();
        if (!$user) {
            return jsons(400, '用户名不存在');
        }
        if (!password_verify($oldPassword, $user->password)) {
            return jsons(400, '密码错误');
        }
        $user->password = password_hash($newPassword, PASSWORD_DEFAULT);
        $user->save();
        return jsons(200, '更新成功');
    }

    //更新用户信息
    public function updateUserInfo(Request $request)
    {
        $uid = $request->user['id'];
        $nickname = $request->post('nickname');
        if (empty($nickname)) {
            return jsons(400, '昵称不能为空');
        }
        $user = User::where('id', $uid)->find();
        if (!$user) {
            return jsons(400, '用户名不存在');
        }
        $user->nickname = $nickname;
        $user->save();
        return jsons(200, '更新成功');
    }

    //获取用户信息
    public function getUserInfo(Request $request)
    {
        $uid = $request->user['id'];
        $user = User::where('id', $uid)->find();
        if (!$user) {
            return jsons(400, '用户名不存在');
        }
        $userinfo = [
            'id' => $user->id,
            'username' => $user->username,
            'nickname' => $user->nickname,
            'role' => $user->role,
            // 'status' => $user->status,
            // 'create_time' => $user->create_time,
            'update_time' => $user->update_time,
        ];
        return jsons(200, '获取成功', ['data' => $userinfo]);
    }

}
