<template>
  <div>
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
      <div class="home-item">
        <div class="title title2">
          <Finished
            style="width: 120px; height: 120px; margin-top: 10px; color: #fff"
          />
        </div>
        <div class="text text2">已完成任务{{ taskStatus.transcribed }}个</div>
      </div>
      <div class="home-item">
        <div class="title title3">
            <Loading style="width: 120px; height: 120px; margin-top: 10px; color: #fff" />
        </div>
        <div class="text text3">执行中任务{{ taskStatus.processing }}个</div>
      </div>
    </div>
    <!-- <el-row :gutter="20" class="mgb20">
      <el-col :span="8">
        <el-card shadow="hover" body-class="card-body">
          <el-icon class="card-icon bg1">
            <User />
          </el-icon>
          <div class="card-content">
            <countup class="card-num color1" :end="6666" />
            <div>用户访问量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" body-class="card-body">
          <el-icon class="card-icon bg2">
            <ChatDotRound />
          </el-icon>
          <div class="card-content">
            <countup class="card-num color2" :end="168" />
            <div>系统消息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" body-class="card-body">
          <el-icon class="card-icon bg3">
            <Goods />
          </el-icon>
          <div class="card-content">
            <countup class="card-num color3" :end="8888" />
            <div>商品数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" body-class="card-body">
          <el-icon class="card-icon bg4">
            <ShoppingCartFull />
          </el-icon>
          <div class="card-content">
            <countup class="card-num color4" :end="568" />
            <div>今日订单量</div>
          </div>
        </el-card>
      </el-col>
    </el-row> -->

    <!-- <el-row :gutter="20" class="mgb20">
            <el-col :span="18">
                <el-card shadow="hover">
                    <div class="card-header">
                        <p class="card-header-title">订单动态</p>
                        <p class="card-header-desc">最近一周订单状态，包括订单成交量和订单退货量</p>
                    </div>
                    <v-chart class="chart" :option="dashOpt1" />
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover">
                    <div class="card-header">
                        <p class="card-header-title">品类分布</p>
                        <p class="card-header-desc">最近一个月销售商品的品类情况</p>
                    </div>
                    <v-chart class="chart" :option="dashOpt2" />
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="20">
            <el-col :span="7">
                <el-card shadow="hover" :body-style="{ height: '400px' }">
                    <div class="card-header">
                        <p class="card-header-title">时间线</p>
                        <p class="card-header-desc">最新的销售动态和活动信息</p>
                    </div>
                    <el-timeline>
                        <el-timeline-item v-for="(activity, index) in activities" :key="index" :color="activity.color">
                            <div class="timeline-item">
                                <div>
                                    <p>{{ activity.content }}</p>
                                    <p class="timeline-desc">{{ activity.description }}</p>
                                </div>
                                <div class="timeline-time">{{ activity.timestamp }}</div>
                            </div>
                        </el-timeline-item>
                    </el-timeline>
                </el-card>
            </el-col>
            <el-col :span="10">
                <el-card shadow="hover" :body-style="{ height: '400px' }">
                    <div class="card-header">
                        <p class="card-header-title">渠道统计</p>
                        <p class="card-header-desc">最近一个月的订单来源统计</p>
                    </div>
                    <v-chart class="map-chart" :option="mapOptions" />
                </el-card>
            </el-col>
            <el-col :span="7">
                <el-card shadow="hover" :body-style="{ height: '400px' }">
                    <div class="card-header">
                        <p class="card-header-title">排行榜</p>
                        <p class="card-header-desc">销售商品的热门榜单Top5</p>
                    </div>
                    <div>
                        <div class="rank-item" v-for="(rank, index) in ranks">
                            <div class="rank-item-avatar">{{ index + 1 }}</div>
                            <div class="rank-item-content">
                                <div class="rank-item-top">
                                    <div class="rank-item-title">{{ rank.title }}</div>
                                    <div class="rank-item-desc">销量：{{ rank.value }}</div>
                                </div>
                                <el-progress
                                    :show-text="false"
                                    striped
                                    :stroke-width="10"
                                    :percentage="rank.percent"
                                    :color="rank.color"
                                />
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row> -->
  </div>
</template>

<script setup lang="ts" name="dashboard">
// import countup from '@/components/countup.vue';
import { ref, reactive, onMounted } from "vue";
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
  processing: 0
});


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
