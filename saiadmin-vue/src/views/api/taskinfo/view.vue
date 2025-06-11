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
        <a-descriptions-item label="任务ID">
          <div v-text="formData?.tid"></div>
        </a-descriptions-item>
        <a-descriptions-item label="原始文件名">
          <div v-text="formData?.filename"></div>
        </a-descriptions-item>
        <a-descriptions-item label="文件大小">
          <div v-text="formData?.size"></div>
        </a-descriptions-item>
        <a-descriptions-item label="文件类型">
          <sa-dict :value="formData?.type" dict="file_type" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="原始文件 URL">
          <div v-text="formData?.url"></div>
        </a-descriptions-item>
        <a-descriptions-item label="提取音频后的 URL">
          <div v-text="formData?.voice_url"></div>
        </a-descriptions-item>
        <a-descriptions-item label="降噪后的 URL">
          <div v-text="formData?.clear_url"></div>
        </a-descriptions-item>
        <a-descriptions-item label="是否提取音频">
          <sa-dict :value="formData?.is_extract" dict="yes_or_no" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="是否降噪">
          <sa-dict :value="formData?.is_clear" dict="yes_or_no" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="是否快速识别">
          <sa-dict :value="formData?.fast_status" dict="yes_or_no" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="是否转写">
          <sa-dict :value="formData?.transcribe_status" dict="yes_or_no" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="有效语音时长">
          <div v-text="formData?.effective_voice"></div>
        </a-descriptions-item>
        <a-descriptions-item label="音频总时长">
          <div v-text="formData?.total_voice"></div>
        </a-descriptions-item>
        <a-descriptions-item label="语言类型">
          <div v-text="formData?.language"></div>
        </a-descriptions-item>
        <a-descriptions-item label="转写内容">
          <div v-text="formData?.text_info"></div>
        </a-descriptions-item>
        <a-descriptions-item label="任务错误信息">
          <div v-text="formData?.error_msg"></div>
        </a-descriptions-item>
        <a-descriptions-item label="失败重试次数">
          <div v-text="formData?.retry_count"></div>
        </a-descriptions-item>
        <a-descriptions-item label="当前处理阶段">
          <sa-dict :value="formData?.step" dict="step_type" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          <div v-text="formData?.create_time"></div>
        </a-descriptions-item>
        <a-descriptions-item label="更新时间">
          <div v-text="formData?.update_time"></div>
        </a-descriptions-item>
      </a-descriptions>
    </a-spin>
    <!-- 详情 end -->
  </component>
</template>

<script setup>
import { ref, reactive } from 'vue'
import tool from '@/utils/tool'
import api from '../api/taskinfo'

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
