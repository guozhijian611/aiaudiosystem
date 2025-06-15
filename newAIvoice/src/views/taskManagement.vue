<template>
  <div class="task-management">
    <div class="task-top">
      <div class="task-top-title">当前用户：{{ username }}</div>
      <div class="task-top-content">
        <div class="task-top-content-item">
          <svg t="1748241047256" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
            p-id="987" width="20" height="20">
            <path
              d="M832 64H192c-70.7 0-128 57.3-128 128v640c0 70.7 57.3 128 128 128h640c70.7 0 128-57.3 128-128V192c0-70.7-57.3-128-128-128z m64 768.2c0 17-6.7 33.2-18.7 45.2s-28.3 18.7-45.2 18.7H192.2c-17.1 0-33.3-6.6-45.4-18.7-12.1-12.1-18.8-28.1-18.8-45.2V192.1c0.1-35.4 28.8-64.1 64.2-64.1h639.9c17 0 33.3 6.8 45.3 18.8s18.7 28.3 18.7 45.3v640.1zM344.1 528.1c-61.9 0-112 50.1-112 112s50.1 112 112 112 112-50.1 112-112c0-61.8-50.1-112-112-112z m34 146c-16.2 16.2-41.6 18.7-60.7 5.9-19.1-12.7-26.5-37.2-17.7-58.3 8.8-21.2 31.3-33.2 53.8-28.7 22.5 4.5 38.7 24.2 38.7 47.1 0 12.8-5.1 25-14.1 34z m39.4-376.6L312.1 402.9l-41.4-41.4c-8.1-8.1-19.9-11.2-30.9-8.3-11 3-19.7 11.6-22.6 22.6-3 11 0.2 22.8 8.3 30.9l64 64c6 6 14.1 9.4 22.6 9.4 8.5 0 16.6-3.4 22.6-9.4l128-128c12.3-12.5 12.3-32.6-0.2-45.1-12.4-12.4-32.5-12.5-45-0.1z m374.6 310.6h-256c-17.7 0-32 14.3-32 32s14.3 32 32 32h256c17.7 0 32-14.3 32-32s-14.3-32-32-32z m0-256.1h-256c-17.7 0-32 14.3-32 32s14.3 32 32 32h256c17.7 0 32-14.3 32-32s-14.3-32-32-32z"
              fill="#2d8cf0" p-id="988"></path>
          </svg>
          <div>总任务数 {{ taskStatus.total }}个</div>
        </div>
        <div class="task-top-content-item">
          <svg t="1748241468327" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
            p-id="1020" width="20" height="20">
            <path
              d="M830.3 152.4H716.9v-15c0-20.4-16.6-37-37-37H347.1c-20.4 0-37 16.6-37 37v15H196.7c-28.3 0-51.4 23.1-51.4 51.4V874c0 28.3 23.1 51.4 51.4 51.4h633.6c28.3 0 51.4-23.1 51.4-51.4V203.8c0-28.3-23.1-51.4-51.4-51.4z m-470.2-2h306.8v50H360.1v-50zM831.7 874c0 0.8-0.6 1.4-1.4 1.4H196.7c-0.8 0-1.4-0.6-1.4-1.4V203.8c0-0.8 0.6-1.4 1.4-1.4h113.4v11c0 20.4 16.6 37 37 37h332.8c20.4 0 37-16.6 37-37v-11h113.4c0.8 0 1.4 0.6 1.4 1.4V874z"
              fill="#14be61" p-id="1021"></path>
            <path
              d="M713.5 702.6h-400c-13.8 0-25 11.2-25 25s11.2 25 25 25h400c13.8 0 25-11.2 25-25s-11.2-25-25-25zM472.1 606.8l35.4-35.4L656 422.9l-35.4-35.3-148.5 148.5-60.9-61-35.4 35.4 61 60.9z"
              fill="#14be61" p-id="1022"></path>
          </svg>
          <div>已完成任务数 {{ taskStatus.transcribed }}个</div>
        </div>
        <div class="task-top-content-item">
          <svg t="1748241593534" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
            p-id="1054" width="20" height="20">
            <path
              d="M362.7008 194.69824h298.7008c20.50048 0 37.2992-16.79872 37.2992-37.2992v-74.7008H586.7008v-13.70112a23.63904 23.63904 0 0 0-23.59808-23.59808H460.9024a23.63904 23.63904 0 0 0-23.59808 23.59808v13.70112H325.2992v74.7008c0 20.50048 16.79872 37.2992 37.4016 37.2992z"
              fill="#e9a745" p-id="1055"></path>
            <path
              d="M848.1024 82.69824h-74.79808V213.2992c0 30.80192-25.20064 56.09984-56.09984 56.09984H306.80064c-30.80192 0-56.09984-25.20064-56.09984-56.09984V82.69824h-74.8032c-41.00096 0-74.5984 33.60256-74.5984 74.5984v746.79808c0 41.00096 33.60256 74.5984 74.5984 74.5984h672.19968c41.00096 0 74.5984-33.60256 74.5984-74.5984V157.30176c0.00512-41.10336-33.59744-74.60352-74.59328-74.60352zM512 876.00128c-144.30208 0-261.2992-117.00224-261.2992-261.2992S367.69792 353.39776 512 353.39776s261.2992 117.00224 261.2992 261.2992-116.99712 261.30432-261.2992 261.30432z"
              fill="#e9a745" p-id="1056"></path>
            <path
              d="M661.2992 577.30048h-112V453.89824c0-19.39968-15.8976-35.3024-35.3024-35.3024h-4.096c-19.39968 0-35.3024 15.8976-35.3024 35.3024v162.80064c0 19.39968 15.8976 35.3024 35.3024 35.3024h151.5008c20.50048 0 37.2992-16.79872 37.2992-37.2992 0-20.60288-16.79872-37.4016-37.4016-37.4016z"
              fill="#e9a745" p-id="1057"></path>
          </svg>
          <div>正在处理任务数 {{ taskStatus.processing }}个</div>
        </div>
        <!-- <div class="task-top-content-item">
          <svg t="1748241688659" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
            p-id="1084" width="20" height="20">
            <path
              d="M163.2256 896.6912a98.4064 98.4064 0 0 0 89.4976 56.5248H794.368a98.4064 98.4064 0 0 0 89.4976-56.5248c16.4864-35.328 11.776-75.3664-11.776-103.6288l-233.1648-292.0448 235.52-289.664c23.552-30.6176 28.2624-70.656 11.776-103.6288A98.4064 98.4064 0 0 0 796.7488 51.2H255.0528a98.4064 98.4064 0 0 0-89.472 56.5248c-16.4864 35.328-11.776 75.3664 11.776 103.6288l235.52 289.664-235.52 289.6896c-25.9072 30.6176-30.6176 70.656-14.1312 105.984z m58.88-723.0208a39.552 39.552 0 0 1-4.7104-42.3936c7.0656-14.1312 21.1968-23.552 35.328-23.552H794.368c16.4864 0 28.2624 9.4208 35.328 23.552a39.552 39.552 0 0 1-4.7104 42.3936L561.2288 500.992l136.6016 167.2192H351.616l136.6016-167.2192L222.1056 173.6704z m0 654.72l82.432-101.2736H747.264l82.432 101.2736c9.4208 11.776 11.776 28.2624 4.7104 42.3936-7.0656 14.1312-21.1968 23.552-35.328 23.552h-541.696c-16.4608 0-28.2368-9.4208-35.328-23.552-11.776-14.1312-9.3952-30.6176 0-42.3936z"
              fill="#909399" p-id="1085"></path>
          </svg>
          <div>正在排队任务数 1个</div>
        </div> -->
        <div class="task-top-content-item">
          <svg t="1748241768615" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
            p-id="1114" width="20" height="20">
            <path
              d="M760.0128 914.0224H259.2768c-42.3936 0-68.1984-23.552-68.1984-65.7408V178.176c0-42.3936 25.8048-61.0304 68.1984-61.0304h395.0592v119.808c0 23.552 21.0944 44.6464 44.6464 44.6464h136.3968v571.392c2.2528 37.4784-30.72 61.0304-75.3664 61.0304zM233.472 46.4896C172.2368 46.4896 122.88 95.8464 122.88 154.624v714.752c0 58.7776 49.3568 108.1344 110.592 108.1344h557.056c58.7776 0 110.592-49.3568 110.592-108.1344v-604.16L677.6832 46.4896H233.472z"
              fill="#f56c6c" p-id="1115"></path>
          </svg>
          <div>空白任务数 {{ taskStatus.empty }}个</div>
        </div>
      </div>
    </div>
    <div class="task-middle">
      <div class="task-middle-title">创建任务</div>
      <div class="task-middle-content">
        <el-input v-model="inputval" style="width: 240px; margin-right: 15px" placeholder="输入任务名称" clearable />
        <el-button type="primary" @click="createTask1(inputval)">创建任务</el-button>
      </div>
    </div>
    <div class="task-bottom">
      <div class="task-bottom-title">任务列表</div>
      <div class="task-bottom-content">
        <TableSearch :query="query" :options="searchOpt" :search="handleSearch" />
        <TableCustom :columns="columns" :tableData="tableData" :total="page.total" :viewFunc="handleView"
          :delFunc="handleDelete" :editFunc="handleEdit" :pageSize="page.size" :currentPage="page.index"
          :changeSize="changeSize" :changePage="changePage">
          <!-- <template #toolbarBtn>
                    <el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">新增</el-button>
                </template> -->
        </TableCustom>
        <el-dialog :title="isEdit ? '编辑' : '新增'" v-model="visible" width="700px" destroy-on-close
          :close-on-click-modal="false" @close="closeDialog">
          <TableEdit :form-data="rowData" :options="options" :edit="isEdit" :update="updateData" />
        </el-dialog>
        <el-dialog title="查看详情" v-model="visible1" width="700px" destroy-on-close>
          <TableDetail :data="viewData"></TableDetail>
        </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="taskManagement">
import { ref, reactive, onMounted } from "vue";
import TableSearch from "@/components/task-search.vue";
import TableCustom from "@/components/task-custom.vue";
import { ElMessage } from "element-plus";
import { obtainDetails } from "@/api/home";
import { createTask, getTaskList, deleteTask } from "@/api/task";
import service from "@/utils/request";
import { Task } from "@/types/task";
import { FormOptionList, FormOption, User } from "@/types/taskManagement";
import { useRouter } from "vue-router";
import { es } from "element-plus/es/locale";

const router = useRouter();
let returnData = reactive([]);
const inputval = ref("");
const username: string | null = localStorage.getItem("vuems_name");
// 任务详情相关
const taskStatus = ref({
  total: 0,
  transcribed: 0,
  processing: 0,
  empty: 0
});
// 查询相关
const query = reactive({
  name: "",
  status: "",
});

const searchOpt = ref<FormOptionList[]>([
  {
    type: "input",
    prop: "name",
    placeholder: "输入任务名称",
    opts: [],
  },
  {
    type: "select",
    prop: "status",
    placeholder: "任务状态选择",
    activeValue: "",
    opts: [
      { label: "全部", value: "" },
      { label: "空白任务", value: "1" },
      { label: "已检测任务", value: "2" },
      { label: "已完成任务", value: "3" },
      { label: "正在处理任务", value: "4" },
      { label: "暂停任务", value: "5" },
    ],
  },
]);

const handleSearch = () => {
  // changePage(1);
  page.index = 1;
  getData()
};
// 表格相关
let columns = ref([
  { prop: "number", label: "编号", align: "center" },
  { prop: "name", label: "任务名称" },
  { prop: "status", label: "任务状态" },
  { prop: "create_time", label: "创建时间" },
  { prop: "man", label: "创建人" },
  { prop: "operator", label: "操作", width: 400 },
]);
const page = reactive({
  index: 1,
  size: 5,
  total: 0,
});
const tableData = ref<Task[]>([]);
const getData = async () => {
  const res = await getTaskList(page.index, page.size, {
    search: query.name,
    status: query.status || undefined,
  });
  console.log(189, res);
  
  if (res.data.code === 200) {
    page.total = res.data.data.total;
    returnData = res.data.data.list;
    const username = localStorage.getItem("vuems_name");
    const updatedData = returnData.map((item) => ({
      ...item,
      man: username,
    }));
    const statusMap: { [key: number]: string } = {
      1: "空白任务",
      2: "已检测任务",
      3: "已完成任务",
      4: "正在处理任务",
      5: "暂停任务",
    };

    const updatedTwoData = updatedData.map((item) => ({
      ...item,
      man: username,
      status: statusMap[item.status] || item.status,
    }));

    tableData.value = updatedTwoData;
  } else if (res.data.code === 401) {
    router.push("/login");
  }
};

const changePage = (val: number) => {
  page.index = val;
  getData();
};
const changeSize = (val: number) => {
  page.size = val;
  getData();
};

// 新增/编辑弹窗相关
let options = ref<FormOption>({
  labelWidth: "100px",
  span: 12,
  list: [
    { type: "input", label: "用户名", prop: "name", required: true },
    { type: "input", label: "手机号", prop: "phone", required: true },
    { type: "input", label: "密码", prop: "password", required: true },
    { type: "input", label: "邮箱", prop: "email", required: true },
    { type: "input", label: "角色", prop: "role", required: true },
  ],
});
const visible = ref(false);
const isEdit = ref(false);
const rowData = ref({});
const handleEdit = (row: User) => {
  rowData.value = { ...row };
  isEdit.value = true;
  visible.value = true;
};
const updateData = () => {
  closeDialog();
  getData();
};

const closeDialog = () => {
  visible.value = false;
  isEdit.value = false;
};

// 查看详情弹窗相关
const visible1 = ref(false);
const viewData = ref({
  row: {},
  list: [],
});
const handleView = (row: User) => {
  viewData.value.row = { ...row };
  viewData.value.list = [
    {
      prop: "id",
      label: "用户ID",
    },
    {
      prop: "name",
      label: "用户名",
    },
    {
      prop: "password",
      label: "密码",
    },
    {
      prop: "email",
      label: "邮箱",
    },
    {
      prop: "phone",
      label: "电话",
    },
    {
      prop: "role",
      label: "角色",
    },
    {
      prop: "date",
      label: "注册日期",
    },
  ];
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
      getTaskDEtailINfo()
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
const getTaskDEtailINfo = async ()=>{
  try {
    const res = await obtainDetails();
    // console.log(180, res);

    if (res.data.code === 200) {
      taskStatus.value = res.data.data;
    }
  } catch (error) {
    console.error('获取任务状态失败:', error);
  }
}
onMounted(async () => {
  getData();
  getTaskDEtailINfo()
  //  tableData.value = [
  //       {
  //           "number": 1,
  //           "name": "任务1",
  //           "money": 123,
  //           "status": 0,
  //           "address": "广东省东莞市长安镇",
  //           "create_time": "2025-6-1",
  //           "thumb": "https://lin-xin.gitee.io/images/post/wms.png",
  //           "man": "张三",
  //       },
  //       {
  //           "number": 2,
  //           "name": "任务2",
  //           "money": 456,
  //           "address": "广东省广州市白云区",
  //           "status": 1,
  //           "create_time": "22025-6-2",
  //           "thumb": "https://lin-xin.gitee.io/images/post/node3.png",
  //           "man": "张三",
  //       },
  //       {
  //           "number": 3,
  //           "name": "任务3",
  //           "status": 2,
  //           "money": 789,
  //           "address": "湖南省长沙市",
  //           "create_time": "2025-6-3",
  //           "thumb": "https://lin-xin.gitee.io/images/post/parcel.png",
  //           "man": "张三",
  //       },
  //       {
  //           "number": 4,
  //           "name": "任务4",
  //           "status": 3,
  //           "money": 1011,
  //           "address": "福建省厦门市鼓浪屿",
  //           "create_time": "2025-6-4",
  //           "thumb": "https://lin-xin.gitee.io/images/post/notice.png",
  //           "man": "张三",
  //       }
  //   ]
});
// 创建任务
const createTask1 = async (name) => {
  console.log(123456, name);
  if (name !== "") {
    const res = await createTask(name);
    if (res.data.code === 200) {
      ElMessage.success("创建成功");
      inputval.value = "";
      // location.reload()
      getData();
      getTaskDEtailINfo()
    } else if (res.data.code === 403) {
      ElMessage.error("权限不足");
    } else if (res.data.code === 401) {
      router.push("/login");
    } else {
      ElMessage.error("创建失败");
    }
  } else {
    ElMessage.error("请输入任务名称！");
  }
};
</script>

<style scoped lang="scss">
.task-management {
  //   background-color: #fff;
  width: 100%;
  height: 100%;
}

.task-top,
.task-middle,
.task-bottom {
  width: 100%;
  background-color: #fff;
  border-radius: 10px;
  padding: 10px;
  box-sizing: border-box;

  .task-top-title,
  .task-middle-title,
  .task-bottom-title {
    font-weight: bolder;
    font-size: 20px;
  }

  .task-top-content,
  .task-middle-content,
  .task-bottom-content {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    margin-top: 20px;

    .task-top-content-item {
      display: flex;
      align-items: center;

      svg {
        margin-right: 5px;
      }
    }
  }

  .task-bottom-content {
    display: block;
  }
}

.task-middle,
.task-bottom {
  margin-top: 20px;

  .task-middle-content {
    justify-content: flex-start;
  }
}

.task-bottom {
  height: 500px;
  overflow-y: auto;
  box-sizing: border-box;
}
</style>