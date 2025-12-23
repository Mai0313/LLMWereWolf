import axios, { AxiosInstance } from 'axios'

// 类型定义
type AvailableModels = Record<string, string[]>

// 公司 API 服务器配置
const LLM_SERVERS = {
  server1: (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_LLM_SERVER_1) ||
             (typeof process !== 'undefined' && process.env?.REACT_APP_LLM_SERVER_1) ||
             'http://100.80.20.5:4000/v1',
  server2: (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_LLM_SERVER_2) ||
             (typeof process !== 'undefined' && process.env?.REACT_APP_LLM_SERVER_2) ||
             'http://100.82.5.110:30001'
}

// 可用模型列表
export const AVAILABLE_MODELS: AvailableModels = {
  'http://100.80.20.5:4000/v1': [
    'nvidia/Llama-3_3-Nemotron-Super-49B-v1_5',
    'mistralai/Devstral-Small-2507',
    'jinaai/jina-embeddings-v4',
    'google/gemma-3-27b-it',
    'openai/gpt-oss-120b'
  ],
  'http://100.82.5.110:30001': [
    'meta-llama/Llama-3.3-70B-Instruct'
  ]
}

// 默认模型
export const DEFAULT_MODEL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_DEFAULT_MODEL) ||
                           (typeof process !== 'undefined' && process.env?.REACT_APP_DEFAULT_MODEL) ||
                           'meta-llama/Llama-3.3-70B-Instruct'

// 模型别名映射（更友好的显示名称）
const MODEL_ALIASES: Record<string, string> = {
  'meta-llama/Llama-3.3-70B-Instruct': 'Llama-3.3-70B',
  'nvidia/Llama-3_3-Nemotron-Super-49B-v1_5': 'Nemotron-49B',
  'mistralai/Devstral-Small-2507': 'Devstral-Small',
  'jinaai/jina-embeddings-v4': 'Jina-Embeddings',
  'google/gemma-3-27b-it': 'Gemma-3-27B',
  'openai/gpt-oss-120b': 'GPT-OSS-120B'
}

// 服务器别名映射
const SERVER_ALIASES: Record<string, string> = {
  'http://100.80.20.5:4000/v1': '主服务器',
  'http://100.82.5.110:30001': '备用服务器'
}

// 创建 API 客户端
function createAPIClient(baseURL: string): AxiosInstance {
  return axios.create({
    baseURL,
    timeout: 30000, // 30秒超时
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'LLM-Werewolf-UI/1.0'
    }
  })
}

class LLMService {
  private clients: Record<string, AxiosInstance> = {}

  constructor() {
    // 初始化所有服务器的客户端
    Object.entries(LLM_SERVERS).forEach(([key, url]) => {
      this.clients[key] = createAPIClient(url)
    })
  }

  // 获取服务器上可用的模型
  async getAvailableModels(serverKey?: string): Promise<Array<{
    id: string
    name: string
    server: string
    serverAlias: string
    available: boolean
    size?: string
    type?: 'chat' | 'embeddings'
  }>> {
    const models: Array<{
      id: string
      name: string
      server: string
      serverAlias: string
      available: boolean
      size?: string
      type?: 'chat' | 'embeddings'
    }> = []

    const serversToCheck = serverKey ? [serverKey] : Object.keys(LLM_SERVERS)

    for (const serverKey of serversToCheck) {
      const serverUrl = LLM_SERVERS[serverKey as keyof typeof LLM_SERVERS]
      const modelList = AVAILABLE_MODELS[serverUrl]

      for (const modelId of modelList) {
        models.push({
          id: modelId,
          name: MODEL_ALIASES[modelId] || modelId,
          server: serverUrl,
          serverAlias: SERVER_ALIASES[serverUrl] || serverUrl,
          available: true, // 假设都可用，实际可以调用健康检查
          size: this.getModelSize(modelId),
          type: this.getModelType(modelId)
        })
      }
    }

    return models.sort((a, b) => {
      // 优先显示默认模型
      if (a.id === DEFAULT_MODEL) return -1
      if (b.id === DEFAULT_MODEL) return 1
      // 按服务器别名排序
      if (a.serverAlias !== b.serverAlias) {
        return a.serverAlias.localeCompare(b.serverAlias)
      }
      return a.name.localeCompare(b.name)
    })
  }

  // 获取模型大小信息
  private getModelSize(modelId: string): string {
    if (modelId.includes('70B')) return '70B'
    if (modelId.includes('49B')) return '49B'
    if (modelId.includes('27B')) return '27B'
    if (modelId.includes('120B')) return '120B'
    if (modelId.includes('Small')) return 'Small'
    return 'Unknown'
  }

  // 获取模型类型
  private getModelType(modelId: string): 'chat' | 'embeddings' {
    if (modelId.includes('embeddings')) return 'embeddings'
    return 'chat'
  }

  // 发送对话请求
  async chatCompletion(
    model: string,
    messages: Array<{ role: string; content: string }>,
    options: {
      temperature?: number
      max_tokens?: number
      stream?: boolean
      top_p?: number
      frequency_penalty?: number
      presence_penalty?: number
    } = {}
  ): Promise<any> {
    // 找到模型所在的服务器
    let serverUrl: string | undefined
    let serverKey: string | undefined

    for (const [key, url] of Object.entries(LLM_SERVERS)) {
      if (AVAILABLE_MODELS[url].includes(model)) {
        serverUrl = url
        serverKey = key
        break
      }
    }

    if (!serverUrl || !serverKey) {
      throw new Error(`未找到模型 ${model} 的服务器`)
    }

    const payload = {
      model,
      messages,
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 2000,
      top_p: options.top_p || 1,
      frequency_penalty: options.frequency_penalty || 0,
      presence_penalty: options.presence_penalty || 0,
      stream: options.stream || false
    }

    try {
      const response = await this.clients[serverKey].post('/chat/completions', payload)
      return response.data
    } catch (error) {
      throw new Error(`调用模型 ${model} 失败: ${error}`)
    }
  }

  // 获取嵌入向量
  async getEmbeddings(
    model: string,
    input: string | string[],
    options: {
      encoding_format?: string
      dimensions?: number
      user?: string
    } = {}
  ): Promise<any> {
    let serverUrl: string | undefined
    let serverKey: string | undefined

    for (const [key, url] of Object.entries(LLM_SERVERS)) {
      if (AVAILABLE_MODELS[url].includes(model)) {
        serverUrl = url
        serverKey = key
        break
      }
    }

    if (!serverUrl || !serverKey) {
      throw new Error(`未找到模型 ${model} 的服务器`)
    }

    const payload = {
      model,
      input,
      encoding_format: options.encoding_format || 'float',
      dimensions: options.dimensions,
      user: options.user
    }

    try {
      const response = await this.clients[serverKey].post('/embeddings', payload)
      return response.data
    } catch (error) {
      throw new Error(`调用嵌入模型 ${model} 失败: ${error}`)
    }
  }

  // 测试模型连接
  async testModelConnection(model: string): Promise<boolean> {
    try {
      await this.chatCompletion(model, [
        { role: 'user', content: '测试连接' }
      ], { max_tokens: 10 })
      return true
    } catch {
      return false
    }
  }

  // 获取服务器状态
  async getServerStatus(): Promise<Record<string, { available: boolean; latency: number; models_count: number }>> {
    const status: Record<string, { available: boolean; latency: number; models_count: number }> = {}

    for (const [serverKey, serverUrl] of Object.entries(LLM_SERVERS)) {
      try {
        const startTime = Date.now()
        await this.clients[serverKey].get('/models', { timeout: 5000 })
        const latency = Date.now() - startTime

        status[serverKey] = {
          available: true,
          latency,
          models_count: AVAILABLE_MODELS[serverUrl].length
        }
      } catch {
        status[serverKey] = {
          available: false,
          latency: -1,
          models_count: 0
        }
      }
    }

    return status
  }

  // 获取模型的推荐配置
  getModelRecommendedConfig(model: string) {
    if (model.includes('70B')) {
      return {
        temperature: 0.7,
        max_tokens: 1500,
        top_p: 0.9
      }
    }
    if (model.includes('49B')) {
      return {
        temperature: 0.8,
        max_tokens: 2000,
        top_p: 0.95
      }
    }
    if (model.includes('Small')) {
      return {
        temperature: 0.6,
        max_tokens: 1000,
        top_p: 0.8
      }
    }
    if (model.includes('27B')) {
      return {
        temperature: 0.7,
        max_tokens: 1200,
        top_p: 0.85
      }
    }
    if (model.includes('120B')) {
      return {
        temperature: 0.6,
        max_tokens: 2500,
        top_p: 0.9
      }
    }

    // 默认配置
    return {
      temperature: 0.7,
      max_tokens: 2000,
      top_p: 0.9
    }
  }
}

// 创建服务实例
export const llmService = new LLMService()

// 导出常用工具函数
export const getModelDisplayName = (modelId: string): string => {
  return MODEL_ALIASES[modelId] || modelId
}

export const getServerDisplayName = (serverUrl: string): string => {
  return SERVER_ALIASES[serverUrl] || serverUrl
}

export const isEmbeddingModel = (modelId: string): boolean => {
  return MODEL_ALIASES[modelId]?.includes('Embeddings') || modelId.includes('embeddings')
}

// 在开发环境中暴露到 window 对象
if (process.env.NODE_ENV === 'development') {
  (window as any).llmService = llmService
}