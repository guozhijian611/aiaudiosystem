<?php

namespace app\controller;

use support\Request;
use support\Response;
use plugin\saiadmin\basic\BaseController;
use plugin\saiadmin\app\logic\system\SystemAttachmentLogic;

class UploadController extends BaseController
{
    
    /**
     * 上传文件
     * @param Request $request
     * @return Response
     */
    public function upload(Request $request): Response
    {
        try {
            $logic = new SystemAttachmentLogic();
            $type = $request->input('mode', 'system');
            
            // 判断是否强制本地上传
            if ($type == 'local') {
                $result = $logic->uploadBase('file', true);
            } else {
                $result = $logic->uploadBase('file');
            }
            
            return $this->success($result, '文件上传成功');
        } catch (\Exception $e) {
            return $this->fail('文件上传失败：' . $e->getMessage());
        }
    }


}
