<?php

namespace app\controller;

use support\Request;
use app\api\model\User;
use Tinywan\Jwt\JwtToken;

class UserController
{
    /**
     * 用户登录
     */
    public function login(Request $request)
    {
        $username = $request->post('username');
        $password = $request->post('password');
        
        // 参数验证
        if (empty($username) || empty($password)) {
            return jsons(400, '用户名和密码不能为空');
        }
        
        try {
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
                'status' => $user->status,
                'create_time' => $user->create_time,
                'update_time' => $user->update_time,
            ];
            
            // 更新登录时间 - 让数据库自动更新 update_time
            $user->save();
            
            $token = JwtToken::generateToken($userinfo);
            return jsons(200, '登录成功', ['userinfo' => $userinfo, 'token' => $token]);
        } catch (\Exception $e) {
            return jsons(500, '登录失败：' . $e->getMessage());
        }
    }

    /**
     * 用户注册
     */
    public function register(Request $request)
    {
        $username = $request->post('username');
        $password = $request->post('password');
        $nickname = $request->post('nickname', ''); // 如果为空，使用数据库默认值
        
        // 参数验证
        if (empty($username) || empty($password)) {
            return jsons(400, '用户名和密码不能为空');
        }
        
        // 用户名长度验证（数据库限制50字符）
        if (strlen($username) < 3 || strlen($username) > 50) {
            return jsons(400, '用户名长度必须在3-50个字符之间');
        }
        
        // 昵称长度验证（数据库限制20字符）
        if (!empty($nickname) && strlen($nickname) > 20) {
            return jsons(400, '昵称长度不能超过20个字符');
        }
        
        // 密码强度验证
        if (strlen($password) < 6) {
            return jsons(400, '密码长度不能少于6位');
        }
        
        try {
            // 检查用户名是否已存在
            $existUser = User::where('username', $username)->find();
            if ($existUser) {
                return jsons(400, '用户名已存在');
            }
            
            $user = new User();
            $user->username = $username;
            if (!empty($nickname)) {
                $user->nickname = $nickname;
            }
            $user->password = password_hash($password, PASSWORD_DEFAULT);
            // role 和 status 使用数据库默认值
            $user->save();
            
            return jsons(200, '注册成功');
        } catch (\Exception $e) {
            return jsons(500, '注册失败：' . $e->getMessage());
        }
    }
    
    /**
     * 用户退出
     */
    public function logout(Request $request)
    {
        // 这里可以添加token失效逻辑
        return jsons(200, '退出成功');
    }

    /**
     * 更新密码
     */
    public function updatePassword(Request $request)
    {
        $uid = $request->user['id'];
        $oldPassword = $request->post('oldPassword');
        $newPassword = $request->post('newPassword');
        
        // 参数验证
        if (empty($oldPassword) || empty($newPassword)) {
            return jsons(400, '旧密码和新密码不能为空');
        }
        
        if ($oldPassword == $newPassword) {
            return jsons(400, '新旧密码不能相同');
        }
        
        // 新密码强度验证
        if (strlen($newPassword) < 6) {
            return jsons(400, '新密码长度不能少于6位');
        }
        
        try {
            $user = User::where('id', $uid)->find();
            if (!$user) {
                return jsons(400, '用户不存在');
            }
            
            if (!password_verify($oldPassword, $user->password)) {
                return jsons(400, '原密码错误');
            }
            
            $user->password = password_hash($newPassword, PASSWORD_DEFAULT);
            // update_time 会自动更新
            $user->save();
            
            return jsons(200, '密码更新成功');
        } catch (\Exception $e) {
            return jsons(500, '密码更新失败：' . $e->getMessage());
        }
    }

    /**
     * 更新用户信息
     */
    public function updateUserInfo(Request $request)
    {
        $uid = $request->user['id'];
        $nickname = $request->post('nickname');
        
        // 参数验证
        if (empty($nickname)) {
            return jsons(400, '昵称不能为空');
        }
        
        // 昵称长度验证（数据库限制20字符）
        if (strlen($nickname) > 20) {
            return jsons(400, '昵称长度不能超过20个字符');
        }
        
        try {
            $user = User::where('id', $uid)->find();
            if (!$user) {
                return jsons(400, '用户不存在');
            }
            
            $user->nickname = $nickname;
            // update_time 会自动更新
            $user->save();
            
            return jsons(200, '用户信息更新成功');
        } catch (\Exception $e) {
            return jsons(500, '用户信息更新失败：' . $e->getMessage());
        }
    }

    /**
     * 获取用户信息
     */
    public function getUserInfo(Request $request)
    {
        $uid = $request->user['id'];
        
        try {
            $user = User::where('id', $uid)->find();
            if (!$user) {
                return jsons(400, '用户不存在');
            }
            
            $userinfo = [
                'id' => $user->id,
                'username' => $user->username,
                'nickname' => $user->nickname,
                'role' => $user->role,
                'status' => $user->status,
                'create_time' => $user->create_time,
                'update_time' => $user->update_time,
            ];
            
            return jsons(200, '获取成功', $userinfo);
        } catch (\Exception $e) {
            return jsons(500, '获取用户信息失败：' . $e->getMessage());
        }
    }
}
