<template>
  <div class="prediction">
    <h2>🤖 截留率预测系统</h2>

    <el-alert
      title="模型说明"
      type="info"
      description="本系统使用XGBoost模型预测有机污染物在不同膜材料上的截留率。输入特征包括污染物分子量、电荷、logD以及膜材料的MWCO、接触角、Zeta电位。"
      show-icon
      :closable="false"
      style="margin-bottom: 20px"
    />

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="selector-card">
          <template #header>
            <span>🧪 选择污染物</span>
          </template>
          <el-select
            v-model="selectedSolute"
            placeholder="选择或搜索污染物..."
            filterable
            remote
            :remote-method="searchSolutes"
            :loading="loadingSolute"
            size="large"
            style="width: 100%"
            @change="handleSoluteChange"
          >
            <el-option
              v-for="s in soluteOptions"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            >
              <div class="solute-option">
                <span class="name">{{ s.name }}</span>
                <span class="props">MW: {{ s.MW }}, logD: {{ s.logD }}</span>
              </div>
            </el-option>
          </el-select>

          <div v-if="selectedSoluteData" class="selected-info">
            <el-descriptions :column="1" size="small" border style="margin-top: 15px">
              <el-descriptions-item label="名称">{{ selectedSoluteData.name }}</el-descriptions-item>
              <el-descriptions-item label="分子量 (MW)">{{ selectedSoluteData.MW }}</el-descriptions-item>
              <el-descriptions-item label="电荷 (charge)">{{ selectedSoluteData.charge }}</el-descriptions-item>
              <el-descriptions-item label="logD">{{ selectedSoluteData.logD }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="selector-card">
          <template #header>
            <span>🧇 选择膜材料</span>
          </template>
          <el-select
            v-model="selectedMembrane"
            placeholder="选择或搜索膜材料..."
            filterable
            remote
            :remote-method="searchMembranes"
            :loading="loadingMembrane"
            size="large"
            style="width: 100%"
            @change="handleMembraneChange"
          >
            <el-option
              v-for="m in membraneOptions"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            >
              <div class="membrane-option">
                <span class="name">{{ m.name }}</span>
                <span class="props">{{ m.membrane_type }}, MWCO: {{ m.MWCO }}</span>
              </div>
            </el-option>
          </el-select>

          <div v-if="selectedMembraneData" class="selected-info">
            <el-descriptions :column="1" size="small" border style="margin-top: 15px">
              <el-descriptions-item label="名称">{{ selectedMembraneData.name }}</el-descriptions-item>
              <el-descriptions-item label="类型">{{ selectedMembraneData.membrane_type }}</el-descriptions-item>
              <el-descriptions-item label="MWCO">{{ selectedMembraneData.MWCO }}</el-descriptions-item>
              <el-descriptions-item label="接触角">{{ selectedMembraneData.contact_angle }}</el-descriptions-item>
              <el-descriptions-item label="Zeta电位">{{ selectedMembraneData.zeta_potential }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="predict-card">
      <template #header>
        <span>🎯 预测结果</span>
      </template>

      <div class="predict-area">
        <el-button
          type="primary"
          size="large"
          :disabled="!selectedSolute || !selectedMembrane"
          :loading="predicting"
          @click="doPredict"
        >
          预测截留率
        </el-button>
      </div>

      <div v-if="predictionResult" class="result-display">
        <el-divider content-position="center">预测结果</el-divider>
        <div class="result-value">
          <span class="big-number">{{ predictionResult.rejection_rate }}%</span>
          <span class="label">预测截留率</span>
        </div>

        <el-descriptions :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="污染物">{{ predictionResult.solute_name }}</el-descriptions-item>
          <el-descriptions-item label="膜材料">{{ predictionResult.membrane_name }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="center">特征向量</el-divider>
        <el-table :data="featureTableData" stripe size="small">
          <el-table-column prop="feature" label="特征" />
          <el-table-column prop="value" label="值" />
          <el-table-column prop="source" label="来源" />
        </el-table>
      </div>

      <el-empty v-if="showEmpty" description="请先选择污染物和膜材料" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { soluteApi, membraneApi, predictApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()

const selectedSolute = ref(null)
const selectedMembrane = ref(null)
const selectedSoluteData = ref(null)
const selectedMembraneData = ref(null)
const soluteOptions = ref([])
const membraneOptions = ref([])
const loadingSolute = ref(false)
const loadingMembrane = ref(false)
const predicting = ref(false)
const predictionResult = ref(null)

let soluteTimer = null
let membraneTimer = null

const searchSolutes = async (query) => {
  loadingSolute.value = true
  try {
    const res = await soluteApi.search(query)
    soluteOptions.value = res.data.data || []
  } catch (e) {
    console.error('Search solute error:', e)
  } finally {
    loadingSolute.value = false
  }
}

const searchMembranes = async (query) => {
  loadingMembrane.value = true
  try {
    const res = await membraneApi.search(query)
    membraneOptions.value = res.data.data || []
  } catch (e) {
    console.error('Search membrane error:', e)
  } finally {
    loadingMembrane.value = false
  }
}

const handleSoluteChange = (soluteId) => {
  selectedSoluteData.value = soluteOptions.value.find(s => s.id === soluteId) || null
  predictionResult.value = null
}

const handleMembraneChange = (membraneId) => {
  selectedMembraneData.value = membraneOptions.value.find(m => m.id === membraneId) || null
  predictionResult.value = null
}

const doPredict = async () => {
  if (!selectedSolute.value || !selectedMembrane.value) {
    ElMessage.warning('请选择污染物和膜材料')
    return
  }

  predicting.value = true
  try {
    const res = await predictApi.predict(selectedSolute.value, selectedMembrane.value)
    if (res.data.success) {
      predictionResult.value = res.data.data
      ElMessage.success('预测完成')
    } else {
      ElMessage.error(res.data.error || '预测失败')
    }
  } catch (e) {
    ElMessage.error('预测请求失败: ' + e.message)
  } finally {
    predicting.value = false
  }
}

const featureTableData = computed(() => {
  if (!predictionResult.value?.features) return []
  const f = predictionResult.value.features
  return [
    { feature: 'MW', value: f.MW, source: '污染物' },
    { feature: 'charge', value: f.charge, source: '污染物' },
    { feature: 'logD', value: f.logD, source: '污染物' },
    { feature: 'MWCO', value: f.MWCO, source: '膜材料' },
    { feature: 'contact_angle', value: f.contact_angle, source: '膜材料' },
    { feature: 'zeta_potential', value: f.zeta_potential, source: '膜材料' }
  ]
})

const showEmpty = computed(() => !selectedSolute.value || !selectedMembrane.value)

onMounted(() => {
  searchSolutes('')
  searchMembranes('')

  // Handle query params for pre-selection
  if (route.query.solute) {
    selectedSolute.value = parseInt(route.query.solute)
    searchSolutes('').then(() => {
      handleSoluteChange(selectedSolute.value)
    })
  }
  if (route.query.membrane) {
    selectedMembrane.value = parseInt(route.query.membrane)
    searchMembranes('').then(() => {
      handleMembraneChange(selectedMembrane.value)
    })
  }
})
</script>

<style scoped>
.prediction {
  max-width: 1200px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.selector-card {
  margin-bottom: 20px;
}

.solute-option, .membrane-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.solute-option .props, .membrane-option .props {
  color: #999;
  font-size: 12px;
}

.predict-card {
  margin-top: 20px;
}

.predict-area {
  text-align: center;
  padding: 20px;
}

.result-display {
  text-align: center;
}

.result-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
}

.big-number {
  font-size: 64px;
  font-weight: bold;
  color: #667eea;
  line-height: 1.2;
}

.result-value .label {
  font-size: 18px;
  color: #666;
  margin-top: 10px;
}
</style>