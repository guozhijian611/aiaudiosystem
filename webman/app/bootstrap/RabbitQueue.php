<?php

namespace app\bootstrap;

use Webman\Bootstrap;
use app\service\RabbitMQ;

class RabbitQueue implements Bootstrap
{
    /**
     * 内存中的初始化标志
     */
    private static bool $initialized = false;

    /**
     * 任务类型配置
     * 根据 ai_task_info 表的实际业务逻辑定义队列
     */
    private static array $taskTypes = [
        'voice_extract' => [
            'queue' => 'voice_extract_queue',
            'routing_key' => 'audio.extract',
            'description' => '语音提取任务'
        ],
        'audio_clear' => [
            'queue' => 'audio_clear_queue', 
            'routing_key' => 'audio.clear',
            'description' => '音频降噪任务'
        ],
        'fast_process' => [
            'queue' => 'fast_process_queue',
            'routing_key' => 'audio.fast', 
            'description' => '快速处理任务'
        ],
        'transcribe' => [
            'queue' => 'transcribe_queue',
            'routing_key' => 'audio.transcribe',
            'description' => '语音转录任务'
        ]
    ];

    /**
     * 启动时初始化 RabbitMQ 队列
     * @param $worker
     */
    public static function start($worker)
    {
        // 判断是否为控制台环境
        $is_console = !$worker;
        if ($is_console) {
            // 控制台环境不执行
            return;
        }

        // 只允许第一个worker进程初始化队列
        // 检查worker名称和ID
        $workerName = $worker->name ?? 'unknown';
        $workerId = $worker->id ?? 0;
        
        // 只有名为 'webman' 且 ID 为 0 的worker才执行初始化
        if ($workerName !== 'webman' || $workerId !== 0) {
            // echo "[RabbitQueue] Worker {$workerName}#{$workerId} 跳过队列初始化\n";
            return;
        }

        // 防止重复初始化（内存级别）
        if (self::$initialized) {
            echo "[RabbitQueue] 队列已初始化，跳过重复操作\n";
            return;
        }

        echo "[RabbitQueue] Worker {$workerName}#{$workerId} 开始初始化队列\n";

        try {
            echo "[RabbitQueue] 开始初始化 RabbitMQ 队列...\n";
            
            // 创建 RabbitMQ 服务实例
            $rabbitmq = new RabbitMQ();
            
            // 检查 RabbitMQ 服务状态
            if (!$rabbitmq->isAlive()) {
                echo "[RabbitQueue] 警告: RabbitMQ 服务不可用，跳过队列初始化\n";
                return;
            }
            
            // 获取交换机名称（从环境变量或使用默认值）
            $exchangeName = getenv('MQ_SWITCH') ?: 'task';
            
            // 创建主交换机（direct 模式）
            self::createMainExchange($rabbitmq, $exchangeName);
            
            // 创建任务队列
            self::createTaskQueues($rabbitmq, $exchangeName);
            
            // 创建死信队列
            self::createDeadLetterQueue($rabbitmq, $exchangeName);
            
            // 标记为已初始化
            self::$initialized = true;
            
            echo "[RabbitQueue] RabbitMQ 队列初始化完成\n";
            
        } catch (\Exception $e) {
            echo "[RabbitQueue] 错误: 队列初始化失败 - " . $e->getMessage() . "\n";
            // 不抛出异常，避免影响应用启动
        }
    }

    /**
     * 创建主交换机
     * @param RabbitMQ $rabbitmq
     * @param string $exchangeName
     */
    private static function createMainExchange(RabbitMQ $rabbitmq, string $exchangeName): void
    {
        try {
            $rabbitmq->createExchange($exchangeName, 'direct', [
                'durable' => true,
                'auto_delete' => false,
                'arguments' => []
            ]);
            echo "[RabbitQueue] 创建交换机: {$exchangeName} (direct 模式)\n";
        } catch (\Exception $e) {
            echo "[RabbitQueue] 交换机 {$exchangeName} 已存在或创建失败: " . $e->getMessage() . "\n";
        }
    }

    /**
     * 创建任务队列
     * @param RabbitMQ $rabbitmq
     * @param string $exchangeName
     */
    private static function createTaskQueues(RabbitMQ $rabbitmq, string $exchangeName): void
    {
        foreach (self::$taskTypes as $taskType => $config) {
            try {
                // 创建队列
                $rabbitmq->createQueue($config['queue'], [
                    'durable' => true,
                    'auto_delete' => false,
                    'arguments' => [
                        'x-message-ttl' => 3600000, // 消息TTL: 1小时
                        'x-max-priority' => 10,     // 支持优先级
                        'x-dead-letter-exchange' => $exchangeName . '_dlx',
                        'x-dead-letter-routing-key' => 'dead_letter'
                    ]
                ]);
                
                // 绑定队列到交换机
                $rabbitmq->createBinding($exchangeName, $config['queue'], $config['routing_key']);
                
                echo "[RabbitQueue] 创建队列: {$config['queue']} -> {$config['description']}\n";
                
            } catch (\Exception $e) {
                echo "[RabbitQueue] 队列 {$config['queue']} 创建失败: " . $e->getMessage() . "\n";
            }
        }
    }

    /**
     * 创建死信队列
     * @param RabbitMQ $rabbitmq
     * @param string $exchangeName
     */
    private static function createDeadLetterQueue(RabbitMQ $rabbitmq, string $exchangeName): void
    {
        try {
            $dlxName = $exchangeName . '_dlx';
            $dlqName = $exchangeName . '_dead_letter_queue';
            
            // 创建死信交换机
            $rabbitmq->createExchange($dlxName, 'direct', [
                'durable' => true,
                'auto_delete' => false
            ]);
            
            // 创建死信队列
            $rabbitmq->createQueue($dlqName, [
                'durable' => true,
                'auto_delete' => false,
                'arguments' => []
            ]);
            
            // 绑定死信队列
            $rabbitmq->createBinding($dlxName, $dlqName, 'dead_letter');
            
            echo "[RabbitQueue] 创建死信队列: {$dlqName}\n";
            
        } catch (\Exception $e) {
            echo "[RabbitQueue] 死信队列创建失败: " . $e->getMessage() . "\n";
        }
    }

    /**
     * 获取任务类型配置
     * @return array
     */
    public static function getTaskTypes(): array
    {
        return self::$taskTypes;
    }

    /**
     * 获取指定任务类型的队列名称
     * @param string $taskType
     * @return string|null
     */
    public static function getQueueName(string $taskType): ?string
    {
        return self::$taskTypes[$taskType]['queue'] ?? null;
    }

    /**
     * 获取指定任务类型的路由键
     * @param string $taskType
     * @return string|null
     */
    public static function getRoutingKey(string $taskType): ?string
    {
        return self::$taskTypes[$taskType]['routing_key'] ?? null;
    }

    /**
     * 检查任务类型是否存在
     * @param string $taskType
     * @return bool
     */
    public static function isValidTaskType(string $taskType): bool
    {
        return isset(self::$taskTypes[$taskType]);
    }

    /**
     * 添加新的任务类型
     * @param string $taskType
     * @param array $config
     */
    public static function addTaskType(string $taskType, array $config): void
    {
        self::$taskTypes[$taskType] = $config;
    }

    /**
     * 获取队列统计信息
     * @return array
     */
    public static function getQueueStats(): array
    {
        try {
            $rabbitmq = new RabbitMQ();
            $stats = [];
            
            foreach (self::$taskTypes as $taskType => $config) {
                try {
                    $queueStats = $rabbitmq->getQueueStats($config['queue']);
                    $stats[$taskType] = [
                        'queue' => $config['queue'],
                        'description' => $config['description'],
                        'messages' => $queueStats['messages'],
                        'consumers' => $queueStats['consumers'],
                        'state' => $queueStats['state']
                    ];
                } catch (\Exception $e) {
                    $stats[$taskType] = [
                        'queue' => $config['queue'],
                        'description' => $config['description'],
                        'error' => $e->getMessage()
                    ];
                }
            }
            
            return $stats;
        } catch (\Exception $e) {
            return ['error' => $e->getMessage()];
        }
    }
}
