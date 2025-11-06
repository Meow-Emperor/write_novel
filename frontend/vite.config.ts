import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import path from 'path'
import VueDevTools from 'vite-plugin-vue-devtools'

// Use env var VITE_API_BASE_URL when available; fallback remains Docker-friendly
// For local dev (no Docker), set VITE_API_BASE_URL=http://localhost:8000 in frontend/.env
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // Default target for Docker Compose network; override in local .env
  const apiTarget = env.VITE_API_BASE_URL || 'http://backend:8000'

  return {
    plugins: [
      vue(),
      vueJsx(),
      VueDevTools(),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          rewrite: (p) => p
        }
      }
    },
    css: {
      postcss: {
        plugins: [
          require('tailwindcss'),
          require('autoprefixer'),
        ],
      },
    },
  }
})
