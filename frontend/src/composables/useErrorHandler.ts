import { ElMessage, ElNotification } from 'element-plus'

export interface ErrorOptions {
  showNotification?: boolean
  showMessage?: boolean
  logToConsole?: boolean
}

export function useErrorHandler() {
  const handleError = (error: any, options: ErrorOptions = {}) => {
    const {
      showNotification = false,
      showMessage = true,
      logToConsole = true
    } = options

    const message = error?.response?.data?.detail || error?.message || 'Unknown error occurred'

    if (logToConsole) {
      console.error('Error:', error)
    }

    if (showNotification) {
      ElNotification({
        title: 'Error',
        message,
        type: 'error',
        duration: 5000
      })
    } else if (showMessage) {
      ElMessage({
        message,
        type: 'error',
        duration: 3000
      })
    }

    return message
  }

  const handleSuccess = (message: string, showNotification = false) => {
    if (showNotification) {
      ElNotification({
        title: 'Success',
        message,
        type: 'success',
        duration: 3000
      })
    } else {
      ElMessage({
        message,
        type: 'success',
        duration: 2000
      })
    }
  }

  const handleWarning = (message: string) => {
    ElMessage({
      message,
      type: 'warning',
      duration: 3000
    })
  }

  return {
    handleError,
    handleSuccess,
    handleWarning
  }
}
