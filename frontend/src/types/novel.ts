export type NovelStatus = 'DRAFT' | 'IN_PROGRESS' | 'COMPLETED' | 'PUBLISHED'

export interface Novel {
  id: string
  title: string
  author?: string | null
  genre?: string | null
  description?: string | null
  status: NovelStatus
  created_at: string
  updated_at: string
}

export interface NovelCreate {
  title: string
  author?: string | null
  genre?: string | null
  description?: string | null
  status?: NovelStatus
}

export interface NovelUpdate {
  title?: string
  author?: string | null
  genre?: string | null
  description?: string | null
  status?: NovelStatus
}
