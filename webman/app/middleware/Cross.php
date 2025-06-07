<?php

namespace app\middleware;

use Webman\MiddlewareInterface;
use Webman\Http\Response;
use Webman\Http\Request;

class Cross implements MiddlewareInterface
{
    public function process(Request $request, callable $handler): Response
    {
        // 禁止访问隐藏文件
        if (strpos($request->path(), '/.') !== false) {
            return response('<h1>403 Forbidden</h1>', 403);
        }

        // 处理预检请求
        if ($request->method() === 'OPTIONS') {
            $origin = $request->header('origin');
            $headers = [
                'Access-Control-Allow-Methods' => 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers' => $request->header('access-control-request-headers', 
                    'Authorization, Content-Type, X-Requested-With'),
            ];
            
            // 动态设置跨域凭证
            if ($origin) {
                $headers['Access-Control-Allow-Origin'] = $origin;
                $headers['Access-Control-Allow-Credentials'] = 'true';
            } else {
                $headers['Access-Control-Allow-Origin'] = '*';
                $headers['Access-Control-Allow-Credentials'] = 'false';
            }

            return response('')->withHeaders($headers);
        }

        // 处理正常请求
        $response = $handler($request);
        
        // 统一添加跨域头
        $origin = $request->header('origin');
        if ($origin) {
            $response->withHeader('Access-Control-Allow-Origin', $origin)
                     ->withHeader('Access-Control-Allow-Credentials', 'true');
        } else {
            $response->withHeader('Access-Control-Allow-Origin', '*')
                     ->withHeader('Access-Control-Allow-Credentials', 'false');
        }

        return $response;
    }
}