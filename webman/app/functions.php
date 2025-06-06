<?php
/**
 * Here is your custom functions.
 */

function jsons($code, $msg, $data = [])
{
    return json(
        [
            'code' => $code,
            'msg' => $msg,
            'data' => $data
        ]
    );
}