#!/usr/bin/env php
<?php

chdir(__DIR__);
require_once __DIR__ . '/vendor/autoload.php';
ini_set('memory_limit', '4096M');
support\App::run();
