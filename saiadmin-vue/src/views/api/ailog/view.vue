<template>
  <component
    is="a-drawer"
    v-model:visible="visible"
    :width="tool.getDevice() === 'mobile' ? '100%' : '60%'"
    title="查看详情"
    :footer="false">
    <!-- 详情 start -->
    <a-spin :loading="loading" class="w-full">
      <a-descriptions :column="1" bordered>
        <a-descriptions-item label="ID">
          <div v-text="formData?.id"></div>
        </a-descriptions-item>
        <a-descriptions-item label="任务详情ID">
          <div v-text="formData?.task_id"></div>
        </a-descriptions-item>
        <a-descriptions-item label="日志信息">
          <div v-text="formData?.log"></div>
        </a-descriptions-item>
        <a-descriptions-item label="任务类型">
          <sa-dict :value="formData?.task_type" dict="node_type" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <sa-dict :value="formData?.status" dict="log_status" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="消息">
          <div v-text="formData?.message"></div>
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          <div v-text="formData?.create_time"></div>
        </a-descriptions-item>
      </a-descriptions>
    </a-spin>
    <!-- 详情 end -->
  </component>
</template>

<script setup>
import { ref, reactive } from 'vue'
import tool from '@/utils/tool'
import api from '../api/ailog'

const emit = defineEmits(['success'])

// 引用定义
const rowData = ref()
const formData = ref()
const visible = ref(false)
const loading = ref(false)

// 打开弹框
const open = async (record) => {
  rowData.value = record
  formData.value = {}
  visible.value = true
  await initPage()
}

// 初始化页面数据
const initPage = async () => {
  loading.value = true
  const resp = await api.read(rowData.value?.id)
  if (resp.code === 200) {
    formData.value = resp.data
  }
  loading.value = false
}

defineExpose({ open })
</script>
