<?php

namespace app\controller;

use support\Request;

class TaskInfoController
{
    public function index(Request $request)
    {
        return response(__CLASS__);
    }

}
