/**
 * Pinia状态管理入口
 * 创建Pinia实例并导出所有Store
 */
import { createPinia } from 'pinia'

// 创建Pinia实例
export const pinia = createPinia()

// 导出各个Store
export { useNovelStore } from './novel'  // 小说管理Store
export { useAIStore } from './ai'  // AI服务Store
