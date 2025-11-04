/**
 * 前端应用入口文件
 * 初始化Vue应用、配置路由、状态管理和UI组件库
 */
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 创建Vue应用实例
const app = createApp(App)

// 注册Pinia状态管理
app.use(pinia)
// 注册Vue Router路由
app.use(router)
// 注册Element Plus UI组件库
app.use(ElementPlus)

// 挂载应用到DOM
app.mount('#app')
