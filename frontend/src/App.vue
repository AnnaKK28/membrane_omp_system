<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🧪 Membrane OMP System</h1>
          <p class="subtitle">膜分离性能预测与有机污染物截留数据库系统</p>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu :default-active="$route.path" router class="sidebar-menu">
            <el-menu-item index="/">
              <span>📊 Dashboard</span>
            </el-menu-item>
            <el-menu-item index="/solute">
              <span>🔍 污染物查询</span>
            </el-menu-item>
            <el-menu-item index="/membrane">
              <span>🧇 膜材料查询</span>
            </el-menu-item>
            <el-menu-item index="/predict">
              <span>🤖 截留率预测</span>
            </el-menu-item>
            <el-menu-item index="/visualization">
              <span>📈 可视化</span>
            </el-menu-item>
            <el-menu-item index="/data">
              <span>📋 数据浏览</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { healthApi } from '@/api'

onMounted(async () => {
  try {
    const res = await healthApi.check()
    console.log('API Connected:', res.data)
  } catch (e) {
    console.warn('API not available:', e.message)
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f5f7fa;
}

#app {
  height: 100vh;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  height: auto !important;
  padding: 20px;
}

.header-content h1 {
  font-size: 24px;
  margin-bottom: 5px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.el-main {
  padding: 20px;
  overflow-y: auto;
}

.el-aside {
  background: white;
  box-shadow: 2px 0 8px rgba(0,0,0,0.05);
}
</style>