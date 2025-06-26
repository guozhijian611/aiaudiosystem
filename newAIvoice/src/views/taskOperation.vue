<template>
  <div class="operationBox">
    <!-- 任务名称显示 -->
    <div class="task-header" v-if="taskInfo.name">
      <h2 class="task-title">
        <el-icon><Document /></el-icon>
        <span>{{ taskInfo.name }}</span>
      </h2>
      <div class="task-meta">
        <span class="task-number">任务编号：{{ taskInfo.number }}</span>
        <span class="task-status" :class="getTaskStatusClass(taskInfo.status)">
          {{ getTaskStatusText(taskInfo.status) }}
        </span>
      </div>
    </div>
    
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
      <el-tab-pane label="统计信息" name="fifth">
        <el-tabs v-model="activeName5" class="demo-tabs5" @tab-click="handleClick5">
          <el-tab-pane label="任务概览" name="first5">
            <!-- 任务信息卡片 -->
            <div class="task-info-cards">
              <el-card class="info-card" shadow="hover">
                <div class="card-header-custom">
                  <el-icon><Document /></el-icon>
                  <span>文件统计</span>
                </div>
                <div class="card-content-custom">
                  <div class="stat-item">
                    <span class="stat-label">总文件数：</span>
                    <span class="stat-value primary">{{ fileINfo.total }}个</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">有效文件数：</span>
                    <span class="stat-value success">{{ fileINfo.valid }}个</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">已转写文件：</span>
                    <span class="stat-value info">{{ fileINfo.transcribed }}个</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">已降噪文件：</span>
                    <span class="stat-value warning">{{ fileINfo.cleared }}个</span>
                  </div>
                </div>
              </el-card>

              <el-card class="info-card" shadow="hover">
                <div class="card-header-custom">
                  <el-icon><Loading /></el-icon>
                  <span>处理进度</span>
                </div>
                <div class="card-content-custom">
                  <div class="progress-item">
                    <span class="progress-label">检测进度：</span>
                    <el-progress 
                      :percentage="Math.round((fileINfo.valid / fileINfo.total) * 100) || 0" 
                      :color="progressColors"
                      :stroke-width="8"
                    />
                  </div>
                  <div class="progress-item">
                    <span class="progress-label">转写进度：</span>
                    <el-progress 
                      :percentage="Math.round((fileINfo.transcribed / fileINfo.total) * 100) || 0" 
                      :color="progressColors"
                      :stroke-width="8"
                    />
                  </div>
                  <div class="progress-item">
                    <span class="progress-label">降噪进度：</span>
                    <el-progress 
                      :percentage="Math.round((fileINfo.cleared / fileINfo.total) * 100) || 0" 
                      :color="progressColors"
                      :stroke-width="8"
                    />
                  </div>
                </div>
              </el-card>

              <el-card class="info-card" shadow="hover">
                <div class="card-header-custom">
                  <el-icon><View /></el-icon>
                  <span>任务状态</span>
                </div>
                <div class="card-content-custom">
                  <div class="status-overview">
                    <div class="status-circle">
                      <div class="circle-progress" :style="{ '--progress': ((fileINfo.transcribed / fileINfo.total) * 100) || 0 }">
                        <span class="percentage">{{ Math.round(((fileINfo.transcribed / fileINfo.total) * 100)) || 0 }}%</span>
                      </div>
                      <span class="status-label">总体完成度</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="详细信息" name="second5">
            <!-- 详细信息 -->
            <div class="task-details">
              <el-descriptions title="任务详细信息" :column="2" border>
                <el-descriptions-item label="任务ID">{{ id }}</el-descriptions-item>
                <el-descriptions-item label="总文件数">{{ fileINfo.total }}个</el-descriptions-item>
                <el-descriptions-item label="有效文件数">{{ fileINfo.valid }}个</el-descriptions-item>
                <el-descriptions-item label="已转写文件">{{ fileINfo.transcribed }}个</el-descriptions-item>
                <el-descriptions-item label="已降噪文件">{{ fileINfo.cleared }}个</el-descriptions-item>
                <el-descriptions-item label="待处理文件">{{ fileINfo.total - fileINfo.transcribed }}个</el-descriptions-item>
                <el-descriptions-item label="转写完成率">{{ Math.round(((fileINfo.transcribed / fileINfo.total) * 100)) || 0 }}%</el-descriptions-item>
                <el-descriptions-item label="降噪完成率">{{ Math.round(((fileINfo.cleared / fileINfo.total) * 100)) || 0 }}%</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>
      
      <el-tab-pane label="任务详情" name="fourth">
        <el-tabs v-model="activeName4" class="demo-tabs4" @tab-click="handleClick4">
          <el-tab-pane label="文件列表" name="first4">
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
          <el-table :data="tableData" border style="width: 100%" @selection-change="handleSelectionChange" :row-class-name="getRowClassName">
            <el-table-column type="selection" align="center" width="55" :selectable="isRowSelectable" />
          
            <el-table-column label="文件名称" align="center" prop="filename" />
            <el-table-column label="大小" align="center" prop="size" />
            <el-table-column label="时长" align="center" prop="total_voice" show-overflow-tooltip />
            <el-table-column label="有效时长" align="center" prop="effective_voice" />
            <el-table-column label="语种" align="center" prop="language" />
            <el-table-column label="上传时间" align="center" prop="create_time" />
            <el-table-column label="处理状态" align="center" prop="step" width="180" show-overflow-tooltip>
              <template #default="scope">
                <el-tag 
                  :type="scope.row.step === '所有处理完成' ? 'success' : 'info'"
                  :effect="scope.row.step === '所有处理完成' ? 'dark' : 'light'"
                  style="white-space: normal; height: auto; line-height: 1.4; padding: 4px 8px;"
                >
                  {{ scope.row.step }}
                  <span v-if="scope.row.step === '所有处理完成'" style="margin-left: 4px;">✓</span>
                </el-tag>
              </template>
            </el-table-column>

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
            <el-button type="primary" class="btn" @click="batchTranscription" :loading="isBatchProcessing">选择文件转写</el-button>
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
    
    <!-- 批量转写进度弹窗 -->
    <el-dialog 
      v-model="batchProcessingVisible" 
      title="批量转写处理" 
      width="700px" 
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      :show-close="true"
      @close="handleBatchDialogClose"
    >
      <!-- 处理中状态 -->
      <div v-if="isBatchProcessing" class="batch-processing-status">
        <div class="processing-card">
          <div class="card-header processing">
            <el-icon class="header-icon rotating"><Loading /></el-icon>
            <h3>正在处理中...</h3>
          </div>
          <div class="card-content">
            <div class="status-info">
              <div class="status-item">
                <span class="label">当前状态：</span>
                <el-tag type="warning" effect="plain">{{ batchCurrentStatus }}</el-tag>
              </div>
              <div class="status-item">
                <span class="label">处理文件：</span>
                <span class="filename">{{ batchProcessingFiles.length }}个文件</span>
              </div>
              <div class="status-item">
                <span class="label">预计时间：</span>
                <span class="time">{{ batchEstimatedTime }}</span>
              </div>
            </div>
            
            <!-- 进度条 -->
            <div class="progress-section">
              <div class="progress-header">
                <span>处理进度</span>
                <span>{{ batchProcessingProgress }}%</span>
              </div>
              <el-progress 
                :percentage="batchProcessingProgress" 
                :status="batchProcessingProgress === 100 ? 'success' : ''"
                :stroke-width="8"
                :color="progressColors"
              />
            </div>
            
            <!-- 文件处理列表 -->
            <div class="file-list-section">
              <h4>文件处理状态</h4>
              <div class="file-list">
                <div 
                  v-for="file in batchProcessingFiles" 
                  :key="file.id" 
                  class="file-item"
                  :class="getFileStatusClass(file.currentStatus)"
                >
                  <div class="file-info">
                    <el-icon class="file-icon"><Document /></el-icon>
                    <span class="file-name">{{ file.filename }}</span>
                  </div>
                  <div class="file-status">
                    <el-tag 
                      :type="getFileTagType(file.currentStatus)" 
                      size="small"
                    >
                      {{ getFileStatusText(file.currentStatus) }}
                    </el-tag>
                    <el-icon v-if="file.currentStatus === 'processing'" class="loading-icon"><Loading /></el-icon>
                    <el-icon v-else-if="file.currentStatus === 'completed'" class="success-icon"><CircleCheck /></el-icon>
                    <el-icon v-else-if="file.currentStatus === 'failed'" class="error-icon"><InfoFilled /></el-icon>
                  </div>
                  <!-- 显示跳过原因 -->
                  <div v-if="file.currentStatus === 'failed' && file.errorMessage" class="skip-reason">
                    <span class="reason-label">跳过原因：</span>
                    <span class="reason-text">{{ file.errorMessage }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 处理步骤 -->
            <div class="steps-section">
              <div class="step-item" :class="{ active: batchCurrentStep >= 1, completed: batchCurrentStep > 1 }">
                <div class="step-icon">
                  <el-icon v-if="batchCurrentStep > 1"><Check /></el-icon>
                  <el-icon v-else-if="batchCurrentStep === 1"><Loading /></el-icon>
                  <span v-else>1</span>
                </div>
                <span class="step-text">排队等待</span>
              </div>
              <div class="step-line" :class="{ completed: batchCurrentStep > 1 }"></div>
              <div class="step-item" :class="{ active: batchCurrentStep >= 2, completed: batchCurrentStep > 2 }">
                <div class="step-icon">
                  <el-icon v-if="batchCurrentStep > 2"><Check /></el-icon>
                  <el-icon v-else-if="batchCurrentStep === 2"><Loading /></el-icon>
                  <span v-else>2</span>
                </div>
                <span class="step-text">文本转写</span>
              </div>
              <div class="step-line" :class="{ completed: batchCurrentStep > 2 }"></div>
              <div class="step-item" :class="{ active: batchCurrentStep >= 3, completed: batchCurrentStep > 3 }">
                <div class="step-icon">
                  <el-icon v-if="batchCurrentStep > 3"><Check /></el-icon>
                  <el-icon v-else-if="batchCurrentStep === 3"><Loading /></el-icon>
                  <span v-else>3</span>
                </div>
                <span class="step-text">完成处理</span>
              </div>
            </div>
            
            <div class="processing-tips">
              <el-alert
                title="处理提示"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  <p>• 批量转写正在进行中，请保持页面打开</p>
                  <p>• 处理时间取决于文件数量和大小</p>
                  <p>• 处理完成后将自动刷新任务数据</p>
                </template>
              </el-alert>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 处理完成状态 -->
      <div v-else-if="batchProcessComplete" class="batch-process-complete">
        <div class="processing-card">
          <div class="card-header success">
            <el-icon class="header-icon"><CircleCheck /></el-icon>
            <h3>处理完成</h3>
          </div>
          <div class="card-content">
            <p class="success-message">批量转写处理已完成！共处理了 {{ batchProcessingFiles.length }} 个文件。</p>
            
            <!-- 完成文件列表 -->
            <div class="completed-files">
              <h4>处理结果</h4>
              <div class="file-list">
                <div 
                  v-for="file in batchProcessingFiles" 
                  :key="file.id" 
                  class="file-item completed"
                >
                  <div class="file-info">
                    <el-icon class="file-icon"><Document /></el-icon>
                    <span class="file-name">{{ file.filename }}</span>
                  </div>
                  <div class="file-status">
                    <el-tag 
                      :type="file.currentStatus === 'failed' ? 'warning' : 'success'" 
                      size="small"
                    >
                      {{ file.currentStatus === 'failed' ? '已跳过' : '已完成' }}
                    </el-tag>
                    <el-icon v-if="file.currentStatus === 'failed'" class="warning-icon"><InfoFilled /></el-icon>
                    <el-icon v-else class="success-icon"><CircleCheck /></el-icon>
                  </div>
                  <!-- 显示跳过原因 -->
                  <div v-if="file.currentStatus === 'failed' && file.errorMessage" class="skip-reason">
                    <span class="reason-label">跳过原因：</span>
                    <span class="reason-text">{{ file.errorMessage }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="action-buttons">
              <el-button type="success" @click="closeBatchProcessingDialog">确认</el-button>
              <el-button type="primary" @click="refreshTaskData">刷新任务数据</el-button>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer" v-if="!isBatchProcessing && !batchProcessComplete">
          <el-button @click="batchProcessingVisible = false">取消</el-button>
        </div>
      </template>
    </el-dialog>
    <el-button v-for="button in buttons" :key="button.text" :type="button.type" class="returnBtn" text
      @click="() => $router.push({ name: 'task-management' })">
      {{ button.text }}
    </el-button>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, reactive, nextTick, onMounted, watch, onActivated, onUnmounted } from "vue";
import type { TabsPaneContext } from "element-plus";
import { ArrowDown, Document, CirclePlus, SuccessFilled, CircleClose, DocumentAdd, Loading, EditPen, View, Download, Search, MuteNotification, Check, CircleCheck, InfoFilled } from "@element-plus/icons-vue";
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
// 任务基本信息
const taskInfo = ref({
  id: '',
  name: '',
  number: '',
  status: '',
  create_time: '',
  update_time: ''
});
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

// 进度条颜色配置
const progressColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
];

// 批量处理相关状态
const batchProcessingVisible = ref(false);
const isBatchProcessing = ref(false);
const batchProcessComplete = ref(false);
const batchCurrentStatus = ref('等待处理');
const batchEstimatedTime = ref('约2-5分钟');
const batchProcessingProgress = ref(0);
const batchCurrentStep = ref(0);
const batchProcessingFiles = ref([]); // 存储处理中的文件信息

// 批量处理定时器
let batchProcessingTimer = null;
let batchStatusCheckTimer = null;

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
  4: '音频降噪完成，等待转写',
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
  if (batchProcessingTimer) {
    clearInterval(batchProcessingTimer);
  }
  if (batchStatusCheckTimer) {
    clearTimeout(batchStatusCheckTimer);
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
      { label: "音频降噪完成，等待转写", value: "音频降噪完成，等待转写" },
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
const activeName5 = ref("first5");

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
    } else if (tab.props.name === "fifth") {
      // 切换到统计信息页面时重新获取数据
      refreshTaskStatistics();
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

const handleClick5 = async (tab: TabsPaneContext, event: Event) => {
  nextTick(() => {
    (document.activeElement as HTMLElement | null)?.blur?.();
  });
  
  // 每次切换统计信息的子标签页时重新获取数据
  try {
    const res = await getTaskStatistics(id.value);
    if (res.data.code === 200) {
      fileINfo.value = res.data.data;
      console.log('重新获取任务统计信息：', fileINfo.value);
    } else if (res.data.code === 401) {
      router.push("/login");
    } else {
      ElMessage.error(res.data.msg || "获取任务统计失败");
    }
  } catch (error) {
    console.error("获取任务统计失败:", error);
    ElMessage.error("获取任务统计失败，请稍后重试");
  }
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
      // 处理任务基本信息
      if (res.data.data.task_info) {
        taskInfo.value = res.data.data.task_info;
        console.log('任务基本信息：', taskInfo.value);
      }
      
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

// 控制行是否可选择
const isRowSelectable = (row: any, index: number) => {
  // step为8或"所有处理完成"的文件不能选择
  return !(row.step === 8 || row.step === '所有处理完成');
};

// 获取行样式类名
const getRowClassName = ({ row, rowIndex }: { row: any, rowIndex: number }) => {
  // 为已完成的文件添加特殊样式
  if (row.step === 8 || row.step === '所有处理完成') {
    return 'completed-row';
  }
  return '';
};

// 批量转写函数
const batchTranscription = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择要转写的文件');
    return;
  }

  // 检查选中文件中是否有"所有处理完成"的文件
  const completedFiles = selectedFiles.value.filter(file => {
    // step为8表示"所有处理完成"，或者step文本为"所有处理完成"
    return file.step === 8 || file.step === '所有处理完成';
  });

  if (completedFiles.length > 0) {
    const completedFileNames = completedFiles.map(file => file.filename).join('、');
    ElMessage.warning(`以下文件已完成所有处理，无需重复转写：${completedFileNames}`);
    return;
  }

  try {
    // 初始化处理文件列表，记录初始状态
    batchProcessingFiles.value = selectedFiles.value.map(file => {
      // 找到原始数字step值
      const originalFile = tableData.value.find(f => f.id === file.id);
      const originalStep = originalFile ? originalFile.step : 0;
      
      // 如果step是字符串，需要转换回数字
      let numericStep = 0;
      if (typeof originalStep === 'string') {
        // 从stepStatusMap反向查找数字
        for (const [key, value] of Object.entries(stepStatusMap)) {
          if (value === originalStep) {
            numericStep = parseInt(key);
            break;
          }
        }
      } else {
        numericStep = originalStep || 0;
      }
      
      console.log(`文件 ${file.filename} 初始状态:`, {
        id: file.id,
        filename: file.filename,
        originalStep: originalStep,
        numericStep: numericStep,
        update_time: file.update_time
      });
      
      return {
        id: file.id,
        filename: file.filename,
        currentStatus: 'waiting', // waiting, processing, completed, failed
        initialStep: numericStep,
        initialUpdateTime: file.update_time || new Date().toISOString(),
        errorMessage: '' // 存储错误信息
      };
    });

    // 显示处理弹窗
    batchProcessingVisible.value = true;
    isBatchProcessing.value = true;
    batchProcessComplete.value = false;
    batchCurrentStep.value = 1;
    batchCurrentStatus.value = '排队等待中';
    batchProcessingProgress.value = 0;
    
    // 开始进度模拟
    startBatchProcessingSimulation();

    // 获取选中文件的id数组
    const fileIds = selectedFiles.value.map(file => file.id);
    console.log('要转写的文件ID数组：', fileIds);
    console.log('初始文件状态：', batchProcessingFiles.value);
    
    // 调用转写接口
    const res = await workflow(id.value, 4, fileIds);
    console.log('转写接口返回数据：', res);
    
    if (res.data.code === 200) {
      const results = res.data.data.results || [];
      const stat = res.data.data.stat || {};
      
      console.log('解析的results:', results);
      console.log('解析的stat:', stat);
      
      // 更新文件状态，标记推送失败的文件
      batchProcessingFiles.value.forEach(file => {
        const result = results.find(r => r.id === file.id);
        if (result) {
          if (result.status === 'failed') {
            file.currentStatus = 'failed';
            file.errorMessage = result.msg;
          } else if (result.status === 'success') {
            file.currentStatus = 'waiting';
          }
        }
      });
      
      // 检查是否有推送成功的文件
      const successCount = stat.success || 0;
      const failedCount = stat.failed || 0;
      
      if (successCount === 0 && failedCount > 0) {
        // 全部推送失败 - 显示为处理完成状态，因为已经有了明确的结果
        isBatchProcessing.value = false;
        batchProcessComplete.value = true;
        ElMessage.warning(`批量转写完成，共${failedCount}个文件因不符合条件而跳过`);
      } else if (failedCount > 0) {
        // 部分推送失败
        ElMessage.warning(`${successCount}个文件推送成功，${failedCount}个文件跳过处理`);
        // 继续检查处理状态
        setTimeout(checkBatchProcessingStatus, 3000);
      } else {
        // 全部推送成功
        ElMessage.success('转写任务已启动');
        // 开始检查处理状态
        setTimeout(checkBatchProcessingStatus, 3000);
      }
    } else {
      // 接口调用失败，关闭弹窗
      isBatchProcessing.value = false;
      batchProcessingVisible.value = false;
      ElMessage.error(res.data.msg || '启动转写失败');
    }
  } catch (error) {
    console.error('启动转写失败:', error);
    isBatchProcessing.value = false;
    batchProcessingVisible.value = false;
    ElMessage.error('启动转写失败，请稍后重试');
  }
};

// 开始批量处理进度模拟
const startBatchProcessingSimulation = () => {
  let progress = 0;
  
  batchProcessingTimer = setInterval(() => {
    // 进度增长但不会到达100%，最高到95%
    progress += Math.random() * 2 + 0.5; // 随机增加0.5-2.5%
    
    // 限制最高到95%，留给真实状态检查来完成
    if (progress > 95) {
      progress = 95;
    }
    
    // 更新步骤状态
    if (progress < 20) {
      batchCurrentStep.value = 1;
      batchCurrentStatus.value = '排队等待中';
      batchEstimatedTime.value = '约3-5分钟';
    } else if (progress < 80) {
      batchCurrentStep.value = 2;
      batchCurrentStatus.value = '正在转写中';
      batchEstimatedTime.value = '约1-3分钟';
    } else {
      batchCurrentStep.value = 3;
      batchCurrentStatus.value = '即将完成';
      batchEstimatedTime.value = '不到1分钟';
    }
    
    batchProcessingProgress.value = Math.floor(progress);
  }, 1200); // 每1.2秒更新一次
};

// 检查批量处理状态
const checkBatchProcessingStatus = async () => {
  try {
    // 获取文件详情信息
    const res = await getTaskDetail(id.value, 1, 1000, {}); // 获取所有文件
    if (res.data.code === 200) {
      const allFiles = res.data.data.list;
      let hasChanges = false;
      let completedCount = 0;
      
      // 检查每个处理中的文件状态
      batchProcessingFiles.value.forEach(processingFile => {
        const currentFile = allFiles.find(f => f.id === processingFile.id);
        if (currentFile) {
          // 对比update_time和step来判断状态变化
          const timeChanged = new Date(currentFile.update_time) > new Date(processingFile.initialUpdateTime);
          const stepChanged = currentFile.step !== processingFile.initialStep;
          
          console.log(`文件 ${processingFile.filename} 状态检查:`, {
            timeChanged,
            stepChanged,
            currentStep: currentFile.step,
            initialStep: processingFile.initialStep,
            currentTime: currentFile.update_time,
            initialTime: processingFile.initialUpdateTime
          });
          
          if (timeChanged || stepChanged) {
            hasChanges = true;
            
            // 根据step状态判断文件处理状态
            if (currentFile.step >= 8) { // 8表示所有处理完成
              processingFile.currentStatus = 'completed';
              completedCount++;
            } else if (currentFile.step >= 7) { // 7表示正在文本转写
              processingFile.currentStatus = 'processing';
            } else {
              processingFile.currentStatus = 'waiting';
            }
            
            // 更新初始状态，避免重复检测
            processingFile.initialStep = currentFile.step;
            processingFile.initialUpdateTime = currentFile.update_time;
          } else {
            // 没有变化的文件，根据当前状态计数
            if (processingFile.currentStatus === 'completed') {
              completedCount++;
            }
          }
        }
      });
      
      // 更新整体进度
      const totalFiles = batchProcessingFiles.value.length;
      const progress = Math.floor((completedCount / totalFiles) * 100);
      
      // 如果有真实进度，停止模拟进度
      if (hasChanges && batchProcessingTimer) {
        clearInterval(batchProcessingTimer);
        batchProcessingTimer = null;
        batchProcessingProgress.value = progress;
      }
      
      // 检查是否全部完成
      if (completedCount === totalFiles) {
        // 全部处理完成
        isBatchProcessing.value = false;
        batchProcessComplete.value = true;
        batchProcessingProgress.value = 100;
        batchCurrentStep.value = 3;
        batchCurrentStatus.value = '全部处理完成';
        
        // 清理定时器
        if (batchProcessingTimer) {
          clearInterval(batchProcessingTimer);
          batchProcessingTimer = null;
        }
        if (batchStatusCheckTimer) {
          clearTimeout(batchStatusCheckTimer);
          batchStatusCheckTimer = null;
        }
        
        ElMessage.success(`批量转写处理已完成！共完成 ${completedCount} 个文件`);
        
        // 更新任务统计信息
        const statsRes = await getTaskStatistics(id.value);
        if (statsRes.data.code === 200) {
          fileINfo.value = statsRes.data.data;
        }
      } else {
        // 仍在处理中，继续检查
        if (isBatchProcessing.value) {
          batchStatusCheckTimer = setTimeout(checkBatchProcessingStatus, 3000); // 3秒后再次检查
        }
      }
    }
  } catch (error) {
    console.error('检查批量处理状态失败:', error);
    // 出错时也继续检查
    if (isBatchProcessing.value) {
      batchStatusCheckTimer = setTimeout(checkBatchProcessingStatus, 5000); // 5秒后重试
    }
  }
};

// 处理弹窗关闭
const handleBatchDialogClose = () => {
  // 清理定时器
  if (batchProcessingTimer) {
    clearInterval(batchProcessingTimer);
    batchProcessingTimer = null;
  }
  if (batchStatusCheckTimer) {
    clearTimeout(batchStatusCheckTimer);
    batchStatusCheckTimer = null;
  }
  
  // 重置状态
  isBatchProcessing.value = false;
  batchProcessComplete.value = false;
};

// 关闭批量处理弹窗
const closeBatchProcessingDialog = () => {
  handleBatchDialogClose();
  batchProcessingVisible.value = false;
  
  // 刷新表格数据
  getTaskDetail1();
};

// 获取文件状态样式类
const getFileStatusClass = (status) => {
  switch (status) {
    case 'waiting': return 'file-waiting';
    case 'processing': return 'file-processing';
    case 'completed': return 'file-completed';
    case 'failed': return 'file-failed';
    default: return '';
  }
};

// 获取文件标签类型
const getFileTagType = (status) => {
  switch (status) {
    case 'waiting': return 'info';
    case 'processing': return 'warning';
    case 'completed': return 'success';
    case 'failed': return 'danger';
    default: return 'info';
  }
};

// 获取文件状态文本
const getFileStatusText = (status) => {
  switch (status) {
    case 'waiting': return '等待处理';
    case 'processing': return '正在转写';
    case 'completed': return '已完成';
    case 'failed': return '跳过处理';
    default: return '未知状态';
  }
};

// 刷新任务数据
const refreshTaskData = async () => {
  try {
    const res = await getTaskStatistics(id.value);
    if (res.data.code === 200) {
      fileINfo.value = res.data.data;
      ElMessage.success('任务数据已刷新');
    }
    getTaskDetail1(); // 刷新表格
  } catch (error) {
    console.error('刷新任务数据失败:', error);
    ElMessage.error('刷新失败');
  }
};

// 刷新任务统计信息
const refreshTaskStatistics = async () => {
  try {
    const res = await getTaskStatistics(id.value);
    if (res.data.code === 200) {
      fileINfo.value = res.data.data;
      console.log('刷新任务统计信息：', fileINfo.value);
    } else if (res.data.code === 401) {
      router.push("/login");
    } else {
      ElMessage.error(res.data.msg || "获取任务统计失败");
    }
  } catch (error) {
    console.error("获取任务统计失败:", error);
    ElMessage.error("获取任务统计失败，请稍后重试");
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

// 获取任务状态文本
const getTaskStatusText = (status) => {
  const statusMap = {
    1: '空任务',
    2: '已检测', 
    3: '已转写',
    4: '处理中',
    5: '暂停中'
  };
  return statusMap[status] || '未知状态';
};

// 获取任务状态样式类
const getTaskStatusClass = (status) => {
  const classMap = {
    1: 'status-empty',
    2: 'status-detected',
    3: 'status-transcribed', 
    4: 'status-processing',
    5: 'status-paused'
  };
  return classMap[status] || 'status-unknown';
};
</script>

<style scoped lang="scss">
.operationBox {
  position: relative;
  width: 100%;
  height: 100%;
}

/* 任务头部样式 */
.task-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.task-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  
  .el-icon {
    font-size: 28px;
  }
}

.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .task-number {
    font-size: 14px;
    opacity: 0.9;
  }
  
  .task-status {
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
    
    &.status-empty {
      background: rgba(144, 147, 153, 0.2);
      color: #909399;
    }
    
    &.status-detected {
      background: rgba(103, 194, 58, 0.2);
      color: #67C23A;
    }
    
    &.status-transcribed {
      background: rgba(64, 158, 255, 0.2);
      color: #409EFF;
    }
    
    &.status-processing {
      background: rgba(230, 162, 60, 0.2);
      color: #E6A23C;
    }
    
    &.status-paused {
      background: rgba(245, 108, 108, 0.2);
      color: #F56C6C;
    }
    
    &.status-unknown {
      background: rgba(144, 147, 153, 0.2);
      color: #909399;
    }
  }
}

.demo-tabs1,
.demo-tabs2,
.demo-tabs3,
.demo-tabs4,
.demo-tabs5 {
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

/* 任务信息卡片样式 */
.task-info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.info-card {
  border-radius: 8px;
  overflow: hidden;
}

.card-header-custom {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.card-content-custom {
  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .stat-label {
      font-size: 14px;
      color: #666;
    }
    
    .stat-value {
      font-size: 16px;
      font-weight: 600;
      
      &.primary { color: #409EFF; }
      &.success { color: #67C23A; }
      &.info { color: #909399; }
      &.warning { color: #E6A23C; }
    }
  }
  
  .progress-item {
    margin-bottom: 16px;
    
    .progress-label {
      font-size: 14px;
      color: #666;
      margin-bottom: 8px;
      display: block;
    }
  }
  
  .status-overview {
    display: flex;
    justify-content: center;
    align-items: center;
    
    .status-circle {
      text-align: center;
      
      .circle-progress {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(#409EFF calc(var(--progress) * 1%), #f0f0f0 0);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin: 0 auto 12px;
        
        &::before {
          content: '';
          width: 80px;
          height: 80px;
          background: white;
          border-radius: 50%;
          position: absolute;
        }
        
        .percentage {
          font-size: 24px;
          font-weight: 600;
          color: #333;
          z-index: 1;
        }
      }
      
      .status-label {
        font-size: 14px;
        color: #666;
      }
    }
  }
}

.task-details {
  margin-top: 20px;
}

/* 批量处理弹窗样式 */
.batch-processing-status,
.batch-process-complete {
  .processing-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e4e7ed;
  }

  .card-header {
    padding: 20px 24px;
    background: linear-gradient(135deg, #409eff, #67c23a);
    color: white;
    display: flex;
    align-items: center;
    gap: 12px;

    &.processing {
      background: linear-gradient(135deg, #e6a23c, #f56c6c);
    }

    &.success {
      background: linear-gradient(135deg, #67c23a, #5cb87a);
    }

    .header-icon {
      font-size: 24px;

      &.rotating {
        animation: rotating 2s linear infinite;
      }
    }

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .card-content {
    padding: 24px;
  }

  .status-info {
    margin-bottom: 24px;
  }

  .status-item {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    
    .label {
      color: #909399;
      margin-right: 12px;
      min-width: 80px;
    }

    .filename {
      color: #409eff;
      font-weight: 500;
    }

    .time {
      color: #67c23a;
      font-weight: 500;
    }
  }

  .progress-section {
    margin-bottom: 32px;
  }

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    span {
      font-weight: 500;
      color: #303133;
    }
  }

  .steps-section {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;
    padding: 20px 0;
  }

  .step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    
    .step-icon {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #f5f7fa;
      border: 2px solid #e4e7ed;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #c0c4cc;
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 8px;
      transition: all 0.3s ease;
    }

    .step-text {
      font-size: 14px;
      color: #909399;
      text-align: center;
      transition: all 0.3s ease;
    }

    &.active {
      .step-icon {
        background: #409eff;
        border-color: #409eff;
        color: white;
        
        .el-icon {
          font-size: 16px;
          animation: rotating 2s linear infinite;
        }
      }

      .step-text {
        color: #409eff;
        font-weight: 500;
      }
    }

    &.completed {
      .step-icon {
        background: #67c23a;
        border-color: #67c23a;
        color: white;
      }

      .step-text {
        color: #67c23a;
        font-weight: 500;
      }
    }
  }

  .step-line {
    flex: 1;
    height: 2px;
    background: #e4e7ed;
    margin: 0 16px;
    position: relative;
    top: -18px;
    transition: all 0.3s ease;

    &.completed {
      background: #67c23a;
    }
  }

  .processing-tips {
    margin-top: 20px;

    :deep(.el-alert__content) {
      p {
        margin: 4px 0;
        font-size: 14px;
        line-height: 1.5;
      }
    }
  }

  .success-message {
    color: #606266;
    margin-bottom: 20px;
    line-height: 1.6;
    text-align: center;
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 12px;
  }

  // 文件列表相关样式
  .file-list-section,
  .completed-files {
    margin: 20px 0;
    
    h4 {
      margin: 0 0 12px 0;
      color: #303133;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .file-list {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    background: #fafafa;
  }

  .file-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #e4e7ed;
    transition: all 0.3s ease;

    &:last-child {
      border-bottom: none;
    }

    &.file-waiting {
      background: #f8f9fa;
    }

    &.file-processing {
      background: #fff7e6;
      border-left: 3px solid #e6a23c;
    }

    &.file-completed,
    &.completed {
      background: #f0f9ff;
      border-left: 3px solid #67c23a;
    }

    &.file-failed {
      background: #fef0f0;
      border-left: 3px solid #f56c6c;
    }

    .file-info {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;

      .file-icon {
        color: #909399;
        font-size: 16px;
      }

      .file-name {
        color: #303133;
        font-size: 14px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .file-status {
      display: flex;
      align-items: center;
      gap: 8px;

      .loading-icon {
        color: #e6a23c;
        animation: rotating 2s linear infinite;
        font-size: 14px;
      }

      .success-icon {
        color: #67c23a;
        font-size: 14px;
      }

      .error-icon {
        color: #e6a23c;
        font-size: 14px;
      }

      .warning-icon {
        color: #e6a23c;
        font-size: 14px;
      }
    }

    .skip-reason {
      margin-top: 6px;
      padding: 6px 8px;
      background: #fdf6ec;
      border: 1px solid #f5dab1;
      border-radius: 4px;
      font-size: 12px;
      line-height: 1.4;
      
      .reason-label {
        color: #e6a23c;
        font-weight: 500;
      }
      
      .reason-text {
        color: #606266;
        word-break: break-word;
      }
    }
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 已完成行的样式 - 简化版本，只处理勾选框 */
:deep(.completed-row) {
  .el-checkbox {
    pointer-events: none;
    opacity: 0.5;
  }
}
</style>
