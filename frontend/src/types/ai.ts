// Shared AI types to align frontend <-> backend contract

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

export type AIContextType = 'character' | 'world' | 'plot' | 'content' | 'chapter' | 'outline'

export interface AIGenerateRequest {
  novel_id: string
  prompt: string
  context_type: AIContextType
  max_tokens?: number
  temperature?: number
  provider?: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export interface AIGenerateResponse {
  content: string
  tokens_used: number
  model: string
}

export interface AICharacterGenerateRequest {
  novel_id: string
  character_role: 'protagonist' | 'antagonist' | 'supporting'
  character_traits?: string
  temperature?: number
  provider?: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export interface AIPlotGenerateRequest {
  novel_id: string
  plot_type: 'main' | 'subplot' | 'twist'
  plot_length?: 'short' | 'medium' | 'long'
  temperature?: number
  provider?: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export interface AIChapterOutlineRequest {
  novel_id: string
  chapter_number: number
  chapter_theme?: string
  temperature?: number
  provider?: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export interface AIContentExpandRequest {
  novel_id: string
  // Backend accepts numeric chapter ID primary key; use string | number to match router params
  chapter_id?: string | number
  content_snippet: string
  expansion_style?: 'brief' | 'detailed' | 'dramatic'
  temperature?: number
  provider?: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export interface AIWorldGenerateRequest {
  novel_id: string
  focus?: 'era' | 'rules' | 'locations' | 'culture' | 'overall'
  temperature?: number
  provider?: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export interface AITestRequest {
  provider: Provider
  base_url?: string
  api_key?: string
  model_name?: string
}

export interface AITestResponse {
  ok: boolean
  provider: string
  message: string
}

// AI Assistant types
export type AssistantRole = 'conceptualizer' | 'blueplanner' | 'outliner' | 'novelist' | 'extractor' | 'evaluator'

export interface AssistantInfo {
  role: AssistantRole
  name: string
  description: string
}

export interface AssistantRequest {
  role: AssistantRole
  novel_id: string
  user_input: string
  provider?: Provider
  model_name?: string
  base_url?: string
  api_key?: string
  temperature?: number
  max_tokens?: number
}

export interface AssistantResponse {
  role: AssistantRole
  content: string
  tokens_used: number
}

export interface MultipleVersionsResponse {
  role: 'novelist'
  versions: string[]
  count: number
}

