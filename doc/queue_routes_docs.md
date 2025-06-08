# 队列系统路由配置文档

## 路由组：/queue

所有队列相关的接口都在 `/queue` 路由组下，使用POST方法。

### 1. 推送任务到队列
**路由**: `POST /queue/push`  
**控制器方法**: `QueueController::pushTaskToQueue`  
**描述**: 将任务推送到队列系统进行处理  
**用途**: 前端用户开始任务处理时调用

**请求参数**:
```json
{
    "task_id": 123,           // 任务ID，必需
    "task_flow": 1            // 任务流程类型，必需
                             // 1: 快速识别流程
                             // 2: 完整流程
}
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "任务推送成功",
    "data": null
}
```

### 2. 队列任务回调接口
**路由**: `POST /queue/callback`  
**控制器方法**: `QueueController::handleTaskCallback`  
**描述**: 队列节点处理完成后的回调接口  
**用途**: 队列节点调用，更新任务状态和推送下一步

**请求参数**:
```json
{
    "task_id": 123,                    // 任务ID，必需
    "task_type": 1,                   // 任务类型，必需
                                     // 1: 音频提取
                                     // 2: 音频降噪
                                     // 3: 快速识别
                                     // 4: 文本转写
    "status": "success",              // 处理状态，必需
                                     // success: 成功
                                     // failed: 失败
    "data": {                        // 处理结果数据（成功时必需）
        "voice_url": "文件URL",
        "clear_url": "降噪文件URL",
        "text_info": "识别结果",
        // 其他根据任务类型的字段...
    },
    "message": "错误信息"             // 失败时的错误描述（失败时必需）
}
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "回调处理成功",
    "data": null
}
```

### 3. 文件上传接口
**路由**: `POST /queue/upload`  
**控制器方法**: `QueueController::upload`  
**描述**: 队列节点上传处理结果文件  
**用途**: 队列节点先上传文件，再调用回调接口

**请求参数**:
- Content-Type: `multipart/form-data`
- `file`: 文件数据（必需）
- `task_type`: 任务类型（可选，用于文件格式验证）

**响应示例**:
```json
{
    "code": 200,
    "msg": "文件上传成功",
    "data": {
        "field_name": "file",
        "file_info": {
            "url": "http://domain/storage/queue/20241220/abc123.mp3",
            "origin_name": "result_audio.mp3",
            "object_name": "abc123.mp3",
            "hash": "abc123def456...",
            "mime_type": "audio/mpeg",
            "storage_path": "public/storage/queue/20241220/abc123.mp3",
            "suffix": "mp3",
            "size_byte": 1048576,
            "size_info": "1.00 MB"
        }
    }
}
```

### 4. 继续转写接口
**路由**: `POST /queue/continue-transcribe`  
**控制器方法**: `QueueController::continueToTranscribe`  
**描述**: 用户主动选择继续进行文本转写  
**用途**: 快速识别完成后，用户决定进行完整转写时调用

**请求参数**:
```json
{
    "task_info_id": 456      // TaskInfo ID，必需
}
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "转写任务已开始",
    "data": null
}
```

### 5. 测试接口
**路由**: `POST /queue/test`  
**控制器方法**: `QueueController::test`  
**描述**: 测试队列功能  
**用途**: 开发和调试时使用

## 使用流程示例

### 完整工作流程

#### 1. 用户发起任务
```bash
curl -X POST http://domain/queue/push \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123, "task_flow": 2}'
```

#### 2. 节点处理音频提取
节点完成音频提取后：

```bash
# 2.1 上传提取的音频文件
curl -X POST http://domain/queue/upload \
  -F "file=@extracted_audio.mp3" \
  -F "task_type=1"

# 2.2 调用回调接口
curl -X POST http://domain/queue/callback \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 123,
    "task_type": 1,
    "status": "success",
    "data": {"voice_url": "返回的文件URL"}
  }'
```

#### 3. 节点处理音频降噪
节点完成音频降噪后：

```bash
# 3.1 上传降噪后的音频文件
curl -X POST http://domain/queue/upload \
  -F "file=@cleared_audio.mp3" \
  -F "task_type=2"

# 3.2 调用回调接口
curl -X POST http://domain/queue/callback \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 123,
    "task_type": 2,
    "status": "success",
    "data": {"clear_url": "返回的文件URL"}
  }'
```

#### 4. 节点处理文本转写
节点完成文本转写后：

```bash
# 4.1 上传转写结果文件
curl -X POST http://domain/queue/upload \
  -F "file=@transcribe_result.json" \
  -F "task_type=4"

# 4.2 调用回调接口
curl -X POST http://domain/queue/callback \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 123,
    "task_type": 4,
    "status": "success",
    "data": {
      "text_info": "转写的文本内容",
      "effective_voice": "有效语音时长",
      "total_voice": "总语音时长",
      "language": "中文"
    }
  }'
```

### 快速识别后继续转写

如果用户选择了快速识别流程，但后来想要完整转写：

```bash
curl -X POST http://domain/queue/continue-transcribe \
  -H "Content-Type: application/json" \
  -d '{"task_info_id": 456}'
```

## 错误码说明

- `200`: 操作成功
- `400`: 请求参数错误或业务逻辑错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 注意事项

1. **文件上传限制**: 默认最大100MB，支持的格式根据task_type而定
2. **任务锁机制**: 正在处理中的任务会被锁定，防止重复提交
3. **错误重试**: 失败的任务会记录重试次数
4. **文件存储**: 队列上传的文件存储在`storage/queue/日期/`目录下
5. **回调时序**: 必须先调用upload接口上传文件，再调用callback接口处理业务逻辑 