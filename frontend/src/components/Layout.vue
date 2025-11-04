<template>
  <div class="app-layout">
    <!-- Header Navigation -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo" @click="router.push('/')">
          <el-icon :size="32" color="#fff"><EditPen /></el-icon>
          <span class="logo-text">AI 小说创作平台</span>
        </div>
        <nav class="nav-menu">
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            background-color="transparent"
            text-color="#fff"
            active-text-color="#ffd04b"
            @select="handleMenuSelect"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/novels">我的小说</el-menu-item>
            <el-menu-item index="/admin/login">管理后台</el-menu-item>
            <el-sub-menu index="tools" v-if="currentNovelId">
              <template #title>创作工具</template>
              <el-menu-item :index="`/novels/${currentNovelId}`">小说详情</el-menu-item>
              <el-menu-item :index="`/novels/${currentNovelId}/world`">世界观设定</el-menu-item>
              <el-menu-item :index="`/novels/${currentNovelId}/characters`">角色管理</el-menu-item>
              <el-menu-item :index="`/novels/${currentNovelId}/plot`">情节架构</el-menu-item>
              <el-menu-item :index="`/novels/${currentNovelId}/chapters`">章节蓝图</el-menu-item>
              <el-menu-item :index="`/novels/${currentNovelId}/editor`">内容编辑</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </nav>
        <div class="header-actions">
          <el-button circle @click="showAIConfig = true">
            <el-icon><Setting /></el-icon>
          </el-button>
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
    <el-dialog v-model="showAIConfig" title="AI 配置" width="600px">
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
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAIStore } from '@/stores/ai'
import { useNovelStore } from '@/stores/novel'
import { ElMessage } from 'element-plus'
import { EditPen, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
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

watch(config, (newConfig) => {
  aiConfig.value = { ...newConfig }
}, { immediate: true })

const handleMenuSelect = (index: string) => {
  router.push(index)
}

const handleSaveConfig = () => {
  aiStore.updateConfig(aiConfig.value)
  ElMessage.success('AI配置已保存')
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

.nav-menu :deep(.el-menu) {
  border: none;
}

.nav-menu :deep(.el-menu-item) {
  font-size: 15px;
  font-weight: 500;
  border-bottom: none !important;
}

.nav-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.nav-menu :deep(.el-sub-menu__title) {
  border-bottom: none !important;
}

.header-actions :deep(.el-button) {
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
}

.header-actions :deep(.el-button:hover) {
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
