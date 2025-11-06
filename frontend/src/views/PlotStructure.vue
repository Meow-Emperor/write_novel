<template>
  <div class="plot-structure">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>情节架构</h2>
          <div>
            <el-button class="mr-8" @click="openAIDialog">
              <el-icon><Plus /></el-icon>
              AI 生成情节
            </el-button>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建情节
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="plots" v-loading="loading" stripe>
        <el-table-column prop="order" label="顺序" width="80" />
        <el-table-column prop="title" label="情节标题" width="220" />
        <el-table-column prop="description" label="情节描述" show-overflow-tooltip />
        <el-table-column prop="act" label="幕次" width="100" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row, $index }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="moveUp($index)" :disabled="$index === 0">上移</el-button>
            <el-button size="small" @click="moveDown($index)" :disabled="$index === plots.length - 1">下移</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑情节 -->
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑情节' : '新建情节'" width="720px" @close="resetForm">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="情节标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入情节标题" />
        </el-form-item>
        <el-form-item label="情节描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="4" placeholder="请输入情节描述" />
        </el-form-item>
        <el-form-item label="幕次" prop="act">
          <el-select v-model="formData.act" placeholder="请选择幕次" clearable style="width: 100%">
            <el-option label="第一幕" value="第一幕" />
            <el-option label="第二幕" value="第二幕" />
            <el-option label="第三幕" value="第三幕" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键事件" prop="key_events">
          <el-input v-model="formData.key_events" type="textarea" :rows="3" placeholder="请输入关键事件（可分行）" />
        </el-form-item>
        <el-form-item label="相关角色" prop="characters">
          <el-input v-model="formData.characters" type="textarea" :rows="2" placeholder="请输入相关角色（可分行）" />
        </el-form-item>
        <el-form-item label="冲突/转折" prop="conflicts">
          <el-input v-model="formData.conflicts" type="textarea" :rows="3" placeholder="请输入冲突与转折" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- AI 生成情节 -->
    <el-dialog v-model="aiDialogVisible" title="AI 生成情节" width="520px">
      <el-form :model="aiForm" label-width="100px">
        <el-form-item label="情节类型">
          <el-select v-model="aiForm.plot_type" style="width: 100%">
            <el-option label="主线" value="main" />
            <el-option label="支线" value="subplot" />
            <el-option label="反转" value="twist" />
          </el-select>
        </el-form-item>
        <el-form-item label="长度">
          <el-select v-model="aiForm.plot_length" style="width: 100%">
            <el-option label="简短" value="short" />
            <el-option label="适中" value="medium" />
            <el-option label="详细" value="long" />
          </el-select>
        </el-form-item>
        <el-form-item label="保存方式">
          <el-radio-group v-model="aiForm.mode">
            <el-radio label="preview">预览并编辑</el-radio>
            <el-radio label="auto">直接创建</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="aiDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAIGeneratePlot" :loading="aiSubmitting">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { parsePlot } from '@/utils/aiParse'
import { useAIStore } from '@/stores/ai'

const aiStore = useAIStore()
const route = useRoute()
const novelId = route.params.id as string

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const plots = ref<any[]>([])
const formRef = ref<FormInstance>()

const aiDialogVisible = ref(false)
const aiSubmitting = ref(false)
const aiForm = ref<{ plot_type: string; plot_length: string; mode: 'preview' | 'auto' }>({ plot_type: 'main', plot_length: 'medium', mode: 'preview' })

interface PlotFormData {
  id?: string
  title: string
  description: string
  act: string
  key_events: string
  characters: string
  conflicts: string
}

const formData = ref<PlotFormData>({
  title: '',
  description: '',
  act: '',
  key_events: '',
  characters: '',
  conflicts: ''
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入情节标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度为 1 到 200 个字符', trigger: 'blur' }
  ]
}

async function fetchPlots() {
  loading.value = true
  try {
    const response = await request.get('/api/plots', { params: { novel_id: novelId } })
    plots.value = (response.data || []).sort((a: any, b: any) => (a.order ?? 0) - (b.order ?? 0))
  } catch (error) {
    console.error('Failed to fetch plots:', error)
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  isEditing.value = false
  dialogVisible.value = true
  formData.value = { title: '', description: '', act: '', key_events: '', characters: '', conflicts: '' }
}

function handleEdit(row: any) {
  isEditing.value = true
  formData.value = {
    title: row.title,
    description: row.description,
    act: row.act || '',
    key_events: row.key_events || '',
    characters: row.characters || '',
    conflicts: row.conflicts || ''
  }
  ;(formData.value as any).id = row.id
  dialogVisible.value = true
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定要删除这个情节吗？', '提示', { type: 'warning' })
    await request.delete(`/api/plots/${row.id}`)
    ElMessage.success('删除成功')
    fetchPlots()
  } catch (error) {
    if (error !== 'cancel') console.error('Failed to delete plot:', error)
  }
}

async function moveUp(index: number) {
  if (index === 0) return
  const current = plots.value[index]
  const prev = plots.value[index - 1]
  try {
    await request.put(`/api/plots/${current.id}`, { order: prev.order })
    await request.put(`/api/plots/${prev.id}`, { order: current.order })
    fetchPlots()
  } catch (e) {
    console.error('Failed to move up:', e)
  }
}

async function moveDown(index: number) {
  if (index === plots.value.length - 1) return
  const current = plots.value[index]
  const next = plots.value[index + 1]
  try {
    await request.put(`/api/plots/${current.id}`, { order: next.order })
    await request.put(`/api/plots/${next.id}`, { order: current.order })
    fetchPlots()
  } catch (e) {
    console.error('Failed to move down:', e)
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload: any = { ...formData.value }
      delete payload.id
      if (isEditing.value && (formData.value as any).id) {
        await request.put(`/api/plots/${(formData.value as any).id}`, payload)
        ElMessage.success('更新成功')
      } else {
        const maxOrder = plots.value.length > 0 ? Math.max(...plots.value.map((p: any) => p.order ?? 0)) : 0
        await request.post('/api/plots', { ...payload, novel_id: novelId, order: maxOrder + 1 })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchPlots()
    } catch (e) {
      console.error('Submit failed:', e)
    } finally {
      submitting.value = false
    }
  })
}

function openAIDialog() {
  aiForm.value = { plot_type: 'main', plot_length: 'medium', mode: 'preview' }
  aiDialogVisible.value = true
}

async function handleAIGeneratePlot() {
  try {
    aiSubmitting.value = true
    const cfg = aiStore.config
    const resp = await request.post('/api/ai/generate-plot', {
      novel_id: novelId,
      plot_type: aiForm.value.plot_type,
      plot_length: aiForm.value.plot_length,
      provider: cfg.provider,
      base_url: cfg.base_url,
      api_key: cfg.api_key,
      model_name: cfg.model_name,
      temperature: cfg.temperature
    })
    const content: string = resp.data?.content || ''
    const parsed = parsePlot(content)

    if (aiForm.value.mode === 'auto') {
      const maxOrder = plots.value.length > 0 ? Math.max(...plots.value.map((p: any) => p.order ?? 0)) : 0
      await request.post('/api/plots', {
        novel_id: novelId,
        title: parsed.title,
        description: parsed.description,
        key_events: parsed.key_events,
        characters: parsed.characters,
        conflicts: parsed.conflicts,
        order: maxOrder + 1
      })
      ElMessage.success('AI 已生成并创建情节')
      aiDialogVisible.value = false
      fetchPlots()
    } else {
      // 预览并编辑：填充到表单并打开编辑弹窗
      isEditing.value = false
      formData.value = {
        title: parsed.title || 'AI 生成情节',
        description: parsed.description || content,
        act: '',
        key_events: parsed.key_events || '',
        characters: parsed.characters || '',
        conflicts: parsed.conflicts || ''
      }
      aiDialogVisible.value = false
      dialogVisible.value = true
      ElMessage.success('AI 已生成内容，已填入表单供编辑')
    }
  } catch (e) {
    // 拦截器已提示
  } finally {
    aiSubmitting.value = false
  }
}

onMounted(() => {
  fetchPlots()
})
</script>

<style scoped>
.plot-structure { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h2 { margin: 0; font-size: 20px; }
.mr-8 { margin-right: 8px; }
</style>

