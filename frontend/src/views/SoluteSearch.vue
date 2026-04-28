<template>
  <div class="solute-search">
    <h2>🔍 污染物查询系统</h2>

    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-input
            v-model="searchName"
            placeholder="输入污染物名称进行模糊搜索..."
            clearable
            size="large"
            @input="handleSearch"
          >
            <template #prefix>
              <span>🔍</span>
            </template>
          </el-input>
        </el-col>
        <el-col :span="12">
          <el-select
            v-model="selectedSolute"
            placeholder="或从列表中选择..."
            filterable
            remote
            :remote-method="searchSolutes"
            :loading="loading"
            size="large"
            style="width: 100%"
            @change="handleSelect"
          >
            <el-option
              v-for="s in searchResults"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            >
              <span>{{ s.name }}</span>
              <span style="color: #999; font-size: 12px; margin-left: 10px">MW: {{ s.MW }}</span>
            </el-option>
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="selectedSoluteData" class="result-card">
      <template #header>
        <span>📋 污染物详情: {{ selectedSoluteData.name }}</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="污染物名称">{{ selectedSoluteData.name }}</el-descriptions-item>
        <el-descriptions-item label="分子量 (MW)">{{ selectedSoluteData.MW }}</el-descriptions-item>
        <el-descriptions-item label="表面电荷 (charge)">{{ selectedSoluteData.charge }}</el-descriptions-item>
        <el-descriptions-item label="分配系数 (logD)">{{ selectedSoluteData.logD }}</el-descriptions-item>
      </el-descriptions>

      <div class="action-buttons">
        <el-button type="primary" @click="goToPredict(selectedSoluteData.id)">
          使用此污染物预测
        </el-button>
      </div>
    </el-card>

    <el-card class="all-solutes">
      <template #header>
        <span>📜 所有污染物列表 (分页)</span>
      </template>
      <el-table :data="solutes" stripe v-loading="loadingList">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="污染物名称" />
        <el-table-column prop="MW" label="分子量 (MW)" width="120" />
        <el-table-column prop="charge" label="电荷" width="100" />
        <el-table-column prop="logD" label="logD" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="selectSolute(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadSolutes"
          @current-change="loadSolutes"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { soluteApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()

const searchName = ref('')
const searchResults = ref([])
const selectedSolute = ref(null)
const selectedSoluteData = ref(null)
const solutes = ref([])
const loading = ref(false)
const loadingList = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

let searchTimer = null

const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    searchSolutes(searchName.value)
  }, 300)
}

const searchSolutes = async (query) => {
  loading.value = true
  try {
    const res = await soluteApi.search(query)
    searchResults.value = res.data.data || []
  } catch (e) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleSelect = (soluteId) => {
  const solute = searchResults.value.find(s => s.id === soluteId)
  if (solute) {
    selectedSoluteData.value = solute
  }
}

const selectSolute = (solute) => {
  selectedSolute.value = solute.id
  selectedSoluteData.value = solute
}

const loadSolutes = async () => {
  loadingList.value = true
  try {
    const res = await soluteApi.list(currentPage.value, pageSize.value)
    solutes.value = res.data.data || []
    total.value = res.data.pagination?.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loadingList.value = false
  }
}

const goToPredict = (soluteId) => {
  router.push({ path: '/predict', query: { solute: soluteId } })
}

onMounted(() => {
  loadSolutes()
  searchSolutes('')
})
</script>

<style scoped>
.solute-search {
  max-width: 1200px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.search-card {
  margin-bottom: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.action-buttons {
  margin-top: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>