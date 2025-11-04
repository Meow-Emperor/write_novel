import { ref } from 'vue'

export function useLoading(initialState = false) {
  const loading = ref(initialState)
  const error = ref<string | null>(null)

  const startLoading = () => {
    loading.value = true
    error.value = null
  }

  const stopLoading = () => {
    loading.value = false
  }

  const setError = (err: string) => {
    error.value = err
    loading.value = false
  }

  const withLoading = async <T>(fn: () => Promise<T>): Promise<T | null> => {
    startLoading()
    try {
      const result = await fn()
      stopLoading()
      return result
    } catch (err: any) {
      setError(err?.message || 'An error occurred')
      throw err
    }
  }

  return {
    loading,
    error,
    startLoading,
    stopLoading,
    setError,
    withLoading
  }
}
