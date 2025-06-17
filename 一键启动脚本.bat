@echo off
chcp 65001
echo ========================================
echo           一键启动脚本
echo ========================================

REM 检查 php 是否安装
echo 检查 PHP 环境...
php -v
if %errorlevel% neq 0 (
    echo 错误: PHP 未安装或未配置环境变量
    pause
    exit /b 1
)

echo.
echo ========================================
echo 检查基础服务连接状态
echo ========================================

REM 检查 MySQL 连接
echo [1/3] 检查 MySQL 连接...
php -r "
try {
    $pdo = new PDO('mysql:host=localhost;port=3306;dbname=aiaudiosystem', 'root', '123456');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo '✓ MySQL 连接成功\n';
} catch (PDOException $e) {
    echo '✗ MySQL 连接失败: ' . $e->getMessage() . '\n';
    exit(1);
}
"
if %errorlevel% neq 0 (
    echo 错误: MySQL 连接失败，请检查 MySQL 服务是否启动
    echo 请确保 MySQL 服务正在运行，并且配置正确
    pause
    exit /b 1
)

REM 检查 Redis 连接
echo [2/3] 检查 Redis 连接...
php -r "
try {
    $redis = new Redis();
    $redis->connect('127.0.0.1', 6379);
    $redis->ping();
    echo '✓ Redis 连接成功\n';
} catch (Exception $e) {
    echo '✗ Redis 连接失败: ' . $e->getMessage() . '\n';
    exit(1);
}
"
if %errorlevel% neq 0 (
    echo 错误: Redis 连接失败，请检查 Redis 服务是否启动
    echo 请确保 Redis 服务正在运行，并且配置正确
    pause
    exit /b 1
)

REM 检查 RabbitMQ 连接
echo [3/4] 检查 RabbitMQ 连接...
php -r "
try {
    $connection = new AMQPConnection([
        'host' => 'localhost',
        'port' => 5672,
        'login' => 'admin',
        'password' => 'admin'
    ]);
    $connection->connect();
    echo '✓ RabbitMQ 连接成功\n';
} catch (Exception $e) {
    echo '✗ RabbitMQ 连接失败: ' . $e->getMessage() . '\n';
    exit(1);
}
"
if %errorlevel% neq 0 (
    echo 错误: RabbitMQ 连接失败，请检查 RabbitMQ 服务是否启动
    echo 请确保 RabbitMQ 服务正在运行，并且配置正确
    pause
    exit /b 1
)

REM 检查 FFmpeg 是否安装
echo [4/4] 检查 FFmpeg 安装...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: FFmpeg 未安装或未配置环境变量
    echo 请安装 FFmpeg 并确保其在系统 PATH 中
    echo.
    echo 安装方法:
    echo 1. 下载 FFmpeg: https://ffmpeg.org/download.html
    echo 2. 解压到 C:\ffmpeg 目录
    echo 3. 将 C:\ffmpeg\bin 添加到系统环境变量 PATH 中
    echo 4. 重启命令行窗口
    pause
    exit /b 1
) else (
    echo ✓ FFmpeg 安装正常
)

echo.
echo ✓ 所有基础服务和工具检查完成！
echo.

echo 启动顺序:
echo 1. Webman 后端服务
echo 2. 中台管理系统
echo 3. 前台应用
echo 4. Cut Node (音频提取)
echo 5. Clear Node (音频降噪)
echo 6. Quick Node (语音识别)
echo 7. Translate Node (语音转写)
echo.

REM 1. 启动 webman (后台运行)
echo [1/7] 启动 Webman 后端服务...
start "Webman Backend" cmd /k "cd /d %~dp0aiaudiosystem\webman && php windows.php"
timeout /t 3 /nobreak >nul

REM 2. 启动中台 (后台运行)
echo [2/7] 启动中台管理系统...
start "Admin Frontend" cmd /k "cd /d %~dp0aiaudiosystem\saiadmin-vue && npm run dev"
timeout /t 3 /nobreak >nul

REM 3. 启动前台 (后台运行)
echo [3/7] 启动前台应用...
start "Main Frontend" cmd /k "cd /d %~dp0aiaudiosystem\newAIvoice && npm run dev"
timeout /t 3 /nobreak >nul

REM 4. 启动 cut_node (后台运行)
echo [4/7] 启动 Cut Node (音频提取)...
start "Cut Node" cmd /k "cd /d %~dp0aiaudiosystem\cut_node && conda activate CutNode && python src/main.py"
timeout /t 3 /nobreak >nul

REM 5. 启动 clear_node (后台运行)
echo [5/7] 启动 Clear Node (音频降噪)...
start "Clear Node" cmd /k "cd /d %~dp0aiaudiosystem\clear_node && conda activate ClearerVoice-Studio && python run.py"
timeout /t 3 /nobreak >nul

REM 6. 启动 quick_node (后台运行)
echo [6/7] 启动 Quick Node (语音识别)...
start "Quick Node" cmd /k "cd /d %~dp0aiaudiosystem\quick_node && conda activate funasr && python run.py"
timeout /t 3 /nobreak >nul

REM 7. 启动 translate_node (后台运行)
echo [7/7] 启动 Translate Node (语音转写)...
start "Translate Node" cmd /k "cd /d %~dp0aiaudiosystem\translate_node && conda activate whisperx && python main.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 所有服务启动完成！
echo ========================================
echo.
echo 服务访问地址:
echo - 前台: http://localhost:3000
echo - 中台: http://localhost:3001
echo - 后端: http://localhost:8787
echo - RabbitMQ 管理: http://localhost:15672 (admin/admin)
echo.
echo 提示: 每个服务都在独立的窗口中运行
echo 关闭服务时请分别关闭对应的窗口
echo.
pause