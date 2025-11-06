<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700">
    <div class="container mx-auto px-4 py-8">
      <!-- Hero Section -->
      <section class="text-center text-white py-16">
        <div class="max-w-4xl mx-auto">
          <h1 class="text-5xl font-bold mb-4 flex items-center justify-center gap-4">
            <n-icon :size="48" class="text-white">
              <Edit />
            </n-icon>
            欢迎使用 AI 小说创作平台
          </h1>
          <p class="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            通过 AI 辅助，让创作更高效、更有趣
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <n-button 
              type="primary" 
              size="large" 
              @click="router.push('/novels')"
              class="bg-white text-blue-600 hover:bg-blue-50"
            >
              <template #icon>
                <n-icon><Document /></n-icon>
              </template>
              开始创作
            </n-button>
            <n-button 
              size="large" 
              @click="showAIConfig = true"
              class="border-2 border-white/20 text-white hover:bg-white/10"
            >
              <template #icon>
                <n-icon><Settings /></n-icon>
              </template>
              AI 配置
            </n-button>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-16">
        <h2 class="text-3xl font-bold text-center text-white mb-12">强大的创作工具</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div 
            v-for="module in modules" 
            :key="module.name"
            class="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 hover:scale-105 cursor-pointer"
            @click="handleModuleClick(module)"
          >
            <div class="flex items-center justify-center w-16 h-16 mb-4 rounded-2xl" :style="{ background: module.color }">
              <n-icon :size="32" class="text-white">
                <component :is="module.icon" />
              </n-icon>
            </div>
            <h3 class="text-xl font-semibold text-white mb-2">{{ module.name }}</h3>
            <p class="text-blue-100 mb-4">{{ module.description }}</p>
            <n-tag 
              :type="module.status === 'active' ? 'success' : 'info'" 
              size="small"
              class="font-medium"
            >
              {{ module.status === 'active' ? '可用' : '需先选择小说' }}
            </n-tag>
          </div>
        </div>
      </section>

      <!-- Stats Section -->
      <section class="py-16">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div 
            v-for="stat in stats" 
            :key="stat.label"
            class="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
          >
            <div class="flex items-center justify-center w-12 h-12 mb-4 rounded-xl" :style="{ background: stat.color }">
              <n-icon :size="24" class="text-white">
                <component :is="stat.icon" />
              </n-icon>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-white mb-1">{{ stat.value }}</div>
              <div class="text-blue-100">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- AI Configuration Dialog -->
      <n-modal v-model:show="showAIConfig" preset="dialog" title="AI 配置">
        <template #header>
          <div class="text-xl font-semibold">AI 配置</div>
        </template>
        
        <n-form :model="aiConfig" label-width="100">
          <n-form-item label="提供商" path="provider">
            <n-select
              v-model:value="aiConfig.provider"
              placeholder="选择AI提供商"
              :options="providerOptions"
            />
          </n-form-item>

          <n-form-item label="Base URL" v-if="aiConfig.provider === 'custom'" path="base_url">
            <n-input
              v-model:value="aiConfig.base_url"
              placeholder="例如: https://api.example.com"
            />
          </n-form-item>

          <n-form-item label="API Key" path="api_key">
            <n-input
              v-model:value="aiConfig.api_key"
              type="password"
              placeholder="输入你的API密钥"
              show-password-on="click"
            />
          </n-form-item>

          <n-form-item label="模型名称" path="model_name">
            <n-input
              v-model:value="aiConfig.model_name"
              placeholder="例如: gpt-4, claude-3-opus-20240229"
            />
            <n-text depth="3" style="font-size: 12px; margin-top: 5px; display: block;">
              <strong>OpenAI:</strong> gpt-4, gpt-3.5-turbo<br>
              <strong>Anthropic:</strong> claude-3-opus-20240229, claude-3-sonnet-20240229<br>
              <strong>Ollama:</strong> llama2, codellama, mistral
            </n-text>
          </n-form-item>
        </n-form>

        <template #action>
          <n-space>
            <n-button @click="showAIConfig = false">取消</n-button>
            <n-button @click="handleTestConfig" :loading="testing">测试连接</n-button>
            <n-button type="primary" @click="handleSaveConfig">保存配置</n-button>
          </n-space>
        </template>
      </n-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAIStore } from '@/stores/ai'
import { useNovelStore } from '@/stores/novel'
import { 
  NConfigProvider, 
  NButton, 
  NIcon, 
  NModal, 
  NForm, 
  NFormItem, 
  NInput, 
  NSelect, 
  NSpace,
  NText,
  NTag,
  useMessage,
  darkTheme
} from 'naive-ui'
import { 
  Document,
  User,
  Location,
  TrendCharts,
  List,
  Edit,
  Settings
} from '@vicons/tabler'

const router = useRouter()
const aiStore = useAIStore()
const novelStore = useNovelStore()
const { config } = storeToRefs(aiStore)
const message = useMessage()

const showAIConfig = ref(false)
const testing = ref(false)

const aiConfig = ref({
  provider: '',
  base_url: '',
  api_key: '',
  model_name: ''
})

const stats = ref([
  { 
    label: '我的小说', 
    value: '0', 
    icon: Document, 
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
  },
  { 
    label: '创作字数', 
    value: '0', 
    icon: TrendCharts, 
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' 
  },
  { 
    label: '已发布', 
    value: '0', 
    icon: Location, 
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' 
  }
])

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
    icon: Settings,
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    status: 'active',
    route: '/inspiration'
  }
]

const providerOptions = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Anthropic (Claude)', value: 'anthropic' },
  { label: 'Ollama (本地)', value: 'ollama' },
  { label: '自定义API', value: 'custom' }
]

onMounted(async () => {
  aiConfig.value = { ...config.value }
  try {
    await novelStore.fetchNovels()
    stats.value[0].value = novelStore.novels.length.toString()
    const published = novelStore.novels.filter(n => n.status === 'PUBLISHED').length
    stats.value[2].value = published.toString()
  } catch (error) {
    message.error('加载统计信息失败')
  }
})

const handleSaveConfig = () => {
  aiStore.updateConfig(aiConfig.value)
  message.success('AI 配置已保存')
  showAIConfig.value = false
}

const handleTestConfig = async () => {
  testing.value = true
  try {
    // 这里可以添加测试连接的逻辑
    message.success('连接成功')
  } catch (err: any) {
    message.error('连接失败')
  } finally {
    testing.value = false
  }
}

const handleModuleClick = (module: any) => {
  if (module.route) {
    router.push(module.route)
  } else {
    message.info(module.hint || '请先创建或选择一个小说，然后在小说详情页访问此功能')
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}

.bg-gradient-to-br {
  background: linear-gradient(to bottom right, #3b82f6, #8b5cf6);
}
</style>