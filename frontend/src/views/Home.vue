<template>
  <div class="home">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <el-icon :size="48" class="title-icon"><EditPen /></el-icon>
          欢迎使用 AI 小说创作平台
        </h1>
        <p class="hero-subtitle">通过 AI 辅助，让创作更高效、更有趣</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="router.push('/novels')" round>
            <el-icon><Document /></el-icon>
            开始创作
          </el-button>
          <el-button size="large" @click="showAIConfig = true" round plain>
            <el-icon><Setting /></el-icon>
            AI 配置
          </el-button>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h2 class="section-title">强大的创作工具</h2>
      <el-row :gutter="24" class="features-grid">
        <el-col :xs="24" :sm="12" :md="8" v-for="module in modules" :key="module.name">
          <el-card class="feature-card" shadow="hover" @click="handleModuleClick(module)">
            <div class="feature-icon" :style="{ background: module.color }">
              <el-icon :size="40"><component :is="module.icon" /></el-icon>
            </div>
            <h3 class="feature-title">{{ module.name }}</h3>
            <p class="feature-description">{{ module.description }}</p>
            <el-tag :type="module.status === 'active' ? 'success' : 'info'" size="small">
              {{ module.status === 'active' ? '可用' : '需先选择小说' }}
            </el-tag>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Stats Section -->
    <div class="stats-section">
      <el-row :gutter="24">
        <el-col :xs="24" :sm="8" v-for="stat in stats" :key="stat.label">
          <div class="stat-card">
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon :size="32"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- AI Configuration Dialog -->
    <el-dialog v-model="showAIConfig" title="AI 配置" width="600px">
      <el-form :model="aiConfig" label-width="100px">
        <el-form-item label="提供商">
          <el-select v-model="aiConfig.provider" placeholder="选择AI提供商">
            <el-option label="OpenAI" value="openai">
              <span>OpenAI</span>
              <el-tag type="success" size="small" style="float: right;">推荐</el-tag>
            </el-option>
            <el-option label="Anthropic (Claude)" value="anthropic" />
            <el-option label="自定义API" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item label="Base URL" v-if="aiConfig.provider === 'custom'">
          <el-input v-model="aiConfig.base_url" placeholder="例如: https://api.example.com" />
        </el-form-item>

        <el-form-item label="API Key">
          <el-input v-model="aiConfig.api_key" type="password" placeholder="输入你的API密钥" show-password />
        </el-form-item>

        <el-form-item label="模型名称">
          <el-input v-model="aiConfig.model_name" placeholder="例如: gpt-4, claude-3-opus-20240229" />
          <div style="font-size: 12px; color: #999; margin-top: 5px;">
            <strong>OpenAI:</strong> gpt-4, gpt-3.5-turbo<br>
            <strong>Anthropic:</strong> claude-3-opus-20240229, claude-3-sonnet-20240229
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAIConfig = false">取消</el-button>
        <el-button @click="handleTestConfig" :loading="testing">测试连接</el-button>
        <el-button type="primary" @click="handleSaveConfig">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAIStore } from '@/stores/ai'
import { useNovelStore } from '@/stores/novel'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import {
  Document,
  User,
  Location,
  TrendCharts,
  List,
  Edit,
  EditPen,
  Setting,
  DataLine,
  Notebook,
  Collection
} from '@element-plus/icons-vue'

const router = useRouter()
const aiStore = useAIStore()
const novelStore = useNovelStore()
const { config } = storeToRefs(aiStore)

const showAIConfig = ref(false)
const aiConfig = ref({
  provider: '',
  base_url: '',
  api_key: '',
  model_name: ''
})
const testing = ref(false)

const stats = ref([
  { label: '我的小说', value: '0', icon: Notebook, color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { label: '创作字数', value: '0', icon: DataLine, color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { label: '已发布', value: '0', icon: Collection, color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }
])

onMounted(async () => {
  aiConfig.value = { ...config.value }
  try {
    await novelStore.fetchNovels()
    stats.value[0].value = novelStore.novels.length.toString()
    const published = novelStore.novels.filter(n => n.status === 'PUBLISHED').length
    stats.value[2].value = published.toString()
  } catch (error) {
    ElMessage.error('加载统计信息失败')
  }
})

const handleSaveConfig = () => {
  aiStore.updateConfig(aiConfig.value)
  ElMessage.success('AI 配置已保存')
  showAIConfig.value = false
}

const handleTestConfig = async () => {
  testing.value = true
  try {
    const resp = await request.post('/api/ai/test-config', {
      provider: aiConfig.value.provider,
      base_url: aiConfig.value.base_url || undefined,
      api_key: aiConfig.value.api_key || undefined,
      model_name: aiConfig.value.model_name || undefined
    })
    ElMessage.success(resp.data?.message || '连接成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || err.message || '连接失败')
  } finally {
    testing.value = false
  }
}

const handleModuleClick = (module: any) => {
  if (module.route) {
    router.push(module.route)
  } else {
    ElMessage.info('请先创建或选择一个小说，然后在小说详情页访问此功能')
  }
}

const modules = [
  {
    name: '小说管理',
    description: '创建和管理你的小说作品',
    icon: Document,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    status: 'active',
    route: '/novels'
  },
  {
    name: '角色管理',
    description: '塑造丰富立体的人物形象（需先选择小说）',
    icon: User,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    status: 'coming',
    hint: '请先进入具体小说',
    route: '/novels'
  },
  {
    name: '情节架构',
    description: '设计引人入胜的故事脉络（需先选择小说）',
    icon: TrendCharts,
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    status: 'coming',
    hint: '请先进入具体小说',
    route: '/novels'
  },
  {
    name: '世界观设定',
    description: '构建独特的小说世界（需先选择小说）',
    icon: Location,
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    status: 'coming',
    hint: '请先进入具体小说',
    route: '/novels'
  },
  {
    name: '章节蓝图',
    description: '详细规划每个章节内容（需先选择小说）',
    icon: List,
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    status: 'coming',
    hint: '请先进入具体小说',
    route: '/novels'
  },
  {
    name: 'AI 内容生成',
    description: '智能辅助创作精彩内容（需先选择小说）',
    icon: Edit,
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    status: 'coming',
    hint: '请先进入具体小说',
    route: '/novels'
  },
  {
    name: '灵感模式',
    description: '对话式引导，快速构建雏形',
    icon: EditPen,
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    status: 'active',
    route: '/inspiration'
  }
]
</script>

<style scoped>
.home { padding: 0; }

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 40px;
  text-align: center;
  border-radius: 0 0 50% 50% / 0 0 30px 30px;
  margin-bottom: 60px;
}

.hero-content { max-width: 800px; margin: 0 auto; }
.hero-title { font-size: 48px; font-weight: bold; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 12px; }
.hero-subtitle { font-size: 16px; color: rgba(255,255,255,0.9); margin-bottom: 24px; }
.hero-actions { display: flex; gap: 12px; justify-content: center; }

.section-title { font-size: 24px; font-weight: 600; margin: 20px 0; }
.features-grid { margin-top: 10px; }
.feature-card { cursor: pointer; text-align: center; }
.feature-icon { width: 72px; height: 72px; border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 12px; color: #fff; }
.feature-title { margin: 0 0 8px; }
.feature-description { color: #666; min-height: 40px; }

.stats-section { margin-top: 40px; }
.stat-card { display: flex; align-items: center; gap: 12px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.stat-icon { width: 56px; height: 56px; border-radius: 50%; color: #fff; display: inline-flex; align-items: center; justify-content: center; }
.stat-content { text-align: left; }
.stat-value { font-size: 24px; font-weight: bold; line-height: 1; }
.stat-label { color: #666; }

.title-icon { vertical-align: middle; }
</style>
