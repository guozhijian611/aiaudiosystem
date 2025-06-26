<template>
  <div class="dashboard-container">
    <div class="home-top">
      <div class="username">{{ username }}</div>
      <div class="welcome">欢迎使用AI语音转写降噪系统!</div>
    </div>
    <div class="home-bottom">
      <div class="home-item">
        <div class="title title1">
          <User
            style="width: 120px; height: 120px; margin-top: 10px; color: #fff"
          />
        </div>
        <div class="text text1">{{ username }}</div>
      </div>
      <div class="home-item" @click="goToTaskManagement">
        <div class="title title2">
          <Finished
            style="width: 120px; height: 120px; margin-top: 10px; color: #fff"
          />
        </div>
        <div class="text text2">已完成任务{{ taskStatus.transcribed }}个</div>
      </div>
      <div class="home-item" @click="showProcessingTasks">
        <div class="title title3">
            <Loading style="width: 120px; height: 120px; margin-top: 10px; color: #fff" />
        </div>
        <div class="text text3">执行中任务{{ taskStatus.processing }}个</div>
      </div>
    </div>
    
    <!-- 处理中任务弹窗 -->
    <Teleport to="body">
      <el-dialog
        v-model="processingTasksVisible"
        title="执行中任务"
        width="600px"
        :before-close="() => processingTasksVisible = false"
        append-to-body
      >
        <div v-if="taskStatus.processing_tasks && taskStatus.processing_tasks.length > 0">
          <div 
            v-for="task in taskStatus.processing_tasks" 
            :key="task.id"
            class="processing-task-item"
            @click="goToTaskOperation(task)"
          >
            <div class="task-header">
              <span class="task-name">{{ task.name }}</span>
              <span class="task-number">{{ task.number }}</span>
            </div>
            <div class="task-info">
              <span class="task-time">创建时间：{{ formatTime(task.create_time) }}</span>
              <span class="task-time">更新时间：{{ formatTime(task.update_time) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-tasks">
          <el-empty description="暂无执行中的任务" />
        </div>
        
        <template #footer>
          <el-button @click="processingTasksVisible = false">关闭</el-button>
          <el-button type="primary" @click="goToTaskManagement">查看所有任务</el-button>
        </template>
      </el-dialog>
    </Teleport>
  </div>
</template>

<script setup lang="ts" name="dashboard">
// import countup from '@/components/countup.vue';
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { use, registerMap } from "echarts/core";
import { BarChart, LineChart, PieChart, MapChart } from "echarts/charts";
import {obtainDetails} from "@/api/home";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  VisualMapComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import VChart from "vue-echarts";
import { dashOpt1, dashOpt2, mapOptions } from "./chart/options";
import chinaMap from "@/utils/china";
use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  LineChart,
  PieChart,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  VisualMapComponent,
  MapChart,
]);
registerMap("china", chinaMap);
const username: string | null = localStorage.getItem("vuems_name");
const taskStatus = ref({
  transcribed: 0,
  processing: 0,
  processing_tasks: []
});

// 弹窗相关状态
const processingTasksVisible = ref(false);

const router = useRouter();

// 跳转到后处理任务页面
const goToTaskManagement = () => {
  processingTasksVisible.value = false; // 关闭弹窗
  router.push({ name: 'task-management' });
};

// 显示处理中任务弹窗
const showProcessingTasks = () => {
  if (taskStatus.value.processing > 0) {
    processingTasksVisible.value = true;
  }
};

// 跳转到任务操作页面
const goToTaskOperation = (task) => {
  processingTasksVisible.value = false; // 关闭弹窗
  router.push({ 
    name: 'task-operation', 
    query: { 
      id: task.id,
      index: '4' // 直接跳转到第4个标签页（任务详情）
    } 
  });
};

// 格式化时间显示
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  return new Date(timeStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

onMounted(async () => {
  try {
    const res = await obtainDetails();
    console.log(180, res);
    
    if (res.data.code === 200) {
      taskStatus.value = res.data.data;
    }
  } catch (error) {
    console.error('获取任务状态失败:', error);
  }
})
</script>

<style>
.card-body {
  display: flex;
  align-items: center;
  height: 100px;
  padding: 0;
}
</style>
<style scoped lang="scss">
.dashboard-container {
  width: 100%;
  height: 100%;
}

.home-top {
  width: 90%;
  margin: 0 auto;
  height: 200px;
  background-color: #ffffff;
  margin-bottom: 50px;
  border-radius: 10px;
  box-sizing: border-box;
  padding: 20px;
  color: #2d8cf0;
  .username {
    font-size: 80px;
    margin-bottom: 20px;
  }
  .welcome {
    font-size: 40px;
  }
}
.home-bottom {
  width: 90%;
  margin: 0 auto;
  height: 500px;
  // background-color: #fff;
  // border-radius: 20px;
  display: flex;
  justify-content: space-between;
  .home-item {
    // margin: 50px;
    background-color: #fff;
    width: 26%;
    border-radius: 10px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .title {
      width: 100%;
      height: 30%;
      align-items: center;
      text-align: center;
    }
    .title1 {
      background-color: #2d8cf0;
    }
     .title2 {
      background-color: #14be61;
    }
     .title3 {
      background-color: #e9a745;
    }
    .text {
      text-align: center;
      font-size: 40px;
      line-height: 300px;
    }
    .text1 {
      color: #3b94f0;
    }
     .text2 {
      color: #14be61;
    }
     .text3 {
      color: #e9a745;
    }
  }
}
.card-content {
  flex: 1;
  text-align: center;
  font-size: 14px;
  color: #999;
  padding: 0 20px;
}

.card-num {
  font-size: 30px;
}

.card-icon {
  font-size: 50px;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
  color: #fff;
}

.bg1 {
  background: #2d8cf0;
}

.bg2 {
  background: #64d572;
}

.bg3 {
  background: #f25e43;
}

.bg4 {
  background: #e9a745;
}

.color1 {
  color: #2d8cf0;
}

.color2 {
  color: #64d572;
}

.color3 {
  color: #f25e43;
}

.color4 {
  color: #e9a745;
}

.chart {
  width: 100%;
  height: 400px;
}

.card-header {
  padding-left: 10px;
  margin-bottom: 20px;
}

.card-header-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.card-header-desc {
  font-size: 14px;
  color: #999;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  color: #000;
}

.timeline-time,
.timeline-desc {
  font-size: 12px;
  color: #787878;
}

.rank-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.rank-item-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f2f2f2;
  text-align: center;
  line-height: 40px;
  margin-right: 10px;
}

.rank-item-content {
  flex: 1;
}

.rank-item-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #343434;
  margin-bottom: 10px;
}

.rank-item-desc {
  font-size: 14px;
  color: #999;
}
.map-chart {
  width: 100%;
  height: 350px;
}
</style>

<style scoped>
/* 处理中任务弹窗样式 */
.processing-task-item {
  padding: 16px;
  margin-bottom: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.processing-task-item:hover {
  background: #e3f2fd;
  border-color: #2196f3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
}

.processing-task-item:last-child {
  margin-bottom: 0;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.task-number {
  font-size: 12px;
  color: #666;
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 12px;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-time {
  font-size: 12px;
  color: #888;
}

.no-tasks {
  text-align: center;
  padding: 40px 0;
}

/* 执行中任务卡片额外提示 */
.home-item:hover .text3::after {
  content: " (点击查看详情)";
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}
</style>
