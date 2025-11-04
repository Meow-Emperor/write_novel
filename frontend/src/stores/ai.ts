/**
 * AI服务状态管理Store
 * 管理AI配置、内容生成和错误处理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

// AI提供商类型
export type Provider = 'openai' | 'anthropic' | 'custom'

/**
 * AI配置接口
 */
export interface AIConfig {
  provider: Provider  // AI提供商
  model_name: string  // 模型名称
  base_url?: string  // 自定义API端点
  api_key?: string  // API密钥
  temperature?: number  // 温度参数（控制随机性）
  max_tokens?: number  // 最大生成token数
  fallback_provider?: Provider  // 备用提供商
}

/**
 * AI生成请求接口
 */
export interface AIRequest {
  novel_id: string  // 关联的小说ID
  prompt: string  // 用户提示词
  context_type: 'character' | 'world' | 'plot' | 'content'  // 上下文类型
  max_tokens?: number  // 最大生成token数
  provider?: Provider  // AI提供商
  base_url?: string  // 自定义API端点
  api_key?: string  // API密钥
  model_name?: string  // 模型名称
}

export const useAIStore = defineStore('ai', () => {
  // 状态变量
  const generating = ref(false)  // 是否正在生成中
  const generatedContent = ref('')  // 生成的内容
  const error = ref<string | null>(null)  // 错误信息
  const config = ref<AIConfig>({  // AI配置
    provider: 'openai',
    model_name: 'gpt-4',
    temperature: 0.7,
    max_tokens: 2000
  })

  /**
   * 使用AI生成内容
   * @param request AI生成请求参数
   * @returns 生成的内容文本
   */
  async function generateContent(request: AIRequest) {
    generating.value = true
    error.value = null
    try {
      const response = await axios.post('/api/ai/generate', {
        novel_id: request.novel_id,
        prompt: request.prompt,
        context_type: request.context_type,
        max_tokens: request.max_tokens ?? config.value.max_tokens ?? 2000,
        provider: request.provider ?? config.value.provider,
        base_url: request.base_url ?? config.value.base_url,
        api_key: request.api_key ?? config.value.api_key,
        model_name: request.model_name ?? config.value.model_name
      })
      generatedContent.value = response.data.content
      return response.data.content
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    } finally {
      generating.value = false
    }
  }

  /**
   * 更新AI配置
   * @param newConfig 新的配置项（部分更新）
   */
  function updateConfig(newConfig: Partial<AIConfig>) {
    config.value = { ...config.value, ...newConfig }
  }

  /**
   * 清除生成的内容和错误信息
   */
  function clearGenerated() {
    generatedContent.value = ''
    error.value = null
  }

  return {
    generating,
    generatedContent,
    error,
    config,
    generateContent,
    updateConfig,
    clearGenerated
  }
})
