<template>
  <div class="world-settings">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2>世界观设定</h2>
          <el-button v-if="!worldSetting" type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建世界观
          </el-button>
        </div>
      </template>

      <div v-if="worldSetting" class="world-content">
        <el-form :model="formData" ref="formRef" label-width="120px">
          <el-form-item label="时代背景">
            <el-input
              v-model="formData.era"
              :disabled="!isEditing"
              placeholder="请输入时代背景，如：现代、古代、未来等"
            />
          </el-form-item>

          <el-form-item label="主要地点">
            <el-card shadow="never" class="json-card">
              <div v-if="!isEditing">
                <div v-if="formData.locations && Object.keys(formData.locations).length">
                  <div v-for="(value, key) in formData.locations" :key="key" class="json-item">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
                <el-empty v-else description="暂无地点设定" :image-size="60" />
              </div>
              <el-input
                v-else
                v-model="locationsText"
                type="textarea"
                :rows="4"
                placeholder='JSON格式，如: {"主城": "繁华的都市中心", "郊外": "宁静的乡村"}'
              />
            </el-card>
          </el-form-item>

          <el-form-item label="世界规则">
            <el-card shadow="never" class="json-card">
              <div v-if="!isEditing">
                <div v-if="formData.rules && Object.keys(formData.rules).length">
                  <div v-for="(value, key) in formData.rules" :key="key" class="json-item">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
                <el-empty v-else description="暂无规则设定" :image-size="60" />
              </div>
              <el-input
                v-else
                v-model="rulesText"
                type="textarea"
                :rows="4"
                placeholder='JSON格式，如: {"魔法体系": "基于元素的魔法", "社会制度": "君主制"}'
              />
            </el-card>
          </el-form-item>

          <el-form-item label="文化设定">
            <el-card shadow="never" class="json-card">
              <div v-if="!isEditing">
                <div v-if="formData.culture && Object.keys(formData.culture).length">
                  <div v-for="(value, key) in formData.culture" :key="key" class="json-item">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
                <el-empty v-else description="暂无文化设定" :image-size="60" />
              </div>
              <el-input
                v-else
                v-model="cultureText"
                type="textarea"
                :rows="4"
                placeholder='JSON格式，如: {"语言": "通用语", "宗教": "多神教"}'
              />
            </el-card>
          </el-form-item>

          <el-form-item>
            <el-button v-if="!isEditing" type="primary" @click="startEdit">编辑</el-button>
            <template v-else>
              <el-button type="primary" @click="handleSave" :loading="submitting">保存</el-button>
              <el-button @click="cancelEdit">取消</el-button>
            </template>
          </el-form-item>
        </el-form>
      </div>

      <el-empty v-else description="还没有创建世界观设定" :image-size="100" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const novelId = route.params.id as string

const loading = ref(false)
const submitting = ref(false)
const isEditing = ref(false)
const worldSetting = ref<any>(null)
const formRef = ref<FormInstance>()

const formData = ref({
  era: '',
  locations: {} as Record<string, any>,
  rules: {} as Record<string, any>,
  culture: {} as Record<string, any>
})

const locationsText = ref('')
const rulesText = ref('')
const cultureText = ref('')

const fetchWorldSetting = async () => {
  loading.value = true
  try {
    const response = await request.get(`/api/worlds/novel/${novelId}`)
    worldSetting.value = response.data
    formData.value = {
      era: response.data.era || '',
      locations: response.data.locations || {},
      rules: response.data.rules || {},
      culture: response.data.culture || {}
    }
  } catch (error: any) {
    if (error.response?.status !== 404) {
      console.error('Failed to fetch world setting:', error)
    }
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  submitting.value = true
  try {
    const response = await request.post('/api/worlds', {
      novel_id: novelId,
      era: '',
      locations: {},
      rules: {},
      culture: {}
    })
    worldSetting.value = response.data
    formData.value = {
      era: '',
      locations: {},
      rules: {},
      culture: {}
    }
    ElMessage.success('创建成功')
    isEditing.value = true
  } catch (error) {
    console.error('Failed to create world setting:', error)
  } finally {
    submitting.value = false
  }
}

const startEdit = () => {
  isEditing.value = true
  locationsText.value = JSON.stringify(formData.value.locations || {}, null, 2)
  rulesText.value = JSON.stringify(formData.value.rules || {}, null, 2)
  cultureText.value = JSON.stringify(formData.value.culture || {}, null, 2)
}

const cancelEdit = () => {
  isEditing.value = false
  if (worldSetting.value) {
    formData.value = {
      era: worldSetting.value.era || '',
      locations: worldSetting.value.locations || {},
      rules: worldSetting.value.rules || {},
      culture: worldSetting.value.culture || {}
    }
  }
}

const handleSave = async () => {
  submitting.value = true
  try {
    let locations = {}
    let rules = {}
    let culture = {}

    try {
      locations = locationsText.value ? JSON.parse(locationsText.value) : {}
    } catch (e) {
      ElMessage.error('地点设定JSON格式错误')
      submitting.value = false
      return
    }

    try {
      rules = rulesText.value ? JSON.parse(rulesText.value) : {}
    } catch (e) {
      ElMessage.error('世界规则JSON格式错误')
      submitting.value = false
      return
    }

    try {
      culture = cultureText.value ? JSON.parse(cultureText.value) : {}
    } catch (e) {
      ElMessage.error('文化设定JSON格式错误')
      submitting.value = false
      return
    }

    await request.put(`/api/worlds/${worldSetting.value.id}`, {
      era: formData.value.era,
      locations,
      rules,
      culture
    })
    
    ElMessage.success('保存成功')
    isEditing.value = false
    fetchWorldSetting()
  } catch (error) {
    console.error('Failed to save world setting:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchWorldSetting()
})
</script>

<style scoped>
.world-settings {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.world-content {
  margin-top: 20px;
}

.json-card {
  width: 100%;
  background-color: #f5f7fa;
}

.json-item {
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
}

.json-item:last-child {
  border-bottom: none;
}

.json-item strong {
  color: #409eff;
  margin-right: 8px;
}
</style>
