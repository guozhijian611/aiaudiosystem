<?php

namespace app\exception;

use Webman\Http\Request;
use Webman\Http\Response;
use support\exception\BusinessException;

/**
 * API异常类 - 返回JSON格式响应
 */
class ApiException extends BusinessException
{
    public function render(Request $request): ?Response
    {
        return json([
            'code' => $this->getCode() ?: 400,
            'message' => $this->getMessage(),
            'data' => []
        ]);
    }
} 