import { createPinia } from 'pinia'

export const pinia = createPinia()

export { useNovelStore } from './novel'
export { useAIStore } from './ai'
