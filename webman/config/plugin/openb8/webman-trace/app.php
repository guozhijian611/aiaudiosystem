<?php

return [
    // 启用插件
    'enable' => true,
    
    // 记录 SQL 查询日志
    'log_sql' => true,
    
    // 记录异常日志
    'log_exception' => true,
    
    // 记录请求日志
    'log_request' => true,
    
    // 仅在调试模式下记录详细日志
    'debug_only' => false,
    
    // 控制台显示选项
    'console_output' => [
        // 是否在控制台显示trace信息
        'enable' => true,
        // 控制台显示的日志级别
        'levels' => ['request', 'response', 'exception', 'slow_query', 'custom'],
        // 是否显示详细信息
        'verbose' => true,
        // 美化输出样式
        'beautiful' => true,
    ],
    
    // Web查询界面配置
    'web_interface' => [
        // 是否启用web查询接口
        'enable' => true,
        // 访问路径前缀
        'path_prefix' => '/trace',
        // 是否需要认证（开发环境建议false，生产环境建议true）
        'auth_required' => true,
        // 简单的访问密码（auth_required为true时生效）
        'access_password' => 'trace123',
        // 每页显示条数
        'per_page' => 20,
    ],
    
    // Trace ID 在响应头中的键名
    'trace_id_key' => 'X-Trace-Id',
    
    // 日志通道名称
    'log_channel' => 'trace',
    
    // 日志文件路径
    'log_file' => 'runtime/logs/trace.log',
    
    // Trace ID 生成器类
    'trace_id_generator' => \OpenB8\WebmanTrace\Generator\UuidGenerator::class,
    
    // 需要忽略的请求路径（支持正则表达式）
    'ignore_paths' => [
        '/favicon.ico',
        '/robots.txt',
        '/health',
    ],
    
    // 404 处理配置
    'handle_404' => [
        // 是否启用404追踪
        'enable' => true,
        // 是否自定义404响应页面（false=只记录日志，true=返回自定义页面）
        'custom_response' => false,
        // 自定义404页面内容
        'response_body' => '<!DOCTYPE html><html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1><p>The page you requested was not found.</p></body></html>',
    ],
    
    // SQL 查询慢查询阈值（毫秒）
    'slow_query_threshold' => 1000,
    
    // 是否记录请求体和响应体
    'log_body' => [
        'request' => true,
        'response' => true,
        // 最大记录长度
        'max_length' => 1024,
    ],
    
    // 日志级别映射
    'log_levels' => [
        'request' => 'info',
        'response' => 'info',
        'sql' => 'debug',
        'exception' => 'error',
        'slow_query' => 'warning',
        'custom' => 'info',
    ],
]; 