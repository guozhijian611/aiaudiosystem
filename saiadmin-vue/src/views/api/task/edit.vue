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
          <a-form-item label="用户 id" field="uid">
            <a-select
              v-model="formData.uid"
              :field-names="{ label: '', value: '' }"
              :options="optionData.uid"
              placeholder="请选择用户 id"
              allow-clear
            />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="任务编号" field="number">
            <a-input v-model="formData.number" placeholder="请输入任务编号" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="任务昵称" field="name">
            <a-input v-model="formData.name" placeholder="请输入任务昵称" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="状态" field="status">
            <sa-select v-model="formData.status" dict="task_type" placeholder="请选择状态" allow-clear />
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
import api from '../api/task'

const emit = defineEmits(['success'])
// 引用定义
const visible = ref(false)
const loading = ref(false)
const formRef = ref()
const mode = ref('')
const optionData = reactive({
  uid: [],
})

let title = computed(() => {
  return '任务管理' + (mode.value == 'add' ? '-新增' : '-编辑')
})

// 表单初始值
const initialFormData = {
  id: null,
  uid: null,
  number: '',
  name: '',
  status: 1,
}

// 表单信息
const formData = reactive({ ...initialFormData })

// 验证规则
const rules = {
  uid: [{ required: true, message: '用户 id必需填写' }],
  number: [{ required: true, message: '任务编号必需填写' }],
  name: [{ required: true, message: '任务昵称必需填写' }],
  status: [{ required: true, message: '状态必需填写' }],
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
  const resp_uid = await commonApi.commonGet('/api/User/index?saiType=all')
  optionData.uid = resp_uid.data
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
