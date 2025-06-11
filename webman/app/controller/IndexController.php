<?php

namespace app\controller;

use support\Request;
use app\api\model\Task;

class IndexController
{
    public function index(Request $request)
    {
        return jsons(200, 'success', [
          'version' => '1.0.0',
          'name' => ' OpenB8AI语音处理系统',
          'author' => '城南',
          'email' => 'allen@gzj2001.com',
          'url' => 'https://www.gzj2001.com',
          'time' => date('Y-m-d H:i:s'),
          'copyright' => 'Copyright © 2025 OpenB8AI. All rights reserved.',
        ]);
    }

    /**
     * 任务状态统计
     * 需要返回共计 1.空任务 2.已检测 3.已转写 4.处理中 5.暂停中
     */
    public function taskStatusCount(Request $request)
    {
        $uid = $request->user['id'];
        $task_empty= Task::where('uid', $uid)->where('status', 1)->count();
        $task_detected = Task::where('uid', $uid)->where('status', 2)->count();
        $task_transcribed = Task::where('uid', $uid)->where('status', 3)->count();
        $task_processing = Task::where('uid', $uid)->where('status', 4)->count();
        $task_paused = Task::where('uid', $uid)->where('status', 5)->count();
        return jsons(200, 'success', [
            'total' => $task_empty + $task_detected + $task_transcribed + $task_processing + $task_paused,
            'empty' => $task_empty,
            'detected' => $task_detected,
            'transcribed' => $task_transcribed,
            'processing' => $task_processing,
            'paused' => $task_paused
        ]);
    }
}
