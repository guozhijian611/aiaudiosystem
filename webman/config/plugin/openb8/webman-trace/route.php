<?php

use Webman\Route;
use OpenB8\WebmanTrace\Controller\TraceWebController;

// 获取配置
$config = config('plugin.openb8.webman-trace.app', []);
$webConfig = $config['web_interface'] ?? [];
$enable = $webConfig['enable'] ?? false;
$pathPrefix = rtrim($webConfig['path_prefix'] ?? '/trace', '/');

// 如果启用了 web 界面，则注册路由
if ($enable) {
    // 主页面
    Route::get($pathPrefix, [TraceWebController::class, 'index']);
    
    // API 接口
    Route::get($pathPrefix . '/list', [TraceWebController::class, 'list']);
    Route::get($pathPrefix . '/detail', [TraceWebController::class, 'detail']);
    Route::post($pathPrefix . '/clear', [TraceWebController::class, 'clear']);
} 