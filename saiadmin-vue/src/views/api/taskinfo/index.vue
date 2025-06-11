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
          <a-form-item label="任务ID" field="tid">
            <a-select v-model="searchForm.tid" :options="[]" placeholder="请选择任务ID" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="原始文件名" field="filename">
            <a-input v-model="searchForm.filename" placeholder="请输入原始文件名" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="文件类型" field="type">
            <sa-select v-model="searchForm.type" dict="file_type" placeholder="请选择文件类型" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="是否提取音频" field="is_extract">
            <sa-select v-model="searchForm.is_extract" dict="yes_or_no" placeholder="请选择是否提取音频" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="是否降噪" field="is_clear">
            <sa-select v-model="searchForm.is_clear" dict="yes_or_no" placeholder="请选择是否降噪" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="是否快速识别" field="fast_status">
            <sa-select v-model="searchForm.fast_status" dict="yes_or_no" placeholder="请选择是否快速识别" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="是否转写" field="transcribe_status">
            <sa-select v-model="searchForm.transcribe_status" dict="yes_or_no" placeholder="请选择是否转写" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="有效语音时长" field="effective_voice">
            <a-input v-model="searchForm.effective_voice" placeholder="请输入有效语音时长" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="音频总时长" field="total_voice">
            <a-input v-model="searchForm.total_voice" placeholder="请输入音频总时长" allow-clear />
          </a-form-item>
        </a-col>
        <a-col :sm="8" :xs="24">
          <a-form-item label="语言类型" field="language">
            <a-input v-model="searchForm.language" placeholder="请输入语言类型" allow-clear />
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
import api from '../api/taskinfo'

// 引用定义
const crudRef = ref()
const editRef = ref()
const viewRef = ref()

// 搜索表单
const searchForm = ref({
  id: '',
  tid: '',
  filename: '',
  type: '',
  is_extract: '',
  is_clear: '',
  fast_status: '',
  transcribe_status: '',
  effective_voice: '',
  total_voice: '',
  language: '',
})


// SaTable 基础配置
const options = reactive({
  api: api.getPageList,
  rowSelection: { showCheckedAll: true },
  view: {
    show: true,
    auth: ['/api/TaskInfo/read'],
    func: async (record) => {
      viewRef.value?.open(record)
    },
  },
  add: {
    show: true,
    auth: ['/api/TaskInfo/save'],
    func: async () => {
      editRef.value?.open()
    },
  },
  edit: {
    show: true,
    auth: ['/api/TaskInfo/update'],
    func: async (record) => {
      editRef.value?.open('edit')
      editRef.value?.setFormData(record)
    },
  },
  delete: {
    show: true,
    auth: ['/api/TaskInfo/destroy'],
    func: async (params) => {
      const resp = await api.destroy(params)
      if (resp.code === 200) {
        Message.success(`删除成功！`)
        crudRef.value?.refresh()
      }
    },
  },
  export: { show: true, url: '/api/TaskInfo/export', auth: ['/api/TaskInfo/export'] },
})

// SaTable 列配置
const columns = reactive([
  { title:'ID', dataIndex:'id', width:180, sortable:{ sortDirections:['ascend', 'descend'] } },
  { title:'任务ID', dataIndex:'tid', width:180 },
  { title:'原始文件名', dataIndex:'filename', width:180 },
  { title:'文件大小', dataIndex:'size', width:180 },
  { title:'文件类型', dataIndex:'type', type:'dict', dict:'file_type', width:180 },
  { title:'原始文件 URL', dataIndex:'url', width:180 },
  { title:'提取音频后的 URL', dataIndex:'voice_url', width:180 },
  { title:'降噪后的 URL', dataIndex:'clear_url', width:180 },
  { title:'是否提取音频', dataIndex:'is_extract', type:'dict', dict:'yes_or_no', width:180 },
  { title:'是否降噪', dataIndex:'is_clear', type:'dict', dict:'yes_or_no', width:180 },
  { title:'是否快速识别', dataIndex:'fast_status', type:'dict', dict:'yes_or_no', width:180 },
  { title:'是否转写', dataIndex:'transcribe_status', type:'dict', dict:'yes_or_no', width:180 },
  { title:'有效语音时长', dataIndex:'effective_voice', width:180 },
  { title:'音频总时长', dataIndex:'total_voice', width:180, sortable:{ sortDirections:['ascend', 'descend'] } },
  { title:'语言类型', dataIndex:'language', width:180 },
  { title:'失败重试次数', dataIndex:'retry_count', width:180 },
  { title:'当前处理阶段', dataIndex:'step', type:'dict', dict:'step_type', width:180 },
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
