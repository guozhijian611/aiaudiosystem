<?php
/**
 * This file is part of webman.
 *
 * Licensed under The MIT License
 * For full copyright and license information, please see the MIT-LICENSE.txt
 * Redistributions of files must retain the above copyright notice.
 *
 * @author    walkor<walkor@workerman.net>
 * @copyright walkor<walkor@workerman.net>
 * @link      http://www.workerman.net/
 * @license   http://www.opensource.org/licenses/mit-license.php MIT License
 */

use Webman\Route;
use app\controller\QueueController;
use app\controller\UserController;
use app\controller\AdminController;
use app\controller\TaskController;
use app\controller\TaskInfoController;
use app\controller\IndexController;

Route::options('/{path:.+}', function ($request, $path) {
    return response('');
});

Route::group('/index', function () {
    Route::post('/taskStatusCount', [IndexController::class, 'taskStatusCount']);
});

Route::group('/user', function () {
    Route::post('/login', [UserController::class, 'login']);
    Route::post('/register', [UserController::class, 'register']);
    Route::post('/logout', [UserController::class, 'logout']);
    Route::post('/updatePassword', [UserController::class, 'updatePassword']);
    Route::post('/updateUserInfo', [UserController::class, 'updateUserInfo']);
    Route::post('/getUserInfo', [UserController::class, 'getUserInfo']);
});

Route::group('/admin', function () {
    Route::post('/updateUserStatus', [AdminController::class, 'updateUserStatus']);
    Route::post('/getTaskList', [AdminController::class, 'getTaskList']);
});

Route::group('/task', function () {
    Route::post('/createTask', [TaskController::class, 'createTask']);
    Route::post('/taskList', [TaskController::class, 'taskList']);
    Route::post('/deleteTask', [TaskController::class, 'deleteTask']);
    Route::post('/updateTask', [TaskController::class, 'updateTask']);
    Route::post('/upload', [TaskController::class, 'upload']);
    Route::post('/getTaskInfo', [TaskInfoController::class, 'getTaskInfo']);
});

Route::group('/queue', function () {
    // 队列任务管理接口
    Route::post('/push', [QueueController::class, 'pushTaskToQueue']);
    
    // 单独推送任务接口
    Route::post('/push-single', [QueueController::class, 'pushSingleTask']);
    
    // 批量推送任务接口
    Route::post('/push-batch', [QueueController::class, 'pushBatchTasks']);
    
    // 队列任务回调接口（供节点调用）
    Route::post('/callback', [QueueController::class, 'handleTaskCallback']);
    
    // 文件上传接口（供节点调用）
    Route::post('/upload', [QueueController::class, 'upload']);
    
    // 用户主动继续转写接口
    Route::post('/continue-transcribe', [QueueController::class, 'continueToTranscribe']);
    
    // 测试接口
    Route::post('/test', [QueueController::class, 'test']);
});

//拦截 404
Route::fallback(function(){
    return jsons(404, 'Route Not Found');
});