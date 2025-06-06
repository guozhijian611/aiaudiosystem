<?php

namespace app\service;

/**
 * RabbitMQ HTTP API 服务类
 * 通过 RabbitMQ Management HTTP API 进行操作
 */
class RabbitMQ
{
    /**
     * RabbitMQ HTTP API 基础URL
     */
    private string $baseUrl;
    
    /**
     * 用户名
     */
    private string $username;
    
    /**
     * 密码
     */
    private string $password;
    
    /**
     * 虚拟主机
     */
    private string $vhost;
    
    /**
     * HTTP 客户端选项
     */
    private array $httpOptions;

    /**
     * 构造函数
     */
    public function __construct()
    {
        // 根据实际 .env 配置读取 MQ_ 前缀的配置项
        $host = getenv('MQ_HOST') ?: '127.0.0.1';
        $httpPort = getenv('MQ_HTTP_PORT') ?: '15672';
        $protocol = getenv('MQ_HTTP_PROTOCOL') ?: 'http';
        
        // 构建 HTTP API URL
        $this->baseUrl = "{$protocol}://{$host}:{$httpPort}";
        
        $this->username = getenv('MQ_USER') ?: 'guest';
        $this->password = getenv('MQ_PASS') ?: 'guest';
        $this->vhost = trim(getenv('MQ_VHOST') ?: '/');
        
        $this->httpOptions = [
            'timeout' => (int)(getenv('MQ_HTTP_TIMEOUT') ?: 30),
            'headers' => [
                'Content-Type: application/json',
                'Authorization: Basic ' . base64_encode($this->username . ':' . $this->password)
            ]
        ];
    }

    /**
     * 发送 HTTP 请求
     * @param string $method HTTP 方法
     * @param string $endpoint API 端点
     * @param array $data 请求数据
     * @return array
     * @throws \Exception
     */
    private function httpRequest(string $method, string $endpoint, array $data = []): array
    {
        $url = $this->baseUrl . '/api' . $endpoint;
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->httpOptions['timeout'],
            CURLOPT_HTTPHEADER => $this->httpOptions['headers'],
            CURLOPT_CUSTOMREQUEST => strtoupper($method),
        ]);
        
        if (!empty($data) && in_array(strtoupper($method), ['POST', 'PUT', 'PATCH'])) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new \Exception("CURL Error: {$error}");
        }
        
        $result = json_decode($response, true);
        
        if ($httpCode >= 400) {
            $errorMsg = $result['reason'] ?? $result['error'] ?? "HTTP Error {$httpCode}";
            throw new \Exception("RabbitMQ API Error: {$errorMsg}");
        }
        
        return $result ?: [];
    }

    /**
     * 获取集群概览信息
     * @return array
     */
    public function getOverview(): array
    {
        return $this->httpRequest('GET', '/overview');
    }

    /**
     * 获取所有队列
     * @return array
     */
    public function getQueues(): array
    {
        $vhost = urlencode($this->vhost);
        return $this->httpRequest('GET', "/queues/{$vhost}");
    }

    /**
     * 获取指定队列信息
     * @param string $queueName 队列名称
     * @return array
     */
    public function getQueue(string $queueName): array
    {
        $vhost = urlencode($this->vhost);
        $queue = urlencode($queueName);
        return $this->httpRequest('GET', "/queues/{$vhost}/{$queue}");
    }

    /**
     * 创建队列
     * @param string $queueName 队列名称
     * @param array $options 队列选项
     * @return bool
     */
    public function createQueue(string $queueName, array $options = []): bool
    {
        $vhost = urlencode($this->vhost);
        $queue = urlencode($queueName);
        
        $defaultOptions = [
            'durable' => true,
            'auto_delete' => false,
            'arguments' => []
        ];
        
        $queueOptions = array_merge($defaultOptions, $options);
        
        try {
            $this->httpRequest('PUT', "/queues/{$vhost}/{$queue}", $queueOptions);
            return true;
        } catch (\Exception $e) {
            throw new \Exception("创建队列失败: " . $e->getMessage());
        }
    }

    /**
     * 删除队列
     * @param string $queueName 队列名称
     * @param bool $ifUnused 仅在未使用时删除
     * @param bool $ifEmpty 仅在为空时删除
     * @return bool
     */
    public function deleteQueue(string $queueName, bool $ifUnused = false, bool $ifEmpty = false): bool
    {
        $vhost = urlencode($this->vhost);
        $queue = urlencode($queueName);
        
        $params = [];
        if ($ifUnused) $params[] = 'if-unused=true';
        if ($ifEmpty) $params[] = 'if-empty=true';
        
        $queryString = !empty($params) ? '?' . implode('&', $params) : '';
        
        try {
            $this->httpRequest('DELETE', "/queues/{$vhost}/{$queue}{$queryString}");
            return true;
        } catch (\Exception $e) {
            throw new \Exception("删除队列失败: " . $e->getMessage());
        }
    }

    /**
     * 清空队列
     * @param string $queueName 队列名称
     * @return bool
     */
    public function purgeQueue(string $queueName): bool
    {
        $vhost = urlencode($this->vhost);
        $queue = urlencode($queueName);
        
        try {
            $this->httpRequest('DELETE', "/queues/{$vhost}/{$queue}/contents");
            return true;
        } catch (\Exception $e) {
            throw new \Exception("清空队列失败: " . $e->getMessage());
        }
    }

    /**
     * 发布消息到队列
     * @param string $queueName 队列名称
     * @param mixed $message 消息内容
     * @param array $properties 消息属性
     * @return bool
     */
    public function publishMessage(string $queueName, $message, array $properties = []): bool
    {
        $vhost = urlencode($this->vhost);
        
        $defaultProperties = [
            'delivery_mode' => 2, // 持久化消息
            'content_type' => 'application/json'
        ];
        
        $messageProperties = array_merge($defaultProperties, $properties);
        
        $payload = [
            'properties' => $messageProperties,
            'routing_key' => $queueName,
            'payload' => is_string($message) ? $message : json_encode($message),
            'payload_encoding' => 'string'
        ];
        
        try {
            $this->httpRequest('POST', "/exchanges/{$vhost}/amq.default/publish", $payload);
            return true;
        } catch (\Exception $e) {
            throw new \Exception("发布消息失败: " . $e->getMessage());
        }
    }

    /**
     * 从队列获取消息（消费消息）
     * @param string $queueName 队列名称
     * @param int $count 获取消息数量
     * @param bool $ackMode 确认模式 (true: ack_requeue_false, false: ack_requeue_true)
     * @return array
     */
    public function getMessages(string $queueName, int $count = 1, bool $ackMode = true): array
    {
        $vhost = urlencode($this->vhost);
        $queue = urlencode($queueName);
        
        $payload = [
            'count' => $count,
            'ackmode' => $ackMode ? 'ack_requeue_false' : 'ack_requeue_true',
            'encoding' => 'auto'
        ];
        
        try {
            return $this->httpRequest('POST', "/queues/{$vhost}/{$queue}/get", $payload);
        } catch (\Exception $e) {
            throw new \Exception("获取消息失败: " . $e->getMessage());
        }
    }

    /**
     * 获取所有交换机
     * @return array
     */
    public function getExchanges(): array
    {
        $vhost = urlencode($this->vhost);
        return $this->httpRequest('GET', "/exchanges/{$vhost}");
    }

    /**
     * 创建交换机
     * @param string $exchangeName 交换机名称
     * @param string $type 交换机类型 (direct, topic, fanout, headers)
     * @param array $options 交换机选项
     * @return bool
     */
    public function createExchange(string $exchangeName, string $type = 'direct', array $options = []): bool
    {
        $vhost = urlencode($this->vhost);
        $exchange = urlencode($exchangeName);
        
        $defaultOptions = [
            'type' => $type,
            'durable' => true,
            'auto_delete' => false,
            'arguments' => []
        ];
        
        $exchangeOptions = array_merge($defaultOptions, $options);
        
        try {
            $this->httpRequest('PUT', "/exchanges/{$vhost}/{$exchange}", $exchangeOptions);
            return true;
        } catch (\Exception $e) {
            throw new \Exception("创建交换机失败: " . $e->getMessage());
        }
    }

    /**
     * 删除交换机
     * @param string $exchangeName 交换机名称
     * @param bool $ifUnused 仅在未使用时删除
     * @return bool
     */
    public function deleteExchange(string $exchangeName, bool $ifUnused = false): bool
    {
        $vhost = urlencode($this->vhost);
        $exchange = urlencode($exchangeName);
        
        $queryString = $ifUnused ? '?if-unused=true' : '';
        
        try {
            $this->httpRequest('DELETE', "/exchanges/{$vhost}/{$exchange}{$queryString}");
            return true;
        } catch (\Exception $e) {
            throw new \Exception("删除交换机失败: " . $e->getMessage());
        }
    }

    /**
     * 创建绑定
     * @param string $exchangeName 交换机名称
     * @param string $queueName 队列名称
     * @param string $routingKey 路由键
     * @param array $arguments 绑定参数
     * @return bool
     */
    public function createBinding(string $exchangeName, string $queueName, string $routingKey = '', array $arguments = []): bool
    {
        $vhost = urlencode($this->vhost);
        $exchange = urlencode($exchangeName);
        $queue = urlencode($queueName);
        
        $payload = [
            'routing_key' => $routingKey,
            'arguments' => $arguments
        ];
        
        try {
            $this->httpRequest('POST', "/bindings/{$vhost}/e/{$exchange}/q/{$queue}", $payload);
            return true;
        } catch (\Exception $e) {
            throw new \Exception("创建绑定失败: " . $e->getMessage());
        }
    }

    /**
     * 获取队列绑定
     * @param string $queueName 队列名称
     * @return array
     */
    public function getQueueBindings(string $queueName): array
    {
        $vhost = urlencode($this->vhost);
        $queue = urlencode($queueName);
        return $this->httpRequest('GET', "/queues/{$vhost}/{$queue}/bindings");
    }

    /**
     * 获取连接列表
     * @return array
     */
    public function getConnections(): array
    {
        return $this->httpRequest('GET', '/connections');
    }

    /**
     * 获取通道列表
     * @return array
     */
    public function getChannels(): array
    {
        return $this->httpRequest('GET', '/channels');
    }

    /**
     * 检查 RabbitMQ 服务状态
     * @return bool
     */
    public function isAlive(): bool
    {
        try {
            $this->httpRequest('GET', '/aliveness-test/' . urlencode($this->vhost));
            return true;
        } catch (\Exception $e) {
            return false;
        }
    }

    /**
     * 获取节点信息
     * @return array
     */
    public function getNodes(): array
    {
        return $this->httpRequest('GET', '/nodes');
    }

    /**
     * 批量发布消息
     * @param string $queueName 队列名称
     * @param array $messages 消息数组
     * @return bool
     */
    public function publishBatchMessages(string $queueName, array $messages): bool
    {
        $successCount = 0;
        $totalCount = count($messages);
        
        foreach ($messages as $message) {
            try {
                if ($this->publishMessage($queueName, $message)) {
                    $successCount++;
                }
            } catch (\Exception $e) {
                // 记录错误但继续处理其他消息
                error_log("批量发布消息失败: " . $e->getMessage());
            }
        }
        
        return $successCount === $totalCount;
    }

    /**
     * 获取队列统计信息
     * @param string $queueName 队列名称
     * @return array
     */
    public function getQueueStats(string $queueName): array
    {
        $queue = $this->getQueue($queueName);
        
        return [
            'name' => $queue['name'] ?? '',
            'messages' => $queue['messages'] ?? 0,
            'messages_ready' => $queue['messages_ready'] ?? 0,
            'messages_unacknowledged' => $queue['messages_unacknowledged'] ?? 0,
            'consumers' => $queue['consumers'] ?? 0,
            'memory' => $queue['memory'] ?? 0,
            'state' => $queue['state'] ?? 'unknown'
        ];
    }
}
