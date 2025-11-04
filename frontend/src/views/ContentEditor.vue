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
            <el-tag :type="getStatusType(chapter?.status || 'draft')">
              {{ getStatusText(chapter?.status || 'draft') }}
            </el-tag>
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
        </div>

        <el-input
          ref="editorRef"
          v-model="content"
          type="textarea"
          :rows="25"
          placeholder="开始写作..."
          class="content-textarea"
          @input="updateWordCount"
        />

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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DocumentCopy } from '@element-plus/icons-vue'
import request from '@/utils/request'

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

const route = useRoute()
const router = useRouter()
const novelId = route.params.id as string
const chapterId = route.params.chapterId as string

const loading = ref(false)
const saving = ref(false)
const chapter = ref<Chapter | null>(null)
const content = ref('')
const status = ref('draft')
const notes = ref('')
const editorRef = ref()

const wordCount = computed(() => {
  return content.value.replace(/\s/g, '').length
})

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    draft: 'info',
    in_progress: 'warning',
    completed: 'success',
    published: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成',
    published: '已发布'
  }
  return map[status] || status
}

const fetchChapter = async () => {
  if (!chapterId) {
    ElMessage.error('章节ID不存在')
    goBack()
    return
  }

  loading.value = true
  try {
    const response = await request.get(`/api/chapters/${chapterId}`)
    chapter.value = response.data
    content.value = chapter.value?.content || ''
    status.value = chapter.value?.status || 'draft'
    notes.value = chapter.value?.notes || ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取章节信息失败')
    goBack()
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!chapterId) return

  saving.value = true
  try {
    await request.put(`/api/chapters/${chapterId}`, {
      content: content.value,
      word_count: wordCount.value,
      status: status.value,
      notes: notes.value
    })
    ElMessage.success('保存成功')
    if (chapter.value) {
      chapter.value.content = content.value
      chapter.value.word_count = wordCount.value
      chapter.value.status = status.value
      chapter.value.notes = notes.value
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const insertText = (before: string, after: string) => {
  const textarea = editorRef.value?.textarea
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)
  const newText = before + selectedText + after
  
  content.value = content.value.substring(0, start) + newText + content.value.substring(end)
  
  // Set cursor position after inserted text
  setTimeout(() => {
    textarea.focus()
    const newPosition = start + before.length + selectedText.length
    textarea.setSelectionRange(newPosition, newPosition)
  }, 0)
}

const updateWordCount = () => {
  // Word count is computed automatically
}

const goBack = () => {
  router.push({
    name: 'ChapterBlueprint',
    params: { id: novelId }
  })
}

// Auto-save every 2 minutes
let autoSaveTimer: number | null = null

onMounted(() => {
  fetchChapter()
  
  // Setup auto-save
  autoSaveTimer = window.setInterval(() => {
    if (content.value && !saving.value) {
      handleSave()
    }
  }, 120000) // 2 minutes
})

// Cleanup on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})
</script>

<style scoped>
.content-editor {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.word-count {
  color: #606266;
  font-size: 14px;
}

.editor-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.editor-toolbar {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.ml-10 {
  margin-left: 10px;
}

.content-textarea {
  font-family: 'Courier New', Courier, monospace;
  font-size: 16px;
  line-height: 1.8;
}

.content-textarea :deep(textarea) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 16px;
  line-height: 1.8;
}

.editor-footer {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
