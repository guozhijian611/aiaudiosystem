<?php

use OpenB8\WebmanTrace\Middleware\TraceMiddleware;

return [
    // 全局中间件，优先级最高
    'app\\middleware' => [
        TraceMiddleware::class,
    ],
    '' => [
        TraceMiddleware::class,
    ]
]; 