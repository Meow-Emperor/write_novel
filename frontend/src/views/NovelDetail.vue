<template>
  <div class="novel-detail" v-loading="novelStore.loading">
    <el-page-header @back="router.push('/novels')" :content="novel?.title ?? '加载中...'" />

    <el-card v-if="novel" class="detail-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>{{ novel.title }}</h2>
          <el-tag :type="getStatusType(novel.status)">
            {{ getStatusLabel(novel.status) }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="作者">
          {{ novel.author || '未设置' }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          {{ novel.genre || '未设置' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(novel.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">
          {{ formatDate(novel.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="简介" :span="2">
          {{ novel.description || '暂无简介' }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="actions">
        <el-button type="primary" @click="router.push(`/novels/${novel.id}/editor`)">
          <el-icon><Edit /></el-icon>
          开始创作
        </el-button>
        <el-button @click="router.push(`/novels/${novel.id}/world`)">
          世界观设定
        </el-button>
        <el-button @click="router.push(`/novels/${novel.id}/characters`)">
          角色管理
        </el-button>
        <el-button @click="router.push(`/novels/${novel.id}/plot`)">
          情节架构
        </el-button>
      </div>
    </el-card>

    <el-empty v-else-if="!novelStore.loading" description="小说不存在" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNovelStore } from '@/stores/novel'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const novelStore = useNovelStore()

const novelId = computed(() => route.params.id as string)
const novel = computed(() => novelStore.currentNovel)

onMounted(async () => {
  try {
    await novelStore.fetchNovel(novelId.value)
  } catch (error) {
    ElMessage.error('加载小说信息失败')
  }
})

function getStatusType(status: string) {
  const typeMap: Record<string, string> = {
    DRAFT: 'info',
    IN_PROGRESS: 'warning',
    COMPLETED: 'success',
    PUBLISHED: 'primary'
  }
  return typeMap[status] ?? 'info'
}

function getStatusLabel(status: string) {
  const labelMap: Record<string, string> = {
    DRAFT: '草稿',
    IN_PROGRESS: '进行中',
    COMPLETED: '已完成',
    PUBLISHED: '已发布'
  }
  return labelMap[status] ?? status
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('zh-CN')
}
</script>

<style scoped>
.novel-detail {
  padding: 20px;
}

.detail-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
