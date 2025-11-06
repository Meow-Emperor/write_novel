<template>
  <n-config-provider :theme="theme">
    <div class="app-layout">
      <!-- Header Navigation -->
      <header class="app-header">
        <div class="header-content">
          <div class="logo" @click="router.push('/')">
            <n-icon :size="32" color="#fff">
              <Edit />
            </n-icon>
            <span class="logo-text">AI 小说创作平台</span>
          </div>
          <nav class="nav-menu">
            <n-menu
              mode="horizontal"
              :value="activeMenu"
              :options="menuOptions"
              @update:value="handleMenuSelect"
            />
          </nav>
          <div class="header-actions">
            <n-button circle @click="showAIConfig = true">
              <template #icon>
                <n-icon><Settings /></n-icon>
              </template>
            </n-button>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="app-main">
        <div class="main-content">
          <slot></slot>
        </div>
      </main>

      <!-- Footer -->
      <footer class="app-footer">
        <div class="footer-content">
          <p>© 2024 AI 小说创作平台 - 让创作更智能</p>
        </div>
      </footer>

      <!-- AI Configuration Dialog -->
      <n-modal v-model:show="showAIConfig" preset="dialog" title="AI 配置">
        <template #header>
          <div>AI 配置</div>
        </template>
        
        <n-form :model="aiConfig" label-width="100">
          <n-form-item label="提供商">
            <n-select
              v-model:value="aiConfig.provider"
              placeholder="选择AI提供商"
              :options="providerOptions"
            />
          </n-form-item>

          <n-form-item label="Base URL" v-if="aiConfig.provider === 'custom'">
            <n-input
              v-model:value="aiConfig.base_url"
              placeholder="例如: https://api.example.com"
            />
          </n-form-item>

          <n-form-item label="API Key">
            <n-input
              v-model:value="aiConfig.api_key"
              type="password"
              placeholder="输入你的API密钥"
              show-password-on="click"
            />
          </n-form-item>

          <n-form-item label="模型名称">
            <n-input
              v-model:value="aiConfig.model_name"
              placeholder="例如: gpt-4, claude-3-opus-20240229"
            />
            <n-text depth="3" style="font-size: 12px; margin-top: 5px; display: block;">
              OpenAI: gpt-4, gpt-3.5-turbin<br>
              Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229<br>
              Ollama: llama2, codellama, mistral
            </n-text>
          </n-form-item>
        </n-form>

        <template #action>
          <n-space>
            <n-button @click="showAIConfig = false">取消</n-button>
            <n-button type="primary" @click="handleSaveConfig">保存</n-button>
          </n-space>
        </template>
      </n-modal>
    </div>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, watch, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAIStore } from '@/stores/ai'
import { useNovelStore } from '@/stores/novel'
import { 
  NConfigProvider, 
  NMenu, 
  NButton, 
  NIcon, 
  NModal, 
  NForm, 
  NFormItem, 
  NInput, 
  NSelect, 
  NSpace,
  NText,
  useMessage,
  darkTheme,
  type MenuOption
} from 'naive-ui'
import { Edit, Settings } from '@vicons/tabler'

const router = useRouter()
const route = useRoute()
const aiStore = useAIStore()
const novelStore = useNovelStore()
const { config } = storeToRefs(aiStore)
const message = useMessage()

const showAIConfig = ref(false)
const theme = computed(() => darkTheme)

const aiConfig = ref({
  provider: '',
  base_url: '',
  api_key: '',
  model_name: ''
})

const providerOptions = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Anthropic (Claude)', value: 'anthropic' },
  { label: 'Ollama (本地)', value: 'ollama' },
  { label: '自定义API', value: 'custom' }
]

const activeMenu = computed(() => {
  if (route.path === '/') return '/'
  if (route.path.startsWith('/novels')) return '/novels'
  return route.path
})

const currentNovelId = computed(() => {
  if (novelStore.currentNovel) {
    return novelStore.currentNovel.id
  }
  if (route.params.id) {
    return route.params.id as string
  }
  return null
})

const menuOptions = computed<MenuOption[]>(() => {
  const baseOptions: MenuOption[] = [
    {
      label: '首页',
      key: '/'
    },
    {
      label: '我的小说',
      key: '/novels'
    },
    {
      label: '管理后台',
      key: '/admin'
    }
  ]

  if (currentNovelId.value) {
    baseOptions.push({
      label: '创作工具',
      key: 'tools',
      children: [
        {
          label: '小说详情',
          key: `/novels/${currentNovelId.value}`
        },
        {
          label: '世界观设定',
          key: `/novels/${currentNovelId.value}/world`
        },
        {
          label: '角色管理',
          key: `/novels/${currentNovelId.value}/characters`
        },
        {
          label: '情节架构',
          key: `/novels/${currentNovelId.value}/plot`
        },
        {
          label: '章节蓝图',
          key: `/novels/${currentNovelId.value}/chapters`
        },
        {
          label: '内容编辑',
          key: `/novels/${currentNovelId.value}/editor`
        }
      ]
    })
  }

  return baseOptions
})

watch(config, (newConfig) => {
  aiConfig.value = { ...newConfig }
}, { immediate: true })

const handleMenuSelect = (key: string) => {
  router.push(key)
}

const handleSaveConfig = () => {
  aiStore.updateConfig(aiConfig.value)
  message.success('AI配置已保存')
  showAIConfig.value = false
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  letter-spacing: 0.5px;
}

.nav-menu {
  flex: 1;
  margin: 0 40px;
}

.nav-menu :deep(.n-menu) {
  background: transparent;
  border: none;
}

.nav-menu :deep(.n-menu-item) {
  color: #fff;
  font-size: 15px;
  font-weight: 500;
}

.nav-menu :deep(.n-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.header-actions :deep(.n-button) {
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
}

.header-actions :deep(.n-button:hover) {
  background-color: rgba(255, 255, 255, 0.3);
}

.app-main {
  flex: 1;
  padding: 30px 20px;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 220px);
}

.app-footer {
  background: rgba(0, 0, 0, 0.2);
  color: #fff;
  padding: 20px 0;
  text-align: center;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}
</style>