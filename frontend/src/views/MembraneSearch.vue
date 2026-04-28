<template>
  <div class="membrane-search">
    <h2>🧇 膜材料查询系统</h2>

    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-input
            v-model="searchName"
            placeholder="输入膜材料名称进行模糊搜索..."
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
            v-model="selectedMembrane"
            placeholder="或从列表中选择..."
            filterable
            remote
            :remote-method="searchMembranes"
            :loading="loading"
            size="large"
            style="width: 100%"
            @change="handleSelect"
          >
            <el-option
              v-for="m in searchResults"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            >
              <span>{{ m.name }}</span>
              <span style="color: #999; font-size: 12px; margin-left: 10px">{{ m.membrane_type }}</span>
            </el-option>
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="selectedMembraneData" class="result-card">
      <template #header>
        <span>📋 膜材料详情: {{ selectedMembraneData.name }}</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="膜名称">{{ selectedMembraneData.name }}</el-descriptions-item>
        <el-descriptions-item label="膜类型">{{ selectedMembraneData.membrane_type }}</el-descriptions-item>
        <el-descriptions-item label="分子量截留量 (MWCO)">{{ selectedMembraneData.MWCO }}</el-descriptions-item>
        <el-descriptions-item label="接触角 (Contact angle)">{{ selectedMembraneData.contact_angle }}</el-descriptions-item>
        <el-descriptions-item label="表面电势 (Zeta potential)">{{ selectedMembraneData.zeta_potential }}</el-descriptions-item>
      </el-descriptions>

      <div class="action-buttons">
        <el-button type="primary" @click="goToPredict(selectedMembraneData.id)">
          使用此膜材料预测
        </el-button>
      </div>
    </el-card>

    <el-card class="all-membranes">
      <template #header>
        <span>📜 所有膜材料列表 (分页)</span>
      </template>
      <el-table :data="membranes" stripe v-loading="loadingList">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="膜名称" />
        <el-table-column prop="membrane_type" label="类型" width="80" />
        <el-table-column prop="MWCO" label="MWCO" width="100" />
        <el-table-column prop="contact_angle" label="接触角" width="100" />
        <el-table-column prop="zeta_potential" label="Zeta电位" width="120" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="selectMembrane(row)">查看</el-button>
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
          @size-change="loadMembranes"
          @current-change="loadMembranes"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { membraneApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()

const searchName = ref('')
const searchResults = ref([])
const selectedMembrane = ref(null)
const selectedMembraneData = ref(null)
const membranes = ref([])
const loading = ref(false)
const loadingList = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

let searchTimer = null

const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    searchMembranes(searchName.value)
  }, 300)
}

const searchMembranes = async (query) => {
  loading.value = true
  try {
    const res = await membraneApi.search(query)
    searchResults.value = res.data.data || []
  } catch (e) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleSelect = (membraneId) => {
  const membrane = searchResults.value.find(m => m.id === membraneId)
  if (membrane) {
    selectedMembraneData.value = membrane
  }
}

const selectMembrane = (membrane) => {
  selectedMembrane.value = membrane.id
  selectedMembraneData.value = membrane
}

const loadMembranes = async () => {
  loadingList.value = true
  try {
    const res = await membraneApi.list(currentPage.value, pageSize.value)
    membranes.value = res.data.data || []
    total.value = res.data.pagination?.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loadingList.value = false
  }
}

const goToPredict = (membraneId) => {
  router.push({ path: '/predict', query: { membrane: membraneId } })
}

onMounted(() => {
  loadMembranes()
  searchMembranes('')
})
</script>

<style scoped>
.membrane-search {
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