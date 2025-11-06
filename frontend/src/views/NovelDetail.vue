<template>
  <div class="novel-detail" v-loading="novelStore.loading">
    <div v-if="novel" class="detail-container">
      <!-- Header Section -->
      <div class="detail-header">
        <el-button @click="router.push('/novels')" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div class="header-content">
          <h1 class="novel-title">{{ novel.title }}</h1>
          <div class="novel-meta">
            <el-tag :type="getStatusType(novel.status)" size="large">{{ getStatusLabel(novel.status) }}</el-tag>
            <span v-if="novel.author" class="meta-item"><el-icon><User /></el-icon>{{ novel.author }}</span>
            <span v-if="novel.genre" class="meta-item"><el-icon><PriceTag /></el-icon>{{ getGenreLabel(novel.genre) }}</span>
          </div>
        </div>
      </div>

      <!-- Info Card -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <div>
              <el-button class="mr-8" text @click="router.push({ path: '/inspiration', query: { novelId: novel.id } })">
                <el-icon><Edit /></el-icon>
                AI 快速完善
              </el-button>
              <el-button type="primary" text @click="router.push(`/novels/${novel.id}/editor`)">
                <el-icon><Edit /></el-icon>
                编辑信息
              </el-button>
            </div>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="作者" label-align="right"><span>{{ novel.author || '未设置' }}</span></el-descriptions-item>
          <el-descriptions-item label="类型" label-align="right"><span>{{ getGenreLabel(novel.genre) || '未设置' }}</span></el-descriptions-item>
          <el-descriptions-item label="创建时间" label-align="right"><span>{{ formatDate(novel.created_at) }}</span></el-descriptions-item>
          <el-descriptions-item label="最后更新" label-align="right"><span>{{ formatDate(novel.updated_at) }}</span></el-descriptions-item>
          <el-descriptions-item label="简介" :span="2" label-align="right">
            <div class="description-text">{{ novel.description || '暂无简介' }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Action Cards -->
      <div class="action-section">
        <h2 class="section-title">创作工具</h2>
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="8" v-for="tool in tools" :key="tool.name">
            <el-card class="tool-card" shadow="hover" @click="handleToolClick(tool)">
              <div class="tool-icon" :style="{ background: tool.color }">
                <el-icon :size="32"><component :is="tool.icon" /></el-icon>
              </div>
              <h3 class="tool-name">{{ tool.name }}</h3>
              <p class="tool-description">{{ tool.description }}</p>
              <el-tag :type="tool.available ? 'success' : 'info'" size="small">{{ tool.available ? '可用' : '即将推出' }}</el-tag>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <el-empty v-else-if="!novelStore.loading" description="小说不存在">
      <el-button type="primary" @click="router.push('/novels')">返回列表</el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNovelStore } from '@/stores/novel'
import { ElMessage } from 'element-plus'
import { Edit, ArrowLeft, User, PriceTag, Location, TrendCharts, List, EditPen } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const novelStore = useNovelStore()

const novelId = computed(() => route.params.id as string)
const novel = computed(() => novelStore.currentNovel)

const tools = computed(() => [
  { name: '章节蓝图', description: '详细规划章节内容', icon: List, color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', route: `/novels/${novelId.value}/chapters`, available: true },
  { name: '角色管理', description: '塑造丰富立体的人物', icon: User, color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', route: `/novels/${novelId.value}/characters`, available: true },
  { name: '情节架构', description: '设计引人入胜的故事脉络', icon: TrendCharts, color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', route: `/novels/${novelId.value}/plot`, available: true },
  { name: '世界观设定', description: '构建独特的小说世界', icon: Location, color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', route: `/novels/${novelId.value}/world`, available: true },
  { name: '内容编辑', description: '开始创作你的小说内容', icon: EditPen, color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', route: `/novels/${novelId.value}/editor`, available: true }
])

onMounted(async () => {
  try {
    await novelStore.fetchNovel(novelId.value)
  } catch (error) {
    ElMessage.error('加载小说信息失败')
  }
})

function handleToolClick(tool: any) {
  if (tool.available) router.push(tool.route)
  else ElMessage.info('该功能即将推出，敬请期待')
}

function getStatusType(status: string) {
  const map: Record<string, string> = { DRAFT: 'info', IN_PROGRESS: 'warning', COMPLETED: 'success', PUBLISHED: 'primary' }
  return map[status] ?? 'info'
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = { DRAFT: '草稿', IN_PROGRESS: '进行中', COMPLETED: '已完成', PUBLISHED: '已发布' }
  return map[status] ?? status
}

function getGenreLabel(genre: string | null | undefined) {
  if (!genre) return ''
  const map: Record<string, string> = { fantasy: '奇幻', 'sci-fi': '科幻', modern: '现代', historical: '历史', mystery: '悬疑', romance: '言情', wuxia: '武侠', other: '其他' }
  return map[genre] ?? genre
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.novel-detail { padding: 40px; min-height: 600px; }
.detail-container { max-width: 1200px; margin: 0 auto; }
.detail-header { display: flex; align-items: flex-start; gap: 20px; margin-bottom: 30px; }
.header-content { flex: 1; }
.novel-title { font-size: 36px; font-weight: bold; color: #333; margin-bottom: 16px; line-height: 1.4; }
.novel-meta { display: flex; gap: 12px; align-items: center; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; color: #666; }
.info-card { margin-bottom: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.mr-8 { margin-right: 8px; }
.description-text { white-space: pre-wrap; color: #444; }
.action-section { margin-top: 24px; }
.section-title { font-size: 20px; font-weight: 600; margin-bottom: 12px; }
.tool-card { cursor: pointer; }
.tool-icon { width: 64px; height: 64px; border-radius: 12px; color: #fff; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.tool-name { margin: 0 0 8px; }
.tool-description { color: #666; min-height: 40px; }
</style>

