<template>
  <div class="audio-wave-container">
    <div ref="waveformRef" class="waveform"></div>
    <div class="controls">
      <button @click="togglePlay">{{ isPlaying ? '暂停' : '播放' }}</button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import WaveSurfer from 'wavesurfer.js'

const waveformRef = ref<HTMLDivElement | null>(null)
const wavesurfer = ref<WaveSurfer | null>(null)
const isPlaying = ref(false)

// props
const props = defineProps<{
  audioUrl: string
  bindVideo?: HTMLVideoElement // 可选：绑定的视频对象
}>()

onMounted(() => {
  if (!waveformRef.value) return

  wavesurfer.value = WaveSurfer.create({
    container: waveformRef.value,
    waveColor: '#ddd',
    progressColor: '#4CAF50',
    cursorColor: '#f00',
    height: 80,
    responsive: true
  })

  wavesurfer.value.load(props.audioUrl)

  // 监听播放状态
  wavesurfer.value.on('play', () => {
    isPlaying.value = true
    props.bindVideo?.play()
  })

  wavesurfer.value.on('pause', () => {
    isPlaying.value = false
    props.bindVideo?.pause()
  })

  // 拖动时同步视频时间
  wavesurfer.value.on('seek', (progress: number) => {
    if (props.bindVideo) {
      const duration = props.bindVideo.duration
      props.bindVideo.currentTime = duration * progress
    }
  })
})

onBeforeUnmount(() => {
  wavesurfer.value?.destroy()
})

function togglePlay() {
  wavesurfer.value?.playPause()
}
</script>

<style scoped>
.audio-wave-container {
  width: 100%;
}
.waveform {
  width: 100%;
  height: 80px;
}
.controls {
  margin-top: 10px;
}
</style>
