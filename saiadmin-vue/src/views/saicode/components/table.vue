<template>
    <a-modal fullscreen v-model:visible="visible" title="选择数据模型" @ok="handleChoose" unmount-on-close>
        <div class="ma-content-block lg:flex justify-between">
            <div class="lg:w-8/12 w-full">
                <sa-table ref="crudRef" :options="options" :columns="columns" :searchForm="searchForm"
                    @selection-change="selectionChange" @resetSearch="handleReset">
                    <!-- 搜索表单 start -->
                    <template #tableSearch>
                        <a-col :span="8">
                            <a-form-item field="table_name" label="表名称">
                                <a-input v-model="searchForm.table_name" placeholder="请输入数据表名称" allow-clear />
                            </a-form-item>
                        </a-col>
                    </template>
                    <!-- 搜索表单 end -->
                    <!-- Table 自定义渲染 start -->
                    <template #tpl_category="{ record }">
                        <a-tag v-if="record.tpl_category == 'single'" color="green">单表CRUD</a-tag>
                        <a-tag v-else color="red">树表CRUD</a-tag>
                    </template>
                    <!-- Table 自定义渲染 end -->
                </sa-table>
            </div>
            <div class="lg:w-4/12 pt-4 pl-2 pr-2">
                <a-card title="配置区域">
                    <a-space direction="vertical" fill>
                        <a-space>
                            <span class="config-label">字段Label：</span>
                            <a-select
                                :style="{width:'320px'}"
                                v-model="config.field_label"
                                :field-names="{ label: 'column_comment', value: 'column_name' }"
                                :options="optionData || []">
                                <template #label="{ data }">
                                    <span>{{data?.column_comment}} - {{data?.column_name}}</span>
                                </template>
                                <template #option="{ data }">
                                    <span>{{data?.column_comment}} - {{data?.column_name}}</span>
                                </template>
                            </a-select>
                        </a-space>
                        <a-space>
                            <span class="config-label">字段Value：</span>
                            <a-select
                                :style="{width:'320px'}"
                                v-model="config.field_value"
                                :field-names="{ label: 'column_comment', value: 'column_name' }"
                                :options="optionData || []">
                                <template #label="{ data }">
                                    <span>{{data?.column_comment}} - {{data?.column_name}}</span>
                                </template>
                                <template #option="{ data }">
                                    <span>{{data?.column_comment}} - {{data?.column_name}}</span>
                                </template>
                            </a-select>
                        </a-space>
                        <a-space>
                            <span class="config-label">请求地址：</span>
                            <a-input v-model="config.url" :style="{width:'320px'}"></a-input>
                        </a-space>
                    </a-space>
                </a-card>
            </div>
        </div>
    </a-modal>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from "vue";
import { findIndex } from 'lodash'
import api from "../api/table";

const emit = defineEmits(['choose'])

const visible = ref(false)
const crudRef = ref()

const optionData = ref([])

const config = reactive({
    field_label: '',
    field_value: '',
    url: ''
})

const handleReset = () => {
    config.field_label = ''
    config.field_value = ''
    config.url = ''

    optionData.value = []
}

const handleChoose = () => {
    emit('choose', config)
    visible.value = false
}

// 搜索表单
const searchForm = ref({
    table_name: '',
})

const options = reactive({
  pk: 'id',
  api: api.getPageList,
  height: '650px',
  rowSelection: { type: 'radio' },
  operationColumn: false,
})

const columns = reactive([
  { title: '表名称', dataIndex: 'table_name', width: 160, align: 'left' },
  { title: '表描述', dataIndex: 'table_comment', width: 120, align: 'left' },
  { title: '应用类型', dataIndex: 'template', width: 100 },
  { title: '应用名称', dataIndex: 'namespace', width: 100 },
  { title: '类名称', dataIndex: 'class_name', width: 150 },
  { title: '类型', dataIndex: 'tpl_category', width: 110 },
  { title: '数据源', dataIndex: 'source', width: 100 },
])

const selectionChange = async (selection) => {
    config.field_label = ''
    config.field_value = ''
    config.url = ''
    if (selection.length > 0) {
        const resp = await api.getTableColumns({ table_id: selection[0] })
        optionData.value = resp.data
        const tableData = crudRef.value?.getTableData()
        const index = findIndex(tableData, (item) => item.id === selection[0])
        const row = tableData[index]
        let path = ''
        if (row['template'] == 'plugin') {
            path = '/app/' + row['namespace'] + (row['package_name'] != "" ? "/" + row['package_name'] : "") + '/' + row['class_name'];
        } else {
            path = '/' + row['namespace'] + (row['package_name'] != "" ? "/" + row['package_name'] : "") + '/'+ row['class_name'];
        }
        path = path + '/index'
        if (row['tpl_category'] != 'tree') {
            path = path + '?saiType=all'
        }
        config.url = path
    } else {
        optionData.value = []
    }
}

const open = async () => {
    visible.value = true;
    await nextTick()
    initPage()
}

const initPage = () => {
    crudRef.value?.refresh()
}

defineExpose({ open })
</script>

<style scoped>
.config-label {
  width: 100px;
  text-align: end;
}
.config-label-field {
  width: 180px;
  text-align: end;
}
</style>