import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export type Provider = 'openai' | 'anthropic' | 'custom'

export interface AIConfig {
  provider: Provider
  model_name: string
  base_url?: string
  api_key?: string
  temperature?: number
  max_tokens?: number
  fallback_provider?: Provider
}

export interface AIRequest {
  novel_id: string
  prompt: string
  context_type: 'character' | 'world' | 'plot' | 'content'
  max_tokens?: number
  provider?: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export const useAIStore = defineStore('ai', () => {
  const generating = ref(false)
  const generatedContent = ref('')
  const error = ref<string | null>(null)
  const config = ref<AIConfig>({
    provider: 'openai',
    model_name: 'gpt-4',
    temperature: 0.7,
    max_tokens: 2000
  })

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

  function updateConfig(newConfig: Partial<AIConfig>) {
    config.value = { ...config.value, ...newConfig }
  }

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
