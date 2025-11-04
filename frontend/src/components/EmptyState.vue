<template>
  <div class="empty-state">
    <el-empty
      :description="description"
      :image="image"
      :image-size="imageSize"
    >
      <template v-if="$slots.default">
        <slot />
      </template>
      <el-button v-else-if="actionText" type="primary" @click="handleAction">
        {{ actionText }}
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
interface Props {
  description?: string
  image?: string
  imageSize?: number
  actionText?: string
}

interface Emits {
  (e: 'action'): void
}

withDefaults(defineProps<Props>(), {
  description: 'No data available',
  imageSize: 200
})

const emit = defineEmits<Emits>()

const handleAction = () => {
  emit('action')
}
</script>

<style scoped>
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  padding: 40px 20px;
}
</style>
