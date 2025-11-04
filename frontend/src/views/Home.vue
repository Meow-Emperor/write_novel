<template>
  <div class="home">
    <el-card class="welcome-card">
      <h1>欢迎使用 AI Novel 小说创作平台</h1>
      <p>通过AI辅助，让创作更高效、更有趣</p>
      <div style="display: flex; gap: 10px; justify-content: center;">
        <el-button type="primary" size="large" @click="router.push('/novels')">
          开始创作
        </el-button>
        <el-button size="large" @click="showAIConfig = true">
          AI配置
        </el-button>
      </div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 30px;">
      <el-col :span="8" v-for="module in modules" :key="module.name">
        <el-card class="module-card" shadow="hover">
          <div class="module-icon" :style="{ background: module.color }">
            <el-icon :size="40"><component :is="module.icon" /></el-icon>
          </div>
          <h3>{{ module.name }}</h3>
          <p>{{ module.description }}</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI Configuration Dialog -->
    <el-dialog v-model="showAIConfig" title="AI配置" width="600px">
      <el-form :model="aiConfig" label-width="100px">
        <el-form-item label="提供商">
          <el-select v-model="aiConfig.provider" placeholder="选择AI提供商">
            <el-option label="OpenAI" value="openai" />
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
            OpenAI: gpt-4, gpt-3.5-turbo<br>
            Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAIConfig = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAIStore } from '@/stores/ai'
import { ElMessage } from 'element-plus'
import { Document, User, Location, TrendCharts, List, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const aiStore = useAIStore()
const { config } = storeToRefs(aiStore)

const showAIConfig = ref(false)
const aiConfig = ref({
  provider: '',
  base_url: '',
  api_key: '',
  model_name: ''
})

onMounted(() => {
  // Load current config
  aiConfig.value = { ...config.value }
})

const handleSaveConfig = () => {
  aiStore.updateConfig(aiConfig.value)
  ElMessage.success('AI配置已保存')
  showAIConfig.value = false
}

const modules = [
  {
    name: '小说草稿',
    description: '智能创作助手',
    icon: Document,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    name: '角色管理',
    description: '塑造丰富人物',
    icon: User,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    name: '情节架构',
    description: '设计故事脉络',
    icon: TrendCharts,
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    name: '世界书',
    description: '构建世界观',
    icon: Location,
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  },
  {
    name: '章节蓝图',
    description: '详细章节规划',
    icon: List,
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  },
  {
    name: '正文生成',
    description: '智能内容创作',
    icon: Edit,
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
  }
]
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-card h1 {
  font-size: 36px;
  margin-bottom: 20px;
}

.welcome-card p {
  font-size: 18px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.module-card {
  text-align: center;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.module-card:hover {
  transform: translateY(-5px);
}

.module-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: white;
}

.module-card h3 {
  font-size: 20px;
  margin-bottom: 10px;
}

.module-card p {
  color: #666;
  font-size: 14px;
}
</style>
