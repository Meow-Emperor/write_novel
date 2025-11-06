import axios from 'axios'
import { ElMessage } from 'element-plus'

// In development, use empty baseURL to rely on Vite proxy
// The proxy will forward /api/* to backend:8000
const request = axios.create({
  baseURL: '',  // Always use empty string to rely on Vite dev proxy
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
request.interceptors.request.use(
  (config) => {
    const adminToken = localStorage.getItem('admin_token')
    const url = config.url || ''
    const isAdminAPI = url.includes('/admin')
    const isAuthEndpoint = url.endsWith('/admin/login') || url.endsWith('/admin/register')
    if (adminToken && isAdminAPI && !isAuthEndpoint) {
      config.headers.Authorization = `Bearer ${adminToken}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Unknown error'

    console.error('Response error:', error)

    // Show error message
    ElMessage.error(message)

    return Promise.reject(error)
  }
)

export default request
