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
          <a-form-item label="用户名" field="username">
            <a-input v-model="formData.username" placeholder="请输入用户名" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="密码" field="password">
            <a-input v-model="formData.password" placeholder="请输入密码" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="昵称" field="nickname">
            <a-input v-model="formData.nickname" placeholder="请输入昵称" />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="角色" field="role">
            <sa-select v-model="formData.role" dict="user_type" placeholder="请选择角色" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :span="24">
          <a-form-item label="状态" field="status">
            <sa-switch v-model="formData.status" />
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
import api from '../api/user'

const emit = defineEmits(['success'])
// 引用定义
const visible = ref(false)
const loading = ref(false)
const formRef = ref()
const mode = ref('')
const optionData = reactive({
})

let title = computed(() => {
  return '用户管理' + (mode.value == 'add' ? '-新增' : '-编辑')
})

// 表单初始值
const initialFormData = {
  id: null,
  username: '',
  password: '',
  nickname: '',
  role: 2,
  status: 1,
}

// 表单信息
const formData = reactive({ ...initialFormData })

// 验证规则
const rules = {
  username: [{ required: true, message: '用户名必需填写' }],
  password: [{ required: true, message: '密码必需填写' }],
  nickname: [{ required: true, message: '昵称必需填写' }],
  role: [{ required: true, message: '角色必需填写' }],
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
