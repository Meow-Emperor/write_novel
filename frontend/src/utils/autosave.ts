export class AutoSaveManager {
  private timer: number | null = null
  private interval: number = 30000 // 30 seconds
  private callback: (() => Promise<void>) | null = null

  start(saveCallback: () => Promise<void>) {
    this.callback = saveCallback
    this.stop() // Clear any existing timer

    this.timer = window.setInterval(async () => {
      if (this.callback) {
        try {
          await this.callback()
          console.log('[AutoSave] Saved at', new Date().toLocaleTimeString())
        } catch (error) {
          console.error('[AutoSave] Failed:', error)
        }
      }
    }, this.interval)
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
  }

  async saveNow() {
    if (this.callback) {
      try {
        await this.callback()
        console.log('[AutoSave] Manual save at', new Date().toLocaleTimeString())
      } catch (error) {
        console.error('[AutoSave] Manual save failed:', error)
      }
    }
  }

  setInterval(ms: number) {
    this.interval = ms
    if (this.timer && this.callback) {
      this.start(this.callback)
    }
  }
}

export const autoSaveManager = new AutoSaveManager()
