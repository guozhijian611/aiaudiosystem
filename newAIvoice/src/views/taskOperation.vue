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
                <input type="file" multiple @change="handleFileChange" accept="audio/*,video/*" style="display: none;" ref="fileInput" />
                <el-button type="primary" size="large" @click="triggerFileInput"><el-icon>
                    <CirclePlus />
                  </el-icon>添加文件</el-button>
              </div>
            </div>
          </div>
          <div class="fileAction">
            <el-button class="btn" size="large" type="primary" @click="uploadFiles" :disabled="isButtonDisabled"><el-icon>
                <DocumentAdd />
              </el-icon>上传文件</el-button>
            <el-button class="btn" size="large" type="primary" @click="detection" :disabled="isButtonDisabled"><el-icon>
                <Loading />
              </el-icon>启动检测</el-button>
            <el-button class="btn" size="large" type="primary" @click="transcription" :disabled="isButtonDisabled"><el-icon>
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
          <el-table :data="tableData" border style="width: 100%" @selection-change="handleSelectionChange">
            <el-table-column type="selection" align="center" width="55" />

            <el-table-column label="文件名称" align="center" prop="filename" />
            <el-table-column label="大小" align="center" prop="size" />
            <el-table-column label="时长" align="center" prop="total_voice" show-overflow-tooltip />
            <el-table-column label="有效时长" align="center" prop="effective_voice" />
            <el-table-column label="语种" align="center" prop="language" />
            <el-table-column label="处理状态" align="center" prop="step" />

            <el-table-column label="操作" align="center" width="500">
              <!-- 你可以在这里放操作按钮 -->
              <template #default="scope">
                <el-button type="success" @click="handlePreview(scope.row)"><el-icon>
                    <View />
                  </el-icon>转写预览</el-button>
                <el-dropdown style="margin: 0 10px">
                  <el-button color="#626aef"><el-icon>
                      <Download />
                    </el-icon> 转写下载<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="downloadText('withTimestamp')">带时间戳的转写文件</el-dropdown-item>
                      <el-dropdown-item @click="downloadText('withoutTimestamp')">无时间戳转写文件</el-dropdown-item>
                      <el-dropdown-item @click="downloadText('word')">word文档</el-dropdown-item>
                      <el-dropdown-item @click="downloadText('noise')">降噪文件</el-dropdown-item>
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
            <el-button type="primary" class="btn" @click="batchTranscription">选择文件转写</el-button>
            <el-pagination :current-page="page.index" :page-size="page.size" :page-sizes="[5, 10, 15, 20]"
              layout="total, sizes, prev, pager, next, jumper" :total="page.total" @size-change="changeSize"
              @current-change="changePage" />
          </div>
        </div>
        <el-dialog v-model="dialogVisible" title="转写预览" width="600" :style="{ height: '500px' }"
          >
          <div class="transcriptionPreviewContent">
            <div v-if="previewText" class="lyrics-container">
              <div v-for="(segment, index) in JSON.parse(previewText).segments" :key="index" class="lyric-line">
                <span class="time-stamp">[{{ formatTime(segment.start) }} - {{ formatTime(segment.end) }}]</span>
                <span v-if="segment.speaker" class="speaker">({{ segment.speaker }})</span>
                <span class="lyric-text">{{ segment.text }}</span>
              </div>
            </div>
            <div v-else class="no-content">
              暂无转写内容
            </div>
          </div>
          <template #footer>
            <div class="dialog-footer">
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
import { ArrowDown, Document, CirclePlus, SuccessFilled, CircleClose, DocumentAdd, Loading, EditPen, View, Download, Search, MuteNotification } from "@element-plus/icons-vue";
import TableSearch from "@/components/operation-search.vue";
import { useRouter, useRoute } from "vue-router";
import { getTaskDetail, uploadTask, workflow,getFileProgress,getFileTranscriptionProgress,getTaskStatistics } from "@/api/task";
import { Document as DocxDocument, Paragraph, Packer, TextRun } from 'docx';
const id = ref("");
const isHover = ref(false);
const selectedFile = ref(null);
const uploadFileList = reactive([]);
const selectedFiles = ref<any[]>([]);
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

const fileInput = ref(null);

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = async (event) => {
  const files = event.target.files;
  if (files && files.length > 0) {
    // 将文件添加到列表中
    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // 检查文件类型
      const is_quick = file.type.toLowerCase();
      const isAudioOrVideo = is_quick.startsWith('audio/') || is_quick.startsWith('video/');

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
      selectedFiles.value.push({
        id: fileId,
        name: file.name,
        isHover: false,
        file: file // 保存文件对象
      });
    }
  } else {
    ElMessage.warning("请选择要上传的文件");
  }
  // 清空input的值，这样同一个文件可以重复上传
  event.target.value = "";
};

const deleteFile = (index) => {
  const fileId = uploadFileList[index].id;
  selectedFiles.value = selectedFiles.value.filter(file => file.id !== fileId);
  uploadFileList.splice(index, 1);
};

// 添加按钮状态控制变量
const isButtonDisabled = ref(false);

// 修改uploadFiles函数
const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning("请先选择文件");
    return;
  }

  try {
    // 禁用按钮
    isButtonDisabled.value = true;
    
    // 构建文件对象
    const fileObjects = {};
    let index = 1;
    for (const file of selectedFiles.value) {
      fileObjects[`file${index}`] = file.file;
      index++;
    }
    ElMessage.success("正在上传文件...");
    // 调用上传API
    const res = await uploadTask(Number(id.value), fileObjects);
    console.log(187, res);

    if (res.data.code === 200) {
      ElMessage.success("文件上传成功");
      // 清空已上传的文件列表
      uploadFileList.length = 0;
      selectedFiles.value = [];
      
      // 重新获取任务统计信息
      const statsRes = await getTaskStatistics(id.value);
      if (statsRes.data.code === 200) {
        fileINfo.value = statsRes.data.data;
        console.log('更新后的任务统计信息：', fileINfo.value);
      }
      
      // 3秒后启用按钮
      setTimeout(() => {
        isButtonDisabled.value = false;
        ElMessage.success("可以开始检测或转写");
      }, 3000);
    } else if (res.data.code === 401) {
      router.push("/login");
    } else {
      ElMessage.error(res.data.msg || "文件上传失败");
      // 上传失败时也启用按钮
      isButtonDisabled.value = false;
    }
  } catch (error) {
    console.error("文件上传失败:", error);
    ElMessage.error("文件上传失败，请稍后重试");
    // 发生错误时也启用按钮
    isButtonDisabled.value = false;
  }
};

// 添加访问控制变量
const canAccessDetection = ref(false);
const canAccessTranscription = ref(false);

// 添加step状态映射
const stepStatusMap = {
  0: '文件已上传，等待处理',
  1: '正在提取音频',
  2: '音频提取完成，等待降噪',
  3: '正在音频降噪',
  4: '音频降噪完成，等待下一步处理',
  5: '正在快速识别',
  6: '快速识别完成，等待用户选择是否转写',
  7: '正在文本转写',
  8: '所有处理完成',
  9: '处理失败',
  10: '任务暂停',
  11: '未降噪的文本转写'
};

// 添加定时器变量
let detectionTimer = null;
let transcriptionTimer = null;

// 修改检测函数
const detection = async () => {
  try {
    // 检查是否有文件
    if (fileINfo.value.total === 0) {
      ElMessage.warning('请先上传文件');
      return;
    }

    activeName.value = "second";
    canAccessDetection.value = true; // 允许访问检测页面
    const res1 = await getFileProgress(id.value);
    console.log(1799, res1);
    detectionFile.value = res1.data.data;
    
    // 清除之前的定时器
    if (detectionTimer) {
      clearInterval(detectionTimer);
    }
    
    // 设置定时器，每10秒请求一次进度
    detectionTimer = setInterval(async () => {
      const res = await getFileProgress(id.value);
      if (res.data.code === 200) {
        detectionFile.value = res.data.data;
        // 如果进度达到100%，清除定时器
        if (res.data.data.progress === 100) {
          clearInterval(detectionTimer);
        }
      }
    }, 10000);
    
    // 等待2秒让服务器处理文件
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const res = await workflow(id.value, 3);
    console.log(179, res);
    
    if (res.data.code === 200) {
      // ElMessage.success("检测任务已启动");
    } else {
      ElMessage.error(res.data.msg || "启动检测失败");
      clearInterval(detectionTimer);
    }
  } catch (error) {
    console.error("启动检测失败:", error);
    ElMessage.error("启动检测失败，请稍后重试");
    clearInterval(detectionTimer);
  }
};

// 修改转写函数
const transcription = async () => {
  try {
    // 检查是否有文件
    if (fileINfo.value.total === 0) {
      ElMessage.warning('请先上传文件');
      return;
    }

    activeName.value = "third";
    canAccessTranscription.value = true; // 允许访问转写页面
    const res1 = await getFileTranscriptionProgress(id.value);
    console.log(1799, res1);
    transitionFile.value = res1.data.data;
    
    // 清除之前的定时器
    if (transcriptionTimer) {
      clearInterval(transcriptionTimer);
    }
    
    // 设置定时器，每10秒请求一次进度
    transcriptionTimer = setInterval(async () => {
      const res = await getFileTranscriptionProgress(id.value);
      if (res.data.code === 200) {
        transitionFile.value = res.data.data;
        // 如果进度达到100%，清除定时器
        if (res.data.data.progress === 100) {
          clearInterval(transcriptionTimer);
        }
      }
    }, 10000);
    
    // 等待2秒让服务器处理文件
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const res = await workflow(id.value, 4);
    console.log(179, res);
    
    if (res.data.code === 200) {
      // ElMessage.success("转写任务已启动");
    } else {
      ElMessage.error(res.data.msg || "启动转写失败");
      clearInterval(transcriptionTimer);
    }
  } catch (error) {
    console.error("启动转写失败:", error);
    ElMessage.error("启动转写失败，请稍后重试");
    clearInterval(transcriptionTimer);
  }
};

// 组件卸载时清除所有定时器
onUnmounted(() => {
  if (detectionTimer) {
    clearInterval(detectionTimer);
  }
  if (transcriptionTimer) {
    clearInterval(transcriptionTimer);
  }
});

const router = useRouter();
const route = useRoute();

const dialogVisible = ref(false);
const previewText = ref('');

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
  is_quick: "",
  step: "",
});
const handleSearch = () => {
  console.log('触发搜索，当前搜索条件：', {
    is_quick: query.is_quick,
    step: query.step
  });
  page.index = 1;
  getTaskDetail1();
};
const searchOpt = ref([
  {
    type: "select",
    prop: "is_quick",
    placeholder: "文件类型",
    activeValue: "全部文件",
    opts: [
      { label: "全部文件", value: "全部文件" },
      { label: "有效文件", value: "有效文件" },
    ],
  },
  {
    type: "select",
    prop: "step",
    placeholder: "处理状态",
    activeValue: "全部",
    opts: [
      { label: "全部", value: "全部" },
      { label: "文件已上传，等待处理", value: "文件已上传，等待处理" },
      { label: "正在提取音频", value: "正在提取音频" },
      { label: "音频提取完成，等待降噪", value: "音频提取完成，等待降噪" },
      { label: "正在音频降噪", value: "正在音频降噪" },
      { label: "音频降噪完成，等待下一步处理", value: "音频降噪完成，等待下一步处理" },
      { label: "正在快速识别", value: "正在快速识别" },
      { label: "快速识别完成，等待用户选择是否转写", value: "快速识别完成，等待用户选择是否转写" },
      { label: "正在文本转写", value: "正在文本转写" },
      { label: "所有处理完成", value: "所有处理完成" },
      { label: "处理失败", value: "处理失败" },
      { label: "任务暂停", value: "任务暂停" },
      { label: "未降噪的文本转写", value: "未降噪的文本转写" }
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

  // 如果是降噪操作（index === 2）
  if (index === 2) {
    // 判断clear_url是否为空
    if (!fileInfo.clear_url) {
      // 如果为空，跳转到降噪转写页面
      router.push({
        path: "file-view",
        query: {
          index: "3", // 降噪转写页面
          id: fileId,
          taskId: fileInfo.tid
        }
      });
    } else {
      // 如果不为空，跳转到文件降噪页面
      router.push({
        path: "file-view",
        query: {
          index: "2", // 文件降噪页面
          id: fileId,
          taskId: fileInfo.tid
        }
      });
    }
  } else {
    // 其他操作保持原有逻辑
    router.push({
      path: "file-view",
      query: {
        index,
        id: fileId,
        taskId: fileInfo.tid
      }
    });
  }
};
// 获取文件详情
const page = reactive({
  index: 1,
  size: 5,
  total: 0,
});
// 添加状态映射对象
const statusToNumberMap = {
  '文件已上传，等待处理': '0',
  '正在提取音频': '1',
  '音频提取完成，等待降噪': '2',
  '正在音频降噪': '3',
  '音频降噪完成，等待下一步处理': '4',
  '正在快速识别': '5',
  '快速识别完成，等待用户选择是否转写': '6',
  '正在文本转写': '7',
  '所有处理完成': '8',
  '处理失败': '9',
  '任务暂停': '10',
  '未降噪的文本转写': '11'
};

const getTaskDetail1 = async () => {
  try {
    // 打印搜索参数
    console.log('搜索参数：', {
      is_quick: query.is_quick,
      step: query.step,
      page: page.index,
      size: page.size
    });

    const searchParams = {
      is_quick: query.is_quick === "有效文件" ? "1" : "0",
      step: query.step !== "全部" ? statusToNumberMap[query.step] : null,
      sort: "update_time",
      order: "desc"
    };

    // 打印发送到后端的参数
    console.log('发送到后端的参数：', searchParams);

    const res = await getTaskDetail(id.value, page.index, page.size, searchParams);
    console.log('后端返回的原始数据：', res.data.data);

    if (res.data.code === 200) {
      let filteredData = res.data.data.list;
      console.log('后端返回的列表数据：', filteredData);
      console.log('后端返回的总数：', res.data.data.total);

      // 确保每个文件对象都有id属性，并转换step为文字描述
      filteredData = filteredData.map(file => ({
        ...file,
        id: file.id || file.file_id || file.task_id,
        step: stepStatusMap[file.step] || '未知状态'
      }));

      console.log('处理后的表格数据：', filteredData);
      tableData.value = filteredData;
      
      // 使用后端返回的总数
      page.total = res.data.data.total;
      console.log('设置的分页总数：', page.total);
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

// 处理表格多选
const handleSelectionChange = (selection: any[]) => {
  selectedFiles.value = selection;
  console.log('当前选中的文件：', selection);
};

// 批量转写函数
const batchTranscription = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择要转写的文件');
    return;
  }

  try {
    // 获取选中文件的id数组
    const fileIds = selectedFiles.value.map(file => file.id);
    console.log('要转写的文件ID数组：', fileIds);
    
    // 调用转写接口
    const res = await workflow(id.value, 4, fileIds);
    console.log('转写接口返回数据：', res);
    
    if (res.data.code === 200) {
      ElMessage.success('转写任务已启动');
      // 刷新表格数据
      getTaskDetail1();
    } else {
      ElMessage.error(res.data.msg || '启动转写失败');
    }
  } catch (error) {
    console.error('启动转写失败:', error);
    ElMessage.error('启动转写失败，请稍后重试');
  }
};

// 格式化时间
const formatTime = (time: number) => {
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  const milliseconds = Math.floor((time % 1) * 1000);
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
};

// 修改表格操作列的转写预览按钮点击事件
const handlePreview = (row) => {
  previewText.value = row.text_info;
  dialogVisible.value = true;
};

// 下载文本
const downloadText = (type) => {
  if (!previewText.value) {
    ElMessage.warning('暂无转写内容');
    return;
  }

  try {
    const segments = JSON.parse(previewText.value).segments;
    let content = '';
    const currentFile = tableData.value.find(item => item.text_info === previewText.value);
    const filename = currentFile?.filename.split('.')[0] || '转写文本';

    switch (type) {
      case 'withTimestamp':
        content = segments.map(segment => 
          `[${formatTime(segment.start)} - ${formatTime(segment.end)}]${segment.speaker ? ` (${segment.speaker})` : ''} ${segment.text}`
        ).join('\n');
        downloadFile(content, `${filename}_带时间戳.txt`, 'text/plain');
        break;

      case 'withoutTimestamp':
        content = segments.map(segment => 
          `${segment.speaker ? `(${segment.speaker}) ` : ''}${segment.text}`
        ).join('\n');
        downloadFile(content, `${filename}_无时间戳.txt`, 'text/plain');
        break;

      case 'word':
        // 构建HTML内容
        let htmlContent = `
          <html xmlns:o="urn:schemas-microsoft-com:office:office" 
                xmlns:w="urn:schemas-microsoft-com:office:word" 
                xmlns="http://www.w3.org/TR/REC-html40">
          <head>
            <meta charset="utf-8">
            <title>${filename}</title>
          </head>
          <body>
        `;

        segments.forEach(segment => {
          htmlContent += `
            <p>
              <span style="color: #666;">[${formatTime(segment.start)} - ${formatTime(segment.end)}]</span>
              ${segment.speaker ? `<span style="color: #409EFF;">(${segment.speaker})</span> ` : ''}
              <span style="color: #333;">${segment.text}</span>
            </p>
          `;
        });

        htmlContent += '</body></html>';

        // 创建Blob对象
        const blob = new Blob([htmlContent], { type: 'application/msword' });
        
        // 创建下载链接
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = `${filename}_转写文本.doc`;
        
        // 触发下载
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        window.URL.revokeObjectURL(downloadLink.href);
        break;

      case 'noise':
        if (!currentFile) {
          ElMessage.warning('未找到文件信息');
          return;
        }
        
        if (!currentFile.clear_url) {
          ElMessage.warning('请先进行降噪处理');
          return;
        }
        
        // 下载降噪文件
        const noiseLink = document.createElement('a');
        noiseLink.href = currentFile.clear_url;
        noiseLink.download = `${filename}_降噪文件.${currentFile.clear_url.split('.').pop()}`;
        document.body.appendChild(noiseLink);
        noiseLink.click();
        document.body.removeChild(noiseLink);
        break;
    }
  } catch (error) {
    console.error('下载失败:', error);
    ElMessage.error('下载失败');
  }
};

// 下载文件
const downloadFile = (content, filename, type) => {
  const blob = new Blob([content], { type });
  const url = window.URL.createObjectURL(blob);
  const downloadLink = document.createElement('a');
  downloadLink.href = url;
  downloadLink.download = filename;
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
  window.URL.revokeObjectURL(url);
};
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

.transcriptionPreviewContent {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;

  .lyrics-container {
    .lyric-line {
      margin-bottom: 8px;
      line-height: 1.5;
      display: flex;
      align-items: flex-start;
      gap: 8px;

      .time-stamp {
        color: #666;
        font-size: 14px;
        white-space: nowrap;
      }

      .speaker {
        color: #409EFF;
        font-size: 14px;
        white-space: nowrap;
      }

      .lyric-text {
        color: #333;
        font-size: 14px;
        flex: 1;
      }
    }
  }

  .no-content {
    text-align: center;
    color: #909399;
    font-size: 14px;
    padding: 20px;
  }
}
</style>
