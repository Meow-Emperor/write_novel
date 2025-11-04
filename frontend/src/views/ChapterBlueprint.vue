<template>
  <div class="chapter-blueprint">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>章节蓝图</h2>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建章节
          </el-button>
        </div>
      </template>

      <el-table :data="chapters" v-loading="loading" stripe>
        <el-table-column prop="chapter_number" label="章节号" width="100" sortable />
        <el-table-column prop="title" label="章节标题" width="250" />
        <el-table-column prop="summary" label="章节概要" show-overflow-tooltip />
        <el-table-column prop="word_count" label="字数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="handleWriteContent(row)">写作</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑章节' : '新建章节'"
      width="700px"
      @close="resetForm"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="章节号" prop="chapter_number">
          <el-input-number v-model="formData.chapter_number" :min="1" :step="1" />
        </el-form-item>
        <el-form-item label="章节标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入章节标题" />
        </el-form-item>
        <el-form-item label="章节概要" prop="summary">
          <el-input
            v-model="formData.summary"
            type="textarea"
            :rows="4"
            placeholder="请输入章节概要"
          />
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
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
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

interface ChapterForm {
  title: string
  chapter_number: number
  summary: string
  status: string
  notes: string
}

const route = useRoute()
const router = useRouter()
const novelId = route.params.id as string

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const chapters = ref<Chapter[]>([])
const currentChapterId = ref<string>('')

const formRef = ref<FormInstance>()
const formData = ref<ChapterForm>({
  title: '',
  chapter_number: 1,
  summary: '',
  status: 'draft',
  notes: ''
})

const rules = {
  title: [{ required: true, message: '请输入章节标题', trigger: 'blur' }],
  chapter_number: [{ required: true, message: '请输入章节号', trigger: 'blur' }]
}

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

const fetchChapters = async () => {
  loading.value = true
  try {
    const response = await request.get('/api/chapters/', {
      params: { novel_id: novelId }
    })
    chapters.value = response.data.sort((a: Chapter, b: Chapter) => a.chapter_number - b.chapter_number)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取章节列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  isEditing.value = false
  const nextNumber = chapters.value.length > 0 
    ? Math.max(...chapters.value.map(c => c.chapter_number)) + 1 
    : 1
  formData.value = {
    title: '',
    chapter_number: nextNumber,
    summary: '',
    status: 'draft',
    notes: ''
  }
  dialogVisible.value = true
}

const handleEdit = (chapter: Chapter) => {
  isEditing.value = true
  currentChapterId.value = chapter.id
  formData.value = {
    title: chapter.title,
    chapter_number: chapter.chapter_number,
    summary: chapter.summary || '',
    status: chapter.status,
    notes: chapter.notes || ''
  }
  dialogVisible.value = true
}

const handleWriteContent = (chapter: Chapter) => {
  router.push({
    name: 'ContentEditor',
    params: { id: novelId, chapterId: chapter.id }
  })
}

const handleDelete = async (chapter: Chapter) => {
  try {
    await ElMessageBox.confirm('确定要删除这个章节吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await request.delete(`/api/chapters/${chapter.id}`)
    ElMessage.success('删除成功')
    fetchChapters()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEditing.value) {
        await request.put(`/api/chapters/${currentChapterId.value}`, formData.value)
        ElMessage.success('更新成功')
      } else {
        await request.post('/api/chapters/', {
          ...formData.value,
          novel_id: novelId,
          word_count: 0
        })
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

const resetForm = () => {
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchChapters()
})
</script>

<style scoped>
.chapter-blueprint {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}
</style>
