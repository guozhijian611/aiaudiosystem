<template>
  <a-modal width="1000px" v-model:visible="visible" :footer="false">
    <template #title>预览代码</template>
    <a-tabs v-model:active-key="activeTab">
      <a-tab-pane v-for="item in previewCode" :key="item.name" :title="item.tab_name">
        <div class="relative">
          <ma-code-editor v-model="item.code" readonly miniMap :language="item.lang" :height="600" />
          <a-button class="copy-button" type="primary" @click="copyCode(item.code)"><icon-copy /> 复制</a-button>
        </div>
      </a-tab-pane>
    </a-tabs>
  </a-modal>
</template>

<script setup>
import { ref } from 'vue'
import generate from '@/api/tool/generate'
import { copy } from '@/utils/common'
import { Message } from '@arco-design/web-vue'
import MaCodeEditor from '@/components/ma-codeEditor/index.vue'

const activeTab = ref('controller')
const visible = ref(false)
const previewCode = ref([])

const open = async (id) => {
  const response = await generate.preview(id)
  if (response.code === 200) {
    previewCode.value = response.data
    visible.value = true
  }
}

const copyCode = async (code) => {
  await copy(code)
}

defineExpose({ open })
</script>

<style scoped>
.copy-button {
  position: absolute;
  right: 15px;
  top: 0px;
  z-index: 999;
}
</style>
