// Chapter Version Types

export interface ChapterVersion {
  id: number
  chapter_id: number
  version_label?: string | null
  provider?: string | null
  content: string
  created_at: string
}

export interface ChapterVersionCreate {
  chapter_id: number
  version_label?: string | null
  provider?: string | null
  content: string
}

// Chapter Evaluation Types

export interface ChapterEvaluation {
  id: number
  chapter_id: number
  version_id?: number | null
  decision?: string | null
  feedback?: string | null
  score?: number | null
  created_at: string
}

export interface ChapterEvaluationCreate {
  chapter_id: number
  version_id?: number | null
  decision?: string | null
  feedback?: string | null
  score?: number | null
}

// Extended Chapter with Versions

export interface ChapterWithVersions {
  id: number
  novel_id: string
  chapter_number: number
  title?: string | null
  summary?: string | null
  word_count: number
  status: string
  selected_version_id?: number | null
  created_at: string
  updated_at: string

  // Relations
  versions: ChapterVersion[]
  selected_version?: ChapterVersion | null
  evaluations: ChapterEvaluation[]
}
