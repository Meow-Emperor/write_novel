<template>
  <Layout>
    <ErrorBoundary>
      <router-view />
    </ErrorBoundary>
  </Layout>
</template>

<script setup lang="ts">
import Layout from './components/Layout.vue'
import ErrorBoundary from './components/ErrorBoundary.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Noto Sans SC', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  background-color: #f8fafc;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Naive UI 主题覆盖 */
:root {
  --primary-color: #3b82f6;
  --primary-color-hover: #2563eb;
  --primary-color-pressed: #1d4ed8;
}
</style>
