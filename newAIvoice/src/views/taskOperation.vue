<template>
  <div class="operationBox">
    <el-tabs v-model="activeName" type="card" class="demo-tabs" @tab-click="handleClick">
      <el-tab-pane label="任务操作" name="first">
        <el-tabs v-model="activeName1" class="demo-tabs1" @tab-click="handleClick1">
          <el-tab-pane label="任务名称" name="first1">
            <ul class="taskInfoUl">
              <li>总文件 {{fileINfo.total}}个</li>
              <li>有效文件 {{fileINfo.valid}}个</li>
              <li>已转写文件 {{fileINfo.transcribed}}个</li>
              <li>已降噪文件 {{fileINfo.cleared}}个</li>
            </ul>
          </el-tab-pane>
          <!-- <el-tab-pane label="任务状态" name="second1">
            <ul class="taskInfoUl">
              <li>正在处理 0个</li>
              <li>已完成 0个</li>
              <li>空白任务 0个</li>
            </ul>
          </el-tab-pane> -->
        </el-tabs>
        <div class="fileBox">
          <div class="fileList">
            <div class="fileListContent">
              <ul>
                <li v-for="(file, index) in uploadFileList" :key="file.name" @mouseenter="file.isHover = true"
                  @mouseleave="file.isHover = false">
                  <el-icon class="icon1" color="#909399">
                    <Document />
                  </el-icon>
                  <div>{{ file.name }}</div>
                  <el-icon class="icon2" v-if="!file.isHover" color="#67c23a">
                    <SuccessFilled />
                  </el-icon>
                  <el-icon class="icon3" v-if="file.isHover" color="#f56c6c" @click="deleteFile(index)">
                    <CircleClose />
                  </el-icon>
                </li>
              </ul>
            </div>
            <div class="fileListInput">
              <div class="uploadBtn">
                <input type="file" multiple @change="handleFileChange" accept="audio/*,video/*" />
                <el-button type="primary" size="large"><el-icon>
                    <CirclePlus />
                  </el-icon>添加文件</el-button>
              </div>
            </div>
          </div>
          <div class="fileAction">
            <el-button class="btn" size="large" type="primary" @click="uploadFiles"><el-icon>
                <DocumentAdd />
              </el-icon>上传文件</el-button>
            <el-button class="btn" size="large" type="primary" @click="detection"><el-icon>
                <Loading />
              </el-icon>启动检测</el-button>
            <el-button class="btn" size="large" type="primary" @click="transcription"><el-icon>
                <EditPen />
              </el-icon>启动转写</el-button>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="文件检测" name="second" :disabled="!canAccessDetection">
        <el-tabs v-model="activeName2" class="demo-tabs2" @tab-click="handleClick2">
          <el-tab-pane label="任务名称" name="first2">
            <ul class="taskInfoUl">
              <li>正在进行批量文件检测</li>
            </ul>
          </el-tab-pane>
        </el-tabs>
        <div class="fileBox2">
          <div class="item">文件选择成功,系统开始处理</div>
          <div class="item">文件总数量 {{detectionFile.total}}个</div>
          <div class="item">文件总大小 {{detectionFile.size_info}}</div>
          <div class="item">文件总时长 {{detectionFile.total_voice}}</div>
          <div class="item">预计检测时间 {{detectionFile.estimate_time_info}}</div>
          <div class="item">处理进度：</div>
          <div class="demo-progress">
            <el-progress :percentage="detectionFile.progress" :status="getStatus" />
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="文件转写" name="third" :disabled="!canAccessTranscription">
        <el-tabs v-model="activeName3" class="demo-tabs3" @tab-click="handleClick3">
          <el-tab-pane label="任务名称" name="first3">
            <ul class="taskInfoUl">
              <li>正在进行批量文件转写</li>
            </ul>
          </el-tab-pane>
        </el-tabs>
        <div class="fileBox3">
          <div class="item">文件选择成功,系统开始处理</div>
          <div class="item">文件总数量 {{transitionFile.total}}个</div>
          <div class="item">文件总大小 {{transitionFile.size_info}}</div>
          <div class="item">文件总时长 {{transitionFile.total_voice}}</div>
          <div class="item">预计检测时间 {{transitionFile.estimate_time_info}}</div>
          <div class="item">处理进度：</div>
          <div class="demo-progress">
            <el-progress :percentage="transitionFile.progress" :status="getStatus3" />
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="任务详情" name="fourth">
        <el-tabs v-model="activeName4" class="demo-tabs4" @tab-click="handleClick4">
          <el-tab-pane label="任务名称" name="first4">
            <ul class="taskInfoUl">
              <li>总文件数 {{fileINfo.total}}个</li>
              <li>有效文件数 {{fileINfo.valid}}个</li>
              <li>已转写文件 {{fileINfo.transcribed}}个</li>
              <li>已降噪文件 {{fileINfo.cleared}}个</li>
            </ul>
          </el-tab-pane>
        </el-tabs>
        <div class="fileBox4">
          <TableSearch :query="query" :options="searchOpt" :search="handleSearch" />
          <el-table :data="tableData" border style="width: 100%">
            <!-- <el-table-column type="selection" align="center" width="55" /> -->

            <el-table-column label="文件名称" align="center" prop="filename" />
            <el-table-column label="大小" align="center" prop="size" />
            <el-table-column label="时长" align="center" prop="total_voice" show-overflow-tooltip />
            <el-table-column label="有效时长" align="center" prop="effective_voice" />
            <el-table-column label="语种" align="center" prop="language" />
            <el-table-column label="处理状态" align="center" prop="status" />

            <el-table-column label="操作" align="center" width="500">
              <!-- 你可以在这里放操作按钮 -->
              <template #default="scope">
                <el-button type="success" @click="dialogVisible = true"><el-icon>
                    <View />
                  </el-icon>转写预览</el-button>
                <el-dropdown style="margin: 0 10px">
                  <el-button color="#626aef"><el-icon>
                      <Download />
                    </el-icon> 转写下载<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item>带时间戳的转写文件</el-dropdown-item>
                      <el-dropdown-item>无时间戳转写文件</el-dropdown-item>
                      <el-dropdown-item>word文档</el-dropdown-item>
                      <el-dropdown-item>降噪文件</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-button type="primary" @click="toFile(1, scope.row.id)"><el-icon>
                    <Search />
                  </el-icon>文件查看</el-button>
                <el-button type="warning" @click="toFile(2, scope.row.id)"><el-icon>
                    <MuteNotification />
                  </el-icon>文件降噪</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="operationBottom">
            <el-button type="primary" class="btn" @click="transcription">选择文件转写</el-button>
            <el-pagination :current-page="page.index" :page-size="page.size" :page-sizes="[5, 10, 15, 20]"
              layout="total, sizes, prev, pager, next, jumper" :total="page.total" @size-change="changeSize"
              @current-change="changePage" />
          </div>
        </div>
        <el-dialog v-model="dialogVisible" title="转写预览" width="600" :style="{ height: '500px' }"
          :before-close="handleClose">
          <span>转写的文本预览...</span>
          <template #footer>
            <div class="dialog-footer">
              <!-- <el-button @click="dialogVisible = false">Cancel</el-button> -->
              <el-button type="primary" @click="dialogVisible = false">
                确认
              </el-button>
            </div>
          </template>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>
    <el-button v-for="button in buttons" :key="button.text" :type="button.type" class="returnBtn" text
      @click="() => $router.push({ name: 'task-management' })">
      {{ button.text }}
    </el-button>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, reactive, nextTick, onMounted, watch, onActivated, onUnmounted } from "vue";
import type { TabsPaneContext } from "element-plus";
import { ArrowDown } from "@element-plus/icons-vue";
import TableSearch from "@/components/operation-search.vue";
import { useRouter, useRoute } from "vue-router";
import { getTaskDetail, uploadTask, workflow,getFileProgress,getFileTranscriptionProgress,getTaskStatistics } from "@/api/task";
const id = ref("");
const isHover = ref(false);
const selectedFile = ref(null);
const uploadFileList = reactive([]);
const selectedFiles = reactive(new Map()); // 用于存储选择的文件
import { useUploadStore } from "@/store/uploadStore";
// 任务详情信息
const fileINfo = ref({
  cleared:0,
  total:0,
  transcribed:0,
  valid:0
})
// 文件检测文件信息
const detectionFile = ref({
  total:0,
  size_info:0,
  total_voice:0,
  estimate_time_info:0,
  progress:0
})
// 文件转写文件信息
const transitionFile = ref({
  total:0,
  size_info:0,
  total_voice:0,
  estimate_time_info:0,
  progress:0
})
const uploadStore = useUploadStore();

// 检查文件是否已存在
const isFileExists = (fileName) => {
  return uploadFileList.some(file => file.name === fileName);
};

const handleFileChange = async (event) => {
  const files = event.target.files;
  if (files && files.length > 0) {
    // 将文件添加到列表中
    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // 检查文件类型
      const fileType = file.type.toLowerCase();
      const isAudioOrVideo = fileType.startsWith('audio/') || fileType.startsWith('video/');

      if (!isAudioOrVideo) {
        ElMessage.warning(`文件 "${file.name}" 不是音频或视频文件，已跳过`);
        continue;
      }

      // 检查文件是否已存在
      if (isFileExists(file.name)) {
        ElMessage.warning(`文件 "${file.name}" 已存在`);
        continue;
      }

      const fileId = Date.now() + i; // 生成唯一ID
      uploadFileList.push({
        id: fileId,
        name: file.name,
        isHover: false,
        file: file // 保存文件对象
      });
      selectedFiles.set(fileId, file);
    }
  } else {
    ElMessage.warning("请选择要上传的文件");
  }
  // 清空input的值，这样同一个文件可以重复上传
  event.target.value = "";
};

const deleteFile = (index) => {
  const fileId = uploadFileList[index].id;
  selectedFiles.delete(fileId); // 从Map中删除文件
  uploadFileList.splice(index, 1);
};

const uploadFiles = async () => {
  console.log(1234567);
  if (selectedFiles.size === 0) {
    ElMessage.warning("请先选择文件");
    return;
  }

  try {
    // 构建文件对象
    const fileObjects = {};
    let index = 1;
    for (const [_, file] of selectedFiles) {
      fileObjects[`file${index}`] = file;
      index++;
    }
    ElMessage.success("正在上传文件...");
    // 调用上传API
    const res = await uploadTask(Number(id.value), fileObjects);
    console.log(187, res);

    if (res.data.code === 200) {
      // ElMessage.success("文件上传成功");
      // 清空已上传的文件列表
      uploadFileList.length = 0;
      selectedFiles.clear();
    } else if (res.data.code === 401) {
      router.push("/login");
    } else {
      ElMessage.error(res.data.msg || "文件上传失败");
    }
  } catch (error) {
    console.error("文件上传失败:", error);
    ElMessage.error("文件上传失败，请稍后重试");
  }
};

// 添加访问控制变量
const canAccessDetection = ref(false);
const canAccessTranscription = ref(false);

// 修改检测函数
const detection = async () => {
  try {
    activeName.value = "second";
    canAccessDetection.value = true; // 允许访问检测页面
    const res1 = await getFileProgress(id.value);
    console.log(1799, res1);
    detectionFile.value = res1.data.data;
    
    // 等待2秒让服务器处理文件
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const res = await workflow(id.value, 3);
    console.log(179, res);
    
    if (res.data.code === 200) {
      // ElMessage.success("检测任务已启动");
    } else {
      ElMessage.error(res.data.msg || "启动检测失败");
    }
  } catch (error) {
    console.error("启动检测失败:", error);
    ElMessage.error("启动检测失败，请稍后重试");
  }
};

// 添加定时器来更新进度
let progressTimer: any = null;

// 修改转写函数
const transcription = async () => {
  try {
    activeName.value = "third";
    canAccessTranscription.value = true; // 允许访问转写页面
    const res1 = await getFileTranscriptionProgress(id.value);
    console.log(1799, res1);
    transitionFile.value = res1.data.data;
    
    // 清除之前的定时器
    if (progressTimer) {
      clearInterval(progressTimer);
    }
    
    // 设置定时器定期更新进度
    progressTimer = setInterval(async () => {
      const res = await getFileTranscriptionProgress(id.value);
      if (res.data.code === 200) {
        transitionFile.value = res.data.data;
        // 如果进度达到100%，清除定时器
        if (res.data.data.progress === 100) {
          clearInterval(progressTimer);
        }
      }
    }, 3000);
    
    // 等待2秒让服务器处理文件
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const res = await workflow(id.value, 4);
    console.log(179, res);
    
    if (res.data.code === 200) {
      // ElMessage.success("转写任务已启动");
    } else {
      ElMessage.error(res.data.msg || "启动转写失败");
    }
  } catch (error) {
    console.error("启动转写失败:", error);
    ElMessage.error("启动转写失败，请稍后重试");
  }
};

// 组件卸载时清除定时器
onUnmounted(() => {
  if (progressTimer) {
    clearInterval(progressTimer);
  }
});

const router = useRouter();
const route = useRoute();

const dialogVisible = ref(false);

const handleClose = (done: () => void) => {
  ElMessageBox.confirm("确定关闭窗口吗?")
    .then(() => {
      done();
    })
    .catch(() => {
      // catch error
    });
};
import { fetchFileData } from "@/api";
// 查询相关
const query = reactive({
  fileType: "",
  status: "",
});
const handleSearch = () => {
  page.index = 1;
  getTaskDetail1();
};
const searchOpt = ref<FormOptionList[]>([
  {
    type: "select",
    prop: "fileType",
    placeholder: "文件类型",
    activeValue: "全部文件",
    opts: [
      { label: "全部文件", value: "全部文件" },
      { label: "有效文件", value: "有效文件" },
    ],
  },
  {
    type: "select",
    prop: "status",
    placeholder: "处理状态",
    activeValue: "全部",
    opts: [
      { label: "全部", value: "全部" },
      { label: "已检测", value: "已检测" },
      { label: "已转写", value: "已转写" },
      { label: "已降噪", value: "已降噪" },
    ],
  },
]);
//下载
const downType = ref("");

// 分页相关
let returnData = reactive([]);
const tableData = ref([]);
const changeSize = (val: number) => {
  page.size = val;
  // getTaskDetail1();
};
const changePage = (val: number) => {
  page.index = val;
  getTaskDetail1();
};
// 进度条相关
const percentage = ref(90);
const percentage3 = ref(100);
// 状态只能是 '', 'success', 'exception', 'warning'
const getStatus = computed(() => {
  if (detectionFile.value.progress === 100) return "success";
  return ""; // 默认值
});
const getStatus3 = computed(() => {
  if (transitionFile.value.progress === 100) return "success";
  return ""; // 默认值
});
const activeName = ref("first");
// const activeName = ref("fourth");
const activeName1 = ref("first1");
const activeName2 = ref("first2");
const activeName3 = ref("first3");
const activeName4 = ref("first4");

// 修改tab点击处理函数
const handleClick = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
    
    // 如果是检测或转写页面，且没有权限访问，则阻止切换
    if ((tab.props.name === "second" && !canAccessDetection.value) ||
        (tab.props.name === "third" && !canAccessTranscription.value)) {
      ElMessage.warning("请先启动相应的任务");
      activeName.value = "first"; // 返回任务操作页面
      return;
    }
    
    if (tab.props.name === "fourth") {
      getTaskDetail1();
    }
  });
};
const handleClick1 = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
    // console.log(tab, event);
  });
};
const handleClick2 = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
    // console.log(tab, event);
  });
};
const handleClick3 = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
    // console.log(tab, event);
  });
};
const handleClick4 = (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
    getTaskDetail1()
    // console.log(tab, event);
  });
};
const buttons = [{ type: "primary", text: "⬅ 返回任务管理" }] as const;
import { ElMessage, ElMessageBox } from "element-plus";

// 去文件查看页面
const toFile = (index, fileId) => {
  // 获取当前行的文件信息
  const fileInfo = tableData.value.find(item => item.id === fileId);
  console.log('taskOperation页面传递的文件信息：', fileInfo);
  console.log('当前表格数据：', tableData.value);
  console.log('要查找的文件id：', fileId);

  if (!fileInfo) {
    ElMessage.warning('未找到文件信息');
    return;
  }

  router.push({
    path: "file-view",
    query: {
      index,
      id: fileId, // 文件id
      taskId: fileInfo.tid, // 任务id
      // fileInfo: JSON.stringify(fileInfo) // 将文件信息转换为字符串传递
    }
  });
};
// 获取文件详情
const page = reactive({
  index: 1,
  size: 5,
  total: 0,
});
const getTaskDetail1 = async () => {
  try {
    const res = await getTaskDetail(id.value, page.index, page.size, {
      search: query.fileType !== "全部文件" ? query.fileType : undefined,
      sort: "update_time",
      order: "desc"
    });

    if (res.data.code === 200) {
      let filteredData = res.data.data.list;
      let totalData = res.data.data.list; // 保存原始数据用于计算总数

      // 处理文件类型筛选
      if (query.fileType === "有效文件") {
        filteredData = filteredData.filter(file =>
          file.effective_voice &&
          file.effective_voice !== "0" &&
          file.effective_voice !== ""
        );
        totalData = totalData.filter(file =>
          file.effective_voice &&
          file.effective_voice !== "0" &&
          file.effective_voice !== ""
        );
      }

      // 处理状态筛选
      if (query.status && query.status !== "全部") {
        filteredData = filteredData.filter(file =>
          file.status === query.status
        );
        totalData = totalData.filter(file =>
          file.status === query.status
        );
      }

      // 确保每个文件对象都有id属性
      filteredData = filteredData.map(file => ({
        ...file,
        id: file.id || file.file_id || file.task_id // 尝试不同的可能id字段
      }));

      console.log('设置到表格的数据：', filteredData);
      tableData.value = filteredData;
      // 使用筛选后的数据长度作为总数
      page.total = totalData.length;
    } else if (res.data.code === 401) {
      router.push("/login");
    } else {
      ElMessage.error(res.data.msg || "获取任务详情失败");
    }
  } catch (error) {
    console.error("获取任务详情失败:", error);
    ElMessage.error("获取任务详情失败，请稍后重试");
  }
};

// 监听路由参数变化
watch(
  () => route.query,
  (newQuery) => {
    if (newQuery.id) {
      id.value = newQuery.id as string;
      if (newQuery.index === "4") {
        activeName.value = "fourth";
        getTaskDetail1();
      }
    }
  },
  { immediate: true }
);

// 监听标签页变化
watch(
  () => activeName.value,
  (newValue) => {
    if (newValue === "fourth") {
      getTaskDetail1();
    }
  }
);

// 组件被激活时重新获取数据
onActivated(() => {
  if (activeName.value === "fourth") {
    getTaskDetail1();
  }
});

onMounted(async() => {
  const index = route.query.index;
  id.value = route.query.id as string;
  console.log("查询参数 index:", index);
  console.log("查询参数 id:", id.value);
  const res = await getTaskStatistics(id.value);
  console.log(1499,res);
  fileINfo.value = res.data.data;
  if (index == "1") {
    activeName.value = "first";
  } else if (index == "2") {
    activeName.value = "second";
  } else if (index == "3") {
    activeName.value = "third";
  } else if (index == "4") {
    activeName.value = "fourth";
    getTaskDetail1();
  }
});
</script>

<style scoped lang="scss">
.operationBox {
  position: relative;
  width: 100%;
  height: 100%;
}

.demo-tabs1,
.demo-tabs2,
.demo-tabs3,
.demo-tabs4 {
  width: 96%;
  margin: 0 auto;
  border: 1px solid #dcdfe6;
  padding: 20px;
  border-radius: 10px;
  box-sizing: border-box;
  width: 96%;
  margin: 0 auto;
  border: 1px solid #dcdfe6;
  padding: 20px;
  border-radius: 10px;
  box-sizing: border-box;
}

.demo-tabs1>.el-tabs__content {
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}

.demo-tabs {
  box-sizing: border-box;
}

.demo-tabs>.el-tabs__content {
  padding: 20px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}

.el-tabs {
  background-color: #fff;
  height: 100%;
}

::v-deep(.el-tabs__item.is-active) {
  border-bottom-color: #e4e7ed !important;
}

.returnBtn {
  position: absolute;
  right: 10px;
  top: 5px;
}

.taskInfoUl {
  list-style: none;
  display: flex;
  justify-content: space-between;
}

.fileBox,
.fileBox2,
.fileBox3,
.fileBox4 {
  width: 96%;
  height: 400px;
  border-radius: 10px;
  box-sizing: border-box;
  border: 1px solid #dcdfe6;
  display: flex;
  padding: 20px;
  margin: 0 auto;
  margin-top: 20px;

  .fileList {
    width: 60%;
    height: 90%;
    border-radius: 10px;
    border: 1px solid #dcdfe6;
    display: flex;
    flex-direction: column;

    .fileListContent {
      flex: 1;
      overflow-y: auto;
      padding: 10px;

      ul {
        list-style: none;
        width: 100%;
        margin: 0;
        padding: 0;

        li {
          margin: 10px 0;
          display: flex;
          align-items: center;
          position: relative;
          color: #909399;
          cursor: pointer;
          padding: 5px 10px;

          .icon1 {
            margin-right: 5px;
          }

          .icon2,
          .icon3 {
            position: absolute;
            right: 10px;
          }
        }
      }
    }

    .fileListInput {
      padding: 10px;
      border-top: 1px solid #dcdfe6;

      .uploadBtn {
        position: relative;
        cursor: pointer;
        width: 100%;

        input {
          position: absolute;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          opacity: 0;
          cursor: pointer;
        }

        .el-button {
          width: 100%;
        }
      }
    }
  }

  .fileAction {
    margin-left: 100px;

    .btn {
      display: block;
      margin: 20px auto;
    }
  }
}

.fileBox2,
.fileBox3,
.fileBox4 {
  display: block;

  .item {
    margin: 20px 0;
  }
}

.fileBox4 {
  height: 600px;
  overflow-y: auto;
}

::v-deep(.el-upload-list) {
  //  background-color: red;
  position: fixed;
  left: 11%;
  top: 35%;
  width: 49%;
}

.el-upload-list__item {
  margin: 10px 0;
}

.demo-progress .el-progress--line {
  margin-bottom: 15px;
  max-width: 600px;
}

.operationBottom {
  margin-top: 20px;
  display: flex;

  .btn {
    margin-right: 10px;
  }
}

.dialog-footer {
  position: absolute;
  bottom: 10px;
  right: 10px;
}
</style>
