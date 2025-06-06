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
        <a-descriptions-item label="用户ID">
          <div v-text="formData?.id"></div>
        </a-descriptions-item>
        <a-descriptions-item label="用户名">
          <div v-text="formData?.username"></div>
        </a-descriptions-item>
        <a-descriptions-item label="昵称">
          <div v-text="formData?.nickname"></div>
        </a-descriptions-item>
        <a-descriptions-item label="角色">
          <sa-dict :value="formData?.role" dict="user_type" render="span" />
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <div v-text="formData?.status"></div>
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
import api from '../api/user'

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
