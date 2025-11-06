<template>
  <el-dialog
    v-model="visible"
    title="版本管理"
    width="90%"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-row :gutter="20">
      <!-- 左侧：版本列表 -->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>历史版本 ({{ versions.length }})</span>
              <el-button type="primary" size="small" @click="handleCreateVersion" :loading="creating">
                <el-icon><Plus /></el-icon>
                新建版本
              </el-button>
            </div>
          </template>

          <el-scrollbar height="500px">
            <div v-if="versions.length === 0" class="empty-state">
              <el-empty description="暂无版本记录" />
            </div>

            <div v-else class="version-list">
              <el-card
                v-for="version in versions"
                :key="version.id"
                class="version-item"
                :class="{ active: version.id === selectedVersionId, current: version.id === chapter?.selected_version_id }"
                shadow="hover"
                @click="selectVersion(version)"
              >
                <div class="version-header">
                  <div class="version-info">
                    <el-tag v-if="version.id === chapter?.selected_version_id" type="success" size="small">
                      当前版本
                    </el-tag>
                    <span class="version-label">{{ version.version_label || `版本 #${version.id}` }}</span>
                  </div>
                  <el-dropdown @command="(cmd) => handleVersionCommand(cmd, version)" trigger="click" @click.stop>
                    <el-icon class="more-icon"><MoreFilled /></el-icon>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="use" v-if="version.id !== chapter?.selected_version_id">
                          <el-icon><Check /></el-icon>
                          设为当前版本
                        </el-dropdown-item>
                        <el-dropdown-item command="delete" divided>
                          <el-icon><Delete /></el-icon>
                          删除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>

                <div class="version-meta">
                  <span v-if="version.provider">
                    <el-icon><Cpu /></el-icon>
                    {{ version.provider }}
                  </span>
                  <span>
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(version.created_at) }}
                  </span>
                </div>

                <div class="version-preview">
                  {{ getPreview(version.content) }}
                </div>
              </el-card>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>

      <!-- 右侧：版本内容 -->
      <el-col :span="16">
        <el-card shadow="never" v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>版本内容</span>
              <div class="actions">
                <el-button
                  v-if="selectedVersion && selectedVersion.id !== chapter?.selected_version_id"
                  type="primary"
                  size="small"
                  @click="useVersion(selectedVersion.id)"
                >
                  <el-icon><Check /></el-icon>
                  设为当前版本
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="!selectedVersion" class="empty-state">
            <el-empty description="请从左侧选择一个版本查看详情" />
          </div>

          <div v-else class="version-content">
            <div class="content-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="版本标签">
                  {{ selectedVersion.version_label || '无' }}
                </el-descriptions-item>
                <el-descriptions-item label="生成模型">
                  {{ selectedVersion.provider || '手动创建' }}
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  {{ new Date(selectedVersion.created_at).toLocaleString('zh-CN') }}
                </el-descriptions-item>
                <el-descriptions-item label="字数">
                  {{ selectedVersion.content.replace(/\s/g, '').length }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <el-divider />

            <div class="content-body">
              <el-input
                type="textarea"
                v-model="selectedVersion.content"
                :rows="15"
                readonly
              />
            </div>

            <el-divider>版本对比</el-divider>

            <div v-if="chapter?.selected_version" class="version-compare">
              <el-button @click="showCompare = !showCompare" plain>
                <el-icon><Operation /></el-icon>
                {{ showCompare ? '隐藏对比' : '与当前版本对比' }}
              </el-button>

              <div v-if="showCompare" class="compare-view">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="compare-label">当前版本</div>
                    <el-input
                      type="textarea"
                      :model-value="chapter.selected_version.content"
                      :rows="10"
                      readonly
                    />
                  </el-col>
                  <el-col :span="12">
                    <div class="compare-label">选中版本</div>
                    <el-input
                      type="textarea"
                      :model-value="selectedVersion.content"
                      :rows="10"
                      readonly
                    />
                  </el-col>
                </el-row>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled, Check, Delete, Clock, Cpu, Operation } from '@element-plus/icons-vue'
import request from '@/utils/request'
import type { ChapterVersion, ChapterWithVersions } from '@/types/chapter-version'

const props = defineProps<{
  chapterId: number
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'version-changed': []
}>()

const visible = ref(props.modelValue)
const loading = ref(false)
const creating = ref(false)
const showCompare = ref(false)

const chapter = ref<ChapterWithVersions | null>(null)
const versions = ref<ChapterVersion[]>([])
const selectedVersion = ref<ChapterVersion | null>(null)
const selectedVersionId = ref<number | null>(null)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    fetchChapterWithVersions()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

async function fetchChapterWithVersions() {
  loading.value = true
  try {
    const response = await request.get(`/api/chapter-versions/chapter/${props.chapterId}/with-versions`)
    chapter.value = response.data
    versions.value = response.data.versions || []

    // 默认选中当前版本
    if (chapter.value.selected_version) {
      selectedVersion.value = chapter.value.selected_version
      selectedVersionId.value = chapter.value.selected_version.id
    } else if (versions.value.length > 0) {
      selectedVersion.value = versions.value[0]
      selectedVersionId.value = versions.value[0].id
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载版本列表失败')
  } finally {
    loading.value = false
  }
}

function selectVersion(version: ChapterVersion) {
  selectedVersion.value = version
  selectedVersionId.value = version.id
}

async function useVersion(versionId: number) {
  try {
    await ElMessageBox.confirm('确定要切换到此版本吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await request.post(`/api/chapter-versions/chapter/${props.chapterId}/select/${versionId}`)
    ElMessage.success('版本已切换')
    fetchChapterWithVersions()
    emit('version-changed')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '切换版本失败')
    }
  }
}

async function handleCreateVersion() {
  creating.value = true
  try {
    // 这里可以调用 AI 生成新版本，或让用户手动输入
    ElMessage.info('此功能需要与 AI 生成集成')
  } finally {
    creating.value = false
  }
}

async function handleVersionCommand(command: string, version: ChapterVersion) {
  if (command === 'use') {
    await useVersion(version.id)
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除此版本吗？此操作不可恢复。', '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      })

      await request.delete(`/api/chapter-versions/${version.id}`)
      ElMessage.success('版本已删除')
      fetchChapterWithVersions()
      emit('version-changed')
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error(error.response?.data?.detail || '删除版本失败')
      }
    }
  }
}

function getPreview(content: string): string {
  return content.slice(0, 100) + (content.length > 100 ? '...' : '')
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.version-item {
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.version-item.active {
  border-color: #409eff;
}

.version-item.current {
  background: #f0f9ff;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.version-label {
  font-weight: 600;
  font-size: 14px;
}

.version-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.version-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.version-preview {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.more-icon {
  cursor: pointer;
  font-size: 18px;
  color: #999;
  transition: color 0.3s;
}

.more-icon:hover {
  color: #409eff;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.version-content {
  padding: 16px 0;
}

.content-info {
  margin-bottom: 16px;
}

.content-body :deep(.el-textarea__inner) {
  font-family: 'Microsoft YaHei', sans-serif;
  line-height: 1.8;
}

.version-compare {
  margin-top: 16px;
}

.compare-view {
  margin-top: 16px;
}

.compare-label {
  font-weight: 600;
  margin-bottom: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.actions {
  display: flex;
  gap: 8px;
}
</style>
