<?php

use OpenB8\WebmanTrace\TraceService;
use OpenB8\WebmanTrace\Middleware\TraceMiddleware;
use OpenB8\WebmanTrace\TraceManager;
use OpenB8\WebmanTrace\Logger\TraceLogger;

/**
 * 插件启动时自动执行
 */
return function () {
    // 获取插件配置
    $config = config('plugin.openb8.webman-trace.app', []);
    
    // 如果插件未启用，直接返回
    if (!($config['enable'] ?? true)) {
        return;
    }

    // 初始化追踪服务
    $traceService = new TraceService($config);
    $traceService->init();

    // 注册 404 追踪处理（通过修改中间件优先级）
    $handle404Config = $config['handle_404'] ?? [];
    if ($handle404Config['enable'] ?? true) {
        // 通过修改中间件配置来实现404追踪
        // 这里我们依赖中间件来捕获所有请求，包括404
    }

    // 输出启用信息（仅在 CLI 模式）
    if (php_sapi_name() === 'cli') {
        echo "\033[32m✅ Webman Trace 插件已启用！\033[0m\n";
        echo "📊 Web 界面: http://127.0.0.1:8787" . ($config['web_interface']['path_prefix'] ?? '/trace') . "\n";
        echo "📝 配置文件: config/plugin/openb8/webman-trace/app.php\n";
        if ($config['handle_404']['enable'] ?? true) {
            echo "🔍 404 路由追踪已启用" . ($config['handle_404']['custom_response'] ?? false ? "（自定义响应）" : "（仅记录日志）") . "\n";
        }
    }
}; 