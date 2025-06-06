<?php

namespace app\middleware;

use Webman\MiddlewareInterface;
use Webman\Http\Response;
use Webman\Http\Request;
use Tinywan\Jwt\JwtToken;

class Auth implements MiddlewareInterface
{
    public function process(Request $request, callable $handler): Response
    {
        //白名单内的路由不需要验证
        $whiteList = [
            '/',
            '/test',
            '/user/login',
            '/user/register',
            '/user/logout',
        ];
        // 如果是白名单内的路由，直接放行
        if (in_array($request->path(), $whiteList)) {
            return $handler($request);
        }
        try {
            $jwt = JwtToken::verify();
            // 设置用户信息到request
            $request->user = $jwt['extend'];
            return $handler($request);
        } catch (\Exception $e) {
            return json(['code' => 401, 'msg' => $e->getMessage()]);
        }
    }
}
