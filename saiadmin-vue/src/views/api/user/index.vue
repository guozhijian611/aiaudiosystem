<template>
  <div class="ma-content-block">
    <sa-table ref="crudRef" :options="options" :columns="columns" :searchForm="searchForm">
      <!-- 搜索区 tableSearch -->
      <template #tableSearch>
        <a-col :sm="8" :xs="24">
          <a-form-item label="用户ID" field="id">
            <a-input v-model="searchForm.id" placeholder="请输入用户ID" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="用户名" field="username">
            <a-input v-model="searchForm.username" placeholder="请输入用户名" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="昵称" field="nickname">
            <a-input v-model="searchForm.nickname" placeholder="请输入昵称" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="角色" field="role">
            <sa-select v-model="searchForm.role" dict="user_type" placeholder="请选择角色" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="状态" field="status">
            <a-input v-model="searchForm.status" placeholder="请输入状态" allow-clear />
          </a-form-item>
        </a-col>
      </template>

      <!-- Table 自定义渲染 -->
      <template #status="{ record }">
        <sa-switch v-model="record.status" @change="changeStatus($event, record.id)"></sa-switch>
      </template>
    </sa-table>

    <!-- 编辑表单 -->
    <edit-form ref="editRef" @success="refresh" />

    <!-- 查看表单 -->
    <view-form ref="viewRef" @success="refresh" />
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'
import EditForm from './edit.vue'
import ViewForm from './view.vue'
import api from '../api/user'

// 引用定义
const crudRef = ref()
const editRef = ref()
const viewRef = ref()

// 搜索表单
const searchForm = ref({
  id: '',
  username: '',
  nickname: '',
  role: '',
  status: '',
})

// 修改状态
const changeStatus = async (status, id) => {
  const response = await api.changeStatus({ id, status })
  if (response.code === 200) {
    Message.success(response.message)
    crudRef.value.refresh()
  }
}

// SaTable 基础配置
const options = reactive({
  api: api.getPageList,
  rowSelection: { showCheckedAll: true },
  view: {
    show: true,
    auth: ['/api/User/read'],
    func: async (record) => {
      viewRef.value?.open(record)
    },
  },
  add: {
    show: true,
    auth: ['/api/User/save'],
    func: async () => {
      editRef.value?.open()
    },
  },
  edit: {
    show: true,
    auth: ['/api/User/update'],
    func: async (record) => {
      editRef.value?.open('edit')
      editRef.value?.setFormData(record)
    },
  },
  delete: {
    show: true,
    auth: ['/api/User/destroy'],
    func: async (params) => {
      const resp = await api.destroy(params)
      if (resp.code === 200) {
        Message.success(`删除成功！`)
        crudRef.value?.refresh()
      }
    },
  },
  export: { show: true, url: '/api/User/export', auth: ['/api/User/export'] },
})

// SaTable 列配置
const columns = reactive([
  { title:'用户ID', dataIndex:'id', width:180, sortable:{ sortDirections:['ascend', 'descend'] } },
  { title:'用户名', dataIndex:'username', width:180 },
  { title:'昵称', dataIndex:'nickname', width:180 },
  { title:'角色', dataIndex:'role', type:'dict', dict:'user_type', width:180 },
  { title:'状态', dataIndex:'status', width:180 },
  { title:'创建时间', dataIndex:'create_time', width:180 },
  { title:'更新时间', dataIndex:'update_time', width:180 },
])

// 页面数据初始化
const initPage = async () => {}

// SaTable 数据请求
const refresh = async () => {
  crudRef.value?.refresh()
}

// 页面加载完成执行
onMounted(async () => {
  initPage()
  refresh()
})
</script>
