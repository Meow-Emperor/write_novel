// Simple heuristic parsers to map AI free-form text into structured fields

function getLines(text: string): string[] {
  return (text || '')
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l.length > 0)
}

function captureSection(lines: string[], startIdx: number): { content: string; end: number } {
  // Capture until next heading-like line
  const buf: string[] = []
  let i = startIdx + 1
  for (; i < lines.length; i++) {
    const ln = lines[i]
    if (/^#{1,6}\s+/.test(ln)) break
    if (/^\d+\.|^[-*]\s/.test(ln)) {
      // allow list items inside section
      buf.push(ln)
      continue
    }
    if (/^[A-Za-z\u4e00-\u9fa5][\w\u4e00-\u9fa5\s]+[:：]$/.test(ln)) break
    if (/^(Chapter|Plot|角色|人物|外貌|性格|背景|关系|冲突|地点|规则|文化)[:：]/i.test(ln)) break
    buf.push(ln)
  }
  return { content: buf.join('\n'), end: i }
}

export function parseCharacter(text: string) {
  const lines = getLines(text)
  const out: any = { name: '', role: '', description: '', personality: '', background: '', appearance: '', relationships: '' }
  // Name
  for (const ln of lines) {
    const m = ln.match(/^(Character\s*Name|角色名称|姓名)[:：]\s*(.+)$/i)
    if (m && m[2]) { out.name = m[2].trim(); break }
  }
  // Role
  for (const ln of lines) {
    const m = ln.match(/^(Role|角色)[:：]\s*(.+)$/i)
    if (m && m[2]) { out.role = m[2].trim(); break }
  }
  const labels: Record<string, keyof typeof out> = {
    'Physical Appearance': 'appearance', '外貌描述': 'appearance', '外貌': 'appearance',
    'Personality Traits': 'personality', '性格特点': 'personality', '性格': 'personality',
    'Background Story': 'background', '背景故事': 'background', '背景': 'background',
    'Relationships': 'relationships', '人物关系': 'relationships', '关系': 'relationships',
    'Description': 'description', '描述': 'description'
  }
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i]
    const label = Object.keys(labels).find((k) => new RegExp(`^${k}[:：]`, 'i').test(ln))
    if (label) {
      const { content, end } = captureSection(lines, i)
      const key = labels[label]
      out[key] = content || out[key]
      i = end - 1
    }
  }
  if (!out.description) out.description = text
  return out
}

export function parsePlot(text: string) {
  const lines = getLines(text)
  const out: any = { title: '', description: '', key_events: '', characters: '', conflicts: '' }
  for (const ln of lines) {
    const m = ln.match(/^(Plot\s*Title|标题)[:：]\s*(.+)$/i)
    if (m && m[2]) { out.title = m[2].trim(); break }
  }
  const labels: Record<string, keyof typeof out> = {
    'Main Conflict': 'description', 'Hook': 'description', '主要冲突': 'description',
    'Key Plot Points': 'key_events', '关键事件': 'key_events',
    'Character Involvement': 'characters', '角色参与': 'characters',
    'Conflicts': 'conflicts', '冲突': 'conflicts'
  }
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i]
    const label = Object.keys(labels).find((k) => new RegExp(`^${k}([\s]*|[:：])`, 'i').test(ln))
    if (label) {
      const { content, end } = captureSection(lines, i)
      const key = labels[label]
      out[key] = content || out[key]
      i = end - 1
    }
  }
  if (!out.title) out.title = 'AI 生成情节'
  if (!out.description) out.description = text
  if (!out.key_events) out.key_events = text
  return out
}

export function parseChapterOutline(text: string) {
  const lines = getLines(text)
  const out: any = { title: '', summary: '', keyEvents: '' }
  for (const ln of lines) {
    const m = ln.match(/^(Chapter\s*Title|章节标题)[:：]\s*(.+)$/i)
    if (m && m[2]) { out.title = m[2].trim(); break }
  }
  const labels: Record<string, keyof typeof out> = {
    'Chapter Summary': 'summary', '章节概要': 'summary', 'Summary': 'summary',
    'Key Events': 'keyEvents', '关键事件': 'keyEvents'
  }
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i]
    const label = Object.keys(labels).find((k) => new RegExp(`^${k}[:：]`, 'i').test(ln))
    if (label) {
      const { content, end } = captureSection(lines, i)
      const key = labels[label]
      out[key] = content || out[key]
      i = end - 1
    }
  }
  if (!out.summary) out.summary = text
  return out
}

export function parseWorld(text: string) {
  const lines = getLines(text)
  const out: any = { era: '', rules: {} as Record<string, any>, locations: {} as Record<string, any>, culture: {} as Record<string, any> }
  const pushKV = (obj: Record<string, any>, block: string) => {
    const ls = getLines(block)
    for (const l of ls) {
      const m = l.match(/^[-*\d\.\)]?\s*([^:：]{1,50})[:：]\s*(.+)$/)
      if (m && m[1] && m[2]) obj[m[1].trim()] = m[2].trim()
    }
  }
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i]
    if (/^(Era|Time|时代)[\s]*[:：]/i.test(ln)) {
      const { content, end } = captureSection(lines, i)
      out.era = content || out.era
      i = end - 1
      continue
    }
    if (/^(Rules|Laws|规则|法则)[:：]/i.test(ln)) {
      const { content, end } = captureSection(lines, i)
      pushKV(out.rules, content)
      i = end - 1
      continue
    }
    if (/^(Locations|Places|地点|场景)[:：]/i.test(ln)) {
      const { content, end } = captureSection(lines, i)
      pushKV(out.locations, content)
      i = end - 1
      continue
    }
    if (/^(Culture|文化)[:：]/i.test(ln)) {
      const { content, end } = captureSection(lines, i)
      pushKV(out.culture, content)
      i = end - 1
      continue
    }
  }
  return out
}

