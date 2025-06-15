<template>
    <div>
        <TableSearch :query="query" :options="searchOpt" :search="handleSearch" />
        <div class="container">
            <TableCustom :columns="columns" :tableData="tableData" :total="page.total" row-key="index" :has-pagination="false"
                :viewFunc="handleView" :delFunc="handleDelete" :editFunc="handleEdit" :pageSize="page.size"
                :currentPage="page.index" :changeSize="changeSize" :changePage="changePage">
                <!-- <template #toolbarBtn>
                    <el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">新增</el-button>
                </template> -->
                <template #icon="{ rows }">
                    <el-icon>
                        <component :is="rows.icon"></component>
                    </el-icon>
                </template>
            </TableCustom>

        </div>
        <el-dialog :title="isEdit ? '编辑' : '新增'" v-model="visible" width="700px" destroy-on-close
            :close-on-click-modal="false" @close="closeDialog">
            <TableEdit :form-data="rowData" :options="options" :edit="isEdit" :update="updateData">
                <template #parent>
                    <el-cascader v-model="rowData.pid" :options="cascaderOptions" :props="{ checkStrictly: true }"
                        clearable />
                </template>
            </TableEdit>
        </el-dialog>
        <el-dialog title="查看详情" v-model="visible1" width="700px" destroy-on-close>
            <TableDetail :data="viewData">
                <template #icon="{ rows }">
                    <el-icon>
                        <component :is="rows.icon"></component>
                    </el-icon>
                </template>
            </TableDetail>
        </el-dialog>
    </div>
</template>

<script setup lang="ts" name="system-menu">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { CirclePlusFilled } from '@element-plus/icons-vue';
import TableCustom from '@/components/table-custom.vue';
import TableDetail from '@/components/table-detail.vue';
import { FormOption, FormOptionList } from '@/types/form-option';
import { Menus } from '@/types/menu';
import { menuData } from '@/components/menu';
import { Task } from '@/types/task';
import {getAdminTaskList} from '@/api/admin';
import {deleteTask} from '@/api/task';
import { useRouter } from "vue-router";

const router = useRouter();

// 添加假数据
// const mockTasks = [
//     {
//         id: 1,
//         uid: 1,
//         number: 'TASK-2024-001',
//         name: '视频转码任务',
//         status: '进行中',
//         update_time: '2024-03-20 10:00:00',
//         create_time: '2024-03-20 10:00:00'
//     },
//     {
//         id: 2,
//         uid: 2,
//         number: 'TASK-2024-002',
//         name: '音频降噪处理',
//         status: '已完成',
//         update_time: '2024-03-20 11:00:00',
//         create_time: '2024-03-20 11:00:00'
//     },
//     {
//         id: 3,
//         uid: 3,
//         number: 'TASK-2024-003',
//         name: '视频剪辑任务',
//         status: '等待中',
//         update_time: '2024-03-20 12:00:00',
//         create_time: '2024-03-20 12:00:00'
//     },
//     {
//         id: 4,
//         uid: 4,
//         number: 'TASK-2024-004',
//         name: '音频格式转换',
//         status: '进行中',
//         update_time: '2024-03-20 13:00:00',
//         create_time: '2024-03-20 13:00:00'
//     },
//     {
//         id: 5,
//         uid: 5,
//         number: 'TASK-2024-005',
//         name: '视频特效添加',
//         status: '已完成',
//         update_time: '2024-03-20 14:00:00',
//         create_time: '2024-03-20 14:00:00'
//     }
// ];

// 查询相关
const query = reactive({
    name: '',
});
const searchOpt = ref<FormOptionList[]>([
    { type: 'input', label: '任务名称：', prop: 'name' }
])
const handleSearch = () => {
    // 重置页码到第一页
    page.index = 1;
    // 调用获取数据方法
    getData();
};

// 表格相关
let columns = ref([
    { prop: 'id', label: 'id'},
    // { prop: 'uid', label: '序号' },
    { prop: 'username', label: '昵称' },
    { prop: 'number', label: '编号' },
    { prop: 'name', label: '名称' },
    { prop: 'status', label: '状态' },
    { prop: 'update_time', label: '更新时间' },
    { prop: 'create_time', label: '创建时间' },
    { prop: "operator", label: "操作" },
])

const getOptions = (data: any) => {
    return data.map(item => {
        const a: any = {
            label: item.title,
            value: item.id,
        }
        if (item.children) {
            a.children = getOptions(item.children)
        }
        return a
    })
}
const cascaderOptions = ref(getOptions(menuData));
const page = reactive({
  index: 1,
  size: 5,
  total: 0,
});
// 修改表格数据
const tableData = ref<Task[]>([]);
    const changePage = (val: number) => {
  page.index = val;
  getData();
};
const changeSize = (val: number) => {
  page.size = val;
  getData();
};
// 修改获取数据的方法
const getData = async () => {
    const res = await getAdminTaskList(page.index, page.size, {
        search: query.name || null
    });
    console.log(177,res);
    
    // 处理状态显示
    const processedData = res.data.data.list.map(item => ({
        ...item,
        status: getStatusText(item.status)
    }));
    
    tableData.value = processedData;
    page.total = res.data.data.total;
};

// 添加状态文字转换函数
const getStatusText = (status: number) => {
    const statusMap = {
        1: '空任务',
        2: '已检测',
        3: '已转写',
        4: '处理中',
        5: '暂停中'
    };
    return statusMap[status] || '未知状态';
};

// 添加onMounted钩子
onMounted(() => {
    getData();
});

// 新增/编辑弹窗相关
let options = ref<FormOption>({
    labelWidth: '100px',
    span: 12,
    list: [
        { type: 'input', label: '任务ID', prop: 'id'},
        { type: 'input', label: '序号', prop: 'uid'},
        { type: 'input', label: '任务编号', prop: 'number'},
        { type: 'input', label: '任务名称', prop: 'name'},
        { type: 'input', label: '任务状态', prop: 'status'},
        { type: 'input', label: '更新时间', prop: 'update_time'},
        { type: 'input', label: '创建时间', prop: 'create_time'},
        // { type: 'select', label: '任务状态', prop: 'status', required: true },
    ]
})

const visible = ref(false);
const isEdit = ref(false);
const rowData = ref<any>({});

const handleEdit = (row: Task) => {
    rowData.value = { ...row };
    isEdit.value = true;
    visible.value = true;
};

const updateData = () => {
    closeDialog();
};

const closeDialog = () => {
    visible.value = false;
    isEdit.value = false;
};

// 查看详情弹窗相关
const visible1 = ref(false);
const viewData = ref({
    row: {},
    list: []
});

const handleView = (row: Task) => {
    viewData.value.row = { ...row }
    viewData.value.list = [
        {
            prop: 'id',
            label: '任务ID',
        },
        {
            prop: 'uid',
            label: '序号',
        },
        {
            prop: 'number',
            label: '任务编号',
        },
        {
            prop: 'name',
            label: '任务名称',
        },
        {
            prop: 'status',
            label: '任务状态',
        },
        {
            prop: 'update_time',
            label: '更新时间',
        },
        {
            prop: 'create_time',
            label: '创建时间',
        }
    ]
    visible1.value = true;
};

// 删除相关
const handleDelete = async (row) => {
  try {
    const res = await deleteTask(row.id);
    if (res.data.code === 200) {
      ElMessage.success("删除成功");
      // 重新获取列表数据
      getData();
    } else if (res.data.code === 401) {
      router.push("/login");
    } else {
      ElMessage.error(res.data.message || "删除失败");
    }
  } catch (error) {
    console.error("删除任务失败:", error);
    ElMessage.error("删除失败，请稍后重试");
  }
};
</script>

<style scoped>
.container{
    height: 600px;
    overflow-y: auto;
}
</style>