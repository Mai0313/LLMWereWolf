import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { GameState, GameConfiguration, ApiResponse, WebSocketMessage } from '../types/game'

// API 基础配置
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('❌ API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error('❌ API Response Error:', error)
        const message = error.response?.data?.message || error.message || 'API请求失败'
        return Promise.reject(new Error(message))
      }
    )
  }

  // 游戏相关API
  async startGame(configuration: GameConfiguration): Promise<GameState> {
    try {
      const response = await this.client.post<ApiResponse<GameState>>('/games/start', {
        configuration
      })

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '启动游戏失败')
      }
    } catch (error) {
      throw new Error(`启动游戏失败: ${error}`)
    }
  }

  async pauseGame(gameId: string): Promise<void> {
    try {
      await this.client.post(`/games/${gameId}/pause`)
    } catch (error) {
      throw new Error(`暂停游戏失败: ${error}`)
    }
  }

  async resumeGame(gameId: string): Promise<void> {
    try {
      await this.client.post(`/games/${gameId}/resume`)
    } catch (error) {
      throw new Error(`恢复游戏失败: ${error}`)
    }
  }

  async stopGame(gameId: string): Promise<void> {
    try {
      await this.client.post(`/games/${gameId}/stop`)
    } catch (error) {
      throw new Error(`停止游戏失败: ${error}`)
    }
  }

  async getGameState(gameId: string): Promise<GameState> {
    try {
      const response = await this.client.get<ApiResponse<GameState>>(`/games/${gameId}`)

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '获取游戏状态失败')
      }
    } catch (error) {
      throw new Error(`获取游戏状态失败: ${error}`)
    }
  }

  async getGameList(): Promise<Array<{ id: string; name: string; status: string }>> {
    try {
      const response = await this.client.get<ApiResponse>('/games')
      return response.data.data || []
    } catch (error) {
      throw new Error(`获取游戏列表失败: ${error}`)
    }
  }

  // 配置相关API
  async saveConfiguration(configuration: GameConfiguration): Promise<GameConfiguration> {
    try {
      const response = await this.client.post<ApiResponse<GameConfiguration>>('/configurations', {
        configuration
      })

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || '保存配置失败')
      }
    } catch (error) {
      throw new Error(`保存配置失败: ${error}`)
    }
  }

  async getConfigurations(): Promise<GameConfiguration[]> {
    try {
      const response = await this.client.get<ApiResponse<GameConfiguration[]>>('/configurations')
      return response.data.data || []
    } catch (error) {
      throw new Error(`获取配置列表失败: ${error}`)
    }
  }

  async deleteConfiguration(configId: string): Promise<void> {
    try {
      await this.client.delete(`/configurations/${configId}`)
    } catch (error) {
      throw new Error(`删除配置失败: ${error}`)
    }
  }

  // 统计相关API
  async getGameStatistics(gameId: string): Promise<any> {
    try {
      const response = await this.client.get<ApiResponse>(`/games/${gameId}/statistics`)
      return response.data.data
    } catch (error) {
      throw new Error(`获取游戏统计失败: ${error}`)
    }
  }

  async getPlayerStatistics(playerId: string): Promise<any> {
    try {
      const response = await this.client.get<ApiResponse>(`/players/${playerId}/statistics`)
      return response.data.data
    } catch (error) {
      throw new Error(`获取玩家统计失败: ${error}`)
    }
  }

  // AI 相关API (集成公司LLM服务)
  async testAIConnection(model: string): Promise<boolean> {
    try {
      const { llmService } = await import('@services/llmService')
      return await llmService.testModelConnection(model)
    } catch (error) {
      console.error('测试模型连接失败:', error)
      return false
    }
  }

  async getAvailableModels(): Promise<Array<{
    id: string
    name: string
    available: boolean
    server: string
    serverAlias: string
    size?: string
    type?: 'chat' | 'embeddings'
  }>> {
    try {
      const { llmService } = await import('@services/llmService')
      return await llmService.getAvailableModels()
    } catch (error) {
      console.error('获取模型列表失败:', error)
      // 返回备用模型列表
      return []
    }
  }

  async getServerStatus(): Promise<Record<string, { available: boolean; latency: number; models_count: number }>> {
    try {
      const { llmService } = await import('@services/llmService')
      return await llmService.getServerStatus()
    } catch (error) {
      console.error('获取服务器状态失败:', error)
      return {}
    }
  }

  async getModelRecommendedConfig(modelId: string): Promise<any> {
    try {
      const { llmService } = await import('@services/llmService')
      return llmService.getModelRecommendedConfig(modelId)
    } catch (error) {
      console.error('获取模型配置失败:', error)
      return { temperature: 0.7, max_tokens: 2000, top_p: 0.9 }
    }
  }
}

// WebSocket 连接类
class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000
  private messageHandlers: Record<string, (data: any) => void> = {}

  connect(url: string, gameId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${url}?gameId=${gameId}`)

        this.ws.onopen = () => {
          console.log('🔌 WebSocket 连接已建立')
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('WebSocket 消息解析失败:', error)
          }
        }

        this.ws.onclose = () => {
          console.log('🔌 WebSocket 连接已关闭')
          this.attemptReconnect(url, gameId)
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket 连接错误:', error)
          reject(error)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private handleMessage(message: WebSocketMessage): void {
    const handler = this.messageHandlers[message.type]
    if (handler) {
      handler(message.data)
    } else {
      console.log('未处理的 WebSocket 消息类型:', message.type, message.data)
    }
  }

  private attemptReconnect(url: string, gameId: string): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`🔄 尝试重新连接 WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

      setTimeout(() => {
        this.connect(url, gameId).catch(() => {
          // 重连失败，继续尝试
        })
      }, this.reconnectInterval)
    } else {
      console.error('WebSocket 重连次数已达上限')
    }
  }

  onMessage(type: string, handler: (data: any) => void): void {
    this.messageHandlers[type] = handler
  }

  offMessage(type: string): void {
    delete this.messageHandlers[type]
  }

  send(message: object): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket 未连接，无法发送消息')
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// 创建服务实例
export const apiService = new ApiService()
export const wsService = new WebSocketService()

// 在开发环境中暴露到 window 对象，方便调试
if (process.env.NODE_ENV === 'development') {
  (window as any).apiService = apiService
  (window as any).wsService = wsService
}