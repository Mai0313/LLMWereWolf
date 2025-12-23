import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Select,
  Button,
  Badge,
  Space,
  Tag,
  Tooltip,
  Collapse,
  Progress,
  Divider,
  Alert,
  Switch,
  InputNumber,
  Statistic
} from 'antd'
import {
  RobotOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  ApiOutlined
} from '@ant-design/icons'
import { apiService } from '@utils/api'
import { llmService, getServerDisplayName, getModelDisplayName } from '@services/llmService'

const { Panel } = Collapse

interface ModelInfo {
  id: string
  name: string
  available: boolean
  server: string
  serverAlias: string
  size?: string
  type?: 'chat' | 'embeddings'
}

interface ServerStatus {
  available: boolean
  latency: number
  models_count: number
}

const AIConfigurationPanel: React.FC = () => {
  // 定义服务器配置
  const LLM_SERVERS = {
    server1: 'http://100.80.20.5:4000/v1',
    server2: 'http://100.82.5.110:30001'
  }

  const [models, setModels] = useState<ModelInfo[]>([])
  const [serverStatus, setServerStatus] = useState<Record<string, ServerStatus>>({})
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [isTestingAll, setIsTestingAll] = useState(false)
  const [testResults, setTestResults] = useState<Record<string, boolean>>({})
  const [modelConfig, setModelConfig] = useState({
    temperature: 0.7,
    maxTokens: 2000,
    topP: 0.9,
    streamResponse: false
  })

  // 加载模型和服务器状态
  useEffect(() => {
    loadModelsAndStatus()
    // 设置默认模型
    const defaultModel = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_DEFAULT_MODEL) ||
                         (typeof process !== 'undefined' && process.env?.REACT_APP_DEFAULT_MODEL) ||
                         'meta-llama/Llama-3.3-70B-Instruct'
    setSelectedModel(defaultModel)
  }, [])

  const loadModelsAndStatus = async () => {
    try {
      // 加载模型列表
      const modelList = await apiService.getAvailableModels()
      setModels(modelList)

      // 加载服务器状态
      const status = await apiService.getServerStatus()
      setServerStatus(status)
    } catch (error) {
      console.error('加载模型和状态失败:', error)
    }
  }

  const testAllConnections = async () => {
    setIsTestingAll(true)
    const results: Record<string, boolean> = {}

    for (const model of models) {
      if (model.type === 'chat') { // 只测试聊天模型
        try {
          const isWorking = await apiService.testAIConnection(model.id)
          results[model.id] = isWorking
        } catch {
          results[model.id] = false
        }
      }
    }

    setTestResults(results)
    setIsTestingAll(false)
  }

  const testSingleModel = async (modelId: string) => {
    try {
      const isWorking = await apiService.testAIConnection(modelId)
      setTestResults({ ...testResults, [modelId]: isWorking })
    } catch {
      setTestResults({ ...testResults, [modelId]: false })
    }
  }

  const handleModelChange = async (modelId: string) => {
    setSelectedModel(modelId)
    // 加载该模型的推荐配置
    try {
      const config = await apiService.getModelRecommendedConfig(modelId)
      setModelConfig({
        temperature: config.temperature,
        maxTokens: config.max_tokens,
        topP: config.top_p,
        streamResponse: false
      })
    } catch {
      // 使用默认配置
    }
  }

  const getServerHealthColor = (serverKey: string) => {
    const status = serverStatus[serverKey]
    if (!status) return '#d9d9d9'
    if (!status.available) return '#ff4d4f'
    if (status.latency < 500) return '#52c41a'
    if (status.latency < 1000) return '#faad14'
    return '#ff7a45'
  }

  const getServerHealthText = (serverKey: string) => {
    const status = serverStatus[serverKey]
    if (!status) return '未知'
    if (!status.available) return '不可用'
    if (status.latency < 500) return '良好'
    if (status.latency < 1000) return '正常'
    return '较慢'
  }

  const selectedModelInfo = models.find(m => m.id === selectedModel)

  return (
    <div className="space-y-6">
      {/* 服务器状态概览 */}
      <Card title={<><ApiOutlined /> 服务器状态</>}>
        <Row gutter={[16, 16]}>
          {Object.entries(serverStatus).map(([serverKey, status]) => (
            <Col span={12} key={serverKey}>
              <Card size="small" className="h-full">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">
                    {serverKey === 'server1' ? '主服务器' : '备用服务器'}
                  </span>
                  <Badge
                    color={getServerHealthColor(serverKey)}
                    text={getServerHealthText(serverKey)}
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>模型数量:</span>
                    <span>{status.models_count}</span>
                  </div>
                  {status.available && status.latency > 0 && (
                    <div className="flex justify-between text-sm">
                      <span>延迟:</span>
                      <span>{status.latency}ms</span>
                    </div>
                  )}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 模型配置 */}
      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card
            title={
              <div className="flex items-center justify-between w-full">
                <span><RobotOutlined /> 模型配置</span>
                <div className="flex space-x-2">
                  <Button
                    type="default"
                    icon={<ReloadOutlined />}
                    onClick={loadModelsAndStatus}
                    size="small"
                  >
                    刷新
                  </Button>
                  <Button
                    type="primary"
                    icon={<ThunderboltOutlined />}
                    onClick={testAllConnections}
                    loading={isTestingAll}
                    size="small"
                  >
                    测试全部
                  </Button>
                </div>
              </div>
            }
          >
            {/* 模型选择器 */}
            <div className="mb-6">
              <div className="text-sm font-medium mb-2">选择模型:</div>
              <Select
                value={selectedModel}
                onChange={handleModelChange}
                style={{ width: '100%' }}
                placeholder="选择一个模型"
                optionLabelProp="label"
              >
                {models
                  .filter(m => m.type === 'chat') // 只显示聊天模型
                  .map(model => (
                    <Select.Option
                      key={model.id}
                      value={model.id}
                      label={`${model.name} (${model.size})`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <RobotOutlined />
                          <span>{model.name}</span>
                          <Tag size="small" color="blue">{model.size}</Tag>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Tag size="small">{model.serverAlias}</Tag>
                          {testResults[model.id] !== undefined && (
                            testResults[model.id] ?
                              <CheckCircleOutlined style={{ color: '#52c41a' }} /> :
                              <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
                          )}
                        </div>
                      </div>
                    </Select.Option>
                  ))
                }
              </Select>
            </div>

            {/* 模型详细信息 */}
            {selectedModelInfo && (
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">完整ID:</span>
                    <div className="font-mono text-gray-600">{selectedModelInfo.id}</div>
                  </div>
                  <div>
                    <span className="font-medium">服务器:</span>
                    <div>{selectedModelInfo.serverAlias}</div>
                  </div>
                  <div>
                    <span className="font-medium">类型:</span>
                    <div>{selectedModelInfo.type === 'chat' ? '聊天' : '嵌入'}</div>
                  </div>
                  <div>
                    <span className="font-medium">大小:</span>
                    <div>{selectedModelInfo.size}</div>
                  </div>
                </div>
              </div>
            )}

            {/* 模型参数配置 */}
            {selectedModel && (
              <Collapse>
                <Panel header={<><SettingOutlined /> 模型参数</>} key="model-params">
                  <Row gutter={[16, 16]}>
                    <Col span={8}>
                      <div className="space-y-2">
                        <span className="text-sm font-medium">Temperature</span>
                        <div className="flex items-center space-x-2">
                          <InputNumber
                            min={0}
                            max={2}
                            step={0.1}
                            value={modelConfig.temperature}
                            onChange={(value) => setModelConfig({ ...modelConfig, temperature: value || 0 })}
                          />
                          <span className="text-xs text-gray-500">控制创造性</span>
                        </div>
                      </div>
                    </Col>
                    <Col span={8}>
                      <div className="space-y-2">
                        <span className="text-sm font-medium">Max Tokens</span>
                        <div className="flex items-center space-x-2">
                          <InputNumber
                            min={1}
                            max={8000}
                            value={modelConfig.maxTokens}
                            onChange={(value) => setModelConfig({ ...modelConfig, maxTokens: value || 2000 })}
                          />
                          <span className="text-xs text-gray-500">最大长度</span>
                        </div>
                      </div>
                    </Col>
                    <Col span={8}>
                      <div className="space-y-2">
                        <span className="text-sm font-medium">Top P</span>
                        <div className="flex items-center space-x-2">
                          <InputNumber
                            min={0}
                            max={1}
                            step={0.05}
                            value={modelConfig.topP}
                            onChange={(value) => setModelConfig({ ...modelConfig, topP: value || 0 })}
                          />
                          <span className="text-xs text-gray-500">多样性</span>
                        </div>
                      </div>
                    </Col>
                  </Row>
                  <div className="mt-4">
                    <div className="flex items-center">
                      <Switch
                        checked={modelConfig.streamResponse}
                        onChange={(checked) => setModelConfig({ ...modelConfig, streamResponse: checked })}
                      />
                      <span className="ml-2 text-sm">流式响应（实时显示）</span>
                    </div>
                  </div>
                </Panel>
              </Collapse>
            )}
          </Card>
        </Col>

        <Col span={8}>
          {/* 测试结果 */}
          <Card title="测试结果" size="small">
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {models
                .filter(m => m.type === 'chat')
                .map(model => (
                  <div
                    key={model.id}
                    className={`p-2 rounded border cursor-pointer transition-colors ${
                      selectedModel === model.id ? 'border-blue-400 bg-blue-50' : 'border-gray-200'
                    }`}
                    onClick={() => handleModelChange(model.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium">{getModelDisplayName(model.id)}</span>
                        <Tag size="small" color="blue">{model.size}</Tag>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          size="small"
                          type={testResults[model.id] ? 'primary' : 'default'}
                          icon={testResults[model.id] ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                          onClick={(e) => {
                            e.stopPropagation()
                            testSingleModel(model.id)
                          }}
                        >
                          测试
                        </Button>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {model.serverAlias}
                    </div>
                  </div>
                ))}
            </div>
          </Card>

          {/* 使用提示 */}
          <Card title="使用提示" size="small" className="mt-4">
            <div className="text-sm space-y-2">
              <Alert
                message="推荐模型"
                description="Llama-3.3-70B 提供最佳的游戏推理能力"
                type="info"
                showIcon
                className="mb-2"
              />
              <div className="text-gray-600">
                <p>• 温度越低，输出越确定和保守</p>
                <p>• Max Tokens 控制响应长度</p>
                <p>• 流式响应提供更好的实时体验</p>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default AIConfigurationPanel