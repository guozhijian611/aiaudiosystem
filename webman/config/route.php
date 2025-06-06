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

use app\controller\UserController;
use app\controller\AdminController;
use app\controller\TaskController;
use app\controller\TaskInfoController;
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
});

Route::group('/task', function () {
    Route::post('/createTask', [TaskController::class, 'createTask']);
    Route::post('/taskList', [TaskController::class, 'taskList']);
    Route::post('/deleteTask', [TaskController::class, 'deleteTask']);
    Route::post('/updateTask', [TaskController::class, 'updateTask']);
    Route::post('/upload', [TaskController::class, 'upload']);
    Route::post('/getTaskInfo', [TaskInfoController::class, 'getTaskInfo']);
});

//拦截 404
Route::fallback(function(){
    return jsons(404, 'Route Not Found');
});