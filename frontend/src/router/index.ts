import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/novels',
    name: 'NovelList',
    component: () => import('@/views/NovelList.vue')
  },
  {
    path: '/novels/:id',
    name: 'NovelDetail',
    component: () => import('@/views/NovelDetail.vue')
  },
  {
    path: '/novels/:id/characters',
    name: 'CharacterManagement',
    component: () => import('@/views/CharacterManagement.vue')
  },
  {
    path: '/novels/:id/plot',
    name: 'PlotStructure',
    component: () => import('@/views/PlotStructure.vue')
  },
  {
    path: '/novels/:id/world',
    name: 'WorldSettings',
    component: () => import('@/views/WorldSettings.vue')
  },
  {
    path: '/novels/:id/chapters',
    name: 'ChapterBlueprint',
    component: () => import('@/views/ChapterBlueprint.vue')
  },
  {
    path: '/novels/:id/editor/:chapterId?',
    name: 'ContentEditor',
    component: () => import('@/views/ContentEditor.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
