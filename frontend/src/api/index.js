/**
 * API module for communicating with the backend.
 */
import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Solute APIs
export const soluteApi = {
  search: (name) => api.get('/solute/search', { params: { name } }),
  list: (page = 1, perPage = 20) => api.get('/solute/list', { params: { page, per_page: perPage } }),
  get: (id) => api.get(`/solute/${id}`)
}

// Membrane APIs
export const membraneApi = {
  search: (name) => api.get('/membrane/search', { params: { name } }),
  list: (page = 1, perPage = 20) => api.get('/membrane/list', { params: { page, per_page: perPage } }),
  get: (id) => api.get(`/membrane/${id}`)
}

// Prediction APIs
export const predictApi = {
  predict: (soluteId, membraneId) => api.post('/predict', { solute_id: soluteId, membrane_id: membraneId }),
  experiments: (page = 1, perPage = 20) => api.get('/experiments', { params: { page, per_page: perPage } }),
  statistics: () => api.get('/statistics'),
  membraneComparison: (soluteId) => api.get('/chart/membrane_comparison', { params: { solute_id: soluteId } }),
  soluteComparison: (membraneId) => api.get('/chart/solute_comparison', { params: { membrane_id: membraneId } })
}

// Health check
export const healthApi = {
  check: () => api.get('/health')
}

export default api