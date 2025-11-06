import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'
import type { Provider, AIConfig, AIGenerateRequest, AssistantInfo, AssistantRequest, AssistantResponse, MultipleVersionsResponse } from '@/types/ai'

export const useAIStore = defineStore('ai', () => {
  const STORAGE_KEY = 'ai_config'
  const generating = ref(false)
  const generatedContent = ref('')
  const error = ref<string | null>(null)
  const config = ref<AIConfig>({
    provider: 'openai',
    model_name: 'gpt-4',
    temperature: 0.7,
    max_tokens: 2000
  })

  // Load persisted config
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      config.value = { ...config.value, ...parsed }
    }
  } catch { /* ignore */ }

  async function generateContent(req: AIGenerateRequest) {
    generating.value = true
    error.value = null
    try {
      const response = await request.post('/api/ai/generate', {
        novel_id: req.novel_id,
        prompt: req.prompt,
        context_type: req.context_type,
        max_tokens: req.max_tokens ?? config.value.max_tokens ?? 2000,
        temperature: req.temperature ?? config.value.temperature ?? 0.7,
        provider: req.provider ?? config.value.provider,
        base_url: req.base_url ?? config.value.base_url,
        api_key: req.api_key ?? config.value.api_key,
        model_name: req.model_name ?? config.value.model_name
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
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(config.value)) } catch {}
  }

  function clearGenerated() {
    generatedContent.value = ''
    error.value = null
  }

  // AI Assistants
  const assistants = ref<AssistantInfo[]>([])

  async function fetchAssistants() {
    try {
      const response = await request.get('/api/ai-assistants/')
      assistants.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    }
  }

  async function generateWithAssistant(req: AssistantRequest): Promise<string> {
    generating.value = true
    error.value = null
    try {
      const response = await request.post<AssistantResponse>('/api/ai-assistants/generate', {
        role: req.role,
        novel_id: req.novel_id,
        user_input: req.user_input,
        provider: req.provider ?? config.value.provider,
        model_name: req.model_name ?? config.value.model_name,
        base_url: req.base_url ?? config.value.base_url,
        api_key: req.api_key ?? config.value.api_key,
        temperature: req.temperature ?? config.value.temperature ?? 0.7,
        max_tokens: req.max_tokens ?? config.value.max_tokens ?? 2000
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

  async function generateMultipleVersions(req: AssistantRequest, numVersions: number = 2): Promise<string[]> {
    if (req.role !== 'novelist') {
      throw new Error('Multiple versions only supported for novelist role')
    }
    generating.value = true
    error.value = null
    try {
      const response = await request.post<MultipleVersionsResponse>(`/api/ai-assistants/generate-multiple?num_versions=${numVersions}`, {
        role: req.role,
        novel_id: req.novel_id,
        user_input: req.user_input,
        provider: req.provider ?? config.value.provider,
        model_name: req.model_name ?? config.value.model_name,
        base_url: req.base_url ?? config.value.base_url,
        api_key: req.api_key ?? config.value.api_key,
        temperature: req.temperature ?? config.value.temperature ?? 0.7
      })
      return response.data.versions
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    } finally {
      generating.value = false
    }
  }

  return {
    generating,
    generatedContent,
    error,
    config,
    generateContent,
    updateConfig,
    clearGenerated,
    assistants,
    fetchAssistants,
    generateWithAssistant,
    generateMultipleVersions
  }
})
