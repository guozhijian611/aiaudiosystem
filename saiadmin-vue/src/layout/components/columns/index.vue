<template>
  <a-layout-content class="layout flex justify-between">
    <div id="layout-columns-left-panel" class="ma-ui-menu layout-columns-left-panel hidden lg:flex justify-between">
      <ma-columns-menu />
    </div>

    <div class="layout-columns-right-panel flex flex-col" :style="`width: calc(100% - ${containerWidth}px)`" >

      <ma-columns-header class="ma-ui-header" />
      <ma-worker-area />

    </div>
  </a-layout-content>
</template>
<script setup>
  import { onMounted, ref } from 'vue'
  import ResizeObserver from 'resize-observer-polyfill'
  import MaColumnsHeader from './ma-columns-header.vue'
  import MaColumnsMenu from './ma-columns-menu.vue'

  import MaWorkerArea from '../ma-workerArea.vue'

  const containerWidth = ref(0)

  onMounted(() => {
    const dom = document.getElementById('layout-columns-left-panel')
    const robserver = new ResizeObserver( entries => {
      for (const entry of entries) {
        // 可以通过 判断 entry.target得知当前改变的 Element，分别进行处理。
        switch(entry.target){
          case dom :
            containerWidth.value = entry.contentRect.width
          break
        }
      }
    })
    robserver.observe(dom)
  })
</script>
