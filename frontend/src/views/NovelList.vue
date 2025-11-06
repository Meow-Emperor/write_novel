<template>
  <div class="novel-list">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon :size="32"><Notebook /></el-icon>
          我的小说
        </h1>
        <p class="page-subtitle">管理和组织你的创作作品</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreateDialog" round>
          <el-icon><Plus /></el-icon>
          创建新小说
        </el-button>
      </div>
    </div>

    <div v-if="novelStore.novels.length === 0 && !novelStore.loading" class="empty-state">
      <el-empty description="还没有小说作品">
        <el-button type="primary" @click="openCreateDialog" round>
          <el-icon><Plus /></el-icon>
          创建第一部小说
        </el-button>
      </el-empty>
    </div>

    <div v-else class="novels-grid">
      <el-row :gutter="24" v-loading="novelStore.loading">
        <el-col :xs="24" :sm="12" :lg="8" v-for="novel in novelStore.novels" :key="novel.id">
          <el-card class="novel-card" shadow="hover" @click="handleRowClick(novel)">
            <div class="card-header">
              <el-tag :type="getStatusType(novel.status)" size="small">{{ getStatusLabel(novel.status) }}</el-tag>
              <el-dropdown @command="(cmd) => handleCommand(cmd, novel)" trigger="click" @click.stop>
                <el-icon class="more-icon"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">
                      <el-icon><Edit /></el-icon>
                      编辑
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <div class="card-body">
              <h3 class="novel-title">{{ novel.title }}</h3>
              <div class="novel-meta">
                <span v-if="novel.author">
                  <el-icon><User /></el-icon>
                  {{ novel.author }}
                </span>
                <span v-if="novel.genre">
                  <el-icon><PriceTag /></el-icon>
                  {{ getGenreLabel(novel.genre) }}
                </span>
              </div>
              <p class="novel-description">{{ novel.description || '暂无简介' }}</p>
            </div>

            <div class="card-footer">
              <span class="date-info">
                <el-icon><Clock /></el-icon>
                {{ formatDate(novel.created_at) }}
              </span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="showDialog" :title="editingNovel ? '编辑小说' : '创建新小说'" width="600px" destroy-on-close>
      <el-form :model="novelForm" label-width="80px" :rules="formRules" ref="formRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="novelForm.title" placeholder="请输入小说标题" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="novelForm.author" placeholder="请输入作者名称" />
        </el-form-item>
        <el-form-item label="类型" prop="genre">
          <el-select v-model="novelForm.genre" placeholder="选择类型" style="width: 100%">
            <el-option label="奇幻" value="fantasy" />
            <el-option label="科幻" value="sci-fi" />
            <el-option label="现代" value="modern" />
            <el-option label="历史" value="historical" />
            <el-option label="悬疑" value="mystery" />
            <el-option label="言情" value="romance" />
            <el-option label="武侠" value="wuxia" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="novelForm.status" placeholder="选择状态" style="width: 100%">
            <el-option label="草稿" value="DRAFT" />
            <el-option label="进行中" value="IN_PROGRESS" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已发布" value="PUBLISHED" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input v-model="novelForm.description" type="textarea" :rows="4" placeholder="请输入小说简介，让读者了解你的作品" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="saveNovel" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNovelStore } from '@/stores/novel'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Notebook, MoreFilled, Edit, Delete, User, PriceTag, Clock } from '@element-plus/icons-vue'
import type { Novel, NovelCreate } from '@/types/novel'

const router = useRouter()
const novelStore = useNovelStore()
const showDialog = ref(false)
const editingNovel = ref<Novel | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()

const novelForm = ref<NovelCreate>({ title: '', author: '', genre: '', status: 'DRAFT', description: '' })

const formRules: FormRules = {
  title: [
    { required: true, message: '请输入小说标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度为 1 到 200 个字符', trigger: 'blur' }
  ]
}

onMounted(async () => {
  try {
    await novelStore.fetchNovels()
  } catch (error) {
    ElMessage.error('加载小说列表失败')
  }
})

function handleRowClick(novel: Novel) {
  router.push(`/novels/${novel.id}`)
}

function openCreateDialog() {
  editingNovel.value = null
  showDialog.value = true
  novelForm.value = { title: '', author: '', genre: '', status: 'DRAFT', description: '' }
}

function editNovel(novel: Novel) {
  editingNovel.value = novel
  novelForm.value = {
    title: novel.title,
    author: novel.author ?? '',
    genre: novel.genre ?? '',
    status: novel.status,
    description: novel.description ?? ''
  }
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
  formRef.value?.resetFields()
}

async function saveNovel() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (editingNovel.value) {
        await novelStore.updateNovel(editingNovel.value.id, novelForm.value)
        ElMessage.success('更新成功')
      } else {
        await novelStore.createNovel(novelForm.value)
        ElMessage.success('创建成功')
      }
      showDialog.value = false
    } catch (error) {
      ElMessage.error(editingNovel.value ? '更新失败' : '创建失败')
    } finally {
      saving.value = false
    }
  })
}

async function handleCommand(command: string, novel: Novel) {
  if (command === 'edit') {
    editNovel(novel)
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm(`确定要删除《${novel.title}》吗？此操作不可恢复。`, '删除确认', { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' })
      await novelStore.deleteNovel(novel.id)
      ElMessage.success('删除成功')
    } catch (error) {
      if (error !== 'cancel') ElMessage.error('删除失败')
    }
  }
}

function getStatusType(status: string) {
  const typeMap: Record<string, string> = { DRAFT: 'info', IN_PROGRESS: 'warning', COMPLETED: 'success', PUBLISHED: 'primary' }
  return typeMap[status] ?? 'info'
}

function getStatusLabel(status: string) {
  const labelMap: Record<string, string> = { DRAFT: '草稿', IN_PROGRESS: '进行中', COMPLETED: '已完成', PUBLISHED: '已发布' }
  return labelMap[status] ?? status
}

function getGenreLabel(genre: string) {
  const labelMap: Record<string, string> = { fantasy: '奇幻', 'sci-fi': '科幻', modern: '现代', historical: '历史', mystery: '悬疑', romance: '言情', wuxia: '武侠', other: '其他' }
  return labelMap[genre] ?? genre
}

function formatDate(value: string) {
  const date = new Date(value)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
</script>

<style scoped>
.novel-list { padding: 40px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { display: flex; align-items: center; gap: 12px; font-size: 28px; margin: 0; }
.page-subtitle { color: #666; font-size: 14px; margin: 0; }
.empty-state { padding: 80px 20px; text-align: center; }
.novels-grid { margin-top: 24px; }
.novel-card { cursor: pointer; transition: all 0.3s ease; height: 100%; border-radius: 12px; margin-bottom: 24px; }
.novel-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.more-icon { cursor: pointer; font-size: 20px; color: #999; transition: color 0.3s; }
.more-icon:hover { color: #667eea; }
.card-body { margin-bottom: 16px; }
.novel-title { font-size: 20px; font-weight: 600; color: #333; margin-bottom: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.novel-meta { display: flex; gap: 16px; margin-bottom: 12px; color: #666; font-size: 13px; }
.novel-meta span { display: flex; align-items: center; gap: 4px; }
.novel-description { color: #666; font-size: 14px; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 44px; }
.card-footer { padding-top: 16px; border-top: 1px solid #f0f0f0; }
.date-info { display: flex; align-items: center; gap: 4px; color: #999; font-size: 13px; }
@media (max-width: 768px) {
  .novel-list { padding: 20px; }
  .page-title { font-size: 24px; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .header-right { width: 100%; }
  .header-right :deep(.el-button) { width: 100%; }
}
</style>

