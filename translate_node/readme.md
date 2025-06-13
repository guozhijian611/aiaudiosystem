# 文本转写节点WhisperX

- 注意，如果是基于 50 系列显卡，需要把 pytorch 切换成夜间版本

```yaml
name: whisperx-dev-mixed  
channels:  
  - pytorch-nightly   #这里添加通道
  - pytorch  
  - nvidia  
  - conda-forge  
  - defaults  
  
dependencies:  
  - python>=3.9,<3.13  
  - pytorch-nightly   # 这里添加依赖
  - torchaudio-nightly  
  - numpy>=2.0.2  
```
