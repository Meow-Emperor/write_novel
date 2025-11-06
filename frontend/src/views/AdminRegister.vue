<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>AI小说平台 - 管理员注册</h2>
      </template>
      <el-alert
        title="提示：仅当系统没有任何管理员时允许注册。若已存在管理员，请联系超级管理员添加账号。"
        type="info"
        show-icon
        class="mb-16"
      />
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" placeholder="姓名（可选）" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleRegister" style="width: 100%">注册管理员</el-button>
        </el-form-item>
        <div class="tips">
          已有账号？<el-link type="primary" @click="goLogin">返回登录</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  full_name: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    await request.post('/api/admin/register', {
      username: form.username,
      email: form.email,
      full_name: form.full_name || undefined,
      password: form.password,
      is_superuser: true
    })
    ElMessage.success('注册成功，请登录')
    router.push('/admin/login')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}

const goLogin = () => {
  router.push('/admin/login')
}

onMounted(async () => {
  try {
    const resp = await request.get('/api/admin/can-register')
    if (!resp.data?.can_register) {
      ElMessage.warning('已存在管理员，请联系超级管理员添加账号')
      router.push('/admin/login')
    }
  } catch (_) {
    // 如果检查失败，允许继续尝试注册，以便获取明确的后端提示
  }
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 460px;
}

.register-card h2 {
  text-align: center;
  margin: 0;
}

.mb-16 {
  margin-bottom: 16px;
}

.tips {
  text-align: center;
  color: #666;
}
</style>
