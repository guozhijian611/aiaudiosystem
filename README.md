# AI音频处理系统

智能音频处理系统，支持语音提取、降噪、识别和转录。

## 快速启动

```bash
# 启动后端服务
cd webman
php -d memory_limit=512M start.php start

# 启动Cut Node服务
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
