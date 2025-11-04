<template>
  <div v-if="hasError" class="error-boundary">
    <el-result
      icon="error"
      title="Something went wrong"
      :sub-title="errorMessage"
    >
      <template #extra>
        <el-button type="primary" @click="handleReset">
          Try Again
        </el-button>
        <el-button @click="goHome">
          Go Home
        </el-button>
      </template>
    </el-result>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const hasError = ref(false)
const errorMessage = ref('')

onErrorCaptured((err: any) => {
  hasError.value = true
  errorMessage.value = err.message || 'An unexpected error occurred'
  console.error('Error captured:', err)
  return false
})

const handleReset = () => {
  hasError.value = false
  errorMessage.value = ''
}

const goHome = () => {
  handleReset()
  router.push('/')
}
</script>

<style scoped>
.error-boundary {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 20px;
}
</style>
