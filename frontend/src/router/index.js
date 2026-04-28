import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import SoluteSearch from '@/views/SoluteSearch.vue'
import MembraneSearch from '@/views/MembraneSearch.vue'
import Prediction from '@/views/Prediction.vue'
import Visualization from '@/views/Visualization.vue'
import DataBrowser from '@/views/DataBrowser.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/solute', name: 'SoluteSearch', component: SoluteSearch },
  { path: '/membrane', name: 'MembraneSearch', component: MembraneSearch },
  { path: '/predict', name: 'Prediction', component: Prediction },
  { path: '/visualization', name: 'Visualization', component: Visualization },
  { path: '/data', name: 'DataBrowser', component: DataBrowser }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router