# windows安装教程
请提前安装好 php82，ffmpeg,composer，git，redis，mysql8+，node，rabbitmq，miniconda，显卡驱动，vc++14 build tools
```bash
# windows powershell运行执行脚本
Set-ExecutionPolicy Unrestricted


#0.克隆项目
git clone https://github.com/guozhijian611/aiaudiosystem.git

#1. 安装webman依赖
cd aiaudiosystem/webman
composer install

# 修改env里面的数据库信息，然后记得导入一下数据库
#启动 webman后端，这里用windows的来展示
php windows.php


#2. 启动中台服务
cd aiaudiosystem/saiadmin-vue
# 修改NPM 的淘宝源
npm config set registry https://registry.npmmirror.com

#验证修改
npm config get registry
# 安装依赖
npm install
# 查看本机局域网 ip 之后，修改.env.development 的文件监听地址
# 目前以开发模式运行，如果需要编译封装的话，需要自行 build。 这个中台主要是为了调试使用，调试完后关闭。
npm run dev
# 然后访问后台-系统配置-上传配置-修改一下域名地址

#3. 启动前台服务
cd aiaudiosystem/newAIvoice
npm install
# 编辑 newAIvoice/src/utils/request.ts:5,修改接口的 api 地址为本地局域网的 IP 地址
#旧版本请编辑 vite.config.js
server: {
  host: true,
  port: 5173
}
#启动
npm run dev
# 设置pip清华源
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
# 4. 启动Cut_node
cd aiaudiosystem/cut_node
#创建虚拟环境
conda create -n CutNode python=3.12 -y
conda activate CutNode
pip install -r requirements.txt

# 编辑env配置，然后启动
python src/main.py


# 5.启动降噪节点
cd aiaudiosystem/clear_node
#安装环境
conda env create -f environment.yml -y
conda activate ClearerVoice-Studio
pip install -r requirements.txt
#如果是 50 系列显卡会报错，需要安装夜间版 pytroch，可以覆盖安装
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128  --force-reinstall

# 6. 启动快速识别节点
cd aiaudiosystem/quick_node
conda env create -f enviroment.yml -y
conda activate funasr
pip install -r .\requirements.txt
#修改env后启动脚本
python run.py

# 7.安装文字转写节点
cd aiaudiosystem/translate_node
conda env create -f environment.yml -y
conda activate whisperx
pip install -r .\requirements.txt
#如果是 50 系列显卡会报错，需要安装夜间版 pytroch，可以覆盖安装
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128  --force-reinstall
#配置env，记得配置 HF_TOKEN , 人声对齐需要。
python main.py

# 其他可选节点依赖配置什么的自行安装。

#到此，结束
```
