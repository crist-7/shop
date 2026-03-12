<template>
  <div class="dashboard-container">
    <!-- 顶部数据卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="data-card sales-card" body-style="padding: 20px">
          <div class="card-title">总销售额</div>
          <div class="num">¥ 126,560.00</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card orders-card" body-style="padding: 20px">
          <div class="card-title">订单总量</div>
          <div class="num">8,846</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card visits-card" body-style="padding: 20px">
          <div class="card-title">今日访问</div>
          <div class="num">1,203</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="data-card users-card" body-style="padding: 20px">
          <div class="card-title">新增用户</div>
          <div class="num">235</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ECharts 数据趋势图 -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div style="font-weight: bold; font-size: 16px;">
          <el-icon style="margin-right: 8px; vertical-align: middle;"><TrendCharts /></el-icon>
          <span style="vertical-align: middle;">近七天业务趋势分析</span>
        </div>
      </template>
      <!-- 给 ECharts 准备的容器，必须有宽高 -->
      <div ref="chartRef" style="height: 400px; width: 100%;"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';

// 获取 DOM 元素的引用
const chartRef = ref<HTMLElement | null>(null);
let myChart: echarts.ECharts | null = null;

// 初始化图表的方法
const initChart = () => {
  if (!chartRef.value) return;

  // 销毁旧实例，防止热更新时内存泄漏或重复渲染
  if (myChart) {
    myChart.dispose();
  }

  myChart = echarts.init(chartRef.value);

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } }
    },
    legend: {
      data: ['销售额 (百元)', '订单量', '新增用户'],
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: '销售额 (百元)',
        type: 'line',
        smooth: true, // 平滑曲线
        lineStyle: { width: 3, color: '#f56c6c' },
        showSymbol: false,
        areaStyle: {
          opacity: 0.1,
          color: '#f56c6c'
        },
        data: [120, 132, 101, 134, 90, 230, 210]
      },
      {
        name: '订单量',
        type: 'line',
        smooth: true,
        lineStyle: { width: 3, color: '#409EFF' },
        showSymbol: false,
        areaStyle: {
          opacity: 0.1,
          color: '#409EFF'
        },
        data: [220, 182, 191, 234, 290, 330, 310]
      },
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        lineStyle: { width: 2, color: '#e6a23c', type: 'dashed' },
        showSymbol: false,
        data: [15, 23, 20, 35, 42, 60, 50]
      }
    ]
  };

  myChart.setOption(option);
};

// 监听窗口大小变化，让图表自适应缩放 (极其关键的细节！)
const resizeChart = () => {
  myChart?.resize();
};

onMounted(() => {
  // 确保 DOM 渲染完毕后再初始化图表
  setTimeout(() => {
    initChart();
  }, 100);

  window.addEventListener('resize', resizeChart);
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart);
  myChart?.dispose();
});
</script>

<style scoped>
.dashboard-container {
  padding: var(--space-xl);
}
.card-title {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 15px;
  font-weight: 500;
  letter-spacing: 0.5px;
}
.num {
  font-size: 42px;
  font-weight: 900;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 数据卡片渐变色样式 */
.data-card {
  border: none !important;
  border-radius: var(--radius-xl) !important;
  overflow: hidden;
  transition: all var(--transition-base) !important;
}

.data-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl) !important;
}

.sales-card {
  background: var(--gradient-sales) !important;
}

.orders-card {
  background: var(--gradient-orders) !important;
}

.visits-card {
  background: var(--gradient-visits) !important;
}

.users-card {
  background: var(--gradient-users) !important;
}

/* 图表卡片样式 */
.chart-card {
  border-radius: var(--radius-xl) !important;
  margin-top: var(--space-xl) !important;
  border: 1px solid var(--bg-tertiary);
}

.chart-card :deep(.el-card__header) {
  background-color: var(--bg-tertiary) !important;
  border-bottom: 1px solid var(--bg-tertiary) !important;
  font-weight: 600;
  font-size: 18px;
  color: var(--text-primary);
}
</style>