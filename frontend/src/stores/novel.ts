import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import request from '@/utils/request'
import type { Novel, NovelCreate, NovelUpdate } from '@/types/novel'

export const useNovelStore = defineStore('novel', () => {
  const novels = ref<Novel[]>([])
  const currentNovel = ref<Novel | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const novelCount = computed(() => novels.value.length)
  const draftNovels = computed(() => novels.value.filter((novel) => novel.status === 'DRAFT'))

  async function fetchNovels() {
    loading.value = true
    error.value = null
    try {
      const response = await request.get<Novel[]>('/api/novels')
      novels.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchNovel(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await request.get<Novel>(`/api/novels/${id}`)
      currentNovel.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createNovel(novelData: NovelCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await request.post<Novel>('/api/novels', novelData)
      novels.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateNovel(id: string, novelData: NovelUpdate) {
    loading.value = true
    error.value = null
    try {
      const response = await request.put<Novel>(`/api/novels/${id}`, novelData)
      const index = novels.value.findIndex((novel) => novel.id === id)
      if (index !== -1) {
        novels.value[index] = response.data
      }
      if (currentNovel.value?.id === id) {
        currentNovel.value = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteNovel(id: string) {
    loading.value = true
    error.value = null
    try {
      await request.delete(`/api/novels/${id}`)
      novels.value = novels.value.filter((novel) => novel.id !== id)
      if (currentNovel.value?.id === id) {
        currentNovel.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail ?? err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    novels,
    currentNovel,
    loading,
    error,
    novelCount,
    draftNovels,
    fetchNovels,
    fetchNovel,
    createNovel,
    updateNovel,
    deleteNovel
  }
})
