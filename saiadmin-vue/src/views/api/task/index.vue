<template>
  <div class="ma-content-block">
    <sa-table ref="crudRef" :options="options" :columns="columns" :searchForm="searchForm">
      <!-- 搜索区 tableSearch -->
      <template #tableSearch>
        <a-col :sm="8" :xs="24">
          <a-form-item label="id" field="id">
            <a-input v-model="searchForm.id" placeholder="请输入id" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="用户 id" field="uid">
            <a-select v-model="searchForm.uid" :options="[]" placeholder="请选择用户 id" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="任务编号" field="number">
            <a-input v-model="searchForm.number" placeholder="请输入任务编号" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="任务昵称" field="name">
            <a-input v-model="searchForm.name" placeholder="请输入任务昵称" allow-clear />
          </a-form-item>
        </a-col>
      </template>

      <!-- Table 自定义渲染 -->
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
import api from '../api/task'

// 引用定义
const crudRef = ref()
const editRef = ref()
const viewRef = ref()

// 搜索表单
const searchForm = ref({
  id: '',
  uid: '',
  number: '',
  name: '',
})


// SaTable 基础配置
const options = reactive({
  api: api.getPageList,
  rowSelection: { showCheckedAll: true },
  view: {
    show: true,
    auth: ['/api/Task/read'],
    func: async (record) => {
      viewRef.value?.open(record)
    },
  },
  add: {
    show: true,
    auth: ['/api/Task/save'],
    func: async () => {
      editRef.value?.open()
    },
  },
  edit: {
    show: true,
    auth: ['/api/Task/update'],
    func: async (record) => {
      editRef.value?.open('edit')
      editRef.value?.setFormData(record)
    },
  },
  delete: {
    show: true,
    auth: ['/api/Task/destroy'],
    func: async (params) => {
      const resp = await api.destroy(params)
      if (resp.code === 200) {
        Message.success(`删除成功！`)
        crudRef.value?.refresh()
      }
    },
  },
  export: { show: true, url: '/api/Task/export', auth: ['/api/Task/export'] },
})

// SaTable 列配置
const columns = reactive([
  { title:'id', dataIndex:'id', width:180, sortable:{ sortDirections:['ascend', 'descend'] } },
  { title:'用户 id', dataIndex:'uid', width:180, sortable:{ sortDirections:['ascend', 'descend'] } },
  { title:'任务编号', dataIndex:'number', width:180 },
  { title:'任务昵称', dataIndex:'name', width:180 },
  { title:'状态', dataIndex:'status', type:'dict', dict:'task_type', width:180 },
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
