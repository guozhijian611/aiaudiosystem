# AI音频处理系统

智能音频处理系统，支持语音提取、降噪、识别和转录。

## 后端介绍
本系统由以下后端服务组成
- Webman 中台服务
- Saiadmin-vue  中台前端
- AiVoice 用户前端
- Redis 缓存数据库
- RabbitMQ 消息队列服务
- MySQL84 数据库服务
- MiniO S3文件存储服务【Option】
- Cut_Node 音频切割节点
- Clear_Node 音频降噪节点
- Quick_Node 快速识别有效音频节点
- Translate_Node 文字转写节点
- Real_Node 实时语音转写节点【Dev】

## 工作流
1.文件上传->视频->提取音频->音频降噪->快速识别 (可选继续或跳过)->文字转写

## 快速启动

```bash
# 启动后端服务
cd webman
php -d memory_limit=512M start.php start

# 启动Cut Node服务
#python313
cd cut_node
source venv/bin/activate
python src/main.py
```

## 项目结构

- `webman/` - PHP后端服务（Webman框架）
- `cut_node/` - Python音频处理节点
- `saiadmin-vue/` - Vue.js前端界面
- `doc/` - 项目文档

## 注意事项

项目已配置完整的 `.gitignore` 文件，自动忽略：
- 虚拟环境和依赖包
- 临时文件和工作目录
- 配置文件和密钥
- 音频/视频文件
- 日志和缓存文件
