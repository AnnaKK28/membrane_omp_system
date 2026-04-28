<template>
  <div class="data-browser">
    <h2>📋 实验数据浏览器</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="实验记录" name="experiments">
        <el-card>
          <el-table :data="experiments" stripe v-loading="loading" max-height="500">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="solute_name" label="污染物" />
            <el-table-column prop="membrane_name" label="膜材料" />
            <el-table-column prop="rejection_rate" label="截留率" width="100">
              <template #default="{ row }">
                <el-tag type="success">{{ row.rejection_rate }}%</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="MW" label="MW" width="80" />
            <el-table-column prop="charge" label="电荷" width="80" />
            <el-table-column prop="logD" label="logD" width="80" />
            <el-table-column prop="MWCO" label="MWCO" width="80" />
            <el-table-column prop="contact_angle" label="接触角" width="90" />
            <el-table-column prop="zeta_potential" label="Zeta电位" width="100" />
          </el-table>

          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="expPage"
              v-model:page-size="expPageSize"
              :total="expTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              @size-change="loadExperiments"
              @current-change="loadExperiments"
            />
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="污染物列表" name="solutes">
        <el-card>
          <el-table :data="solutes" stripe v-loading="loadingSolutes" max-height="500">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="MW" label="分子量" width="100" />
            <el-table-column prop="charge" label="电荷" width="100" />
            <el-table-column prop="logD" label="logD" width="100" />
          </el-table>

          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="solutePage"
              v-model:page-size="solutePageSize"
              :total="soluteTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              @size-change="loadSoluteList"
              @current-change="loadSoluteList"
            />
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="膜材料列表" name="membranes">
        <el-card>
          <el-table :data="membranes" stripe v-loading="loadingMembranes" max-height="500">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="membrane_type" label="类型" width="80" />
            <el-table-column prop="MWCO" label="MWCO" width="100" />
            <el-table-column prop="contact_angle" label="接触角" width="100" />
            <el-table-column prop="zeta_potential" label="Zeta电位" width="120" />
          </el-table>

          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="membranePage"
              v-model:page-size="membranePageSize"
              :total="membraneTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              @size-change="loadMembraneList"
              @current-change="loadMembraneList"
            />
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { soluteApi, membraneApi, predictApi } from '@/api'
import { ElMessage } from 'element-plus'

const activeTab = ref('experiments')

// Experiment data
const experiments = ref([])
const loading = ref(false)
const expPage = ref(1)
const expPageSize = ref(20)
const expTotal = ref(0)

// Solute data
const solutes = ref([])
const loadingSolutes = ref(false)
const solutePage = ref(1)
const solutePageSize = ref(20)
const soluteTotal = ref(0)

// Membrane data
const membranes = ref([])
const loadingMembranes = ref(false)
const membranePage = ref(1)
const membranePageSize = ref(20)
const membraneTotal = ref(0)

const loadExperiments = async () => {
  loading.value = true
  try {
    const res = await predictApi.experiments(expPage.value, expPageSize.value)
    experiments.value = res.data.data || []
    expTotal.value = res.data.pagination?.total || 0
  } catch (e) {
    ElMessage.error('加载实验数据失败')
  } finally {
    loading.value = false
  }
}

const loadSoluteList = async () => {
  loadingSolutes.value = true
  try {
    const res = await soluteApi.list(solutePage.value, solutePageSize.value)
    solutes.value = res.data.data || []
    soluteTotal.value = res.data.pagination?.total || 0
  } catch (e) {
    ElMessage.error('加载污染物数据失败')
  } finally {
    loadingSolutes.value = false
  }
}

const loadMembraneList = async () => {
  loadingMembranes.value = true
  try {
    const res = await membraneApi.list(membranePage.value, membranePageSize.value)
    membranes.value = res.data.data || []
    membraneTotal.value = res.data.pagination?.total || 0
  } catch (e) {
    ElMessage.error('加载膜材料数据失败')
  } finally {
    loadingMembranes.value = false
  }
}

onMounted(() => {
  loadExperiments()
  loadSoluteList()
  loadMembraneList()
})
</script>

<style scoped>
.data-browser {
  max-width: 1400px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>