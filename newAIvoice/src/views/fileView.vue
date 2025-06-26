<template>
  <div class="fileViewBox">
    <el-tabs v-model="activeName" type="card" class="demo-tabs" @tab-click="handleClick">
      <el-tab-pane label="原始文件" name="first">
        <el-tabs v-model="activeName1" class="demo-tabs1" @tab-click="handleClick1">
          <el-tab-pane label="任务名称" name="first1">
            <ul class="taskInfoUl">
              <li>文件名称 {{ getFileInfo?.filename || '未知' }}</li>
              <li>文件大小 {{ getFileInfo?.size || '未知' }}</li>
              <li>有效时长 {{ getFileInfo?.effective_voice || '未知' }}</li>
              <li>总时长 {{ getFileInfo?.total_voice || '未知' }}</li>
              <li>语种 {{ getFileInfo?.language || '未知' }}</li>
              <li>是否转写 {{ getFileInfo?.is_extract == '1' ? '是' : '否' }}</li>
              <li>是否降噪 {{ getFileInfo?.is_clear == '1' ? '是' : '否' }}</li>
            </ul>
          </el-tab-pane>
        </el-tabs>
        <div class="fileBox">
          <div class="fileOriginal">
            <div class="fileOriginalTitle">原始文件</div>
            <div class="fileOriginalContent">
              <div class="videoBox">
                <div v-if="isVideoLoading" class="video-loading">
                  <el-icon class="loading-icon">
                    <Loading />
                  </el-icon>
                  <span>媒体加载中...</span>
                </div>
                <div v-else-if="videoLoadError" class="video-error">
                  <el-icon class="error-icon">
                    <CircleClose />
                  </el-icon>
                  <span>媒体加载失败</span>
                  <el-button type="primary" size="small" @click="retryLoadVideo">重试</el-button>
                </div>
                <!-- 视频播放器 -->
                <video v-if="isVideoFile" ref="videoRef" :src="getFileInfo.url" @loadstart="handleVideoLoadStart"
                  @loadeddata="handleVideoLoaded" @error="handleVideoError" controls>
                  您的浏览器不支持 video 标签。
                </video>
                <!-- 音频播放器 -->
                <audio v-else ref="audioRef" :src="getFileInfo.url" @loadstart="handleVideoLoadStart"
                  @loadeddata="handleVideoLoaded" @error="handleVideoError" controls>
                  您的浏览器不支持 audio 标签。
                </audio>
              </div>
              <div class="audioTrack" ref="wavesurferContainer">
                <!-- WaveSurfer 将在这里渲染波形 -->
              </div>
              <div class="audioAction">
                <el-button type="success" plain @click="playVideo">▶ 播放</el-button>
                <!-- <button @click="playVideo">▶ 播放</button> -->
                <el-button type="danger" plain @click="pauseVideo">⏸ 暂停</el-button>
                <el-button type="primary" plain @click="increaseVolume">🔊 增大音量</el-button>
                <el-button color="#626aef" plain @click="decreaseVolume">🔉 减小音量</el-button>
                <!-- <p>当前音量：{{ (currentVolume * 100).toFixed(0) }}%</p> -->
              </div>
            </div>
          </div>
          <div class="transcriptionPreview">
            <div class="transcriptionPreviewTop">
              <div class="transcriptionPreviewTitle">转写预览</div>
              <div class="transcriptionPreviewDownload">
                <el-dropdown>
                  <span class="el-dropdown-link">
                    转写下载
                    <el-icon class="el-icon--right">
                      <arrow-down />
                    </el-icon>
                  </span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="downloadText('withTimestamp')">带时间戳文本</el-dropdown-item>
                      <el-dropdown-item @click="downloadText('withoutTimestamp')">无时间戳文本</el-dropdown-item>
                      <el-dropdown-item @click="downloadText('word')">word文档</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            <div class="transcriptionPreviewContent">
              <div v-if="getFileInfo.text_info" class="lyrics-container">
                <div v-for="(segment, index) in JSON.parse(getFileInfo.text_info).segments" :key="index" class="lyric-line">
                  <span class="time-stamp">[{{ formatTime(segment.start) }} - {{ formatTime(segment.end) }}]</span>
                  <span v-if="segment.speaker" class="speaker">({{ segment.speaker }})</span>
                  <span class="lyric-text">{{ segment.text }}</span>
                </div>
              </div>
              <div v-else class="no-content">
                暂无转写内容
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="文件降噪" name="second">
        <el-tabs v-model="activeName2" class="demo-tabs2" @tab-click="handleClick2">
          <el-tab-pane label="任务名称" name="first2">
            <ul class="taskInfoUl">
              <li>文件名称{{ getFileInfo?.filename || '未知' }}</li>
              <li>文件大小 {{ getFileInfo?.size || '未知' }}</li>
              <li>有效时长 {{ getFileInfo?.effective_voice || '未知' }}</li>
              <li>总时长 {{ getFileInfo?.total_voice || '未知' }}</li>
              <li>语种 {{ getFileInfo?.language || '未知' }}</li>
              <li>是否转写 {{ getFileInfo?.is_extract == '1' ? '是' : '否' }}</li>
              <li>是否降噪 {{ getFileInfo?.is_clear == '1' ? '是' : '否' }}</li>
            </ul>
          </el-tab-pane>
        </el-tabs>
        <div class="fileBox2">
          <div class="fileReduction">
            <div class="fileReductionTop">
              <div class="fileReductionTitle">降噪文件</div>
              <div class="fileReductionDownload">
                <el-dropdown>
                  <span class="el-dropdown-link" @click="downloadClearFile">
                    降噪文件下载
                    <el-icon class="el-icon--right">
                      <!-- <arrow-down /> -->
                    </el-icon>
                  </span>
                </el-dropdown>
              </div>
            </div>
            <div class="fileReductionContent">
              <div class="videoBox">
                <div v-if="isVideoLoading1" class="video-loading">
                  <el-icon class="loading-icon">
                    <Loading />
                  </el-icon>
                  <span>媒体加载中...</span>
                </div>
                <div v-else-if="videoLoadError1" class="video-error">
                  <el-icon class="error-icon">
                    <CircleClose />
                  </el-icon>
                  <span>媒体加载失败</span>
                  <el-button type="primary" size="small" @click="retryLoadVideo1">重试</el-button>
                </div>
                <video v-if="isVideoFile" ref="videoRef1" :src="getFileInfo.clear_url" @loadstart="handleVideoLoadStart1"
                  @loadeddata="handleVideoLoaded1" @error="handleVideoError1" controls>
                  您的浏览器不支持 video 标签。
                </video>
                <!-- 音频播放器 -->
                <audio v-else ref="audioRef1" :src="getFileInfo.clear_url" @loadstart="handleVideoLoadStart1"
                  @loadeddata="handleVideoLoaded1" @error="handleVideoError1" controls>
                  您的浏览器不支持 audio 标签。
                </audio>
              </div>
              <div class="audioTrack" ref="wavesurferContainer1">
                <!-- WaveSurfer 将在这里渲染波形 -->
              </div>
              <div class="audioAction">
                <el-button type="success" plain @click="playVideo1">▶ 播放</el-button>
                <!-- <button @click="playVideo">▶ 播放</button> -->
                <el-button type="danger" plain @click="pauseVideo1">⏸ 暂停</el-button>
                <el-button type="primary" plain @click="increaseVolume1">🔊 增大音量</el-button>
                <el-button color="#626aef" plain @click="decreaseVolume1">🔉 减小音量</el-button>
                <!-- <p>当前音量：{{ (currentVolume * 100).toFixed(0) }}%</p> -->
              </div>
            </div>
          </div>
          <div class="transcriptionPreview">
            <div class="transcriptionPreviewTop">
              <div class="transcriptionPreviewTitle">转写预览</div>
              <div class="transcriptionPreviewDownload">
                <el-dropdown>
                  <span class="el-dropdown-link">
                    转写下载
                    <el-icon class="el-icon--right">
                      <arrow-down />
                    </el-icon>
                  </span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="downloadText('withTimestamp')">带时间戳文本</el-dropdown-item>
                      <el-dropdown-item @click="downloadText('withoutTimestamp')">无时间戳文本</el-dropdown-item>
                      <el-dropdown-item @click="downloadText('word')">word文档</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            <div class="transcriptionPreviewContent">
              <div v-if="getFileInfo.text_info" class="lyrics-container">
                <div v-for="(segment, index) in JSON.parse(getFileInfo.text_info).segments" :key="index" class="lyric-line">
                  <span class="time-stamp">[{{ formatTime(segment.start) }} - {{ formatTime(segment.end) }}]</span>
                  <span v-if="segment.speaker" class="speaker">({{ segment.speaker }})</span>
                  <span class="lyric-text">{{ segment.text }}</span>
                </div>
              </div>
              <div v-else class="no-content">
                暂无转写内容
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="降噪转写" name="third">
        <el-tabs v-model="activeName3" class="demo-tabs3" @tab-click="handleClick3">
          <el-tab-pane label="任务名称" name="first3">
            <ul class="taskInfoUl">
              <li>文件名称 {{ getFileInfo?.filename || '未知' }}</li>
              <li>文件大小 {{ getFileInfo?.size || '未知' }}</li>
              <li>有效时长 {{ getFileInfo?.effective_voice || '未知' }}</li>
              <li>总时长 {{ getFileInfo?.total_voice || '未知' }}</li>
              <li>语种 {{ getFileInfo?.language || '未知' }}</li>
              <li>是否转写 {{ getFileInfo?.is_extract == '1' ? '是' : '否' }}</li>
              <li>是否降噪 {{ getFileInfo?.is_clear == '1' ? '是' : '否' }}</li>
            </ul>
          </el-tab-pane>
        </el-tabs>
        <!-- <div class="fileBox3"> -->
          <el-button type="primary" class="clearbtn" @click="workflow1()">启动降噪</el-button>
          <!-- <div class="item">处理进度：</div>
          <div class="demo-progress">
            <el-progress :percentage="percentage" :status="getStatus" />
          </div> -->
        <!-- </div> -->
      </el-tab-pane>
    </el-tabs>
    <el-button v-for="button in buttons" :key="button.text" :type="button.type" class="returnBtn" text
      @click="router.push({ path: 'task-operation', query: { index: 4, id: taskId } })">
      {{ button.text }}
    </el-button>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, reactive, nextTick, onMounted, watch, onBeforeUnmount } from "vue";
import type { TabsPaneContext } from "element-plus";
import { ArrowDown, Loading, CircleClose } from "@element-plus/icons-vue";
import TableSearch from "@/components/operation-search.vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import WaveSurfer from 'wavesurfer.js';
import { ElMessage, ElMessageBox } from "element-plus";
import type { UploadProps, UploadUserFile } from "element-plus";
import { ElLoading } from "element-plus";
import { getTaskFileDetail, workflow} from "@/api/task"
import Login from "./pages/login.vue";

const router = useRouter();
const route = useRoute();
const id = ref<string>('');
const taskId = ref<string>('');
const fileInfo = ref(null);
const activeName = ref('first');
const activeName1 = ref('first1');
const activeName2 = ref('first2');
const activeName3 = ref('first3');
const percentage = ref(90);
const getStatus = computed(() => {
  if (percentage.value === 100) return "success";
  return ""; // 默认值
});
const workflow1 = async () => {
  try {
    console.log('taskId:', taskId.value, 'id:', id.value);
    const res = await workflow(taskId.value, 2, id.value);
    console.log('降噪转写响应:', res);
    if (res.data.code === 200) {
      ElMessage.success('降噪转写任务已启动');
    } else {
      ElMessage.error(res.data.msg || '启动失败');
    }
  } catch (error) {
    console.error('启动降噪转写失败:', error);
    ElMessage.error('启动降噪转写失败');
  }
};

// WaveSurfer 相关
const wavesurfer = ref(null);
const wavesurfer1 = ref(null);
const wavesurferContainer = ref(null);
const wavesurferContainer1 = ref(null);

// 初始化第一个页面的 WaveSurfer
const initWaveSurfer = () => {
  if (wavesurfer.value) {
    wavesurfer.value.destroy();
  }

  // 显示加载状态
  const loading = ElLoading.service({
    target: wavesurferContainer.value,
    text: '音轨加载中...',
    background: 'rgba(255, 255, 255, 0.9)',
    customClass: 'wave-loading'
  });

  // 确保容器存在
  if (!wavesurferContainer.value) {
    console.error('音轨容器不存在');
    loading.close();
    ElMessage.error('音轨容器不存在');
    return;
  }

  console.log('初始化音轨，音频URL:', getFileInfo.value?.url);
  
  wavesurfer.value = WaveSurfer.create({
    container: wavesurferContainer.value,
    waveColor: '#409EFF',
    progressColor: '#67C23A',
    cursorColor: '#409EFF',
    barWidth: 2,
    barRadius: 3,
    cursorWidth: 1,
    height: 60,
    barGap: 3,
    normalize: true,
    backend: 'WebAudio',
    responsive: true,
    fillParent: true
  });

  // 加载音频
  if (getFileInfo.value?.url) {
    console.log('正在加载音频URL:', getFileInfo.value.url);
    wavesurfer.value.load(getFileInfo.value.url);
  } else {
    console.error('没有找到音频URL');
    loading.close();
    ElMessage.error('没有找到音频文件');
    return;
  }

  // 监听加载完成事件
  wavesurfer.value.on('ready', () => {
    loading.close();
    // 设置初始音量
    wavesurfer.value.setVolume(currentVolume.value);
    console.log('音轨加载完成，总时长：', wavesurfer.value.getDuration());
  });

  // 监听加载错误事件
  wavesurfer.value.on('error', (err) => {
    console.error('音轨加载错误:', err);
    loading.close();
    ElMessage.error('音轨加载失败');
  });

  // 同步视频/音频播放
  if (isVideoFile.value && videoRef.value) {
    // 视频播放时同步音轨
    videoRef.value.addEventListener('play', () => {
      wavesurfer.value?.play();
    });

    // 视频暂停时同步音轨
    videoRef.value.addEventListener('pause', () => {
      wavesurfer.value?.pause();
    });

    // 视频进度变化时同步音轨
    videoRef.value.addEventListener('timeupdate', () => {
      if (videoRef.value && wavesurfer.value) {
        const progress = videoRef.value.currentTime / videoRef.value.duration;
        wavesurfer.value.seekTo(progress);
      }
    });

    // 视频点击时同步音轨
    videoRef.value.addEventListener('seeked', () => {
      if (videoRef.value && wavesurfer.value) {
        const progress = videoRef.value.currentTime / videoRef.value.duration;
        wavesurfer.value.seekTo(progress);
      }
    });

    // 音轨点击时同步视频
    wavesurfer.value.on('seek', (progress) => {
  if (videoRef.value) {
        const seekTime = videoRef.value.duration * progress;
        videoRef.value.currentTime = seekTime;
        if (!videoRef.value.paused) {
    videoRef.value.play();
  }
      }
    });

    // 音轨点击事件
    wavesurfer.value.on('click', (progress) => {
  if (videoRef.value) {
        const seekTime = videoRef.value.duration * progress;
        videoRef.value.currentTime = seekTime;
        if (!videoRef.value.paused) {
          videoRef.value.play();
        }
      }
    });
  } else if (!isVideoFile.value && audioRef.value) {
    // 音频播放时同步音轨
    audioRef.value.addEventListener('play', () => {
      wavesurfer.value?.play();
    });

    // 音频暂停时同步音轨
    audioRef.value.addEventListener('pause', () => {
      wavesurfer.value?.pause();
    });

    // 音频进度变化时同步音轨
    audioRef.value.addEventListener('timeupdate', () => {
      if (audioRef.value && wavesurfer.value) {
        const progress = audioRef.value.currentTime / audioRef.value.duration;
        wavesurfer.value.seekTo(progress);
      }
    });

    // 音频点击时同步音轨
    audioRef.value.addEventListener('seeked', () => {
      if (audioRef.value && wavesurfer.value) {
        const progress = audioRef.value.currentTime / audioRef.value.duration;
        wavesurfer.value.seekTo(progress);
      }
    });

    // 音轨点击时同步音频
    wavesurfer.value.on('seek', (progress) => {
      if (audioRef.value) {
        const seekTime = audioRef.value.duration * progress;
        audioRef.value.currentTime = seekTime;
        if (!audioRef.value.paused) {
          audioRef.value.play();
        }
      }
    });

    // 音轨点击事件
    wavesurfer.value.on('click', (progress) => {
      if (audioRef.value) {
        const seekTime = audioRef.value.duration * progress;
        audioRef.value.currentTime = seekTime;
        if (!audioRef.value.paused) {
          audioRef.value.play();
        }
      }
    });
  }

  // 音轨播放时同步视频/音频
  wavesurfer.value.on('play', () => {
    if (isVideoFile.value && videoRef.value) {
      videoRef.value.play();
    } else if (!isVideoFile.value && audioRef.value) {
      audioRef.value.play();
    }
  });

  // 音轨暂停时同步视频/音频
  wavesurfer.value.on('pause', () => {
    if (isVideoFile.value && videoRef.value) {
    videoRef.value.pause();
    } else if (!isVideoFile.value && audioRef.value) {
      audioRef.value.pause();
    }
  });
};

// 初始化第二个页面的 WaveSurfer
const initWaveSurfer1 = () => {
  if (wavesurfer1.value) {
    wavesurfer1.value.destroy();
  }

  // 显示加载状态
  const loading = ElLoading.service({
    target: wavesurferContainer1.value,
    text: '音轨加载中...',
    background: 'rgba(255, 255, 255, 0.9)',
    customClass: 'wave-loading'
  });

  // 确保容器存在
  if (!wavesurferContainer1.value) {
    console.error('音轨容器不存在');
    loading.close();
    ElMessage.error('音轨容器不存在');
    return;
  }

  console.log('初始化第二个页面音轨，音频URL:', getFileInfo.value?.url);
  
  wavesurfer1.value = WaveSurfer.create({
    container: wavesurferContainer1.value,
    waveColor: '#409EFF',
    progressColor: '#67C23A',
    cursorColor: '#409EFF',
    barWidth: 2,
    barRadius: 3,
    cursorWidth: 1,
    height: 60,
    barGap: 3,
    normalize: true,
    backend: 'WebAudio',
    fillParent: true
  });

  // 加载音频
  if (getFileInfo.value?.url) {
    console.log('正在加载第二个页面音频URL:', getFileInfo.value.url);
    wavesurfer1.value.load(getFileInfo.value.url);
  } else {
    console.error('没有找到音频URL');
    loading.close();
    ElMessage.error('没有找到音频文件');
    return;
  }

  // 监听加载完成事件
  wavesurfer1.value.on('ready', () => {
    loading.close();
    // 设置初始音量
    wavesurfer1.value.setVolume(currentVolume1.value);
    console.log('第二个页面音轨加载完成，总时长：', wavesurfer1.value.getDuration());
  });

  // 监听加载错误事件
  wavesurfer1.value.on('error', (err) => {
    console.error('第二个页面音轨加载错误:', err);
    loading.close();
    ElMessage.error('音轨加载失败');
  });

  // 同步视频/音频播放
  if (isVideoFile.value && videoRef1.value) {
    // 视频播放时同步音轨
    videoRef1.value.addEventListener('play', () => {
      wavesurfer1.value?.play();
    });

    // 视频暂停时同步音轨
    videoRef1.value.addEventListener('pause', () => {
      wavesurfer1.value?.pause();
    });

    // 视频进度变化时同步音轨
    videoRef1.value.addEventListener('timeupdate', () => {
      if (videoRef1.value && wavesurfer1.value) {
        const progress = videoRef1.value.currentTime / videoRef1.value.duration;
        wavesurfer1.value.seekTo(progress);
      }
    });

    // 视频点击时同步音轨
    videoRef1.value.addEventListener('seeked', () => {
      if (videoRef1.value && wavesurfer1.value) {
        const progress = videoRef1.value.currentTime / videoRef1.value.duration;
        wavesurfer1.value.seekTo(progress);
      }
    });

    // 音轨点击时同步视频
    wavesurfer1.value.on('seek', (progress) => {
  if (videoRef1.value) {
        const seekTime = videoRef1.value.duration * progress;
        videoRef1.value.currentTime = seekTime;
        if (!videoRef1.value.paused) {
    videoRef1.value.play();
  }
      }
    });

    // 音轨点击事件
    wavesurfer1.value.on('click', (progress) => {
  if (videoRef1.value) {
        const seekTime = videoRef1.value.duration * progress;
        videoRef1.value.currentTime = seekTime;
        if (!videoRef1.value.paused) {
          videoRef1.value.play();
        }
      }
    });
  } else if (!isVideoFile.value && audioRef1.value) {
    // 音频播放时同步音轨
    audioRef1.value.addEventListener('play', () => {
      wavesurfer1.value?.play();
    });

    // 音频暂停时同步音轨
    audioRef1.value.addEventListener('pause', () => {
      wavesurfer1.value?.pause();
    });

    // 音频进度变化时同步音轨
    audioRef1.value.addEventListener('timeupdate', () => {
      if (audioRef1.value && wavesurfer1.value) {
        const progress = audioRef1.value.currentTime / audioRef1.value.duration;
        wavesurfer1.value.seekTo(progress);
      }
    });

    // 音频点击时同步音轨
    audioRef1.value.addEventListener('seeked', () => {
      if (audioRef1.value && wavesurfer1.value) {
        const progress = audioRef1.value.currentTime / audioRef1.value.duration;
        wavesurfer1.value.seekTo(progress);
      }
    });

    // 音轨点击时同步音频
    wavesurfer1.value.on('seek', (progress) => {
      if (audioRef1.value) {
        const seekTime = audioRef1.value.duration * progress;
        audioRef1.value.currentTime = seekTime;
        if (!audioRef1.value.paused) {
          audioRef1.value.play();
        }
      }
    });

    // 音轨点击事件
    wavesurfer1.value.on('click', (progress) => {
      if (audioRef1.value) {
        const seekTime = audioRef1.value.duration * progress;
        audioRef1.value.currentTime = seekTime;
        if (!audioRef1.value.paused) {
          audioRef1.value.play();
        }
      }
    });
  }

  // 音轨播放时同步视频/音频
  wavesurfer1.value.on('play', () => {
    if (isVideoFile.value && videoRef1.value) {
      videoRef1.value.play();
    } else if (!isVideoFile.value && audioRef1.value) {
      audioRef1.value.play();
    }
  });

  // 音轨暂停时同步视频/音频
  wavesurfer1.value.on('pause', () => {
    if (isVideoFile.value && videoRef1.value) {
      videoRef1.value.pause();
    } else if (!isVideoFile.value && audioRef1.value) {
      audioRef1.value.pause();
    }
  });
};

const getFileInfo = ref({
  filename: '',
  size: '',
  effective_voice: '',
  total_voice: '',
  language: '',
  is_extract: '',
  is_clear: '',
  url: '',
  voice_url: '',
  text_info:'',
  clear_url:'',
});
const isVideoFile = ref(false);
const audioRef = ref(null);
const audioRef1 = ref(null);

// 在组件挂载时获取并解析文件信息
onMounted(async () => {
  const query = route.query;
  id.value = query.id as string;
  taskId.value = query.taskId as string;
  const index = query.index;
  const res = await getTaskFileDetail(id.value);
  console.log('文件详情响应:', res);
  getFileInfo.value = res.data.data;
  
  if (res.data.code == 200) {
    // 根据文件扩展名判断是否为视频文件
    const fileExtension = getFileInfo.value.filename?.split('.').pop()?.toLowerCase();
    console.log('文件扩展名:', fileExtension);
    isVideoFile.value = ['mp4', 'webm', 'ogg', 'mov'].includes(fileExtension || '');
    console.log('是否为视频文件:', isVideoFile.value);
    
    isVideoLoading.value = true;
    isVideoLoading1.value = true;
    videoLoadError.value = false;
    videoLoadError1.value = false;

    // 初始化两个页面的 WaveSurfer
    nextTick(() => {
      console.log('开始初始化音轨');
      initWaveSurfer();
      initWaveSurfer1();
    });
  }
  
  // 设置默认标签页
  if (index == "1") {
    activeName.value = "first";
  } else if (index == "2") {
    activeName.value = "second";
  } else if (index == "3") {
    activeName.value = "third";
  } else {
    activeName.value = "first";
  }
  
  // 解析传递的文件信息
  if (query.fileInfo) {
    try {
      fileInfo.value = JSON.parse(query.fileInfo as string);
      console.log('解析后的文件信息:', fileInfo.value);
      
      // 更新视频URL并判断文件类型
      if (fileInfo.value && fileInfo.value.url) {
        videoUrl.value = fileInfo.value.url;
        // 根据文件扩展名判断是否为视频文件
        const fileExtension = fileInfo.value.filename?.split('.').pop()?.toLowerCase();
        console.log('文件扩展名:', fileExtension);
        isVideoFile.value = ['mp4', 'webm', 'ogg', 'mov'].includes(fileExtension || '');
        console.log('是否为视频文件:', isVideoFile.value);
        
        isVideoLoading.value = true;
        isVideoLoading1.value = true;
        videoLoadError.value = false;
        videoLoadError1.value = false;

        // 初始化两个页面的 WaveSurfer
        nextTick(() => {
          initWaveSurfer();
          initWaveSurfer1();
        });
      }
    } catch (error) {
      console.error('解析文件信息失败：', error);
    }
  }
});

const videoUrl = ref('')
const videoRef = ref(null);
const videoRef1 = ref(null);
const currentVolume = ref(1); // 音量范围是 0~1
const currentVolume1 = ref(1); // 音量范围是 0~1

const isVideoLoading = ref(true);
const videoLoadError = ref(false);

const isVideoLoading1 = ref(true);
const videoLoadError1 = ref(false);

const handleVideoLoadStart = () => {
  isVideoLoading.value = true;
  videoLoadError.value = false;
};

const handleVideoLoaded = () => {
  isVideoLoading.value = false;
  videoLoadError.value = false;
};

const handleVideoError = () => {
  isVideoLoading.value = false;
  videoLoadError.value = true;
};

const handleVideoLoadStart1 = () => {
  isVideoLoading1.value = true;
  videoLoadError1.value = false;
};

const handleVideoLoaded1 = () => {
  isVideoLoading1.value = false;
  videoLoadError1.value = false;
};

const handleVideoError1 = () => {
  isVideoLoading1.value = false;
  videoLoadError1.value = true;
};

const retryLoadVideo = () => {
  if (isVideoFile.value && videoRef.value) {
    isVideoLoading.value = true;
    videoLoadError.value = false;
    videoRef.value.load();
  } else if (!isVideoFile.value && audioRef.value) {
    isVideoLoading.value = true;
    videoLoadError.value = false;
    audioRef.value.load();
  }
};

const retryLoadVideo1 = () => {
  if (isVideoFile.value && videoRef1.value) {
    isVideoLoading1.value = true;
    videoLoadError1.value = false;
    videoRef1.value.load();
  } else if (!isVideoFile.value && audioRef1.value) {
    isVideoLoading1.value = true;
    videoLoadError1.value = false;
    audioRef1.value.load();
  }
};

const playVideo = () => {
  if (isVideoFile.value && videoRef.value) {
    // console.log('点击播放按钮，视频当前时间：', videoRef.value.currentTime);
    videoRef.value.play();
  } else if (!isVideoFile.value && audioRef.value) {
    // console.log('点击播放按钮，音频当前时间：', audioRef.value.currentTime);
    audioRef.value.play();
  }
};

const pauseVideo = () => {
  if (isVideoFile.value && videoRef.value) {
    // console.log('点击暂停按钮，视频当前时间：', videoRef.value.currentTime);
    videoRef.value.pause();
  } else if (!isVideoFile.value && audioRef.value) {
    // console.log('点击暂停按钮，音频当前时间：', audioRef.value.currentTime);
    audioRef.value.pause();
  }
};

const playVideo1 = () => {
  if (videoRef1.value) {
    videoRef1.value.play();
  }
};

const pauseVideo1 = () => {
  if (videoRef1.value) {
    videoRef1.value.pause();
  }
};

const increaseVolume = () => {
  if (isVideoFile.value && videoRef.value) {
    currentVolume.value = Math.min(currentVolume.value + 0.1, 1);
    videoRef.value.volume = currentVolume.value;
    wavesurfer.value?.setVolume(currentVolume.value);
  } else if (!isVideoFile.value && audioRef.value) {
    currentVolume.value = Math.min(currentVolume.value + 0.1, 1);
    audioRef.value.volume = currentVolume.value;
    wavesurfer.value?.setVolume(currentVolume.value);
  }
};

const decreaseVolume = () => {
  if (isVideoFile.value && videoRef.value) {
    currentVolume.value = Math.max(currentVolume.value - 0.1, 0);
    videoRef.value.volume = currentVolume.value;
    wavesurfer.value?.setVolume(currentVolume.value);
  } else if (!isVideoFile.value && audioRef.value) {
    currentVolume.value = Math.max(currentVolume.value - 0.1, 0);
    audioRef.value.volume = currentVolume.value;
    wavesurfer.value?.setVolume(currentVolume.value);
  }
};

const increaseVolume1 = () => {
  if (isVideoFile.value && videoRef1.value) {
    currentVolume1.value = Math.min(currentVolume1.value + 0.1, 1);
    videoRef1.value.volume = currentVolume1.value;
    wavesurfer1.value?.setVolume(currentVolume1.value);
  } else if (!isVideoFile.value && audioRef1.value) {
    currentVolume1.value = Math.min(currentVolume1.value + 0.1, 1);
    audioRef1.value.volume = currentVolume1.value;
    wavesurfer1.value?.setVolume(currentVolume1.value);
  }
};

const decreaseVolume1 = () => {
  if (isVideoFile.value && videoRef1.value) {
    currentVolume1.value = Math.max(currentVolume1.value - 0.1, 0);
    videoRef1.value.volume = currentVolume1.value;
    wavesurfer1.value?.setVolume(currentVolume1.value);
  } else if (!isVideoFile.value && audioRef1.value) {
    currentVolume1.value = Math.max(currentVolume1.value - 0.1, 0);
    audioRef1.value.volume = currentVolume1.value;
    wavesurfer1.value?.setVolume(currentVolume1.value);
  }
};

const handleClick = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
    
    // 如果是文件降噪页面
    if (tab.props.name === "second") {
      // 判断clear_url是否为空
      if (!getFileInfo.value.clear_url) {
        ElMessage.warning('该文件尚未降噪，即将跳转到降噪转写页面');
        // 3秒后跳转到降噪转写页面
        setTimeout(() => {
          activeName.value = "third";
        }, 3000);
        return;
      }
    }
  });
};

const handleClick1 = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
  });
};

const handleClick2 = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
  });
};

const handleClick3 = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
  });
};

const buttons = [{ type: "primary", text: "⬅ 返回任务操作" }] as const;
const dialogVisible = ref(false);

const fileList = ref<UploadUserFile[]>([
  {
    name: "element-plus-logo.svg",
    url: "https://element-plus.org/images/element-plus-logo.svg",
  },
  {
    name: "element-plus-logo2.svg",
    url: "https://element-plus.org/images/element-plus-logo.svg",
  },
]);

const handleRemove: UploadProps["onRemove"] = (file, uploadFiles) => {
  console.log(file, uploadFiles);
};

const handlePreview: UploadProps["onPreview"] = (uploadFile) => {
  console.log(uploadFile);
};

const handleExceed: UploadProps["onExceed"] = (files, uploadFiles) => {
  ElMessage.warning(
    `The limit is 3, you selected ${files.length} files this time, add up to ${files.length + uploadFiles.length
    } totally`
  );
};

const beforeRemove: UploadProps["beforeRemove"] = (uploadFile, uploadFiles) => {
  return ElMessageBox.confirm(
    `Cancel the transfer of ${uploadFile.name} ?`
  ).then(
    () => true,
    () => false
  );
};
const detection = () => {
  // console.log("启动检测");
  activeName.value = "second";
};
const transcription = () => {
  // console.log("启动转写");
  activeName.value = "third";
};

// 在组件卸载前清理事件监听
onBeforeUnmount(() => {
  // 清理第一个页面的 WaveSurfer
  if (wavesurfer.value) {
    wavesurfer.value.destroy();
    wavesurfer.value = null;
  }

  // 清理第二个页面的 WaveSurfer
  if (wavesurfer1.value) {
    wavesurfer1.value.destroy();
    wavesurfer1.value = null;
  }

  // 清理视频事件监听
  if (videoRef.value) {
    videoRef.value.removeEventListener('play', () => {});
    videoRef.value.removeEventListener('pause', () => {});
    videoRef.value.removeEventListener('timeupdate', () => {});
    videoRef.value.removeEventListener('seeked', () => {});
  }

  // 清理音频事件监听
  if (audioRef.value) {
    audioRef.value.removeEventListener('play', () => {});
    audioRef.value.removeEventListener('pause', () => {});
    audioRef.value.removeEventListener('timeupdate', () => {});
    audioRef.value.removeEventListener('seeked', () => {});
  }

  // 清理第二个页面的视频事件监听
  if (videoRef1.value) {
    videoRef1.value.removeEventListener('play', () => {});
    videoRef1.value.removeEventListener('pause', () => {});
    videoRef1.value.removeEventListener('timeupdate', () => {});
    videoRef1.value.removeEventListener('seeked', () => {});
  }

  // 清理第二个页面的音频事件监听
  if (audioRef1.value) {
    audioRef1.value.removeEventListener('play', () => {});
    audioRef1.value.removeEventListener('pause', () => {});
    audioRef1.value.removeEventListener('timeupdate', () => {});
    audioRef1.value.removeEventListener('seeked', () => {});
  }
});

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  const milliseconds = Math.floor((seconds % 1) * 1000);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
};

const downloadText = (type) => {
  if (!getFileInfo.value.text_info) {
    ElMessage.warning('暂无转写内容');
    return;
  }

  try {
    const segments = JSON.parse(getFileInfo.value.text_info).segments;
    let content = '';
    const filename = getFileInfo.value.filename.split('.')[0];

    switch (type) {
      case 'withTimestamp':
        content = segments.map(segment => 
          `[${formatTime(segment.start)} - ${formatTime(segment.end)}]${segment.speaker ? ` (${segment.speaker})` : ''} ${segment.text}`
        ).join('\n');
        downloadFile(content, `${filename}_带时间戳.txt`, 'text/plain');
        break;

      case 'withoutTimestamp':
        content = segments.map(segment => 
          `${segment.speaker ? `(${segment.speaker}) ` : ''}${segment.text}`
        ).join('\n');
        downloadFile(content, `${filename}_无时间戳.txt`, 'text/plain');
        break;

      case 'word':
        content = segments.map(segment => 
          `[${formatTime(segment.start)} - ${formatTime(segment.end)}]${segment.speaker ? ` (${segment.speaker})` : ''} ${segment.text}`
        ).join('\n');
        downloadWord(content, `${filename}_转写文本.docx`);
        break;
    }
  } catch (error) {
    console.error('下载转写文本失败:', error);
    ElMessage.error('下载失败');
  }
};

const downloadFile = (content, filename, type) => {
  const blob = new Blob([content], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const downloadWord = async (content, filename) => {
  try {
    // 创建 Word 文档的基本结构
    const docx = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" 
            xmlns:w="urn:schemas-microsoft-com:office:word" 
            xmlns="http://www.w3.org/TR/REC-html40">
      <head>
        <meta charset="utf-8">
        <title>转写文本</title>
        <style>
          body { font-family: "Microsoft YaHei", sans-serif; }
          p { margin: 0; line-height: 1.5; }
        </style>
      </head>
      <body>
        ${content.split('\n').map(line => `<p>${line}</p>`).join('')}
      </body>
      </html>
    `;

    // 将内容转换为 Word 文档
    const blob = new Blob([docx], { type: 'application/msword' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('下载Word文档失败:', error);
    ElMessage.error('下载Word文档失败');
  }
};

const downloadClearFile = () => {
  if (!getFileInfo.value.clear_url) {
    ElMessage.warning('请先进行文件降噪处理');
    return;
  }

  try {
    const link = document.createElement('a');
    link.href = getFileInfo.value.clear_url;
    link.download = `${getFileInfo.value.filename.split('.')[0]}_降噪文件.${getFileInfo.value.filename.split('.').pop()}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('下载降噪文件失败:', error);
    ElMessage.error('下载失败');
  }
};
</script>

<style scoped lang="scss">
.fileViewBox {
  position: relative;
  width: 100%;
  height: 100%;
}

.demo-tabs1,
.demo-tabs2,
.demo-tabs3,
.demo-tabs4 {
  width: 96%;
  margin: 0 auto;
  border: 1px solid #dcdfe6;
  padding: 20px;
  border-radius: 10px;
  box-sizing: border-box;

  :deep(.el-tabs__content) {
    padding: 0;
  }
}

.demo-tabs1>.el-tabs__content {
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}

.demo-tabs {
  box-sizing: border-box;
}

.demo-tabs>.el-tabs__content {
  padding: 20px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}

.el-tabs {
  background-color: #fff;
  height: 100%;
}

::v-deep(.el-tabs__item.is-active) {
  border-bottom-color: #e4e7ed !important;
}

.returnBtn {
  position: absolute;
  right: 10px;
  top: 5px;
}

.taskInfoUl {
  list-style: none;
  display: flex;
  justify-content: space-between;
  padding: 0;
  margin: 0;
  width: 100%;

  li {
    flex: 1;
    text-align: center;
    padding: 0 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
    color: #606266;
    font-size: 14px;

    &:not(:last-child) {
      border-right: 1px solid #EBEEF5;
    }
  }
}

.fileBox,
.fileBox2,
.fileBox3,
.fileBox4 {
  width: 96%;
  height: 600px;
  border-radius: 10px;
  box-sizing: border-box;
  border: 1px solid #dcdfe6;
  display: flex;
  padding: 20px;
  margin: 0 auto;
  margin-top: 20px;
  overflow-y: scroll;

  .fileOriginal {
    width: 96%;
    margin: 0 auto;

    // background-color: red;
    .fileOriginalTitle {
      font-weight: bolder;
      margin-bottom: 10px;
    }

    .fileOriginalContent {
      width: 90%;
      margin: 0 auto;
      // height: 300px;
      overflow-y: scroll;
      border: 1px solid #dcdfe6;
      border-radius: 10px;
      padding: 10px;
      box-sizing: border-box;

      .videoBox {
        width: 50%;
        margin: 0 auto;
        position: relative;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;

        video {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }

        .video-loading,
        .video-error {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.9);
          z-index: 1;

          .loading-icon {
            font-size: 32px;
            color: #409EFF;
            animation: rotating 2s linear infinite;
          }

          .error-icon {
            font-size: 32px;
            color: #F56C6C;
            margin-bottom: 10px;
          }

          span {
            margin: 10px 0;
            color: #606266;
          }
        }
      }

      .audioTrack {
        width: 50%;
        height: 80px;
        border: 1px solid #dcdfe6;
        border-radius: 10px;
        padding: 10px;
        box-sizing: border-box;
        margin: 10px auto;
        background: #fff;
        position: relative;
        overflow: hidden;

        :deep(.wave-loading) {
          .el-loading-spinner {
            top: 50%;
            margin-top: -15px;
          }

          .el-loading-text {
            font-size: 14px;
            margin-top: 5px;
          }
        }

        :deep(.wavesurfer-container) {
          position: relative;
          width: 100%;
          height: 100%;

          wave {
            width: 100% !important;
            height: 60px !important;
          }
        }
      }

      .audioAction {
        width: 50%;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
      }
    }
  }

  .fileReduction {
    width: 96%;
    margin: 0 auto;

    // background-color: red;
    .fileReductionTop {
      display: flex;
      justify-content: space-between;
      font-weight: bolder;

      .fileReductionTitle {
        font-weight: bolder;
        margin-bottom: 10px;
      }

      .fileReductionDownload {
        color: #409eff !important;
        cursor: pointer;

        .example-showcase .el-dropdown-link {
          cursor: pointer;
          color: #409eff;
          display: flex;
          align-items: center;
        }
      }
    }

    .fileReductionContent {
      width: 90%;
      margin: 0 auto;
      // height: 300px;
      overflow-y: scroll;
      border: 1px solid #dcdfe6;
      border-radius: 10px;
      padding: 10px;
      box-sizing: border-box;

      .videoBox {
        width: 50%;
        margin: 0 auto;
        position: relative;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;

        video {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }

        .video-loading,
        .video-error {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.9);
          z-index: 1;

          .loading-icon {
            font-size: 32px;
            color: #409EFF;
            animation: rotating 2s linear infinite;
          }

          .error-icon {
            font-size: 32px;
            color: #F56C6C;
            margin-bottom: 10px;
          }

          span {
            margin: 10px 0;
            color: #606266;
          }
        }
      }

      .audioTrack {
        width: 50%;
        height: 80px;
        border: 1px solid #dcdfe6;
        border-radius: 10px;
        padding: 10px;
        box-sizing: border-box;
        margin: 10px auto;
        background: #fff;
        position: relative;
        overflow: hidden;

        :deep(.wave-loading) {
          .el-loading-spinner {
            top: 50%;
            margin-top: -15px;
          }

          .el-loading-text {
            font-size: 14px;
            margin-top: 5px;
          }
        }

        :deep(.wavesurfer-container) {
          position: relative;
          width: 100%;
          height: 100%;

          wave {
            width: 100% !important;
            height: 60px !important;
          }
        }
      }

      .audioAction {
        width: 50%;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
      }
    }
  }

  .transcriptionPreview {
    width: 96%;
    margin: 20px auto;

    .transcriptionPreviewTop {
      display: flex;
      justify-content: space-between;
      font-weight: bolder;

      .transcriptionPreviewTitle {
        margin: 20px 0;
      }

      .transcriptionPreviewDownload {
        color: #409eff !important;
        cursor: pointer;

        .example-showcase .el-dropdown-link {
          cursor: pointer;
          color: #409eff;
          display: flex;
          align-items: center;
        }
      }
    }

    .transcriptionPreviewContent {
      width: 100%;
      border-radius: 10px;
      box-sizing: border-box;
      border: 1px solid #dcdfe6;
      padding: 10px;
      height: 600px;
      overflow-y: auto;

      .lyrics-container {
        padding: 10px;
      }

      .lyric-line {
        margin-bottom: 8px;
        line-height: 1.5;
        display: flex;
        align-items: flex-start;
        gap: 8px;

        .time-stamp {
          color: #666;
          font-size: 14px;
          white-space: nowrap;
        }

        .speaker {
          color: #409EFF;
          font-size: 14px;
          white-space: nowrap;
        }

        .lyric-text {
          color: #333;
          font-size: 14px;
          flex: 1;
        }
      }

      .no-content {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        color: #909399;
        font-size: 14px;
      }
    }
  }
}

.fileBox,
.fileBox2,
.fileBox3,
.fileBox4 {
  display: block;

  .item {
    margin: 20px 0;
  }
}

.fileBox3 {
  height: 180px;
  border: none;
}

::v-deep(.el-upload-list) {
  //  background-color: red;
  position: fixed;
  left: 11%;
  top: 35%;
  width: 49%;
}

.el-upload-list__item {
  margin: 10px 0;
}

.demo-progress .el-progress--line {
  margin-bottom: 15px;
  max-width: 600px;
}

.operationBottom {
  margin-top: 20px;
  display: flex;

  .btn {
    margin-right: 10px;
  }
}

.dialog-footer {
  position: absolute;
  bottom: 10px;
  right: 10px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
.clearbtn{
  margin: 20px;
}
</style>
