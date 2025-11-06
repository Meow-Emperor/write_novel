<template>
  <el-dialog
    v-model="visible"
    title="AI 创作助手"
    width="80%"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="assistant-dialog">
      <!-- Step 1: Select Assistant -->
      <div v-if="step === 1" class="step-select">
        <h3>选择助手类型</h3>
        <el-row :gutter="20">
          <el-col
            v-for="assistant in assistants"
            :key="assistant.role"
            :span="8"
          >
            <el-card
              class="assistant-card"
              :class="{ active: selectedRole === assistant.role }"
              shadow="hover"
              @click="selectAssistant(assistant.role)"
            >
              <div class="assistant-icon">
                <el-icon :size="40">
                  <component :is="getAssistantIcon(assistant.role)" />
                </el-icon>
              </div>
              <h4>{{ assistant.name }}</h4>
              <p class="description">{{ assistant.description }}</p>
            </el-card>
          </el-col>
        </el-row>
        <div class="step-actions">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" :disabled="!selectedRole" @click="step = 2">
            下一步
          </el-button>
        </div>
      </div>

      <!-- Step 2: Input & Generate -->
      <div v-if="step === 2" class="step-generate">
        <el-form :model="formData" label-width="100px">
          <el-form-item label="助手类型">
            <el-tag type="primary" size="large">
              {{ getAssistantName(selectedRole) }}
            </el-tag>
            <el-button size="small" style="margin-left: 10px" @click="step = 1">
              更换助手
            </el-button>
          </el-form-item>

          <el-form-item label="创作需求" required>
            <el-input
              v-model="formData.userInput"
              type="textarea"
              :rows="6"
              placeholder="请详细描述您的创作需求..."
            />
          </el-form-item>

          <el-form-item label="AI 配置">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-select v-model="formData.provider" placeholder="Provider">
                  <el-option label="OpenAI" value="openai" />
                  <el-option label="Anthropic" value="anthropic" />
                  <el-option label="Custom" value="custom" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-input
                  v-model="formData.modelName"
                  placeholder="Model (e.g., gpt-4)"
                />
              </el-col>
              <el-col :span="8">
                <el-input-number
                  v-model="formData.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  placeholder="Temperature"
                  style="width: 100%"
                />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item v-if="selectedRole === 'novelist'" label="生成版本数">
            <el-input-number
              v-model="formData.numVersions"
              :min="1"
              :max="5"
              style="width: 100%"
            />
            <span class="form-tip">小说家助手支持生成多个版本供您选择</span>
          </el-form-item>
        </el-form>

        <div class="step-actions">
          <el-button @click="step = 1">上一步</el-button>
          <el-button
            type="primary"
            :loading="generating"
            :disabled="!formData.userInput"
            @click="handleGenerate"
          >
            开始生成
          </el-button>
        </div>
      </div>

      <!-- Step 3: Result -->
      <div v-if="step === 3" class="step-result">
        <div v-if="multipleVersions.length > 0" class="multiple-versions">
          <h3>生成的版本（共 {{ multipleVersions.length }} 个）</h3>
          <el-tabs v-model="activeVersionTab">
            <el-tab-pane
              v-for="(version, index) in multipleVersions"
              :key="index"
              :label="`版本 ${index + 1}`"
              :name="String(index)"
            >
              <div class="version-content">
                <el-input
                  v-model="multipleVersions[index]"
                  type="textarea"
                  :rows="20"
                  readonly
                />
                <div class="version-actions">
                  <el-button type="primary" @click="useVersion(version)">
                    使用此版本
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <div v-else class="single-result">
          <h3>生成结果</h3>
          <el-input
            v-model="generatedContent"
            type="textarea"
            :rows="20"
            readonly
          />
        </div>

        <div class="step-actions">
          <el-button @click="step = 2">重新生成</el-button>
          <el-button type="primary" @click="handleUseContent">
            使用内容
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAIStore } from '@/stores/ai'
import type { AssistantRole, AssistantInfo } from '@/types/ai'
import {
  Document,
  List,
  Edit,
  Check,
  Sunny,
  FolderOpened
} from '@element-plus/icons-vue'

interface Props {
  modelValue: boolean
  novelId: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'content-generated', content: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const aiStore = useAIStore()
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const step = ref(1)
const selectedRole = ref<AssistantRole | null>(null)
const assistants = ref<AssistantInfo[]>([])
const generating = computed(() => aiStore.generating)

const formData = ref({
  userInput: '',
  provider: aiStore.config.provider,
  modelName: aiStore.config.model_name,
  temperature: aiStore.config.temperature ?? 0.7,
  numVersions: 2
})

const generatedContent = ref('')
const multipleVersions = ref<string[]>([])
const activeVersionTab = ref('0')

onMounted(async () => {
  try {
    await aiStore.fetchAssistants()
    assistants.value = aiStore.assistants
  } catch (error) {
    ElMessage.error('加载助手列表失败')
  }
})

function getAssistantIcon(role: AssistantRole) {
  const iconMap = {
    conceptualizer: Sunny,
    blueplanner: Document,
    outliner: List,
    novelist: Edit,
    extractor: FolderOpened,
    evaluator: Check
  }
  return iconMap[role] || Sunny
}

function getAssistantName(role: AssistantRole | null): string {
  if (!role) return ''
  const assistant = assistants.value.find((a) => a.role === role)
  return assistant?.name || role
}

function selectAssistant(role: AssistantRole) {
  selectedRole.value = role
}

async function handleGenerate() {
  if (!selectedRole.value || !formData.value.userInput) {
    ElMessage.warning('请选择助手并输入创作需求')
    return
  }

  try {
    const request = {
      role: selectedRole.value,
      novel_id: props.novelId,
      user_input: formData.value.userInput,
      provider: formData.value.provider,
      model_name: formData.value.modelName,
      temperature: formData.value.temperature
    }

    if (selectedRole.value === 'novelist' && formData.value.numVersions > 1) {
      // Generate multiple versions
      const versions = await aiStore.generateMultipleVersions(
        request,
        formData.value.numVersions
      )
      multipleVersions.value = versions
      generatedContent.value = ''
    } else {
      // Generate single version
      const content = await aiStore.generateWithAssistant(request)
      generatedContent.value = content
      multipleVersions.value = []
    }

    step.value = 3
    ElMessage.success('生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  }
}

function useVersion(content: string) {
  generatedContent.value = content
  multipleVersions.value = []
}

function handleUseContent() {
  if (generatedContent.value) {
    emit('content-generated', generatedContent.value)
    handleClose()
    ElMessage.success('内容已应用')
  } else if (multipleVersions.value.length > 0) {
    ElMessage.warning('请先选择一个版本')
  }
}

function handleClose() {
  visible.value = false
  // Reset state
  setTimeout(() => {
    step.value = 1
    selectedRole.value = null
    formData.value.userInput = ''
    generatedContent.value = ''
    multipleVersions.value = []
    activeVersionTab.value = '0'
  }, 300)
}
</script>

<style scoped>
.assistant-dialog {
  padding: 20px 0;
}

.step-select h3,
.step-generate h3,
.step-result h3 {
  margin-bottom: 20px;
  color: #303133;
}

.assistant-card {
  cursor: pointer;
  text-align: center;
  margin-bottom: 20px;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.assistant-card:hover {
  border-color: #409eff;
  transform: translateY(-2px);
}

.assistant-card.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.assistant-icon {
  color: #409eff;
  margin-bottom: 10px;
}

.assistant-card h4 {
  margin: 10px 0;
  color: #303133;
  font-size: 16px;
}

.assistant-card .description {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  min-height: 60px;
}

.step-actions {
  margin-top: 30px;
  text-align: right;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.multiple-versions {
  margin-bottom: 20px;
}

.version-content {
  margin-top: 10px;
}

.version-actions {
  margin-top: 10px;
  text-align: right;
}

.single-result {
  margin-bottom: 20px;
}
</style>
