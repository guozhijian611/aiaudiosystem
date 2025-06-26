#!/usr/bin/env php
<?php

chdir(__DIR__);
ini_set('memory_limit', '8192M');
echo "Memory limit: " . ini_get('memory_limit') . PHP_EOL;
require_once __DIR__ . '/vendor/autoload.php';
support\App::run();
