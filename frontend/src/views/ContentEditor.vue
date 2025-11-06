<template>
  <div class="content-editor">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
            <h2>{{ chapter?.title || '章节编辑' }}</h2>
          </div>
          <div class="header-right">
            <el-tag :type="getStatusType(chapter?.status || 'draft')">{{ getStatusText(chapter?.status || 'draft') }}</el-tag>
            <span class="word-count">字数: {{ wordCount }}</span>
            <el-button type="primary" @click="handleSave" :loading="saving">
              <el-icon><DocumentCopy /></el-icon>
              保存
            </el-button>
          </div>
        </div>
      </template>

      <div class="editor-container">
        <div class="editor-toolbar">
          <el-button-group>
            <el-button size="small" @click="insertText('**', '**')">加粗</el-button>
            <el-button size="small" @click="insertText('*', '*')">斜体</el-button>
            <el-button size="small" @click="insertText('~~', '~~')">删除线</el-button>
          </el-button-group>
          <el-button-group class="ml-10">
            <el-button size="small" @click="insertText('\n# ', '')">标题1</el-button>
            <el-button size="small" @click="insertText('\n## ', '')">标题2</el-button>
            <el-button size="small" @click="insertText('\n### ', '')">标题3</el-button>
          </el-button-group>
          <el-button-group class="ml-10">
            <el-button size="small" @click="insertText('\n- ', '')">列表</el-button>
            <el-button size="small" @click="insertText('\n> ', '')">引用</el-button>
          </el-button-group>
          <el-button-group class="ml-10">
            <el-button size="small" type="primary" @click="aiExpandSelection" :loading="aiExpanding">AI 扩写选中内容</el-button>
          </el-button-group>
        </div>

        <el-input ref="editorRef" v-model="content" type="textarea" :rows="25" placeholder="开始写作..." class="content-textarea" @input="updateWordCount" />

        <div class="editor-footer">
          <el-form :inline="true" size="small">
            <el-form-item label="状态">
              <el-select v-model="status" style="width: 120px">
                <el-option label="草稿" value="draft" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已发布" value="published" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="notes" placeholder="章节备注" style="width: 300px" />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DocumentCopy } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useAIStore } from '@/stores/ai'

interface Chapter { id: string; novel_id: string; title: string; chapter_number: number; summary?: string; content?: string; word_count: number; status: string; notes?: string; created_at: string; updated_at: string }

const route = useRoute()
const router = useRouter()
const aiStore = useAIStore()
const novelId = route.params.id as string
let chapterId = route.params.chapterId as string | undefined

const loading = ref(false)
const saving = ref(false)
const chapter = ref<Chapter | null>(null)
const content = ref('')
const status = ref('DRAFT')
const notes = ref('')
const editorRef = ref()

const wordCount = computed(() => content.value.replace(/\s/g, '').length)

const getStatusType = (s: string) => ({ DRAFT: 'info', IN_PROGRESS: 'warning', COMPLETED: 'success', PUBLISHED: 'success' }[s] || 'info')
const getStatusText = (s: string) => ({ DRAFT: '草稿', IN_PROGRESS: '进行中', COMPLETED: '已完成', PUBLISHED: '已发布' }[s] || s)

async function fetchChapter() {
  loading.value = true
  try {
    if (!chapterId) {
      // No chapter specified: try to find one or create a default chapter, then redirect
      await ensureChapterAndRedirect()
      return
    }
    const res = await request.get(`/api/chapters/${chapterId}`)
    chapter.value = res.data
    status.value = res.data.status
    notes.value = res.data.notes || ''
    content.value = res.data.content || ''
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载章节失败')
  } finally { loading.value = false }
}

async function ensureChapterAndRedirect() {
  try {
    // 1) Try to get existing chapters
    const list = await request.get('/api/chapters', { params: { novel_id: novelId } })
    const chapters: any[] = Array.isArray(list.data) ? list.data : []
    if (chapters.length > 0) {
      const firstId = chapters[0].id
      await router.replace({ name: 'ContentEditor', params: { id: novelId, chapterId: String(firstId) } })
      chapterId = String(firstId)
      await fetchChapter()
      return
    }
    // 2) Create an initial chapter
    const create = await request.post('/api/chapters/', {
      novel_id: novelId,
      title: '第一章',
      chapter_number: 1,
      summary: '',
      status: 'DRAFT',
      word_count: 0
    })
    const newId = create.data?.id
    if (newId) {
      await router.replace({ name: 'ContentEditor', params: { id: novelId, chapterId: String(newId) } })
      chapterId = String(newId)
      await fetchChapter()
    } else {
      ElMessage.error('无法创建初始章节')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '初始化章节失败')
  }
}

async function handleSave() {
  saving.value = true
  try {
    await request.put(`/api/chapters/${chapterId}`, { content: content.value, word_count: wordCount.value, status: status.value, notes: notes.value })
    ElMessage.success('保存成功')
    if (chapter.value) { chapter.value.content = content.value; chapter.value.word_count = wordCount.value; chapter.value.status = status.value; chapter.value.notes = notes.value }
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '保存失败') } finally { saving.value = false }
}

function insertText(before: string, after: string) {
  const textarea = (editorRef.value as any)?.textarea as HTMLTextAreaElement | undefined
  if (!textarea) return
  const start = textarea.selectionStart, end = textarea.selectionEnd
  const selected = content.value.substring(start, end)
  const newText = before + selected + after
  content.value = content.value.substring(0, start) + newText + content.value.substring(end)
  setTimeout(() => { textarea.focus(); textarea.setSelectionRange(start + before.length + selected.length, start + before.length + selected.length) }, 0)
}

function updateWordCount() { /* computed */ }

function goBack() { router.push({ name: 'ChapterBlueprint', params: { id: novelId } }) }

// AI 扩写选择文本
const aiExpanding = ref(false)
async function aiExpandSelection() {
  const textarea = (editorRef.value as any)?.textarea as HTMLTextAreaElement | undefined
  if (!textarea) return
  const start = textarea.selectionStart, end = textarea.selectionEnd
  const snippet = content.value.substring(start, end).trim()
  if (!snippet) { ElMessage.info('请选择需要扩写的文本'); return }
  try {
    aiExpanding.value = true
    const cfg = aiStore.config
    const resp = await request.post('/api/ai/expand-content', { novel_id: novelId, chapter_id: chapterId, content_snippet: snippet, expansion_style: 'detailed', provider: cfg.provider, base_url: cfg.base_url, api_key: cfg.api_key, model_name: cfg.model_name, temperature: cfg.temperature })
    const generated: string = resp.data?.content || ''
    content.value = content.value.substring(0, start) + generated + content.value.substring(end)
    ElMessage.success('已用 AI 扩写所选文本')
  } catch (e) { /* 拦截器已提示 */ } finally { aiExpanding.value = false }
}

// Auto-save every 2 minutes
let autoSaveTimer: number | null = null
onMounted(() => {
  fetchChapter()
  autoSaveTimer = window.setInterval(() => { if (content.value && !saving.value) handleSave() }, 120000)
})
// React when route changes (e.g., redirected to created chapter)
import { watch } from 'vue'
watch(() => route.params.chapterId, (val) => {
  chapterId = val as string | undefined
  fetchChapter()
})
onUnmounted(() => { if (autoSaveTimer) clearInterval(autoSaveTimer) })
</script>

<style scoped>
.content-editor { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 15px; }
.header-left h2 { margin: 0; font-size: 20px; }
.header-right { display: flex; align-items: center; gap: 15px; }
.word-count { color: #606266; font-size: 14px; }
.editor-container { display: flex; flex-direction: column; gap: 10px; }
.editor-toolbar { display: flex; gap: 10px; padding: 10px; background: #f5f7fa; border-radius: 4px; }
.ml-10 { margin-left: 10px; }
.content-textarea { font-family: 'Courier New', Courier, monospace; font-size: 16px; line-height: 1.8; }
.content-textarea :deep(textarea) { font-family: 'Courier New', Courier, monospace; font-size: 16px; line-height: 1.8; }
.editor-footer { padding: 10px; background: #f5f7fa; border-radius: 4px; }
</style>
