export interface PlotStructure {
  id: string
  novel_id: string
  acts?: Array<Record<string, any>>
  key_events?: Array<Record<string, any>>
  conflicts?: Array<Record<string, any>>
  created_at: string
}

export interface PlotStructureCreate {
  novel_id: string
  acts?: Array<Record<string, any>>
  key_events?: Array<Record<string, any>>
  conflicts?: Array<Record<string, any>>
}

export interface PlotStructureUpdate {
  acts?: Array<Record<string, any>>
  key_events?: Array<Record<string, any>>
  conflicts?: Array<Record<string, any>>
}
