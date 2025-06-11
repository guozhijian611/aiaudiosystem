<template>
  <component
    is="a-modal"
    :width="tool.getDevice() === 'mobile' ? '100%' : '600px'"
    v-model:visible="visible"
    :title="title"
    :mask-closable="false"
    :ok-loading="loading"
    @cancel="close"
    @before-ok="submit">
    <!-- 表单信息 start -->
    <a-form ref="formRef" :model="formData" :rules="rules" :auto-label-width="true">
      <a-row :gutter="10">
        <a-col :span="24">
          <a-form-item label="任务ID" field="tid">
            <a-select
              v-model="formData.tid"
              :field-names="{ label: '', value: '' }"
              :options="optionData.tid"
              placeholder="请选择任务ID"
              allow-clear
            />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="原始文件名" field="filename">
            <a-input v-model="formData.filename" placeholder="请输入原始文件名" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="文件大小" field="size">
            <a-input v-model="formData.size" placeholder="请输入文件大小" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="文件类型" field="type">
            <sa-select v-model="formData.type" dict="file_type" placeholder="请选择文件类型" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="原始文件 URL" field="url">
            <a-input v-model="formData.url" placeholder="请输入原始文件 URL" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="提取音频后的 URL" field="voice_url">
            <a-input v-model="formData.voice_url" placeholder="请输入提取音频后的 URL" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="降噪后的 URL" field="clear_url">
            <a-input v-model="formData.clear_url" placeholder="请输入降噪后的 URL" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="是否提取音频" field="is_extract">
            <sa-select v-model="formData.is_extract" dict="yes_or_no" placeholder="请选择是否提取音频" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="是否降噪" field="is_clear">
            <sa-select v-model="formData.is_clear" dict="yes_or_no" placeholder="请选择是否降噪" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="是否快速识别" field="fast_status">
            <sa-select v-model="formData.fast_status" dict="yes_or_no" placeholder="请选择是否快速识别" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="是否转写" field="transcribe_status">
            <sa-select v-model="formData.transcribe_status" dict="yes_or_no" placeholder="请选择是否转写" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="有效语音时长" field="effective_voice">
            <a-input v-model="formData.effective_voice" placeholder="请输入有效语音时长" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="音频总时长" field="total_voice">
            <a-input v-model="formData.total_voice" placeholder="请输入音频总时长" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="语言类型" field="language">
            <a-input v-model="formData.language" placeholder="请输入语言类型" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="转写内容" field="text_info">
            <a-textarea v-model="formData.text_info" placeholder="请输入转写内容" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="任务错误信息" field="error_msg">
            <a-textarea v-model="formData.error_msg" placeholder="请输入任务错误信息" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="失败重试次数" field="retry_count">
            <a-input v-model="formData.retry_count" placeholder="请输入失败重试次数" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="当前处理阶段" field="step">
            <sa-select v-model="formData.step" dict="step_type" placeholder="请选择当前处理阶段" allow-clear />
          </a-form-item>
        </a-col>
      </a-row>
    </a-form>
    <!-- 表单信息 end -->
  </component>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import tool from '@/utils/tool'
import commonApi from '@/api/common'
import { Message, Modal } from '@arco-design/web-vue'
import api from '../api/taskinfo'

const emit = defineEmits(['success'])
// 引用定义
const visible = ref(false)
const loading = ref(false)
const formRef = ref()
const mode = ref('')
const optionData = reactive({
  tid: [],
})

let title = computed(() => {
  return '任务详情' + (mode.value == 'add' ? '-新增' : '-编辑')
})

// 表单初始值
const initialFormData = {
  id: null,
  tid: null,
  filename: '',
  size: '',
  type: 1,
  url: '',
  voice_url: '',
  clear_url: '',
  is_extract: 2,
  is_clear: 2,
  fast_status: 2,
  transcribe_status: 2,
  effective_voice: '',
  total_voice: '',
  language: '',
  text_info: '',
  error_msg: '',
  retry_count: null,
  step: null,
}

// 表单信息
const formData = reactive({ ...initialFormData })

// 验证规则
const rules = {
  tid: [{ required: true, message: '任务ID必需填写' }],
  type: [{ required: true, message: '文件类型必需填写' }],
  is_extract: [{ required: true, message: '是否提取音频必需填写' }],
  is_clear: [{ required: true, message: '是否降噪必需填写' }],
  fast_status: [{ required: true, message: '是否快速识别必需填写' }],
  transcribe_status: [{ required: true, message: '是否转写必需填写' }],
  retry_count: [{ required: true, message: '失败重试次数必需填写' }],
}

// 打开弹框
const open = async (type = 'add') => {
  mode.value = type
  // 重置表单数据
  Object.assign(formData, initialFormData)
  formRef.value.clearValidate()
  visible.value = true
  await initPage()
}

// 初始化页面数据
const initPage = async () => {
  const resp_tid = await commonApi.commonGet('/api/Task/index?saiType=all')
  optionData.tid = resp_tid.data
}

// 设置数据
const setFormData = async (data) => {
  for (const key in formData) {
    if (data[key] != null && data[key] != undefined) {
      formData[key] = data[key]
    }
  }
}

// 数据保存
const submit = async (done) => {
  const validate = await formRef.value?.validate()
  if (!validate) {
    loading.value = true
    let data = { ...formData }
    let result = {}
    if (mode.value === 'add') {
      // 添加数据
      data.id = undefined
      result = await api.save(data)
    } else {
      // 修改数据
      result = await api.update(data.id, data)
    }
    if (result.code === 200) {
      Message.success('操作成功')
      emit('success')
      done(true)
    }
    // 防止连续点击提交
    setTimeout(() => {
      loading.value = false
    }, 500)
  }
  done(false)
}

// 关闭弹窗
const close = () => (visible.value = false)

defineExpose({ open, setFormData })
</script>
