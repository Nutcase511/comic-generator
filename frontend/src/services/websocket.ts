/**
 * WebSocket服务 - 用于接收实时进度更新
 */

type ProgressCallback = (data: ProgressData) => void

export interface ProgressData {
  type: 'generation_start' | 'panel_start' | 'panel_complete' | 'panel_error' | 'generation_complete' | 'generation_error'
  panel_number?: number
  total?: number
  image_url?: string
  error?: string
  message?: string
  image_urls?: string[]
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectTimer: NodeJS.Timeout | null = null
  private callbacks: Set<ProgressCallback> = new Set()
  private isManualClose = false

  connect() {
    // 构建WebSocket URL - 使用与后端相同的端口
    // 如果前端运行在5173/5175，后端在8002
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//127.0.0.1:8002/ws`

    console.log('连接WebSocket:', wsUrl)

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket连接成功')
        // 发送心跳
        this.startHeartbeat()
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // 处理心跳响应
          if (data.type === 'pong') {
            return
          }

          // 触发所有回调
          this.callbacks.forEach(callback => callback(data))
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket连接关闭:', event.code, event.reason)

        if (!this.isManualClose) {
          // 自动重连
          console.log('5秒后尝试重连...')
          this.reconnectTimer = setTimeout(() => {
            this.connect()
          }, 5000)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        // WebSocket错误是正常的，会在onclose中处理重连
      }
    } catch (error) {
      console.error('创建WebSocket连接失败:', error)
    }
  }

  disconnect() {
    this.isManualClose = true

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.callbacks.clear()
  }

  onProgress(callback: ProgressCallback) {
    this.callbacks.add(callback)
  }

  offProgress(callback: ProgressCallback) {
    this.callbacks.delete(callback)
  }

  private startHeartbeat() {
    // 每30秒发送一次心跳
    setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send('ping')
      }
    }, 30000)
  }
}

// 导出单例
export const wsService = new WebSocketService()
