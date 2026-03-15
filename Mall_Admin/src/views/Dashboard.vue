<template>
  <!--
    Dashboard.vue - 电商后台仪表盘

    功能特性：
    1. 顶部数据卡片（今日销售额、新增用户、订单转化率、待发货订单）
    2. 双图表布局：左侧折线图 + 右侧环形图
    3. 底部最新订单动态表格
    4. 暗黑模式完美适配
    5. 响应式图表（vueuse useResizeObserver）
  -->
  <div class="dashboard-container">
    <!-- ============================================================ -->
    <!-- 顶部数据卡片 -->
    <!-- ============================================================ -->
    <div class="stats-grid">
      <!-- 今日销售额 -->
      <div class="stat-card sales-card">
        <div class="card-glow"></div>
        <div class="stat-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">今日销售额</div>
          <div class="stat-value">
            <span class="currency">¥</span>
            <span class="number">{{ formatNumber(mockStats.todaySales) }}</span>
          </div>
          <div class="stat-footer">
            <span class="trend up">
              <el-icon><Top /></el-icon>
              +12.5%
            </span>
            <span class="compare">较昨日</span>
          </div>
        </div>
      </div>

      <!-- 新增用户 -->
      <div class="stat-card users-card">
        <div class="card-glow"></div>
        <div class="stat-icon">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">新增用户</div>
          <div class="stat-value">
            <span class="number">{{ formatNumber(mockStats.newUsers) }}</span>
            <span class="unit">人</span>
          </div>
          <div class="stat-footer">
            <span class="trend up">
              <el-icon><Top /></el-icon>
              +8.3%
            </span>
            <span class="compare">较昨日</span>
          </div>
        </div>
      </div>

      <!-- 订单转化率 -->
      <div class="stat-card conversion-card">
        <div class="card-glow"></div>
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">订单转化率</div>
          <div class="stat-value">
            <span class="number">{{ mockStats.conversionRate }}</span>
            <span class="unit">%</span>
          </div>
          <div class="stat-footer">
            <span class="trend up">
              <el-icon><Top /></el-icon>
              +2.1%
            </span>
            <span class="compare">较上周</span>
          </div>
        </div>
      </div>

      <!-- 待发货订单 -->
      <div class="stat-card pending-card">
        <div class="card-glow"></div>
        <div class="stat-icon">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">待发货订单</div>
          <div class="stat-value">
            <span class="number highlight">{{ formatNumber(mockStats.pendingOrders) }}</span>
            <span class="unit">笔</span>
          </div>
          <div class="stat-footer">
            <span class="trend warning">
              <el-icon><Warning /></el-icon>
              需处理
            </span>
            <span class="compare">紧急</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- 双图表布局 -->
    <!-- ============================================================ -->
    <div class="charts-grid">
      <!-- 左侧：折线图（近7天销售额走势） -->
      <div class="chart-card line-chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <el-icon><TrendCharts /></el-icon>
            <span>近7天销售额走势</span>
          </div>
          <div class="chart-actions">
            <el-radio-group v-model="chartType" size="small">
              <el-radio-button label="line">折线图</el-radio-button>
              <el-radio-button label="area">面积图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-body">
          <div ref="lineChartRef" class="echarts-container"></div>
        </div>
      </div>

      <!-- 右侧：环形图（商品分类销售占比） -->
      <div class="chart-card pie-chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <el-icon><PieChart /></el-icon>
            <span>商品分类销售占比</span>
          </div>
          <div class="chart-actions">
            <el-button size="small" text @click="refreshPieChart">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
        <div class="chart-body">
          <div ref="pieChartRef" class="echarts-container"></div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- 最新订单动态 -->
    <!-- ============================================================ -->
    <div class="order-table-card">
      <div class="table-header">
        <div class="table-title">
          <el-icon><Document /></el-icon>
          <span>最新订单动态</span>
          <el-tag type="danger" size="small" effect="dark" class="new-badge">
            {{ recentOrders.length }} 条新订单
          </el-tag>
        </div>
        <el-button type="primary" text @click="handleViewAllOrders">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>

      <el-table
        :data="recentOrders"
        style="width: 100%"
        class="order-table"
        :header-cell-style="{ background: 'transparent' }"
      >
        <el-table-column prop="orderSn" label="订单号" min-width="160">
          <template #default="{ row }">
            <span class="order-sn">{{ row.orderSn }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="customer" label="客户" min-width="100" />
        <el-table-column prop="amount" label="金额" min-width="100" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="下单时间" min-width="160" />
        <el-table-column label="操作" min-width="80" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewOrder(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ============================================================ -->
    <!-- 订单详情对话框 -->
    <!-- ============================================================ -->
    <el-dialog
      v-model="dialogVisible"
      title="订单详情"
      width="700px"
      :close-on-click-modal="false"
      class="order-detail-dialog"
    >
      <div v-if="orderDetail" class="order-detail-content">
        <!-- 订单基本信息 -->
        <div class="detail-section">
          <h4>订单信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="订单号">{{ orderDetail.orderSn }}</el-descriptions-item>
            <el-descriptions-item label="订单状态">
              <el-tag :type="getStatusType(orderDetail.status)" size="small">
                {{ orderDetail.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="订单金额">
              <span class="amount">¥{{ orderDetail.amount?.toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="下单时间">{{ orderDetail.createTime }}</el-descriptions-item>
            <el-descriptions-item label="收货人">{{ orderDetail.customer }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ orderDetail.phone || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="收货地址" :span="2">{{ orderDetail.address || '未填写' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 商品清单 -->
        <div class="detail-section" v-if="orderDetail.goods && orderDetail.goods.length > 0">
          <h4>商品清单</h4>
          <el-table :data="orderDetail.goods" size="small">
            <el-table-column prop="name" label="商品名称" />
            <el-table-column prop="quantity" label="数量" width="80" align="center" />
            <el-table-column prop="price" label="单价" width="100" align="right">
              <template #default="{ row }">¥{{ row.price }}</template>
            </el-table-column>
            <el-table-column label="小计" width="100" align="right">
              <template #default="{ row }">¥{{ (row.quantity * row.price).toFixed(2) }}</template>
            </el-table-column>
          </el-table>
        </div>
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
 * - @vueuse/core（响应式监听）
 * - Element Plus（UI 组件）
 *
 * 功能：
 * 1. 数据卡片展示关键指标
 * 2. ECharts 图表可视化
 * 3. 响应式布局适配
 * 4. 暗黑模式完美支持
 */

import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { useResizeObserver } from '@vueuse/core';
import {
  Money,
  UserFilled,
  TrendCharts,
  Box,
  Top,
  Warning,
  Document,
  Refresh,
  ArrowRight,
  PieChart,
} from '@element-plus/icons-vue';
import { getRecentOrders, getOrderDetail } from '@/api/orders';

// ============================================================
// 路由
// ============================================================

const router = useRouter();

// ============================================================
// Mock 数据（后续可替换为真实 API）
// ============================================================

/** 顶部统计卡片数据 */
const mockStats = reactive({
  todaySales: 128456,      // 今日销售额
  newUsers: 328,           // 新增用户
  conversionRate: 15.8,    // 订单转化率
  pendingOrders: 42,       // 待发货订单
});

/** 近7天销售数据 */
const salesTrendData = reactive({
  dates: ['3/9', '3/10', '3/11', '3/12', '3/13', '3/14', '3/15'],
  sales: [18500, 22300, 19800, 25600, 28900, 24600, 32100],
  orders: [65, 78, 72, 89, 95, 82, 108],
});

/** 商品分类销售占比数据 */
const categorySalesData = ref([
  { name: '手机数码', value: 35 },
  { name: '电脑办公', value: 25 },
  { name: '家用电器', value: 18 },
  { name: '服饰鞋包', value: 12 },
  { name: '食品生鲜', value: 10 },
]);

/** 最近订单数据 */
const recentOrders = ref<any[]>([]);

// ============================================================
// 图表相关
// ============================================================

/** 折线图容器引用 */
const lineChartRef = ref<HTMLElement | null>(null);
/** 环形图容器引用 */
const pieChartRef = ref<HTMLElement | null>(null);
/** 折线图实例 */
let lineChart: echarts.ECharts | null = null;
/** 环形图实例 */
let pieChart: echarts.ECharts | null = null;
/** 图表类型（折线/面积） */
const chartType = ref('area');

/**
 * 初始化折线图/面积图
 */
const initLineChart = () => {
  if (!lineChartRef.value) return;

  // 销毁旧实例
  lineChart?.dispose();
  lineChart = echarts.init(lineChartRef.value);

  const isArea = chartType.value === 'area';

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#fff' },
      axisPointer: {
        type: 'cross',
        crossStyle: { color: '#999' },
      },
    },
    legend: {
      data: ['销售额', '订单量'],
      top: 10,
      textStyle: { color: 'rgba(255, 255, 255, 0.7)' },
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
      data: salesTrendData.dates,
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.6)' },
    },
    yAxis: [
      {
        type: 'value',
        name: '销售额',
        nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
        axisLabel: {
          color: 'rgba(255, 255, 255, 0.6)',
          formatter: (value: number) => (value / 10000).toFixed(1) + 'w',
        },
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.08)', type: 'dashed' } },
      },
      {
        type: 'value',
        name: '订单量',
        nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.6)' },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        yAxisIndex: 0,
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#8b5cf6' },
            { offset: 1, color: '#6366f1' },
          ]),
        },
        itemStyle: {
          color: '#8b5cf6',
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: isArea
          ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(139, 92, 246, 0.4)' },
                { offset: 1, color: 'rgba(139, 92, 246, 0.05)' },
              ]),
            }
          : undefined,
        data: salesTrendData.sales,
      },
      {
        name: '订单量',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#f472b6' },
            { offset: 1, color: '#ec4899' },
          ]),
        },
        itemStyle: {
          color: '#f472b6',
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: isArea
          ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(244, 114, 182, 0.4)' },
                { offset: 1, color: 'rgba(244, 114, 182, 0.05)' },
              ]),
            }
          : undefined,
        data: salesTrendData.orders,
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

  // 销毁旧实例
  pieChart?.dispose();
  pieChart = echarts.init(pieChartRef.value);

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#fff' },
      formatter: '{b}: {c}% ({d}%)',
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 13,
      },
      itemWidth: 12,
      itemHeight: 12,
      itemGap: 16,
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
          borderColor: 'rgba(15, 23, 42, 0.8)',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#fff',
          },
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        labelLine: { show: false },
        data: categorySalesData.value.map((item, index) => ({
          ...item,
          itemStyle: {
            color: [
              '#8b5cf6',
              '#6366f1',
              '#ec4899',
              '#f59e0b',
              '#10b981',
            ][index],
          },
        })),
      },
    ],
  };

  pieChart.setOption(option);
};

/**
 * 刷新环形图
 */
const refreshPieChart = () => {
  // 模拟数据刷新
  categorySalesData.value = categorySalesData.value.map((item) => ({
    ...item,
    value: Math.floor(Math.random() * 30) + 10,
  }));
  initPieChart();
};

// ============================================================
// 响应式图表（使用 vueuse）
// ============================================================

useResizeObserver(lineChartRef, () => {
  lineChart?.resize();
});

useResizeObserver(pieChartRef, () => {
  pieChart?.resize();
});

// 监听图表类型变化
watch(chartType, () => {
  nextTick(() => {
    initLineChart();
  });
});

// ============================================================
// 工具函数
// ============================================================

/**
 * 格式化数字（超过1万显示 x.x万）
 */
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  }
  return num.toLocaleString('zh-CN');
};

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

// ============================================================
// 订单相关
// ============================================================

/** 对话框可见性 */
const dialogVisible = ref(false);
/** 订单详情 */
const orderDetail = ref<any>(null);

/**
 * 加载最近订单
 */
const loadRecentOrders = async () => {
  try {
    const response = await getRecentOrders();
    recentOrders.value = response.map((item: any) => ({
      id: item.id,
      orderSn: item.order_sn,
      customer: item.customer,
      amount: item.amount,
      status: item.status,
      createTime: item.create_time,
      phone: item.phone,
      address: item.address,
      goods: item.goods || [],
    }));
  } catch (error) {
    console.error('加载最近订单失败:', error);
    // 使用 mock 数据
    recentOrders.value = [
      { id: 1, orderSn: '20260315001', customer: '张三', amount: 128.5, status: '待发货', createTime: '2026-03-15 10:30' },
      { id: 2, orderSn: '20260315002', customer: '李四', amount: 256.0, status: '已支付', createTime: '2026-03-15 11:15' },
      { id: 3, orderSn: '20260315003', customer: '王五', amount: 89.9, status: '成功', createTime: '2026-03-15 12:45' },
      { id: 4, orderSn: '20260315004', customer: '赵六', amount: 320.8, status: '待支付', createTime: '2026-03-15 14:20' },
      { id: 5, orderSn: '20260315005', customer: '孙七', amount: 45.0, status: '已取消', createTime: '2026-03-15 15:10' },
    ];
  }
};

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
    const response = await getOrderDetail(order.id);
    orderDetail.value = {
      orderSn: response.order_sn,
      status: response.pay_status,
      amount: response.order_mount,
      createTime: response.add_time,
      customer: response.signer_name,
      phone: response.signer_mobile,
      address: response.address,
      goods: response.goods || [],
    };
  } catch (error) {
    console.error('获取订单详情失败:', error);
    // 使用表格中的基本信息
    orderDetail.value = order;
  }
};

// ============================================================
// 生命周期
// ============================================================

onMounted(async () => {
  // 加载订单数据
  await loadRecentOrders();

  // 初始化图表
  nextTick(() => {
    initLineChart();
    initPieChart();
  });
});

onUnmounted(() => {
  // 销毁图表实例
  lineChart?.dispose();
  pieChart?.dispose();
});
</script>

<style scoped>
/* ============================================================ */
/* CSS 变量（暗黑主题） */
/* ============================================================ */

.dashboard-container {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: rgba(30, 41, 59, 0.7);
  --border-color: rgba(255, 255, 255, 0.1);
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.5);
  --gradient-purple: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  --gradient-pink: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  --gradient-blue: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  --gradient-orange: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.3);
  --radius-lg: 16px;
  --radius-md: 12px;
  --transition-base: 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  padding: var(--space-2xl, 40px);
  color: var(--text-primary);
}

/* ============================================================ */
/* 顶部数据卡片 */
/* ============================================================ */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-xl, 32px);
  margin-bottom: var(--space-2xl, 40px);
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  position: relative;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  padding: var(--space-xl, 32px);
  display: flex;
  align-items: center;
  gap: var(--space-lg, 24px);
  overflow: hidden;
  transition: all var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 卡片发光效果 */
.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.sales-card .card-glow {
  background: var(--gradient-purple);
}

.users-card .card-glow {
  background: var(--gradient-blue);
}

.conversion-card .card-glow {
  background: var(--gradient-pink);
}

.pending-card .card-glow {
  background: var(--gradient-orange);
}

/* 图标样式 */
.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.sales-card .stat-icon {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
}

.users-card .stat-icon {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}

.conversion-card .stat-icon {
  background: rgba(236, 72, 153, 0.15);
  color: #f472b6;
}

.pending-card .stat-icon {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

/* 内容样式 */
.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 12px;
}

.stat-value .currency {
  font-size: 20px;
  color: var(--text-secondary);
}

.stat-value .number {
  font-size: 32px;
  font-weight: 700;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-value .number.highlight {
  color: #fbbf24;
  -webkit-text-fill-color: #fbbf24;
}

.stat-value .unit {
  font-size: 14px;
  color: var(--text-muted);
  margin-left: 4px;
}

.stat-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}

.trend.up {
  color: #10b981;
}

.trend.warning {
  color: #fbbf24;
}

.compare {
  color: var(--text-muted);
}

/* ============================================================ */
/* 图表区域 */
/* ============================================================ */

.charts-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--space-xl, 32px);
  margin-bottom: var(--space-2xl, 40px);
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg, 24px);
  border-bottom: 1px solid var(--border-color);
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-title .el-icon {
  font-size: 20px;
  color: #a78bfa;
}

.chart-body {
  padding: var(--space-lg, 24px);
  height: 350px;
}

.echarts-container {
  width: 100%;
  height: 100%;
}

/* ============================================================ */
/* 订单表格 */
/* ============================================================ */

.order-table-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg, 24px);
  border-bottom: 1px solid var(--border-color);
}

.table-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.table-title .el-icon {
  font-size: 20px;
  color: #a78bfa;
}

.new-badge {
  font-size: 11px;
}

/* 表格样式 */
.order-table {
  background: transparent !important;
}

.order-table :deep(.el-table__header) {
  background: rgba(0, 0, 0, 0.2);
}

.order-table :deep(.el-table__header th) {
  background: transparent !important;
  color: var(--text-secondary) !important;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color) !important;
}

.order-table :deep(.el-table__row) {
  background: transparent;
  transition: background-color 0.2s;
}

.order-table :deep(.el-table__row:hover > td) {
  background: rgba(255, 255, 255, 0.05) !important;
}

.order-table :deep(.el-table__cell) {
  background: transparent !important;
  border-bottom: 1px solid var(--border-color) !important;
  color: var(--text-primary);
}

.order-sn {
  font-family: 'SF Mono', 'Monaco', monospace;
  color: #a78bfa;
}

.amount {
  font-weight: 600;
  color: #10b981;
}

/* ============================================================ */
/* 对话框样式 */
/* ============================================================ */

.order-detail-dialog :deep(.el-dialog) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.order-detail-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--border-color);
  padding: 20px 24px;
  margin: 0;
}

.order-detail-dialog :deep(.el-dialog__title) {
  color: var(--text-primary);
  font-weight: 600;
}

.order-detail-dialog :deep(.el-dialog__body) {
  padding: 24px;
  color: var(--text-primary);
}

.order-detail-content {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.order-detail-dialog :deep(.el-descriptions) {
  --el-fill-color-blank: transparent;
}

.order-detail-dialog :deep(.el-descriptions__label) {
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.2);
}

.order-detail-dialog :deep(.el-descriptions__content) {
  color: var(--text-primary);
}

.order-detail-dialog :deep(.el-table) {
  background: transparent;
}

.order-detail-dialog :deep(.el-table th) {
  background: rgba(0, 0, 0, 0.2) !important;
  color: var(--text-secondary);
}

.order-detail-dialog :deep(.el-table td) {
  background: transparent !important;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

/* ============================================================ */
/* 响应式调整 */
/* ============================================================ */

@media (max-width: 768px) {
  .dashboard-container {
    padding: var(--space-lg, 24px);
  }

  .stat-card {
    padding: var(--space-lg, 24px);
  }

  .stat-icon {
    width: 52px;
    height: 52px;
    font-size: 24px;
  }

  .stat-value .number {
    font-size: 26px;
  }

  .chart-body {
    height: 280px;
    padding: var(--space-md, 16px);
  }

  .chart-header {
    padding: var(--space-md, 16px);
    flex-wrap: wrap;
    gap: 12px;
  }

  .chart-actions {
    width: 100%;
  }
}
</style>
