<template>
  <div class="admin-container">
    <el-container>
      <el-aside width="200px" class="admin-sidebar">
        <el-menu
          :default-active="activeMenu"
          class="admin-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="novels">
            <el-icon><Reading /></el-icon>
            <span>小说管理</span>
          </el-menu-item>
          <el-menu-item index="admins">
            <el-icon><User /></el-icon>
            <span>管理员</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="admin-header">
          <h2>AI小说平台 - 管理后台</h2>
          <div class="header-right">
            <span>{{ adminInfo?.username }}</span>
            <el-button type="danger" @click="handleLogout">退出</el-button>
          </div>
        </el-header>

        <el-main class="admin-content">
          <div v-if="activeMenu === 'dashboard'" class="dashboard">
            <h3>平台统计</h3>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card shadow="hover">
                  <el-statistic title="总小说数" :value="stats.novels?.total || 0" />
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <el-statistic title="草稿" :value="stats.novels?.draft || 0" />
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <el-statistic title="进行中" :value="stats.novels?.in_progress || 0" />
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <el-statistic title="已完成" :value="stats.novels?.completed || 0" />
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div v-if="activeMenu === 'novels'" class="novels-management">
            <h3>小说管理</h3>
            <el-table :data="novels" style="width: 100%" v-loading="loading">
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="author" label="作者" />
              <el-table-column prop="genre" label="类型" />
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button size="small" @click="viewNovel(row.id)">查看</el-button>
                  <el-button size="small" type="danger" @click="deleteNovel(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-if="activeMenu === 'admins'" class="admins-management">
            <h3>管理员管理</h3>
            <el-button type="primary" @click="showAddAdmin = true" style="margin-bottom: 20px;">
              添加管理员
            </el-button>
            <el-table :data="admins" style="width: 100%" v-loading="loading">
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="full_name" label="姓名" />
              <el-table-column prop="is_superuser" label="超级管理员">
                <template #default="{ row }">
                  <el-tag :type="row.is_superuser ? 'success' : 'info'">
                    {{ row.is_superuser ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '激活' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button size="small" @click="editAdmin(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteAdmin(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-main>
      </el-container>
    </el-container>

    <el-dialog v-model="showAddAdmin" title="添加管理员" width="500px">
      <el-form :model="newAdmin" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="newAdmin.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="newAdmin.email" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="newAdmin.full_name" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newAdmin.password" type="password" />
        </el-form-item>
        <el-form-item label="超级管理员">
          <el-switch v-model="newAdmin.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddAdmin = false">取消</el-button>
        <el-button type="primary" @click="addAdmin">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, Reading, User } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()
const activeMenu = ref('dashboard')
const loading = ref(false)
const stats = ref<any>({})
const novels = ref<any[]>([])
const admins = ref<any[]>([])
const adminInfo = ref<any>(null)
const showAddAdmin = ref(false)
const newAdmin = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  is_superuser: false
})

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  if (index === 'novels') {
    loadNovels()
  } else if (index === 'admins') {
    loadAdmins()
  } else if (index === 'dashboard') {
    loadStats()
  }
}

const loadStats = async () => {
  try {
    const response = await request.get('/api/admin/stats')
    stats.value = response.data
  } catch (error: any) {
    ElMessage.error('加载统计数据失败')
  }
}

const loadNovels = async () => {
  loading.value = true
  try {
    const response = await request.get('/api/admin/novels')
    novels.value = response.data
  } catch (error: any) {
    ElMessage.error('加载小说列表失败')
  } finally {
    loading.value = false
  }
}

const loadAdmins = async () => {
  loading.value = true
  try {
    const response = await request.get('/api/admin/admins')
    admins.value = response.data
  } catch (error: any) {
    ElMessage.error('加载管理员列表失败')
  } finally {
    loading.value = false
  }
}

const loadAdminInfo = async () => {
  try {
    const response = await request.get('/api/admin/me')
    adminInfo.value = response.data
  } catch (error: any) {
    ElMessage.error('加载管理员信息失败')
    router.push('/admin/login')
  }
}

const addAdmin = async () => {
  try {
    await request.post('/api/admin/register', newAdmin.value)
    ElMessage.success('添加管理员成功')
    showAddAdmin.value = false
    newAdmin.value = {
      username: '',
      email: '',
      full_name: '',
      password: '',
      is_superuser: false
    }
    loadAdmins()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '添加管理员失败')
  }
}

const editAdmin = (admin: any) => {
  ElMessage.info('编辑功能待实现')
}

const deleteAdmin = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该管理员吗？', '警告', {
      type: 'warning'
    })
    await request.delete(`/api/admin/admins/${id}`)
    ElMessage.success('删除成功')
    loadAdmins()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const viewNovel = (id: string) => {
  router.push(`/novels/${id}`)
}

const deleteNovel = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该小说吗？', '警告', {
      type: 'warning'
    })
    await request.delete(`/api/novels/${id}`)
    ElMessage.success('删除成功')
    loadNovels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  router.push('/admin/login')
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    'DRAFT': 'info',
    'IN_PROGRESS': 'warning',
    'COMPLETED': 'success',
    'PUBLISHED': 'success'
  }
  return types[status] || 'info'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadAdminInfo()
  loadStats()
})
</script>

<style scoped>
.admin-container {
  height: 100vh;
}

.admin-sidebar {
  background: #545c64;
}

.admin-menu {
  border-right: none;
}

.admin-header {
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #e6e6e6;
}

.header-right {
  display: flex;
  gap: 15px;
  align-items: center;
}

.admin-content {
  background: #f0f2f5;
  padding: 20px;
}

.dashboard {
  margin-top: 20px;
}

.el-row {
  margin-top: 20px;
}
</style>
