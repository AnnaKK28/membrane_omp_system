<template>
  <div class="visualization">
    <h2>📈 可视化分析</h2>

    <el-row :gutter="20" class="controls-row">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>🧪 选择污染物分析</span>
          </template>
          <el-select
            v-model="selectedSolute"
            placeholder="选择污染物..."
            filterable
            remote
            :remote-method="searchSolutes"
            :loading="loadingSolute"
            style="width: 100%"
            @change="loadMembraneComparison"
          >
            <el-option
              v-for="s in soluteOptions"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            />
          </el-select>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>🧇 选择膜材料分析</span>
          </template>
          <el-select
            v-model="selectedMembrane"
            placeholder="选择膜材料..."
            filterable
            remote
            :remote-method="searchMembranes"
            :loading="loadingMembrane"
            style="width: 100%"
            @change="loadSoluteComparison"
          >
            <el-option
              v-for="m in membraneOptions"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            />
          </el-select>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>📊 图表类型</span>
          </template>
          <el-select v-model="chartType" style="width: 100%">
            <el-option label="柱状图" value="bar" />
            <el-option label="折线图" value="line" />
          </el-select>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>🏆 不同膜对污染物的截留率对比</span>
          </template>
          <div ref="membraneChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>🔬 不同污染物在同一膜上的截留率对比</span>
          </template>
          <div ref="soluteChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { soluteApi, membraneApi, predictApi } from '@/api'

const membraneChartRef = ref(null)
const soluteChartRef = ref(null)
let membraneChart = null
let soluteChart = null

const selectedSolute = ref(null)
const selectedMembrane = ref(null)
const soluteOptions = ref([])
const membraneOptions = ref([])
const loadingSolute = ref(false)
const loadingMembrane = ref(false)
const chartType = ref('bar')

const membraneData = ref([])
const soluteData = ref([])

let soluteTimer = null
let membraneTimer = null

const searchSolutes = async (query) => {
  loadingSolute.value = true
  try {
    const res = await soluteApi.search(query)
    soluteOptions.value = res.data.data || []
  } finally {
    loadingSolute.value = false
  }
}

const searchMembranes = async (query) => {
  loadingMembrane.value = true
  try {
    const res = await membraneApi.search(query)
    membraneOptions.value = res.data.data || []
  } finally {
    loadingMembrane.value = false
  }
}

const loadMembraneComparison = async (soluteId) => {
  if (!soluteId) return
  try {
    const res = await predictApi.membraneComparison(soluteId)
    if (res.data.success) {
      membraneData.value = res.data.data.membranes || []
      renderMembraneChart()
    }
  } catch (e) {
    console.error('Load membrane comparison error:', e)
  }
}

const loadSoluteComparison = async (membraneId) => {
  if (!membraneId) return
  try {
    const res = await predictApi.soluteComparison(membraneId)
    if (res.data.success) {
      soluteData.value = res.data.data.solutes || []
      renderSoluteChart()
    }
  } catch (e) {
    console.error('Load solute comparison error:', e)
  }
}

const renderMembraneChart = () => {
  if (!membraneChart) {
    membraneChart = echarts.init(membraneChartRef.value)
  }

  const names = membraneData.value.map(d => d.name)
  const values = membraneData.value.map(d => d.rejection_rate)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { rotate: 45, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      name: '截留率 (%)',
      min: 0,
      max: 100
    },
    series: [{
      name: '截留率',
      type: chartType.value,
      data: values,
      itemStyle: { color: '#667eea' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }],
    grid: { bottom: 80 }
  }

  membraneChart.setOption(option)
}

const renderSoluteChart = () => {
  if (!soluteChart) {
    soluteChart = echarts.init(soluteChartRef.value)
  }

  const names = soluteData.value.map(d => d.name)
  const values = soluteData.value.map(d => d.rejection_rate)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { rotate: 45, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      name: '截留率 (%)',
      min: 0,
      max: 100
    },
    series: [{
      name: '截留率',
      type: chartType.value,
      data: values,
      itemStyle: { color: '#764ba2' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }],
    grid: { bottom: 80 }
  }

  soluteChart.setOption(option)
}

watch(chartType, () => {
  renderMembraneChart()
  renderSoluteChart()
})

const handleResize = () => {
  membraneChart?.resize()
  soluteChart?.resize()
}

onMounted(() => {
  searchSolutes('')
  searchMembranes('')
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  membraneChart?.dispose()
  soluteChart?.dispose()
})
</script>

<style scoped>
.visualization {
  max-width: 1400px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.controls-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 350px;
  width: 100%;
}
</style>