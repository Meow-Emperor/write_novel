<template>
  <div class="chapter-blueprint">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>章节蓝图</h2>
          <div>
            <el-button class="mr-8" type="success" @click="assistantDialogVisible = true">
              <el-icon><Promotion /></el-icon>
              AI 创作助手
            </el-button>
            <el-button class="mr-8" @click="openAIOutline">
              <el-icon><Plus /></el-icon>
              AI 生成章节大纲
            </el-button>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建章节
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="chapters" v-loading="loading" stripe>
        <el-table-column prop="chapter_number" label="章节号" width="100" sortable />
        <el-table-column prop="title" label="章节标题" width="260" />
        <el-table-column prop="summary" label="章节概要" show-overflow-tooltip />
        <el-table-column prop="word_count" label="字数" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="handleWriteContent(row)">写作</el-button>
            <el-button size="small" @click="handleVersions(row)">版本</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑章节 -->
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑章节' : '新建章节'" width="720px" @close="resetForm">
      <el-form :model="formData" ref="formRef" label-width="100px">
        <el-form-item label="章节号" prop="chapter_number">
          <el-input-number v-model="formData.chapter_number" :min="1" :step="1" />
        </el-form-item>
        <el-form-item label="章节标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入章节标题" />
        </el-form-item>
        <el-form-item label="章节概要" prop="summary">
          <el-input v-model="formData.summary" type="textarea" :rows="4" placeholder="请输入章节概要" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已发布" value="published" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="formData.notes" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>

    <!-- AI 章节大纲 -->
    <el-dialog v-model="aiDialogVisible" title="AI 生成章节大纲" width="520px">
      <el-form :model="aiForm" label-width="100px">
        <el-form-item label="章节序号">
          <el-input-number v-model="aiForm.chapter_number" :min="1" :step="1" />
        </el-form-item>
        <el-form-item label="章节主题">
          <el-input v-model="aiForm.chapter_theme" placeholder="可选：该章主题或侧重点" />
        </el-form-item>
        <el-form-item label="保存方式">
          <el-radio-group v-model="aiForm.mode">
            <el-radio label="preview">预览并编辑</el-radio>
            <el-radio label="auto">直接创建</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="aiDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAIGenerateOutline" :loading="aiSubmitting">生成</el-button>
      </template>
    </el-dialog>

    <!-- 版本管理 -->
    <ChapterVersionManager
      v-model="versionDialogVisible"
      :chapter-id="selectedChapterId"
      @version-changed="fetchChapters"
    />

    <!-- AI 创作助手 -->
    <AIAssistantDialog
      v-model="assistantDialogVisible"
      :novel-id="novelId"
      @content-generated="handleAssistantContent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Promotion } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { parseChapterOutline } from '@/utils/aiParse'
import { useAIStore } from '@/stores/ai'
import ChapterVersionManager from '@/components/ChapterVersionManager.vue'
import AIAssistantDialog from '@/components/AIAssistantDialog.vue'

const aiStore = useAIStore()
const route = useRoute()
const router = useRouter()
const novelId = route.params.id as string

interface Chapter {
  id: string
  novel_id: string
  title: string
  chapter_number: number
  summary?: string
  content?: string
  word_count: number
  status: string
  notes?: string
  created_at: string
  updated_at: string
}

interface ChapterForm {
  title: string
  chapter_number: number
  summary: string
  status: string
  notes: string
}

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const chapters = ref<Chapter[]>([])
const currentChapterId = ref<string>('')

// 版本管理
const versionDialogVisible = ref(false)
const selectedChapterId = ref<number>(0)

// AI 助手
const assistantDialogVisible = ref(false)

const formRef = ref<FormInstance>()
const formData = ref<ChapterForm>({ title: '', chapter_number: 1, summary: '', status: 'DRAFT', notes: '' })

const aiDialogVisible = ref(false)
const aiSubmitting = ref(false)
const aiForm = ref<{ chapter_number: number; chapter_theme: string; mode: 'preview' | 'auto' }>({ chapter_number: 1, chapter_theme: '', mode: 'preview' })

function getStatusType(status: string) {
  const map: Record<string, any> = { DRAFT: 'info', IN_PROGRESS: 'warning', COMPLETED: 'success', PUBLISHED: 'success' }
  return map[status] || 'info'
}

function getStatusText(status: string) {
  const map: Record<string, string> = { DRAFT: '草稿', IN_PROGRESS: '进行中', COMPLETED: '已完成', PUBLISHED: '已发布' }
  return map[status] || status
}

async function fetchChapters() {
  loading.value = true
  try {
    const response = await request.get('/api/chapters/', { params: { novel_id: novelId } })
    chapters.value = (response.data || []).sort((a: Chapter, b: Chapter) => a.chapter_number - b.chapter_number)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取章节列表失败')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  isEditing.value = false
  const nextNumber = chapters.value.length > 0 ? Math.max(...chapters.value.map((c) => c.chapter_number)) + 1 : 1
  formData.value = { title: '', chapter_number: nextNumber, summary: '', status: 'DRAFT', notes: '' }
  dialogVisible.value = true
}

function handleEdit(chapter: Chapter) {
  isEditing.value = true
  currentChapterId.value = chapter.id
  formData.value = { title: chapter.title, chapter_number: chapter.chapter_number, summary: chapter.summary || '', status: chapter.status, notes: chapter.notes || '' }
  dialogVisible.value = true
}

function handleWriteContent(chapter: Chapter) {
  router.push({ name: 'ContentEditor', params: { id: novelId, chapterId: chapter.id } })
}

function handleVersions(chapter: Chapter) {
  selectedChapterId.value = parseInt(chapter.id)
  versionDialogVisible.value = true
}

async function handleDelete(chapter: Chapter) {
  try {
    await ElMessageBox.confirm('确定要删除这个章节吗？', '警告', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    await request.delete(`/api/chapters/${chapter.id}`)
    ElMessage.success('删除成功')
    fetchChapters()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEditing.value) {
        await request.put(`/api/chapters/${currentChapterId.value}`, formData.value)
        ElMessage.success('更新成功')
      } else {
        await request.post('/api/chapters/', { ...formData.value, novel_id: novelId, word_count: 0 })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchChapters()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '提交失败')
    } finally {
      submitting.value = false
    }
  })
}

function openAIOutline() {
  const nextNumber = chapters.value.length > 0 ? Math.max(...chapters.value.map((c) => c.chapter_number)) + 1 : 1
  aiForm.value = { chapter_number: nextNumber, chapter_theme: '', mode: 'preview' }
  aiDialogVisible.value = true
}

async function handleAIGenerateOutline() {
  try {
    aiSubmitting.value = true
    const cfg = aiStore.config
    const resp = await request.post('/api/ai/generate-chapter-outline', {
      novel_id: novelId,
      chapter_number: aiForm.value.chapter_number,
      chapter_theme: aiForm.value.chapter_theme || undefined,
      provider: cfg.provider,
      base_url: cfg.base_url,
      api_key: cfg.api_key,
      model_name: cfg.model_name,
      temperature: cfg.temperature
    })
    const content: string = resp.data?.content || ''
    const parsed = parseChapterOutline(content)

    if (aiForm.value.mode === 'auto') {
      await request.post('/api/chapters/', {
        novel_id: novelId,
        title: parsed.title || `第${aiForm.value.chapter_number}章`,
        chapter_number: aiForm.value.chapter_number,
        summary: parsed.summary || content,
        notes: parsed.keyEvents || '',
        status: 'DRAFT',
        word_count: 0
      })
      ElMessage.success('AI 已生成并创建章节')
      aiDialogVisible.value = false
      fetchChapters()
    } else {
      isEditing.value = false
      formData.value = {
        title: parsed.title || `第${aiForm.value.chapter_number}章`,
        chapter_number: aiForm.value.chapter_number,
        summary: parsed.summary || content,
        status: 'DRAFT',
        notes: parsed.keyEvents || ''
      }
      aiDialogVisible.value = false
      dialogVisible.value = true
      ElMessage.success('AI 已生成内容，已填入表单供编辑')
    }
  } catch (e) {
    // 已由拦截器提示
  } finally {
    aiSubmitting.value = false
  }
}

function handleAssistantContent(content: string) {
  // Apply the AI assistant content to a new chapter summary
  const nextNumber = chapters.value.length > 0 ? Math.max(...chapters.value.map((c) => c.chapter_number)) + 1 : 1
  isEditing.value = false
  formData.value = {
    title: `第${nextNumber}章`,
    chapter_number: nextNumber,
    summary: content,
    status: 'DRAFT',
    notes: ''
  }
  dialogVisible.value = true
  ElMessage.success('AI 助手内容已应用到新章节')
}

onMounted(() => {
  fetchChapters()
})
</script>

<style scoped>
.chapter-blueprint { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h2 { margin: 0; font-size: 20px; }
.mr-8 { margin-right: 8px; }
</style>
