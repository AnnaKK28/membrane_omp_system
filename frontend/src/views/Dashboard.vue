<template>
  <div class="dashboard">
    <h2>📊 系统概览</h2>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon">🧪</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.solute_count || 0 }}</div>
            <div class="stat-label">污染物种类</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon">🧇</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.membrane_count || 0 }}</div>
            <div class="stat-label">膜材料种类</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.experiment_count || 0 }}</div>
            <div class="stat-label">实验记录</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.rejection_stats?.avg || 0 }}%</div>
            <div class="stat-label">平均截留率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="quick-actions">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>🚀 快速操作</span>
          </template>
          <div class="quick-buttons">
            <el-button type="primary" size="large" @click="$router.push('/predict')">
              预测截留率
            </el-button>
            <el-button type="success" size="large" @click="$router.push('/solute')">
              查询污染物
            </el-button>
            <el-button type="warning" size="large" @click="$router.push('/membrane')">
              查询膜材料
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>📋 模型信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="模型类型">XGBoost Regressor</el-descriptions-item>
            <el-descriptions-item label="特征数量">6</el-descriptions-item>
            <el-descriptions-item label="特征向量">[MW, charge, logD, MWCO, contact_angle, zeta_potential]</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="top-lists">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>🏆 热门膜材料</span>
          </template>
          <el-table :data="stats.top_membranes || []" stripe>
            <el-table-column prop="membrane_name" label="膜名称" />
            <el-table-column prop="experiment_count" label="实验次数" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>🔬 热门污染物</span>
          </template>
          <el-table :data="stats.top_solutes || []" stripe>
            <el-table-column prop="solute_name" label="污染物名称" />
            <el-table-column prop="experiment_count" label="实验次数" width="100" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { predictApi } from '@/api'

const stats = ref({})

onMounted(async () => {
  try {
    const res = await predictApi.statistics()
    if (res.data.success) {
      stats.value = res.data.data
    }
  } catch (e) {
    console.warn('Failed to load stats:', e)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  font-size: 36px;
  margin-right: 15px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.quick-actions {
  margin-bottom: 20px;
}

.quick-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.top-lists {
  margin-bottom: 20px;
}
</style>