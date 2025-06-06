<?php

namespace app\controller;

use support\Request;

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
}
