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
    Route::post('/getFileProgress', [TaskController::class, 'getFileProgress']);//获取文件快速检测进度
    Route::post('/getFileTranscriptionProgress', [TaskController::class, 'getFileTranscriptionProgress']);//获取文件转写进度
    Route::post('/getTaskStatistics', [TaskController::class, 'getTaskStatistics']);//获取任务统计
    Route::post('/getTaskFileDetail', [TaskController::class, 'getTaskFileDetail']);//获取任务子文件详细信息
});

Route::group('/queue', function () {
    // 统一入口方法
    Route::post('/queueAction', [QueueController::class, 'queueAction']);
    // 队列任务回调接口（供节点调用）
    Route::post('/callback', [QueueController::class, 'handleTaskCallback']);
    // 队列专用文件上传方法
    Route::post('/upload', [QueueController::class, 'upload']);
});

//拦截 404
Route::fallback(function(){
    return jsons(404, 'Route Not Found');
});