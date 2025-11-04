<template>
  <div class="plot-structure">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>情节架构</h2>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建情节
          </el-button>
        </div>
      </template>

      <el-table :data="plots" v-loading="loading" stripe>
        <el-table-column prop="order" label="顺序" width="80" />
        <el-table-column prop="title" label="情节标题" width="200" />
        <el-table-column prop="description" label="情节描述" show-overflow-tooltip />
        <el-table-column prop="act" label="幕次" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row, $index }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="moveUp($index)" :disabled="$index === 0">上移</el-button>
            <el-button size="small" @click="moveDown($index)" :disabled="$index === plots.length - 1">下移</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑情节' : '新建情节'"
      width="700px"
      @close="resetForm"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="情节标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入情节标题" />
        </el-form-item>
        <el-form-item label="情节描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入情节描述"
          />
        </el-form-item>
        <el-form-item label="幕次" prop="act">
          <el-select v-model="formData.act" placeholder="请选择幕次" clearable>
            <el-option label="第一幕" value="第一幕" />
            <el-option label="第二幕" value="第二幕" />
            <el-option label="第三幕" value="第三幕" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键事件" prop="key_events">
          <el-input
            v-model="formData.key_events"
            type="textarea"
            :rows="3"
            placeholder="请输入关键事件"
          />
        </el-form-item>
        <el-form-item label="相关角色" prop="characters">
          <el-input
            v-model="formData.characters"
            type="textarea"
            :rows="2"
            placeholder="请输入相关角色"
          />
        </el-form-item>
        <el-form-item label="冲突与转折" prop="conflicts">
          <el-input
            v-model="formData.conflicts"
            type="textarea"
            :rows="3"
            placeholder="请输入冲突与转折点"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
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

const route = useRoute()
const novelId = route.params.id as string

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const plots = ref<any[]>([])
const formRef = ref<FormInstance>()

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
    { max: 200, message: '情节标题不能超过200个字符', trigger: 'blur' }
  ]
}

const fetchPlots = async () => {
  loading.value = true
  try {
    const response = await request.get('/api/plots', {
      params: { novel_id: novelId }
    })
    plots.value = response.data.sort((a: any, b: any) => a.order - b.order)
  } catch (error) {
    console.error('Failed to fetch plots:', error)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  isEditing.value = false
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEditing.value = true
  formData.value = {
    title: row.title,
    description: row.description,
    act: row.act,
    key_events: row.key_events,
    characters: row.characters,
    conflicts: row.conflicts
  }
  formData.value.id = row.id
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个情节吗？', '提示', {
      type: 'warning'
    })
    await request.delete(`/api/plots/${row.id}`)
    ElMessage.success('删除成功')
    fetchPlots()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete plot:', error)
    }
  }
}

const moveUp = async (index: number) => {
  if (index === 0) return
  
  const currentPlot = plots.value[index]
  const prevPlot = plots.value[index - 1]
  
  try {
    await request.put(`/api/plots/${currentPlot.id}`, { order: prevPlot.order })
    await request.put(`/api/plots/${prevPlot.id}`, { order: currentPlot.order })
    fetchPlots()
  } catch (error) {
    console.error('Failed to move plot up:', error)
  }
}

const moveDown = async (index: number) => {
  if (index === plots.value.length - 1) return
  
  const currentPlot = plots.value[index]
  const nextPlot = plots.value[index + 1]
  
  try {
    await request.put(`/api/plots/${currentPlot.id}`, { order: nextPlot.order })
    await request.put(`/api/plots/${nextPlot.id}`, { order: currentPlot.order })
    fetchPlots()
  } catch (error) {
    console.error('Failed to move plot down:', error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const data = { ...formData.value }
      delete data.id
      
      if (isEditing.value) {
        await request.put(`/api/plots/${formData.value.id}`, data)
        ElMessage.success('更新成功')
      } else {
        const maxOrder = plots.value.length > 0 
          ? Math.max(...plots.value.map(p => p.order)) 
          : 0
        await request.post('/api/plots', {
          ...data,
          novel_id: novelId,
          order: maxOrder + 1
        })
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      fetchPlots()
    } catch (error) {
      console.error('Failed to submit:', error)
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  formRef.value?.resetFields()
  formData.value = {
    title: '',
    description: '',
    act: '',
    key_events: '',
    characters: '',
    conflicts: ''
  }
}

onMounted(() => {
  fetchPlots()
})
</script>

<style scoped>
.plot-structure {
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
</style>
