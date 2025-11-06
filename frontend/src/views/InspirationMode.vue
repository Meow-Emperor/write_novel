<template>
  <div class="inspiration-mode">
    <el-card class="intro-card">
      <template #header>
        <div class="card-header">
          <h2>灵感模式 · 对话式引导</h2>
          <el-tag type="success" v-if="novelId">已创建：{{ novelTitle }}</el-tag>
        </div>
      </template>

      <el-form label-width="100px" :disabled="initializing">
        <el-form-item label="题材/类型">
          <el-input v-model="form.genre" placeholder="如：奇幻、科幻、现代、历史等" />
        </el-form-item>
        <el-form-item label="故事概念">
          <el-input type="textarea" :rows="3" v-model="form.concept" placeholder="一句话或一小段描述你的想法" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="assistantDialogVisible = true" :icon="Sunny">
            AI 助手引导
          </el-button>
          <el-button type="primary" @click="startFlow" :loading="initializing">开始构建故事雏形</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="novelId" class="steps-card">
      <template #header>
        <div class="card-header"><span>自动生成进度</span></div>
      </template>
      <el-steps :active="activeStep" finish-status="success">
        <el-step title="创建小说" />
        <el-step title="世界观设定" />
        <el-step title="主线情节" />
        <el-step title="核心角色" />
        <el-step title="首章大纲" />
      </el-steps>
      <div class="log">
        <div v-for="(l, i) in logs" :key="i" class="log-line">{{ l }}</div>
      </div>
      <div class="actions">
        <el-button type="primary" @click="gotoNovel" :disabled="!novelId">进入小说详情</el-button>
      </div>
    </el-card>

    <!-- AI Assistant Dialog -->
    <AIAssistantDialog
      v-model="assistantDialogVisible"
      :novel-id="novelId || 'temp'"
      @content-generated="handleAssistantContent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Sunny } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useAIStore } from '@/stores/ai'
import AIAssistantDialog from '@/components/AIAssistantDialog.vue'

const router = useRouter()
const aiStore = useAIStore()

const form = ref({ genre: '', concept: '' })
const initializing = ref(false)
const novelId = ref<string>('')
const novelTitle = ref('新故事')
const activeStep = ref(0)
const logs = ref<string[]>([])
const assistantDialogVisible = ref(false)

function pushLog(msg: string) { logs.value.push(msg) }

function handleAssistantContent(content: string) {
  // Apply the generated content to the concept field
  form.value.concept = content
  ElMessage.success('AI 助手内容已应用到故事概念')
}

async function startFlow() {
  try {
    initializing.value = true
    activeStep.value = 0
    logs.value = []

    // 1) 创建草稿小说（若已带 novelId 则跳过创建）
    if (!novelId.value) {
      novelTitle.value = (form.value.concept?.trim() ? form.value.concept.trim().slice(0, 16) : '新的故事')
      const create = await request.post('/api/novels', {
        title: novelTitle.value,
        genre: form.value.genre || '',
        description: form.value.concept || '',
        status: 'DRAFT'
      })
      novelId.value = create.data.id
      pushLog('✓ 已创建小说：' + novelTitle.value)
    } else {
      pushLog('✓ 使用现有小说：' + novelId.value)
    }
    activeStep.value = 1

    // 2) 生成世界观（整体）并写入
    try {
      const world = await request.post('/api/ai/generate-world', {
        novel_id: novelId.value,
        focus: 'overall',
        provider: aiStore.config.provider,
        base_url: aiStore.config.base_url || undefined,
        api_key: aiStore.config.api_key || undefined,
        model_name: aiStore.config.model_name || undefined,
        temperature: aiStore.config.temperature || undefined
      })
      const content: string = world.data?.content || ''
      let wsId: string | null = null
      try {
        const existing = await request.get(`/api/worlds/novel/${novelId.value}`)
        wsId = existing.data?.id
      } catch (_) { /* 404: none */ }
      if (!wsId) {
        const ws = await request.post('/api/worlds', { novel_id: novelId.value, era: '', locations: {}, rules: {}, culture: {} })
        wsId = ws.data.id
      }
      await request.put(`/api/worlds/${wsId}`, { era: '', locations: {}, rules: { note: content }, culture: {} })
      pushLog('✓ 已生成世界观（可在世界观页面继续完善）')
    } catch (e: any) {
      pushLog('⚠ 世界观生成失败: ' + (e?.response?.data?.detail || e?.message))
    }
    activeStep.value = 2

    // 3) 生成主线情节并创建一条情节记录
    try {
      const plot = await request.post('/api/ai/generate-plot', {
        novel_id: novelId.value,
        plot_type: 'main',
        plot_length: 'medium',
        provider: aiStore.config.provider,
        base_url: aiStore.config.base_url || undefined,
        api_key: aiStore.config.api_key || undefined,
        model_name: aiStore.config.model_name || undefined,
        temperature: aiStore.config.temperature || undefined
      })
      await request.post('/api/plots', {
        novel_id: novelId.value,
        title: '主线',
        description: plot.data?.content || '',
        key_events: plot.data?.content || '',
        order: 1
      })
      pushLog('✓ 已生成主线情节')
    } catch (e: any) {
      pushLog('⚠ 主线情节生成失败: ' + (e?.response?.data?.detail || e?.message))
    }
    activeStep.value = 3

    // 4) 生成三个核心角色（主角/反派/配角）
    const roles = [
      { role: 'protagonist', label: '主角' },
      { role: 'antagonist', label: '反派' },
      { role: 'supporting', label: '配角' }
    ]
    let successCount = 0
    for (const r of roles) {
      try {
        const resp = await request.post('/api/ai/generate-character', {
          novel_id: novelId.value,
          character_role: r.role,
          provider: aiStore.config.provider,
          base_url: aiStore.config.base_url || undefined,
          api_key: aiStore.config.api_key || undefined,
          model_name: aiStore.config.model_name || undefined,
          temperature: aiStore.config.temperature || undefined
        })
        const text: string = resp.data?.content || ''
        const firstLine = text.split(/\r?\n/).map(s => s.trim()).find(Boolean) || ''
        const name = (firstLine.replace(/^[-#*\s]+/, '').slice(0, 30)) || (r.label + '（AI）')
        await request.post('/api/characters', {
          novel_id: novelId.value,
          name,
          role: r.label,
          description: text
        })
        successCount++
      } catch (e: any) {
        pushLog(`⚠ ${r.label}生成失败: ` + (e?.response?.data?.detail || e?.message))
      }
    }
    pushLog(`✓ 已生成核心角色（${successCount}/3）`)
    activeStep.value = 4

    // 5) 生成第一章大纲并创建章节
    try {
      const outline = await request.post('/api/ai/generate-chapter-outline', {
        novel_id: novelId.value,
        chapter_number: 1,
        provider: aiStore.config.provider,
        base_url: aiStore.config.base_url || undefined,
        api_key: aiStore.config.api_key || undefined,
        model_name: aiStore.config.model_name || undefined,
        temperature: aiStore.config.temperature || undefined
      })
      await request.post('/api/chapters/', {
        novel_id: novelId.value,
        title: '第一章',
        chapter_number: 1,
        summary: outline.data?.content || '',
        status: 'DRAFT',
        word_count: 0
      })
      pushLog('✓ 已生成第一章大纲')
    } catch (e: any) {
      pushLog('⚠ 第一章大纲生成失败: ' + (e?.response?.data?.detail || e?.message))
    }
    activeStep.value = 5
    ElMessage.success('灵感模式完成，已生成基础雏形！')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '运行失败')
  } finally {
    initializing.value = false
  }
}

function gotoNovel() {
  if (novelId.value) router.push(`/novels/${novelId.value}`)
}

// If novelId is provided via query, use it
import { useRoute } from 'vue-router'
const route = useRoute()
const qNovelId = (route.query.novelId as string) || ''
if (qNovelId) {
  novelId.value = qNovelId
}
</script>

<style scoped>
.inspiration-mode { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.intro-card, .steps-card { margin-bottom: 16px; }
.log { margin-top: 16px; background: #f5f7fa; padding: 10px; border-radius: 4px; max-height: 260px; overflow: auto; }
.log-line { font-size: 13px; color: #606266; line-height: 1.6; }
.actions { margin-top: 12px; text-align: right; }
</style>
