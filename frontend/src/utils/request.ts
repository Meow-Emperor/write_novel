import axios from 'axios'
import { ElMessage } from 'element-plus'
import { config } from '@/config'

const request = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
request.interceptors.request.use(
  (config) => {
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
    
    if (config.isDevelopment) {
      console.error('Response error:', error)
    }
    
    // Show error message
    ElMessage.error(message)
    
    return Promise.reject(error)
  }
)

export default request
