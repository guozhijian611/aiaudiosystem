# 队列系统增强版API文档

## 概述

队列系统现在支持两种工作模式：

1. **工作流模式**：按照预设的工作流程自动处理（原有功能）
2. **独立任务模式**：单独推送特定类型的任务（新增功能）

## 任务类型和队列映射

| 任务类型 | 常量值 | 队列名称 | 功能描述 |
|---------|--------|----------|----------|
| TASK_TYPE_EXTRACT | 1 | voice_extract_queue | 音频提取 |
| TASK_TYPE_CONVERT | 2 | audio_clear_queue | 音频降噪 |
| TASK_TYPE_FAST_RECOGNITION | 3 | fast_process_queue | 快速识别 |
| TASK_TYPE_TEXT_CONVERT | 4 | transcribe_queue | 文本转写 |

## 任务步骤状态

| 状态常量 | 值 | 描述 |
|---------|---|------|
| STEP_UPLOADED | 0 | 文件已上传，等待处理 |
| STEP_EXTRACTING | 1 | 正在提取音频 |
| STEP_EXTRACT_COMPLETED | 2 | 音频提取完成，等待降噪 |
| STEP_CLEARING | 3 | 正在音频降噪 |
| STEP_CLEAR_COMPLETED | 4 | 音频降噪完成，等待下一步处理 |
| STEP_FAST_RECOGNIZING | 5 | 正在快速识别 |
| STEP_FAST_COMPLETED | 6 | 快速识别完成，等待用户选择是否转写 |
| STEP_TRANSCRIBING | 7 | 正在文本转写 |
| STEP_ALL_COMPLETED | 8 | 所有处理完成 |
| STEP_FAILED | 9 | 处理失败 |
| STEP_PAUSED | 10 | 任务暂停 |

## API接口

### 1. 工作流模式推送（原有功能）

**接口**: `POST /queue/push`

**功能**: 按照工作流程推送任务，支持快速识别流程和完整转写流程

**参数**:
```json
{
    "task_id": 123,
    "task_flow": 1
}
```

- `task_id`: 任务ID（必须）
- `task_flow`: 任务流程类型（必须）
  - `1`: 快速识别流程（提取→降噪→快速识别→等待用户选择）
  - `2`: 完整转写流程（提取→降噪→文本转写）

**响应**:
```json
{
    "code": 200,
    "msg": "任务提交成功",
    "data": null
}
```

### 2. 单独推送任务（新增功能）

**接口**: `POST /queue/push-single`

**功能**: 单独推送指定类型的任务，不依赖工作流程

**参数**:
```json
{
    "task_id": 123,
    "task_type": 4,
    "force": false
}
```

- `task_id`: 任务详情ID（必须）
- `task_type`: 任务类型（必须）1-4
- `force`: 是否强制推送（可选），忽略状态检查

**使用场景**:
- 重新处理失败的任务
- 跳过某些步骤直接处理
- 测试特定的处理节点
- 手动干预和调试

**响应**:
```json
{
    "code": 200,
    "msg": "任务推送成功",
    "data": {
        "queue": "transcribe_queue",
        "task_id": 123,
        "task_type": 4,
        "step": 7
    }
}
```

**示例**:

1. **直接进行文本转写**（跳过快速识别）:
```bash
curl -X POST http://localhost:8787/queue/push-single \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123, "task_type": 4}'
```

2. **重新处理失败的音频降噪**:
```bash
curl -X POST http://localhost:8787/queue/push-single \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123, "task_type": 2, "force": true}'
```

### 3. 批量推送任务（新增功能）

**接口**: `POST /queue/push-batch`

**功能**: 批量推送多个任务到同一类型的队列

**参数**:
```json
{
    "task_ids": [123, 124, 125],
    "task_type": 4,
    "force": false,
    "continue_on_error": true
}
```

- `task_ids`: 任务ID数组（必须）
- `task_type`: 任务类型（必须）
- `force`: 是否强制推送（可选）
- `continue_on_error`: 遇到错误是否继续（可选）

**响应**:
```json
{
    "code": 200,
    "msg": "批量推送完成：成功 2 个，失败 1 个",
    "data": {
        "total": 3,
        "success": 2,
        "failed": 1,
        "details": [
            {
                "task_id": 123,
                "status": "success",
                "queue": "transcribe_queue"
            },
            {
                "task_id": 124,
                "status": "success", 
                "queue": "transcribe_queue"
            },
            {
                "task_id": 125,
                "status": "failed",
                "message": "缺少降噪音频文件URL，请先完成音频降噪"
            }
        ]
    }
}
```

### 4. 继续转写（原有功能）

**接口**: `POST /queue/continue-transcribe`

**功能**: 快速识别完成后，用户选择继续进行文本转写

**参数**:
```json
{
    "task_id": 123
}
```

**响应**:
```json
{
    "code": 200,
    "msg": "已提交转写任务",
    "data": null
}
```

## 前置条件验证

系统会自动验证任务的前置条件：

### 音频提取 (task_type=1)
- ✅ 需要：原始文件URL (`url`)
- ❌ 阻止：音频已提取 (`is_extract=1`)

### 音频降噪 (task_type=2)  
- ✅ 需要：音频文件URL (`voice_url`)
- ❌ 阻止：音频已降噪 (`is_clear=1`)

### 快速识别 (task_type=3)
- ✅ 需要：降噪音频URL (`clear_url`)
- ❌ 阻止：快速识别已完成 (`fast_status=1`)

### 文本转写 (task_type=4)
- ✅ 需要：降噪音频URL (`clear_url`)
- ❌ 阻止：文本转写已完成 (`transcribe_status=1`)

## 错误处理

### 常见错误码

- `400`: 参数错误、任务不存在、前置条件不满足
- `207`: 批量操作部分成功
- `500`: 服务器内部错误

### 错误示例

```json
{
    "code": 400,
    "msg": "缺少降噪音频文件URL，请先完成音频降噪",
    "data": null
}
```

## 使用建议

### 1. 正常工作流程
使用 `/queue/push` 接口，让系统自动按流程处理：

```bash
# 快速识别流程
curl -X POST http://localhost:8787/queue/push \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123, "task_flow": 1}'

# 完整转写流程  
curl -X POST http://localhost:8787/queue/push \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123, "task_flow": 2}'
```

### 2. 跳过步骤处理
如果某些步骤已完成，可以直接推送到后续步骤：

```bash
# 直接进行文本转写（假设音频已降噪）
curl -X POST http://localhost:8787/queue/push-single \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123, "task_type": 4}'
```

### 3. 重新处理失败任务
使用 `force=true` 重新处理：

```bash
curl -X POST http://localhost:8787/queue/push-single \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123, "task_type": 2, "force": true}'
```

### 4. 批量处理
批量推送多个任务：

```bash
curl -X POST http://localhost:8787/queue/push-batch \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [123, 124, 125],
    "task_type": 4,
    "continue_on_error": true
  }'
```

## 监控和调试

### 查看任务状态
通过 `task_info` 表的 `step` 字段监控任务进度：

```sql
SELECT id, step, error_msg, retry_count 
FROM ai_task_info 
WHERE id = 123;
```

### 常用查询

```sql
-- 查看失败的任务
SELECT * FROM ai_task_info WHERE step = 9;

-- 查看正在处理的任务  
SELECT * FROM ai_task_info WHERE step IN (1,3,5,7);

-- 查看等待用户选择的任务
SELECT * FROM ai_task_info WHERE step = 6;
``` 