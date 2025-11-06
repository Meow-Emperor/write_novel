import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import naive from 'naive-ui'
import '@fontsource/noto-sans-sc/400.css'
import '@fontsource/noto-sans-sc/700.css'
import './style.css'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(naive)

app.mount('#app')
