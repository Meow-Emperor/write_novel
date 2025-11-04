/**
 * Vite配置文件
 * 配置Vue插件、路径别名和开发服务器代理
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  // Vue插件配置
  plugins: [vue()],
  
  // 模块解析配置
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')  // @ 别名指向 src 目录
    }
  },
  
  // 开发服务器配置
  server: {
    port: 5173,  // 前端开发服务器端口
    proxy: {
      // API请求代理到后端服务
      '/api': {
        target: 'http://backend:8000',  // 后端服务地址
        changeOrigin: true  // 修改请求头中的origin
      }
    }
  }
})
