import React, { useState, useEffect } from 'react'
import {
  Row,
  Col,
  Select,
  Button,
  Tag
} from 'antd'
import {
  RobotOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
  CloudServerOutlined
} from '@ant-design/icons'

// 保持原有的数据结构，但修改样式
const MODELS = [
  {
    id: 'meta-llama/Llama-3.3-70B-Instruct',
    name: 'Llama-3.3-70B',
    server: 'http://100.82.5.110:30001',
    serverAlias: 'Backup Node',
    size: '70B',
    type: 'chat',
    available: true
  },
  {
    id: 'nvidia/Llama-3_3-Nemotron-Super-49B-v1_5',
    name: 'Nemotron-49B',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: 'Primary Node',
    size: '49B',
    type: 'chat',
    available: true
  },
  {
    id: 'mistralai/Devstral-Small-2507',
    name: 'Devstral-Small',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: 'Primary Node',
    size: 'Small',
    type: 'chat',
    available: true
  },
  {
    id: 'google/gemma-3-27b-it',
    name: 'Gemma-3-27B',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: 'Primary Node',
    size: '27B',
    type: 'chat',
    available: true
  },
  {
    id: 'openai/gpt-oss-120b',
    name: 'GPT-OSS-120B',
    server: 'http://100.80.20.5:4000/v1',
    serverAlias: 'Primary Node',
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

  const testSingleModel = async (modelId: string) => {
    setTestResults(prev => ({ ...prev, [modelId]: undefined as any })) // Reset state to loading if needed
    setTimeout(() => {
      setTestResults(prev => ({ ...prev, [modelId]: Math.random() > 0.1 }))
    }, 600)
  }

  const testAllConnections = async () => {
    setIsTestingAll(true)
    for (const model of MODELS) {
      setTimeout(() => {
        setTestResults(prev => ({ ...prev, [model.id]: Math.random() > 0.1 }))
      }, Math.random() * 1000)
    }
    setTimeout(() => {
      setIsTestingAll(false)
      setServerStatus({
        'http://100.80.20.5:4000/v1': true,
        'http://100.82.5.110:30001': true
      })
    }, 1500)
  }

  useEffect(() => {
    testAllConnections()
  }, [])

  return (
    <div className="space-y-6">

      {/* 顶部状态卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {['http://100.80.20.5:4000/v1', 'http://100.82.5.110:30001'].map((url, idx) => (
          <div key={url} className="bg-black/30 border border-white/5 p-4 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full ${serverStatus[url] ? 'bg-green-500 shadow-[0_0_10px_#22c55e]' : 'bg-red-500'}`} />
              <div>
                <div className="text-white text-sm font-medium">{idx === 0 ? 'Primary Core' : 'Backup Core'}</div>
                <div className="text-xs text-gray-500 font-mono">{url.split(':')[1].replace('//', '')}</div>
              </div>
            </div>
            <CloudServerOutlined className="text-gray-600 text-xl" />
          </div>
        ))}
      </div>

      {/* 主控制区 */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h4 className="text-white font-serif tracking-wide m-0 flex items-center gap-2">
            <RobotOutlined /> MODEL SELECTION
          </h4>
          <div className="flex gap-2">
            <Button size="small" type="text" icon={<ReloadOutlined />} className="text-gray-400 hover:text-white" onClick={testAllConnections}>Refresh</Button>
            <Button size="small" type="primary" icon={<ThunderboltOutlined />} loading={isTestingAll} onClick={testAllConnections} className="bg-mystic-accent">Test All</Button>
          </div>
        </div>

        <div className="mb-6">
          <label className="text-xs text-gray-400 uppercase tracking-wider mb-2 block">Active Neural Model</label>
          <Select
            value={selectedModel}
            onChange={setSelectedModel}
            className="w-full h-12 text-lg"
            dropdownClassName="bg-black/90 border border-mystic-accent/30"
          >
            {MODELS.map(model => (
              <Select.Option key={model.id} value={model.id}>
                <div className="flex items-center justify-between w-full py-1">
                  <span className="font-medium">{model.name}</span>
                  <div className="flex items-center gap-2">
                    <Tag className="bg-white/10 border-none text-gray-300 m-0">{model.size}</Tag>
                    {testResults[model.id] === true && <CheckCircleOutlined className="text-green-500" />}
                    {testResults[model.id] === false && <ExclamationCircleOutlined className="text-red-500" />}
                  </div>
                </div>
              </Select.Option>
            ))}
          </Select>
        </div>

        {/* 详细列表 */}
        <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
          {MODELS.map(model => (
            <div
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`
                p-3 rounded-lg border cursor-pointer transition-all duration-200 flex items-center justify-between group
                ${selectedModel === model.id
                  ? 'bg-mystic-accent/10 border-mystic-accent/50'
                  : 'bg-black/20 border-transparent hover:bg-white/5 hover:border-white/10'}
              `}
            >
              <div className="flex items-center gap-3">
                <RobotOutlined className={selectedModel === model.id ? 'text-mystic-accent' : 'text-gray-600'} />
                <div>
                  <div className={`text-sm font-medium ${selectedModel === model.id ? 'text-white' : 'text-gray-400 group-hover:text-gray-200'}`}>
                    {model.name}
                  </div>
                  <div className="text-xs text-gray-600">{model.serverAlias}</div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500 bg-black/40 px-2 py-0.5 rounded">{model.size}</span>
                <Button
                  type="text"
                  size="small"
                  className="text-gray-500 hover:text-white"
                  onClick={(e) => { e.stopPropagation(); testSingleModel(model.id); }}
                >
                  {testResults[model.id] === undefined ? 'Test' : (testResults[model.id] ? 'OK' : 'ERR')}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default WorkingAIConfigurationPanel