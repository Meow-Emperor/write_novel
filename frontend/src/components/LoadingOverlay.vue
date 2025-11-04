<template>
  <el-overlay v-model="visible" class="loading-overlay">
    <div class="loading-content">
      <el-icon class="loading-icon" :size="50">
        <Loading />
      </el-icon>
      <p v-if="text" class="loading-text">{{ text }}</p>
    </div>
  </el-overlay>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

interface Props {
  visible: boolean
  text?: string
}

withDefaults(defineProps<Props>(), {
  visible: false,
  text: 'Loading...'
})
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  color: var(--el-color-primary);
  animation: rotate 1.5s linear infinite;
}

.loading-text {
  color: var(--el-text-color-primary);
  font-size: 16px;
  margin: 0;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
