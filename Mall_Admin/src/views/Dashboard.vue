<template>
  <!--
    Dashboard.vue - 电商后台仪表盘（亮色主题 + 真实数据）

    功能特性：
    1. 顶部统计卡片（商品总数、用户总数、订单总数、今日销售额占位）
    2. 双图表布局：折线图 + 环形图
    3. 最新订单动态表格（真实数据）
    4. 契合 Element Plus 亮色主题
  -->
  <div class="dashboard-container">
    <!-- ============================================================ -->
    <!-- 顶部统计卡片 -->
    <!-- ============================================================ -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card goods-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><Goods /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">商品总数</div>
              <div class="stat-value">{{ stats.goodsCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card users-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">用户总数</div>
              <div class="stat-value">{{ stats.userCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card orders-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">订单总数</div>
              <div class="stat-value">{{ stats.orderCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card sales-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日销售额</div>
              <div class="stat-value">
                <span class="currency">¥</span>{{ stats.todaySales }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ============================================================ -->
    <!-- 图表区域 -->
    <!-- ============================================================ -->
    <el-row :gutter="20" class="charts-row">
      <!-- 左侧：近7天销售额走势 -->
      <el-col :xs="24" :lg="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><TrendCharts /></el-icon>
                近7天销售额走势
              </span>
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button label="line">折线图</el-radio-button>
                <el-radio-button label="area">面积图</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="lineChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 右侧：商品分类占比 -->
      <el-col :xs="24" :lg="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><PieChart /></el-icon>
                商品分类占比
              </span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ============================================================ -->
    <!-- 最新订单动态 -->
    <!-- ============================================================ -->
    <el-card shadow="hover" class="order-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Document /></el-icon>
            最新订单动态
          </span>
          <el-button type="primary" link @click="handleViewAllOrders">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table
        :data="recentOrders"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="order_sn" label="订单号" min-width="160">
          <template #default="{ row }">
            <span class="order-sn">{{ row.order_sn || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="signer_name" label="客户" min-width="100">
          <template #default="{ row }">
            {{ row.signer_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="order_mount" label="金额" min-width="100" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ (row.order_mount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pay_status" label="状态" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.pay_status)" size="small">
              {{ row.pay_status || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="add_time" label="下单时间" min-width="160">
          <template #default="{ row }">
            {{ formatTime(row.add_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="80" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewOrder(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- ============================================================ -->
    <!-- 订单详情对话框 -->
    <!-- ============================================================ -->
    <el-dialog
      v-model="dialogVisible"
      title="订单详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="orderDetail" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ orderDetail.order_sn }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusType(orderDetail.pay_status)" size="small">
              {{ orderDetail.pay_status || '未知' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="订单金额">
            <span class="amount">¥{{ (orderDetail.order_mount || 0).toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="下单时间">{{ formatTime(orderDetail.add_time) }}</el-descriptions-item>
          <el-descriptions-item label="收货人">{{ orderDetail.signer_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ orderDetail.signer_mobile || '-' }}</el-descriptions-item>
          <el-descriptions-item label="收货地址" :span="2">{{ orderDetail.address || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <el-empty v-else description="订单详情加载失败" />

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * Dashboard.vue - 电商后台仪表盘
 *
 * 技术栈：
 * - Vue 3 Composition API
 * - ECharts 5（数据可视化）
 * - Element Plus（UI 组件）
 * - 真实 API 数据对接
 */

import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { useResizeObserver } from '@vueuse/core';
import {
  Goods,
  User,
  List,
  Money,
  TrendCharts,
  PieChart,
  Document,
  ArrowRight,
} from '@element-plus/icons-vue';
import { getUserList } from '@/api/users';
import { getGoodsList } from '@/api/goods';
import { getOrderList, getOrderDetail } from '@/api/orders';
import { getCategoryList } from '@/api/category';

// ============================================================
// 路由
// ============================================================

const router = useRouter();

// ============================================================
// 响应式状态
// ============================================================

/** 加载状态 */
const loading = ref(false);

/** 统计数据 */
const stats = reactive({
  goodsCount: 0,
  userCount: 0,
  orderCount: 0,
  todaySales: '--',
});

/** 最新订单列表 */
const recentOrders = ref<any[]>([]);

/** 分类列表（用于环形图） */
const categoryList = ref<any[]>([]);

/** 对话框可见性 */
const dialogVisible = ref(false);

/** 订单详情 */
const orderDetail = ref<any>(null);

/** 图表类型 */
const chartType = ref('area');

// ============================================================
// 图表相关
// ============================================================

const lineChartRef = ref<HTMLElement | null>(null);
const pieChartRef = ref<HTMLElement | null>(null);
let lineChart: echarts.ECharts | null = null;
let pieChart: echarts.ECharts | null = null;

/**
 * 初始化折线图/面积图
 */
const initLineChart = () => {
  if (!lineChartRef.value) return;

  lineChart?.dispose();
  lineChart = echarts.init(lineChartRef.value);

  const isArea = chartType.value === 'area';
  const dates = getLast7Days();

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: ['销售额', '订单量'],
      top: 10,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: !isArea,
      data: dates,
    },
    yAxis: [
      {
        type: 'value',
        name: '销售额',
        axisLabel: {
          formatter: (value: number) => (value / 1000).toFixed(0) + 'k',
        },
      },
      {
        type: 'value',
        name: '订单量',
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        yAxisIndex: 0,
        lineStyle: { width: 3, color: '#8b5cf6' },
        itemStyle: { color: '#8b5cf6' },
        areaStyle: isArea
          ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
                { offset: 1, color: 'rgba(139, 92, 246, 0.05)' },
              ]),
            }
          : undefined,
        // 占位数据，后续可对接真实统计接口
        data: [12500, 15300, 12800, 18600, 22100, 19800, 25600],
      },
      {
        name: '订单量',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        lineStyle: { width: 3, color: '#10b981' },
        itemStyle: { color: '#10b981' },
        areaStyle: isArea
          ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
                { offset: 1, color: 'rgba(16, 185, 129, 0.05)' },
              ]),
            }
          : undefined,
        // 占位数据，后续可对接真实统计接口
        data: [45, 58, 52, 72, 85, 78, 96],
      },
    ],
  };

  lineChart.setOption(option);
};

/**
 * 初始化环形图
 */
const initPieChart = () => {
  if (!pieChartRef.value) return;

  pieChart?.dispose();
  pieChart = echarts.init(pieChartRef.value);

  // 使用真实分类名称，数值为占位符
  const pieData = categoryList.value.length > 0
    ? categoryList.value.map((item, index) => ({
        name: item.name,
        value: Math.floor(Math.random() * 30) + 10, // 占位数值
      }))
    : [{ name: '暂无分类', value: 1 }];

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%',
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
    },
    series: [
      {
        name: '销售占比',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
          },
        },
        labelLine: { show: false },
        data: pieData,
      },
    ],
    color: ['#8b5cf6', '#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'],
  };

  pieChart.setOption(option);
};

/**
 * 获取最近7天日期
 */
const getLast7Days = (): string[] => {
  const dates: string[] = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`);
  }
  return dates;
};

// ============================================================
// 响应式图表
// ============================================================

useResizeObserver(lineChartRef, () => {
  lineChart?.resize();
});

useResizeObserver(pieChartRef, () => {
  pieChart?.resize();
});

watch(chartType, () => {
  nextTick(() => {
    initLineChart();
  });
});

// ============================================================
// 数据获取
// ============================================================

/**
 * 加载仪表盘数据
 */
const loadDashboardData = async () => {
  loading.value = true;

  try {
    // 并行请求所有数据
    const [goodsRes, usersRes, ordersRes, categoriesRes] = await Promise.all([
      getGoodsList({ page_size: 1 }).catch(() => null),
      getUserList({ page_size: 1 }).catch(() => null),
      getOrderList({ page_size: 5 }).catch(() => null),
      getCategoryList().catch(() => null),
    ]);

    // 处理商品总数
    if (goodsRes) {
      stats.goodsCount = (goodsRes as any).count || 0;
    }

    // 处理用户总数
    if (usersRes) {
      stats.userCount = (usersRes as any).count || 0;
    }

    // 处理订单总数和最近订单
    if (ordersRes) {
      stats.orderCount = (ordersRes as any).count || 0;
      const results = (ordersRes as any).results || [];
      recentOrders.value = results.slice(0, 5);
    }

    // 处理分类列表
    if (categoriesRes) {
      categoryList.value = (categoriesRes as any).results || (categoriesRes as any[]) || [];
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// ============================================================
// 工具函数
// ============================================================

/**
 * 获取订单状态标签类型
 */
const getStatusType = (status: string): string => {
  const map: Record<string, string> = {
    成功: 'success',
    已支付: 'success',
    待支付: 'warning',
    待发货: 'warning',
    已发货: 'primary',
    已完成: 'info',
    已取消: 'danger',
    超时关闭: 'danger',
  };
  return map[status] || 'info';
};

/**
 * 格式化时间
 */
const formatTime = (time: string): string => {
  if (!time) return '-';
  return time.replace('T', ' ').substring(0, 19);
};

// ============================================================
// 用户操作
// ============================================================

/**
 * 查看全部订单
 */
const handleViewAllOrders = () => {
  router.push('/orders');
};

/**
 * 查看订单详情
 */
const handleViewOrder = async (order: any) => {
  dialogVisible.value = true;
  orderDetail.value = null;

  try {
    const res = await getOrderDetail(order.id);
    orderDetail.value = res;
  } catch (error) {
    console.error('获取订单详情失败:', error);
    orderDetail.value = order;
  }
};

// ============================================================
// 生命周期
// ============================================================

onMounted(async () => {
  // 加载数据
  await loadDashboardData();

  // 初始化图表
  nextTick(() => {
    initLineChart();
    initPieChart();
  });
});

onUnmounted(() => {
  lineChart?.dispose();
  pieChart?.dispose();
});
</script>

<style scoped>
/* ============================================================ */
/* 容器 */
/* ============================================================ */

.dashboard-container {
  padding: 20px;
}

/* ============================================================ */
/* 统计卡片 */
/* ============================================================ */

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.goods-card .stat-icon {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.users-card .stat-icon {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.orders-card .stat-icon {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.sales-card .stat-icon {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stat-value .currency {
  font-size: 16px;
  font-weight: 600;
  margin-right: 2px;
}

/* ============================================================ */
/* 图表卡片 */
/* ============================================================ */

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.card-title .el-icon {
  color: var(--primary-color, #8b5cf6);
}

.chart-container {
  height: 350px;
}

/* ============================================================ */
/* 订单卡片 */
/* ============================================================ */

.order-card {
  border-radius: 12px;
}

.order-sn {
  font-family: 'SF Mono', 'Monaco', monospace;
  color: var(--primary-color, #8b5cf6);
}

.amount {
  font-weight: 600;
  color: #10b981;
}

/* ============================================================ */
/* 响应式调整 */
/* ============================================================ */

@media (max-width: 768px) {
  .dashboard-container {
    padding: 12px;
  }

  .stat-content {
    padding: 4px;
  }

  .stat-icon {
    width: 52px;
    height: 52px;
  }

  .stat-icon .el-icon {
    font-size: 24px;
  }

  .stat-value {
    font-size: 22px;
  }

  .chart-container {
    height: 280px;
  }
}
</style>
