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
              {{ module.status === 'active' ? '可用' : '即将推出' }}
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
    console.error('Failed to load stats:', error)
  }
})

const handleSaveConfig = () => {
  aiStore.updateConfig(aiConfig.value)
  ElMessage.success('AI 配置已保存')
  showAIConfig.value = false
}

const handleModuleClick = (module: any) => {
  if (module.route) {
    router.push(module.route)
  } else {
    ElMessage.info('该功能即将推出')
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
    description: '塑造丰富立体的人物形象',
    icon: User,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    status: 'coming'
  },
  {
    name: '情节架构',
    description: '设计引人入胜的故事脉络',
    icon: TrendCharts,
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    status: 'coming'
  },
  {
    name: '世界观设定',
    description: '构建独特的小说世界',
    icon: Location,
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    status: 'coming'
  },
  {
    name: '章节蓝图',
    description: '详细规划每个章节内容',
    icon: List,
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    status: 'coming'
  },
  {
    name: 'AI 内容生成',
    description: '智能辅助创作精彩内容',
    icon: Edit,
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    status: 'coming'
  }
]
</script>

<style scoped>
.home {
  padding: 0;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 40px;
  text-align: center;
  border-radius: 0 0 50% 50% / 0 0 30px 30px;
  margin-bottom: 60px;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.title-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.hero-subtitle {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.95;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.features-section {
  padding: 40px;
}

.section-title {
  font-size: 32px;
  text-align: center;
  margin-bottom: 40px;
  color: #333;
  font-weight: bold;
}

.features-grid {
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  border-radius: 12px;
  border: 2px solid transparent;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
  border-color: #667eea;
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.feature-title {
  font-size: 20px;
  margin-bottom: 12px;
  color: #333;
  font-weight: 600;
}

.feature-description {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
}

.stats-section {
  padding: 40px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  margin: 40px 0 0;
}

.stat-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .section-title {
    font-size: 24px;
  }

  .stats-section {
    padding: 20px;
  }

  .stat-card {
    margin-bottom: 16px;
  }
}
</style>
