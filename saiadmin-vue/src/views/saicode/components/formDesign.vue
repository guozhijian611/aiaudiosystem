<template>
  <div>
    <a-modal fullscreen v-model:visible="visible" :footer="false" unmount-on-close>
      <template #title>
        <a-space>
          <template #split>
            <a-divider direction="vertical" />
          </template>
          <span>表单设计</span>
          <a-button type="primary" @click="handleSave">保存设计 </a-button>
        </a-space>
      </template>
      <div class="design-page">
        <div class="design-left">
          <a-card title="设计区域">
            <div
              :style="{
                border: '1px dashed #DDDDDE',
                padding: '20px',
                margin: '0 auto',
                width: formConfig.is_full ? '100%' : formConfig.form_width + 'px',
              }">
              <a-form ref="formRef" :model="formData" :auto-label-width="true">
                <div :gutter="16" id="sai-form-design" ref="formDesign" class="arco-row">
                  <template v-for="(item, index) in formColumn">
                    <div
                      v-if="item.insert"
                      :data-id="item.id"
                      class="arco-col"
                      :class="'arco-col-' + (item.span ?? formConfig.form_span)"
                      :style="{ border: checkItem.id === item.id ? '1px solid #165dff' : '' }"
                      @click="handleFocus(item)">
                      <div class="drag-item">
                        <a-form-item :label="item.column_comment" :required="item.is_required == 2">
                          <a-input-password v-if="item.view_type === 'password'" />
                          <a-textarea v-else-if="item.view_type === 'textarea'" v-model="item.default_value" />
                          <a-input-number
                            v-else-if="item.view_type === 'inputNumber'"
                            v-model="item.default_value"
                            :min="item.options.min"
                            :max="item.options.max"
                            :step="item.options.step" />
                          <a-input-tag v-else-if="item.view_type === 'inputTag'" />
                          <sa-switch v-else-if="item.view_type === 'switch'" />
                          <a-slider
                            v-else-if="item.view_type === 'slider'"
                            v-model="item.default_value"
                            :min="item.options.min"
                            :max="item.options.max"
                            :step="item.options.step" />
                          <a-select
                            v-else-if="item.view_type === 'select'"
                            :field-names="{ label: item.options.field_label || 'label', value: item.options.field_value || 'value' }"
                            :options="(item.option && item.option[item.column_name]) || []" />
                          <sa-select v-model="item.default_value" v-else-if="item.view_type === 'saSelect'" :dict="item.dict_type" />
                          <a-tree-select
                            v-else-if="item.view_type === 'treeSelect'"
                            :field-names="{ key: item.options.field_value || 'value', title: item.options.field_label || 'label', icon: 'customIcon' }"
                            :data="(item.option && item.option[item.column_name]) || []" />
                          <sa-radio v-else-if="item.view_type === 'radio'" :dict="item.dict_type" v-model="item.default_value" />
                          <sa-checkbox v-else-if="item.view_type === 'checkbox'" :dict="item.dict_type" />
                          <a-date-picker
                            v-else-if="item.view_type === 'date'"
                            v-model="item.default_value"
                            :mode="item.options.mode"
                            :show-time="item.options.showTime" />
                          <a-time-picker v-else-if="item.view_type === 'time'" v-model="item.default_value" />
                          <a-rate v-else-if="item.view_type === 'rate'" v-model="item.default_value" />
                          <a-cascader
                            v-else-if="item.view_type === 'cascader'"
                            :check-strictly="item.options.check_strictly || false"
                            :field-names="{ label: item.options.field_label || 'label', value: item.options.field_value || 'value' }"
                            :options="(item.option && item.option[item.column_name]) || []" />
                          <sa-user v-else-if="item.view_type === 'userSelect'" :isEcho="true" />
                          <ma-cityLinkage
                            v-else-if="item.view_type === 'cityLinkage'"
                            v-model="item.default_value"
                            :type="item.options.type"
                            :mode="item.options.mode" />
                          <ma-editor v-else-if="item.view_type === 'editor'" :height="item.options.height" />
                          <ma-wangEditor v-else-if="item.view_type === 'wangEditor'" :height="item.options.height" />
                          <ma-codeEditor v-else-if="item.view_type === 'codeEditor'" :height="item.options.height" />
                          <sa-upload-image
                            v-else-if="item.view_type === 'uploadImage'"
                            disabled
                            :multiple="item.options?.multiple || false"
                            :limit="item.options?.limit || 1" />
                          <sa-upload-file
                            v-else-if="item.view_type === 'uploadFile'"
                            disabled
                            :multiple="item.options?.multiple || false"
                            :limit="item.options?.limit || 1" />
                          <a-input v-else v-model="item.default_value" />
                        </a-form-item>
                      </div>
                    </div>
                  </template>
                </div>
              </a-form>
            </div>
          </a-card>
        </div>
        <div class="design-right">
          <a-card title="配置区域">
            <a-space direction="vertical" fill>
              <a-divider orientation="left">页面配置</a-divider>
              <a-space>
                <span class="config-label">表单宽度：</span>
                <a-input-number v-model="formConfig.form_width" :min="300" :max="10000" />
              </a-space>
              <a-space>
                <span class="config-label">是否全屏：</span>
                <a-radio-group v-model="formConfig.is_full">
                  <a-radio :value="true">是</a-radio>
                  <a-radio :value="false">否</a-radio>
                </a-radio-group>
              </a-space>
              <a-space>
                <span class="config-label">表单类型：</span>
                <a-radio-group v-model="formConfig.component_type">
                  <a-radio :value="1">modal表单</a-radio>
                  <a-radio :value="2">drawer表单</a-radio>
                </a-radio-group>
              </a-space>
              <a-space>
                <span class="config-label">栅格：</span>
                <a-radio-group v-model="formConfig.form_span" type="button">
                  <a-radio :value="24">1列</a-radio>
                  <a-radio :value="12">2列</a-radio>
                  <a-radio :value="8">3列</a-radio>
                  <a-radio :value="6">4列</a-radio>
                </a-radio-group>
              </a-space>
            </a-space>
            <a-tabs default-active-key="1" class="mt-4">
              <a-tab-pane key="1" title="基础配置">
                <a-space direction="vertical" fill>
                  <a-divider orientation="left">表单选项</a-divider>
                  <a-space>
                    <span class="config-label">行宽：</span>
                    <a-radio-group v-model="checkItem.span" type="button">
                      <a-radio :value="24">100%</a-radio>
                      <a-radio :value="12">50%</a-radio>
                      <a-radio :value="8">33%</a-radio>
                      <a-radio :value="6">25%</a-radio>
                    </a-radio-group>
                  </a-space>
                  <a-space> <span class="config-label">标题：</span><a-input v-model="checkItem.column_comment"></a-input> </a-space>
                  <a-space> <span class="config-label">字段：</span><a-input v-model="checkItem.column_name" disabled></a-input> </a-space>
                  <a-space v-if="['inputNumber'].includes(checkItem.view_type)">
                    <span class="config-label">默认：</span><a-input-number v-model="checkItem.default_value" />
                  </a-space>
                  <a-space v-else> <span class="config-label">默认：</span><a-input v-model="checkItem.default_value" /></a-space>
                  <a-space>
                    <span class="config-label">必填：</span>
                    <a-radio-group v-model="checkItem.is_required">
                      <a-radio :value="2">是</a-radio>
                      <a-radio :value="1">否</a-radio>
                    </a-radio-group>
                  </a-space>
                  <a-divider orientation="left">控件选项</a-divider>
                  <a-alert v-if="options.tree_parent_id && checkItem.column_name === options.tree_parent_id" type="warning">
                    树表上级自动处理树形下拉框,无需配置
                  </a-alert>
                  <a-space>
                    <span class="config-label">控件：</span>
                    <a-select
                      v-model="checkItem.view_type"
                      :style="{ width: '200px' }"
                      :options="vars.viewComponent"
                      @change="handleTypeChange"></a-select>
                  </a-space>
                  <template v-if="['inputNumber', 'slider'].includes(checkItem.view_type)">
                    <a-space>
                      <span class="config-label">最小值：</span>
                      <a-input-number v-model="checkItem.options.min" />
                    </a-space>
                    <a-space>
                      <span class="config-label">最大值：</span>
                      <a-input-number v-model="checkItem.options.max" />
                    </a-space>
                    <a-space>
                      <span class="config-label">步长：</span>
                      <a-input-number v-model="checkItem.options.step" />
                    </a-space>
                  </template>
                  <a-space v-if="['cascader'].includes(checkItem.view_type)">
                    <span class="config-label">严选模式：</span>
                    <a-radio-group v-model="checkItem.options.check_strictly">
                      <a-radio :value="true">是</a-radio>
                      <a-radio :value="false">否</a-radio>
                    </a-radio-group>
                  </a-space>
                  <template v-if="['select', 'cascader', 'treeSelect'].includes(checkItem.view_type)">
                    <a-space>
                      <span class="config-label"></span>
                      <a-button type="primary" status="warning" @click="handleModal">
                        <template #icon>
                          <icon-select-all />
                        </template>
                        模型选择
                      </a-button>
                    </a-space>
                    <a-space>
                      <span class="config-label">字段Label：</span>
                      <a-input v-model="checkItem.options.field_label"></a-input>
                    </a-space>
                    <a-space>
                      <span class="config-label">字段Value：</span>
                      <a-input v-model="checkItem.options.field_value"></a-input>
                    </a-space>
                    <a-space>
                      <span class="config-label">请求地址：</span>
                      <a-input v-model="checkItem.options.url"></a-input>
                      <a-button shape="circle" @click="handleRequest">
                        <icon-play-arrow-fill />
                      </a-button>
                    </a-space>
                  </template>
                  <a-space v-if="['saSelect', 'radio', 'checkbox'].includes(checkItem.view_type)">
                    <span class="config-label">字典：</span>
                    <a-select
                      v-model="checkItem.dict_type"
                      :options="dictList"
                      allow-clear
                      :field-names="{ label: 'name', value: 'code' }"
                      placeholder="选择数据字典">
                    </a-select>
                  </a-space>
                  <template v-if="['uploadImage', 'uploadFile'].includes(checkItem.view_type)">
                    <a-space>
                      <span class="config-label">是否多选：</span>
                      <a-radio-group v-model="checkItem.options.multiple">
                        <a-radio :value="true">是</a-radio>
                        <a-radio :value="false">否</a-radio>
                      </a-radio-group>
                    </a-space>
                    <a-space>
                      <span class="config-label">上传数量：</span>
                      <a-input-number v-model="checkItem.options.limit" :min="1" />
                    </a-space>
                  </template>
                  <template v-if="['editor', 'wangEditor', 'codeEditor'].includes(checkItem.view_type)">
                    <a-space>
                      <span class="config-label">编辑高度：</span>
                      <a-input-number v-model="checkItem.options.height" />
                    </a-space>
                  </template>
                  <template v-if="['date'].includes(checkItem.view_type)">
                    <a-space>
                      <span class="config-label">类型：</span>
                      <a-select v-model="checkItem.options.mode" allow-clear>
                        <a-option value="date">日期选择器</a-option>
                        <a-option value="week">周选择器</a-option>
                        <a-option value="month">月选择器</a-option>
                        <a-option value="quarter">季度选择器</a-option>
                        <a-option value="year">年选择器</a-option>
                      </a-select>
                    </a-space>
                    <a-space>
                      <span class="config-label">显示时间：</span>
                      <a-radio-group v-model="checkItem.options.showTime">
                        <a-radio :value="true">是</a-radio>
                        <a-radio :value="false">否</a-radio>
                      </a-radio-group>
                    </a-space>
                  </template>
                  <template v-if="['cityLinkage'].includes(checkItem.view_type)">
                    <a-space>
                      <span class="config-label">组件类型：</span>
                      <a-radio-group v-model="checkItem.options.type">
                        <a-radio value="select">下拉</a-radio>
                        <a-radio value="cascader">级联</a-radio>
                      </a-radio-group>
                    </a-space>
                    <a-space>
                      <span class="config-label">返回数据：</span>
                      <a-radio-group v-model="checkItem.options.mode">
                        <a-radio value="code">省市编码</a-radio>
                        <a-radio value="name">省市名称</a-radio>
                      </a-radio-group>
                    </a-space>
                  </template>
                </a-space>
              </a-tab-pane>
              <a-tab-pane key="2" title="字段操作">
                <a-space direction="vertical" fill>
                  <a-space v-for="(item, index) in formColumn" :key="item.id">
                    <span class="config-label-field">{{ item.column_comment }}({{ item.column_name }})：</span>
                    <a-checkbox v-model="item.insert">表单显示</a-checkbox>
                  </a-space>
                </a-space>
              </a-tab-pane>
            </a-tabs>
          </a-card>
        </div>
      </div>
    </a-modal>

    <table-modal ref="tableRef" @choose="handleChooseTable" />
  </div>
  
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { isArray, isFunction, cloneDeep, isObject, isUndefined } from 'lodash'
import Sortable from 'sortablejs'
import { Message } from '@arco-design/web-vue'
import * as vars from '../js/vars.js'
import commonApi from '@/api/common'
import api from '../api/table'
import { dictType } from '@/api/system/dict'
import tableModal from './table.vue'
import { h } from 'vue'

const visible = ref(false)
const dictList = ref([])
const formData = ref({})
const formDesign = ref()
const formColumn = ref([])
const options = ref({})
const tableRef = ref()

const formConfig = reactive({
  id: undefined,
  form_width: 600,
  is_full: false,
  component_type: 1,
  form_span: 24,
})

const checkItem = ref({})

const open = async (id) => {
  const resp = await api.readTable(id)

  if (resp.data.namespace == '') {
    Message.error('请先编辑配置应用名称')
    return false
  }

  formConfig.id = id
  formConfig.form_width = resp.data.form_width
  formConfig.is_full = resp.data.is_full == 2 ? true : false
  formConfig.component_type = resp.data.component_type
  formConfig.form_span = resp.data.span

  options.value = resp.data.options

  const response = await api.getTableColumns({ table_id: id, orderBy: 'form_sort', orderType: 'asc' })

  const data = response.data.map((item, index) => {
    if (item.view_type === 'inputNumber' || item.view_type === 'slider') {
      const obj = { min: 1, max: 100, step: 1 }
      item.options = Object.assign(obj, item.options)
      item.default_value && (item.default_value = Number.parseInt(item.default_value))
    }
    if (['select', 'cascader', 'treeSelect'].includes(item.view_type)) {
      const obj = { check_strictly: false, field_label: 'label', field_value: 'value', url: '' }
      item.options = Object.assign(obj, item.options)
    }
    if (item.view_type === 'uploadImage' || item.view_type === 'uploadFile') {
      const obj = { multiple: false, limit: 3 }
      item.options = Object.assign(obj, item.options)
    }
    if (['editor', 'wangEditor', 'codeEditor'].includes(item.view_type)) {
      const obj = { height: 400 }
      item.options = Object.assign(obj, item.options)
    }
    if (item.view_type === 'date') {
      const obj = { mode: 'date', showTime: false }
      item.options = Object.assign(obj, item.options)
    }
    if (item.view_type === 'cityLinkage') {
      const obj = { type: 'select', mode: 'name' }
      item.options = Object.assign(obj, item.options)
    }
    item.insert = item.is_insert == 2 ? true : false
    item.edit = item.is_edit == 2 ? true : false
    item.form_sort = index
    return item
  })

  formColumn.value = data

  visible.value = true

  nextTick(() => {
    initPage()
  })
}

const handleFocus = (element) => {
  checkItem.value = element
  if (element.view_type === 'inputNumber' || element.view_type === 'slider') {
    const obj = { min: 1, max: 100, step: 1 }
    checkItem.value.options = Object.assign(obj, element.options)
  }
  if (['select', 'cascader', 'treeSelect'].includes(element.view_type)) {
    const obj = { check_strictly: false, field_label: 'label', field_value: 'value', url: '' }
    checkItem.value.options = Object.assign(obj, element.options)
  }
  if (element.view_type === 'upload') {
    const obj = { type: 'image', returnType: 'url', multiple: false, limit: 1 }
    checkItem.value.options = Object.assign(obj, element.options)
  }
  if (['editor', 'wangEditor', 'codeEditor'].includes(element.view_type)) {
    const obj = { height: 400 }
    checkItem.value.options = Object.assign(obj, element.options)
  }
  if (element.view_type === 'date') {
    const obj = { mode: 'date', showTime: false }
    checkItem.value.options = Object.assign(obj, element.options)
  }
  if (element.view_type === 'cityLinkage') {
    const obj = { type: 'select', mode: 'name' }
    checkItem.value.options = Object.assign(obj, element.options)
  }
}

const initPage = () => {
  const sortable = Sortable.create(formDesign.value, {
    //动画效果
    animation: 1000,
    onEnd: function (evt) {
      const dataArr = evt.target.children
      const { oldIndex, newIndex } = evt
      if (oldIndex == newIndex) {
        return
      }
      const column = cloneDeep(formColumn.value)
      let oldSort = null
      let newSort = null
      column.map((item) => {
        if (item.id == dataArr[oldIndex].dataset.id) {
          oldSort = item.form_sort
        }
        if (item.id == dataArr[newIndex].dataset.id) {
          newSort = item.form_sort
        }
      })
      formColumn.value.map((item) => {
        if (item.id == dataArr[oldIndex].dataset.id) {
          item.form_sort = newSort
        }
        if (item.id == dataArr[newIndex].dataset.id) {
          item.form_sort = oldSort
        }
      })
    },
  })
}

const handleTypeChange = async (val) => {
  if (val === 'inputNumber' || val === 'slider') {
    const obj = { min: 1, max: 100, step: 1 }
    checkItem.value.options = obj
  }
  if (['select', 'cascader', 'treeSelect'].includes(val)) {
    const obj = { check_strictly: false, field_label: 'label', field_value: 'value', url: '' }
    checkItem.value.options = obj
  }
  if (val === 'uploadImage') {
    const obj = { multiple: false, limit: 1 }
    checkItem.value.options = obj
  }
  if (val === 'uploadFile') {
    const obj = { multiple: false, limit: 1 }
    checkItem.value.options = obj
  }
  if (['editor', 'wangEditor', 'codeEditor'].includes(val)) {
    const obj = { height: 400 }
    checkItem.value.options = obj
  }
  if (val === 'date') {
    const obj = { mode: 'date', showTime: false }
    checkItem.value.options = obj
  }
  if (val === 'cityLinkage') {
    const obj = { type: 'select', mode: 'name' }
    checkItem.value.options = obj
  }
}

const handleRequest = async () => {
  if (!checkItem.value.options.url) {
    Message.error('请先配置请求地址')
    return
  }
  if (isUndefined(checkItem.value.option)) {
    checkItem.value.option = []
  }
  const { code, data } = await commonApi.commonGet(checkItem.value.options.url)
  if (code === 200) {
    if (!data.total) {
      checkItem.value.option[checkItem.value.column_name] = data
      Message.success('请求成功')
    } else {
      Message.success('接口数据返回格式错误')
    }
  }
}

const handleModal = async () => {
  tableRef.value?.open()
}

const handleChooseTable = async (config) => {
  console.log(config)
  if (checkItem.value.options) {
    checkItem.value.options.field_label = config.field_label
    checkItem.value.options.field_value = config.field_value
    checkItem.value.options.url = config.url
  }

}

const handleSave = async () => {
  const resp = await api.saveDesign({ table: formConfig, columns: formColumn.value })
  if (resp.code === 200) {
    Message.success('保存成功')
    visible.value = false
  }
}

onMounted(async () => {
  const { data } = await dictType.getPageList({ saiType: 'all' })
  dictList.value = data
})

defineExpose({ open })
</script>

<style lang="less" scoped>
.design-page {
  width: 100%;
  display: flex;

  .design-left {
    flex: 1;
  }
  .design-right {
    width: 400px;
  }
}
.drag-item {
  &:focus {
    border: 1px solid #ff0000;
  }
  :deep(label) {
    cursor: move;
  }
}
.arco-form-item {
  margin-bottom: 5px !important;
  margin-top: 5px !important;
}
.config-label {
  width: 80px;
  text-align: end;
}
.config-label-field {
  width: 180px;
  text-align: end;
}
</style>
