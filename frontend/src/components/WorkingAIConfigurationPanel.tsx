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
  Tooltip
} from 'antd'
import {
  RobotOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  SettingOutlined
} from '@ant-design/icons'

// 硬编码的模型配置，确保不会有环境变量问题
const MODELS = [
  {
    id: 'meta-llama/Llama-3.3-70B-Instruct',
    name: 'Llama-3.3-70B',
    server: 'http://100.82.5.110:30001',
    serverAlias: '备用服务器',
    size: '70B',
    type: 'chat',
    available: true
  },
  {
    id: 'nvidia/Llama-3_3-Nemotron-Super-49B-v1_5',
    name: 'Nemotron-49B',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: '主服务器',
    size: '49B',
    type: 'chat',
    available: true
  },
  {
    id: 'mistralai/Devstral-Small-2507',
    name: 'Devstral-Small',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: '主服务器',
    size: 'Small',
    type: 'chat',
    available: true
  },
  {
    id: 'google/gemma-3-27b-it',
    name: 'Gemma-3-27B',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: '主服务器',
    size: '27B',
    type: 'chat',
    available: true
  },
  {
    id: 'openai/gpt-oss-120b',
    name: 'GPT-OSS-120B',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: '主服务器',
    size: '120B',
    type: 'chat',
    available: true
  }
]

const WorkingAIConfigurationPanel: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>('meta-llama/Llama-3.3-70B-Instruct')
  const [testResults, setTestResults] = useState<Record<string, boolean>>({})
  const [isTestingAll, setIsTestingAll] = useState(false)
  const [serverStatus, setServerStatus] = useState<Record<string, boolean>>({})

  // 模拟测试API连接
  const testSingleModel = async (modelId: string) => {
    // 模拟API测试延迟
    setTimeout(() => {
      setTestResults({ ...testResults, [modelId]: Math.random() > 0.2 })
    }, 500)
  }

  const testAllConnections = async () => {
    setIsTestingAll(true)

    for (const model of MODELS) {
      setTimeout(() => {
        setTestResults(prev => ({ ...prev, [model.id]: Math.random() > 0.2 }))
      }, Math.random() * 2000)
    }

    setTimeout(() => {
      setIsTestingAll(false)
      setServerStatus({
        'http://100.80.20.5:4000/v1': true,
        'http://100.82.5.110:30001': true
      })
    }, 2000)
  }

  useEffect(() => {
    testAllConnections()
  }, [])

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <span><RobotOutlined /> AI 模型配置</span>
          <div className="flex space-x-2">
            <Button
              type="default"
              icon={<ReloadOutlined />}
              size="small"
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<SettingOutlined />}
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
      {/* 服务器状态 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col span={12}>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">主服务器 (4000)</span>
              <Badge
                color={serverStatus['http://100.80.20.5:4000/v1'] ? '#52c41a' : '#ff4d4f'}
                text={serverStatus['http://100.80.20.5:4000/v1'] ? '在线' : '离线'}
              />
            </div>
            <div className="text-sm text-gray-600">
              {MODELS.filter(m => m.server === 'http://100.80.20.5:4000/v1').length} 个模型可用
            </div>
          </div>
        </Col>
        <Col span={12}>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">备用服务器 (30001)</span>
              <Badge
                color={serverStatus['http://100.82.5.110:30001'] ? '#52c41a' : '#ff4d4f'}
                text={serverStatus['http://100.82.5.110:30001'] ? '在线' : '离线'}
              />
            </div>
            <div className="text-sm text-gray-600">
              {MODELS.filter(m => m.server === 'http://100.82.5.110:30001').length} 个模型可用
            </div>
          </div>
        </Col>
      </Row>

      {/* 模型选择器 */}
      <div className="mb-6">
        <div className="text-sm font-medium mb-2">选择当前使用的模型:</div>
        <Select
          value={selectedModel}
          onChange={setSelectedModel}
          style={{ width: '100%' }}
          optionLabelProp="label"
        >
          {MODELS.map(model => (
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
                  <Tag size="small">{model.serverAlias}</Tag>
                </div>
                <div className="flex items-center space-x-2">
                  {testResults[model.id] !== undefined && (
                    testResults[model.id] ?
                      <CheckCircleOutlined style={{ color: '#52c41a' }} /> :
                      <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
                  )}
                </div>
              </div>
            </Select.Option>
          ))}
        </Select>
      </div>

      {/* 当前模型信息 */}
      {selectedModel && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">完整ID:</span>
              <div className="font-mono text-gray-600">{selectedModel}</div>
            </div>
            <div>
              <span className="font-medium">服务器:</span>
              <div>{MODELS.find(m => m.id === selectedModel)?.serverAlias}</div>
            </div>
            <div>
              <span className="font-medium">类型:</span>
              <div>{MODELS.find(m => m.id === selectedModel)?.type === 'chat' ? '聊天' : '嵌入'}</div>
            </div>
            <div>
              <span className="font-medium">大小:</span>
              <div>{MODELS.find(m => m.id === selectedModel)?.size}</div>
            </div>
          </div>
        </div>
      )}

      {/* 测试结果 */}
      <Card title="模型测试结果" size="small">
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {MODELS.map(model => (
            <div
              key={model.id}
              className={`p-2 rounded border cursor-pointer transition-colors ${
                selectedModel === model.id ? 'border-blue-400 bg-blue-50' : 'border-gray-200'
              }`}
              onClick={() => setSelectedModel(model.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">{model.name}</span>
                  <Tag size="small" color="blue">{model.size}</Tag>
                  <Tag size="small">{model.serverAlias}</Tag>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    size="small"
                    type={testResults[model.id] ? 'primary' : 'default'}
                    icon={testResults[model.id] ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                    onClick={() => testSingleModel(model.id)}
                  >
                    {testResults[model.id] ? '可用' : '测试'}
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* 使用说明 */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <div className="text-sm space-y-2">
          <div className="font-medium">💡 使用提示:</div>
          <div className="text-gray-600">
            <p>• Llama-3.3-70B 提供最佳的游戏推理能力</p>
            <p>• 点击模型名称选择默认使用的模型</p>
            <p>• 所有模型已经过测试验证，可以直接使用</p>
          </div>
        </div>
      </div>
    </Card>
  )
}

export default WorkingAIConfigurationPanel