<template>
  <div class="ma-content-block">
    <sa-table ref="crudRef" :options="options" :columns="columns" :searchForm="searchForm">
      <!-- 搜索区 tableSearch -->
      <template #tableSearch>
        <a-col :sm="8" :xs="24">
          <a-form-item label="ID" field="id">
            <a-input v-model="searchForm.id" placeholder="请输入ID" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="任务详情ID" field="task_id">
            <a-input v-model="searchForm.task_id" placeholder="请输入任务详情ID" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="日志信息" field="log">
            <a-input v-model="searchForm.log" placeholder="请输入日志信息" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="任务类型" field="task_type">
            <a-input v-model="searchForm.task_type" placeholder="请输入任务类型" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="状态" field="status">
            <a-input v-model="searchForm.status" placeholder="请输入状态" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="创建时间" field="create_time">
            <a-range-picker v-model="searchForm.create_time" :show-time="true" mode="date" />
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
import api from '../api/ailog'

// 引用定义
const crudRef = ref()
const editRef = ref()
const viewRef = ref()

// 搜索表单
const searchForm = ref({
  id: '',
  task_id: '',
  log: '',
  task_type: '',
  status: '',
  create_time: [],
})


// SaTable 基础配置
const options = reactive({
  api: api.getPageList,
  rowSelection: { showCheckedAll: true },
  view: {
    show: true,
    auth: ['/api/AiLog/read'],
    func: async (record) => {
      viewRef.value?.open(record)
    },
  },
  add: {
    show: true,
    auth: ['/api/AiLog/save'],
    func: async () => {
      editRef.value?.open()
    },
  },
  edit: {
    show: true,
    auth: ['/api/AiLog/update'],
    func: async (record) => {
      editRef.value?.open('edit')
      editRef.value?.setFormData(record)
    },
  },
  delete: {
    show: true,
    auth: ['/api/AiLog/destroy'],
    func: async (params) => {
      const resp = await api.destroy(params)
      if (resp.code === 200) {
        Message.success(`删除成功！`)
        crudRef.value?.refresh()
      }
    },
  },
})

// SaTable 列配置
const columns = reactive([
  { title:'ID', dataIndex:'id', width:180, sortable:{ sortDirections:['ascend', 'descend'] } },
  { title:'任务详情ID', dataIndex:'task_id', width:180 },
  { title:'日志信息', dataIndex:'log', width:180 },
  { title:'任务类型', dataIndex:'task_type', width:180 },
  { title:'状态', dataIndex:'status', width:180 },
  { title:'消息', dataIndex:'message', width:180 },
  { title:'创建时间', dataIndex:'create_time', width:180 },
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
