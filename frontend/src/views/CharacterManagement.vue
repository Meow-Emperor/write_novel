<template>
  <div class="character-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>角色管理</h2>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建角色
          </el-button>
        </div>
      </template>

      <el-table :data="characters" v-loading="loading" stripe>
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="role" label="角色类型" width="120" />
        <el-table-column prop="description" label="简介" show-overflow-tooltip />
        <el-table-column prop="personality" label="性格" width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑角色' : '新建角色'"
      width="700px"
      @close="resetForm"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色类型" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色类型" clearable>
            <el-option label="主角" value="主角" />
            <el-option label="配角" value="配角" />
            <el-option label="反派" value="反派" />
            <el-option label="龙套" value="龙套" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色简介"
          />
        </el-form-item>
        <el-form-item label="性格特点" prop="personality">
          <el-input
            v-model="formData.personality"
            type="textarea"
            :rows="3"
            placeholder="请输入角色性格特点"
          />
        </el-form-item>
        <el-form-item label="背景故事" prop="background">
          <el-input
            v-model="formData.background"
            type="textarea"
            :rows="3"
            placeholder="请输入角色背景故事"
          />
        </el-form-item>
        <el-form-item label="外貌描述" prop="appearance">
          <el-input
            v-model="formData.appearance"
            type="textarea"
            :rows="3"
            placeholder="请输入角色外貌描述"
          />
        </el-form-item>
        <el-form-item label="人物关系" prop="relationships">
          <el-input
            v-model="formData.relationships"
            type="textarea"
            :rows="3"
            placeholder="请输入与其他角色的关系"
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
const characters = ref<any[]>([])
const formRef = ref<FormInstance>()

interface CharacterFormData {
  id?: string
  name: string
  role: string
  description: string
  personality: string
  background: string
  appearance: string
  relationships: string
}

const formData = ref<CharacterFormData>({
  name: '',
  role: '',
  description: '',
  personality: '',
  background: '',
  appearance: '',
  relationships: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { max: 100, message: '角色名称不能超过100个字符', trigger: 'blur' }
  ]
}

const fetchCharacters = async () => {
  loading.value = true
  try {
    const response = await request.get('/api/characters', {
      params: { novel_id: novelId }
    })
    characters.value = response.data
  } catch (error) {
    console.error('Failed to fetch characters:', error)
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
    name: row.name,
    role: row.role,
    description: row.description,
    personality: row.personality,
    background: row.background,
    appearance: row.appearance,
    relationships: row.relationships
  }
  formData.value.id = row.id
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个角色吗？', '提示', {
      type: 'warning'
    })
    await request.delete(`/api/characters/${row.id}`)
    ElMessage.success('删除成功')
    fetchCharacters()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete character:', error)
    }
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
        await request.put(`/api/characters/${formData.value.id}`, data)
        ElMessage.success('更新成功')
      } else {
        await request.post('/api/characters', {
          ...data,
          novel_id: novelId
        })
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      fetchCharacters()
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
    name: '',
    role: '',
    description: '',
    personality: '',
    background: '',
    appearance: '',
    relationships: ''
  }
}

onMounted(() => {
  fetchCharacters()
})
</script>

<style scoped>
.character-management {
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
