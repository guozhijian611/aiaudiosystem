FROM continuumio/miniconda3:latest

# 设置工作目录
WORKDIR /app

# 复制环境配置文件
COPY environment.yml .

# 创建conda环境
RUN conda env create -f environment.yml

# 激活环境
SHELL ["conda", "run", "-n", "whisperx", "/bin/bash", "-c"]

# 复制应用代码
COPY . .

# 安装Python依赖（不在environment.yml中的）
RUN conda run -n whisperx pip install -r requirements.txt

# 创建必要的目录
RUN mkdir -p work temp logs models

# 设置环境变量
ENV PYTHONPATH=/app/src:/app

# 暴露端口（如果需要）
# EXPOSE 8000

# 启动命令
CMD ["conda", "run", "-n", "whisperx", "python", "main.py"] 