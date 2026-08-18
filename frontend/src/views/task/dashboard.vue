<template>
  <div class="task-dashboard">
    <el-row :gutter="16">
      <!-- 总览卡片 -->
      <el-col :span="6" v-for="card in summaryCards" :key="card.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value" :style="{ color: card.color }">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <!-- 任务状态分布 -->
      <el-col :span="12">
        <el-card>
          <template #header><span>任务状态分布</span></template>
          <div ref="statusChartRef" style="height:350px"></div>
        </el-card>
      </el-col>
      <!-- 优先级分布 -->
      <el-col :span="12">
        <el-card>
          <template #header><span>优先级分布</span></template>
          <div ref="priorityChartRef" style="height:350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <!-- 任务种类分布 -->
      <el-col :span="12">
        <el-card>
          <template #header><span>任务种类分布</span></template>
          <div ref="categoryChartRef" style="height:350px"></div>
        </el-card>
      </el-col>
      <!-- 难度分布 -->
      <el-col :span="12">
        <el-card>
          <template #header><span>难度等级分布</span></template>
          <div ref="difficultyChartRef" style="height:350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 按人员统计 -->
    <el-card style="margin-top:16px">
      <template #header><span>按人员统计</span></template>
      <el-table :data="personStats" v-loading="personLoading" stripe>
        <el-table-column prop="owner__username" label="用户名" width="120" />
        <el-table-column prop="owner__nickname" label="昵称" width="120" />
        <el-table-column prop="total" label="任务总数" width="100" />
        <el-table-column prop="completed" label="已完成" width="100" />
        <el-table-column prop="in_progress" label="进行中" width="100" />
        <el-table-column label="完成率" min-width="150">
          <template #default="{ row }">
            <el-progress
              :percentage="row.total ? Math.round(row.completed / row.total * 100) : 0"
              :stroke-width="12"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 绩效统计（仅主管/管理员可见） -->
    <el-card v-if="showPerformance" style="margin-top:16px">
      <template #header><span>绩效汇总</span></template>
      <div ref="performanceChartRef" style="height:400px"></div>
      <el-table :data="performanceStats" v-loading="perfLoading" stripe style="margin-top:16px">
        <el-table-column prop="task__owner__username" label="用户名" width="120" />
        <el-table-column prop="task__owner__nickname" label="昵称" width="120" />
        <el-table-column prop="task_count" label="已评分任务数" width="120" />
        <el-table-column prop="sum_score" label="总积分" width="120" sortable />
        <el-table-column prop="avg_score" label="平均积分" width="120" sortable />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getTaskStatsSummary, getTaskStatsByPerson, getPerformanceSummary } from '@/api'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const showPerformance = computed(() => userStore.isAdmin || userStore.permissions.includes('*'))

// 图表 refs
const statusChartRef = ref(null)
const priorityChartRef = ref(null)
const categoryChartRef = ref(null)
const difficultyChartRef = ref(null)
const performanceChartRef = ref(null)
let charts = []

// 总览数据
const summaryCards = ref([
  { label: '任务总数', value: 0, color: '#409eff' },
  { label: '进行中', value: 0, color: '#e6a23c' },
  { label: '已完成', value: 0, color: '#67c23a' },
  { label: '待审核', value: 0, color: '#f56c6c' },
])

// 人员统计
const personStats = ref([])
const personLoading = ref(false)

// 绩效统计
const performanceStats = ref([])
const perfLoading = ref(false)

function initChart(ref, option) {
  if (!ref) return
  const chart = echarts.init(ref)
  chart.setOption(option)
  charts.push(chart)
  return chart
}

function makePieOption(data, title) {
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      name: title,
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: Object.entries(data).map(([name, value]) => ({ name, value })),
    }],
  }
}

function makeBarOption(data, title) {
  const names = Object.keys(data)
  const values = Object.values(data)
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    series: [{
      name: title,
      type: 'bar',
      data: values,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#409eff' },
          { offset: 1, color: '#79bbff' },
        ]),
      },
    }],
    grid: { left: 40, right: 20, top: 20, bottom: 60 },
  }
}

async function fetchSummary() {
  try {
    const res = await getTaskStatsSummary()
    const data = res.data || {}
    summaryCards.value = [
      { label: '任务总数', value: data.total || 0, color: '#409eff' },
      { label: '进行中', value: data.by_status?.['进行中'] || 0, color: '#e6a23c' },
      { label: '已完成', value: data.by_status?.['已完成'] || 0, color: '#67c23a' },
      { label: '待审核', value: data.by_status?.['待审核'] || 0, color: '#f56c6c' },
    ]
    await nextTick()
    initChart(statusChartRef.value, makePieOption(data.by_status || {}, '任务状态'))
    initChart(priorityChartRef.value, makePieOption(data.by_priority || {}, '优先级'))
    initChart(difficultyChartRef.value, makePieOption(data.by_difficulty || {}, '难度等级'))
    // 种类用柱状图
    const catData = {}
    ;(data.by_category || []).forEach(c => { catData[c.category__name || '未分类'] = c.count })
    initChart(categoryChartRef.value, makeBarOption(catData, '任务种类'))
  } catch (e) { /* ignore */ }
}

async function fetchPersonStats() {
  personLoading.value = true
  try {
    const res = await getTaskStatsByPerson()
    personStats.value = res.data?.by_owner || []
  } finally {
    personLoading.value = false
  }
}

async function fetchPerformanceStats() {
  if (!showPerformance.value) return
  perfLoading.value = true
  try {
    const res = await getPerformanceSummary()
    performanceStats.value = res.data?.by_person || []
    await nextTick()
    const names = performanceStats.value.map(p => p.task__owner__username || '未知')
    const scores = performanceStats.value.map(p => p.sum_score || 0)
    initChart(performanceChartRef.value, {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: names, axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', name: '总积分' },
      series: [{
        name: '总积分',
        type: 'bar',
        data: scores,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#67c23a' },
            { offset: 1, color: '#a3e36b' },
          ]),
        },
        label: { show: true, position: 'top' },
      }],
      grid: { left: 50, right: 20, top: 20, bottom: 60 },
    })
  } finally {
    perfLoading.value = false
  }
}

function disposeCharts() {
  charts.forEach(c => c.dispose())
  charts = []
}

onMounted(() => {
  fetchSummary()
  fetchPersonStats()
  fetchPerformanceStats()
})

onUnmounted(disposeCharts)
</script>

<style scoped>
.task-dashboard {
  padding: 20px;
}
.stat-card {
  text-align: center;
  padding: 10px 0;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>