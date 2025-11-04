<template>
  <div class="novel-list">
    <el-page-header @back="router.push('/')" content="小说列表" />

    <div class="header-actions">
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建新小说
      </el-button>
    </div>

    <el-table
      v-loading="novelStore.loading"
      :data="novelStore.novels"
      style="width: 100%"
      @row-click="handleRowClick"
    >
      <el-table-column prop="title" label="标题" width="250" />
      <el-table-column prop="author" label="作者" width="120" />
      <el-table-column prop="genre" label="类型" width="100" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="description" label="简介" show-overflow-tooltip />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click.stop="editNovel(row)">编辑</el-button>
          <el-button size="small" type="danger" @click.stop="confirmDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="showDialog"
      :title="editingNovel ? '编辑小说' : '创建新小说'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="novelForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="novelForm.title" placeholder="请输入小说标题" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="novelForm.author" placeholder="请输入作者名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="novelForm.genre" placeholder="选择类型">
            <el-option label="奇幻" value="fantasy" />
            <el-option label="科幻" value="sci-fi" />
            <el-option label="现代" value="modern" />
            <el-option label="历史" value="historical" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="novelForm.status" placeholder="选择状态">
            <el-option label="草稿" value="DRAFT" />
            <el-option label="进行中" value="IN_PROGRESS" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已发布" value="PUBLISHED" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介">
          <el-input
            v-model="novelForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入小说简介"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="saveNovel">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<!--
  小说列表页面
  功能：展示所有小说、创建新小说、编辑和删除小说
-->
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNovelStore } from '@/stores/novel'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { Novel, NovelCreate } from '@/types/novel'

// 路由实例
const router = useRouter()
// 小说Store实例
const novelStore = useNovelStore()
// 对话框显示状态
const showDialog = ref(false)
// 当前正在编辑的小说（null表示创建新小说）
const editingNovel = ref<Novel | null>(null)
// 小说表单数据
const novelForm = ref<NovelCreate>({
  title: '',
  author: '',
  genre: '',
  status: 'DRAFT',
  description: ''
})

// 组件挂载时加载小说列表
onMounted(async () => {
  try {
    await novelStore.fetchNovels()
  } catch (error) {
    ElMessage.error('加载小说列表失败')
  }
})

/**
 * 处理表格行点击事件 - 跳转到小说详情页
 */
function handleRowClick(row: Novel) {
  router.push(`/novels/${row.id}`)
}

/**
 * 打开创建小说对话框
 */
function openCreateDialog() {
  editingNovel.value = null
  showDialog.value = true
  novelForm.value = {
    title: '',
    author: '',
    genre: '',
    status: 'DRAFT',
    description: ''
  }
}

/**
 * 编辑小说 - 打开编辑对话框并填充数据
 */
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

/**
 * 关闭对话框
 */
function closeDialog() {
  showDialog.value = false
}

/**
 * 保存小说（创建或更新）
 */
async function saveNovel() {
  if (!novelForm.value.title.trim()) {
    ElMessage.warning('请输入小说标题')
    return
  }
  try {
    if (editingNovel.value) {
      // 更新现有小说
      await novelStore.updateNovel(editingNovel.value.id, novelForm.value)
      ElMessage.success('更新成功')
    } else {
      // 创建新小说
      await novelStore.createNovel(novelForm.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
  } catch (error) {
    ElMessage.error(editingNovel.value ? '更新失败' : '创建失败')
  }
}

/**
 * 确认删除小说
 */
async function confirmDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这部小说吗？', '警告', {
      type: 'warning'
    })
    await novelStore.deleteNovel(id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 获取状态对应的标签类型
 */
function getStatusType(status: string) {
  const typeMap: Record<string, string> = {
    DRAFT: 'info',
    IN_PROGRESS: 'warning',
    COMPLETED: 'success',
    PUBLISHED: 'primary'
  }
  return typeMap[status] ?? 'info'
}

/**
 * 获取状态的中文标签
 */
function getStatusLabel(status: string) {
  const labelMap: Record<string, string> = {
    DRAFT: '草稿',
    IN_PROGRESS: '进行中',
    COMPLETED: '已完成',
    PUBLISHED: '已发布'
  }
  return labelMap[status] ?? status
}

/**
 * 格式化日期为本地时间字符串
 */
function formatDate(value: string) {
  return new Date(value).toLocaleString('zh-CN')
}
</script>

<style scoped>
.novel-list {
  padding: 20px;
}

.header-actions {
  margin: 20px 0;
  display: flex;
  justify-content: flex-end;
}
</style>
