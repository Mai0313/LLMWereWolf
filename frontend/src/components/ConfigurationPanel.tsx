import React, { useState } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Slider,
  Switch,
  Button,
  Space,
  Row,
  Col,
  Divider,
  Tag,
  Table,
  message,
  Modal,
  InputNumber,
  Tabs
} from 'antd'
import {
  PlayCircleOutlined,
  SaveOutlined,
  PlusOutlined,
  DeleteOutlined,
  SettingOutlined,
  UserOutlined,
  RobotOutlined
} from '@ant-design/icons'
import WorkingAIConfigurationPanel from './WorkingAIConfigurationPanel'
import { GameConfiguration, AgentConfig } from '../../types/game'
import { useConfiguration, useAvailableConfigurations, setView, useGameStore } from '@store/gameStore'

const { Option } = Select

interface RoleSlot {
  id: string
  role: string
  count: number
  description: string
}

const ConfigurationPanel: React.FC = () => {
  const configuration = useConfiguration()
  const availableConfigurations = useAvailableConfigurations()
  const { setConfiguration } = useGameStore()

  const [form] = Form.useForm()
  const [selectedConfig, setSelectedConfig] = useState<GameConfiguration | null>(null)
  const [isModalVisible, setIsModalVisible] = useState(false)

  // 解决 LLM_SERVERS 未定义的问题
  const LLM_SERVERS = {
    server1: process.env.REACT_APP_LLM_SERVER_1 || 'http://100.80.20.5:4000/v1',
    server2: process.env.REACT_APP_LLM_SERVER_2 || 'http://100.82.5.110:30001'
  }

  // 预设角色数据
  const availableRoles: RoleSlot[] = [
    { id: 'werewolf', role: '狼人', count: 4, description: '每晚可以击杀一名玩家' },
    { id: 'villager', role: '村民', count: 6, description: '普通村民，无特殊技能' },
    { id: 'seer', role: '预言家', count: 1, description: '每晚可以查验一名玩家身份' },
    { id: 'witch', role: '女巫', count: 1, description: '拥有一瓶解药和毒药' },
    { id: 'guard', role: '守卫', count: 1, description: '每晚可以守护一名玩家' },
    { id: 'hunter', role: '猎人', count: 1, description: '死亡时可以开枪带走一人' },
    { id: 'cupid', role: '丘比特', count: 1, description: '游戏开始时连接情侣' },
    { id: 'idiot', role: '白痴', count: 1, description: '被投票出局时可以继续发言' }
  ]

  // AI模型配置
  const availableModels: AgentConfig[] = [
    { model: 'demo', description: 'Demo 智能体（测试用）' },
    { model: 'gpt-4', description: 'GPT-4（需要API密钥）' },
    { model: 'gpt-3.5-turbo', description: 'GPT-3.5 Turbo（需要API密钥）' },
    { model: 'claude-3', description: 'Claude-3（需要API密钥）' },
    { model: 'deepseek-chat', description: 'DeepSeek Chat（需要API密钥）' }
  ]

  const handleLoadConfiguration = (config: GameConfiguration) => {
    setSelectedConfig(config)
    form.setFieldsValue({
      name: config.name,
      playerCount: config.playerCount,
      enablePersonalitySystem: config.enablePersonalitySystem,
      language: config.language,
      timeout: config.timeout
    })
  }

  const handleSaveConfiguration = () => {
    form.validateFields().then((values) => {
      const newConfig: GameConfiguration = {
        id: Date.now().toString(),
        name: values.name,
        playerCount: values.playerCount,
        roles: [], // 根据玩家数量和角色配置生成
        timeout: values.timeout,
        language: values.language,
        enablePersonalitySystem: values.enablePersonalitySystem,
        agents: generateAgentConfigs(values.playerCount)
      }

      setConfiguration(newConfig)
      setSelectedConfig(newConfig)
      message.success('配置保存成功！')
    })
  }

  const generateAgentConfigs = (playerCount: number): AgentConfig[] => {
    return Array.from({ length: playerCount }, (_, i) => ({
      model: availableModels[0].model, // 默认使用第一个模型
      personalityProfile: values.enablePersonalitySystem ? `personality_${i}` : undefined,
      description: `玩家 ${i + 1} 智能体`
    }))
  }

  const handleStartGame = () => {
    if (selectedConfig) {
      //这里将来会调用真实的游戏启动API
      message.success(`正在启动游戏: ${selectedConfig.name}`)
      setView('game')
    } else {
      message.warning('请先选择或创建一个配置')
    }
  }

  const handleAddRole = () => {
    setIsModalVisible(true)
  }

  const handleRemoveRole = (roleId: string) => {
    // 实现角色移除逻辑
    message.info('角色移除功能待实现')
  }

  const handleTestAPIConnection = () => {
    // 实现API连接测试
    message.info('API连接测试功能待实现')
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <Card
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <SettingOutlined />
              <span>游戏配置</span>
            </div>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleStartGame}
              disabled={!selectedConfig}
            >
              启动游戏
            </Button>
          </div>
        }
      >
        <Tabs
          defaultActiveKey="game"
          items={[
            {
              key: 'game',
              label: (
                <span>
                  <SettingOutlined />
                  游戏配置
                </span>
              ),
              children: (
                <Row gutter={[24, 24]}>
                  {/* 左侧：配置表单 */}
                  <Col span={16}>
                    <Form
                      form={form}
                      layout="vertical"
                      initialValues={{
                        name: '自定义游戏',
                        playerCount: 16,
                        enablePersonalitySystem: false,
                        language: 'zh-CN',
                        timeout: {
                          night: 30,
                          dayDiscussion: 60,
                          dayVoting: 30
                        }
                      }}
                    >
                      {/* 基本信息 */}
                      <Card size="small" title="基本信息" className="mb-4">
                        <Row gutter={[16, 16]}>
                          <Col span={12}>
                            <Form.Item
                              label="游戏名称"
                              name="name"
                              rules={[{ required: true, message: '请输入游戏名称' }]}
                            >
                              <Input placeholder="输入游戏名称" />
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              label="玩家人数"
                              name="playerCount"
                              rules={[{ required: true, message: '请选择玩家人数' }]}
                            >
                              <Select placeholder="选择玩家人数">
                                {[6, 8, 10, 12, 14, 16, 18, 20].map(count => (
                                  <Option key={count} value={count}>
                                    {count} 人
                                  </Option>
                                ))}
                              </Select>
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              label="游戏语言"
                              name="language"
                            >
                              <Select>
                                <Option value="zh-CN">简体中文</Option>
                                <Option value="zh-TW">繁体中文</Option>
                                <Option value="en-US">English</Option>
                              </Select>
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              label="启用人格系统"
                              name="enablePersonalitySystem"
                              valuePropName="checked"
                            >
                              <Switch />
                            </Form.Item>
                          </Col>
                        </Row>
                      </Card>

                      {/* 时间配置 */}
                      <Card size="small" title="时间配置" className="mb-4">
                        <Form.Item
                          label="黑夜时间（秒）"
                          name={['timeout', 'night']}
                        >
                          <Slider
                            min={10}
                            max={120}
                            marks={{
                              10: '10s',
                              30: '30s',
                              60: '1m',
                              120: '2m'
                            }}
                          />
                        </Form.Item>
                        <Form.Item
                          label="白天讨论时间（秒）"
                          name={['timeout', 'dayDiscussion']}
                        >
                          <Slider
                            min={30}
                            max={180}
                            marks={{
                              30: '30s',
                              60: '1m',
                              120: '2m',
                              180: '3m'
                            }}
                          />
                        </Form.Item>
                        <Form.Item
                          label="投票时间（秒）"
                          name={['timeout', 'dayVoting']}
                        >
                          <Slider
                            min={15}
                            max={90}
                            marks={{
                              15: '15s',
                              30: '30s',
                              60: '1m',
                              90: '1.5m'
                            }}
                          />
                        </Form.Item>
                      </Card>

                      {/* 操作按钮 */}
                      <div className="flex space-x-4">
                        <Button
                          type="primary"
                          icon={<SaveOutlined />}
                          onClick={handleSaveConfiguration}
                        >
                          保存配置
                        </Button>
                        <Button
                          icon={<PlusOutlined />}
                          onClick={handleAddRole}
                        >
                          添加角色
                        </Button>
                      </div>
                    </Form>
                  </Col>

                  {/* 右侧：预设配置 */}
                  <Col span={8}>
                    <Card size="small" title="预设配置">
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {availableConfigurations.map(config => (
                          <div
                            key={config.id}
                            className={`p-3 border rounded cursor-pointer transition-all ${
                              selectedConfig?.id === config.id
                                ? 'border-blue-400 bg-blue-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                            onClick={() => handleLoadConfiguration(config)}
                          >
                            <div className="font-medium">{config.name}</div>
                            <div className="text-sm text-gray-600">
                              {config.playerCount} 人
                              {config.enablePersonalitySystem && (
                                <Tag size="small" className="ml-2">人格系统</Tag>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card>

                    {/* 角色分配 */}
                    {selectedConfig && (
                      <Card size="small" title="角色分配" className="mt-4">
                        <div className="space-y-2 max-h-64 overflow-y-auto">
                          {availableRoles.map(role => (
                            <div
                              key={role.id}
                              className="flex items-center justify-between p-2 border rounded"
                            >
                              <div className="flex items-center space-x-2">
                                <UserOutlined />
                                <div>
                                  <div className="font-medium">{role.role}</div>
                                  <div className="text-xs text-gray-500">
                                    {role.description}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <InputNumber
                                  size="small"
                                  min={0}
                                  max={selectedConfig.playerCount}
                                  defaultValue={role.count}
                                  style={{ width: 60 }}
                                />
                                <Button
                                  size="small"
                                  type="text"
                                  danger
                                  icon={<DeleteOutlined />}
                                  onClick={() => handleRemoveRole(role.id)}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </Card>
                    )}
                  </Col>
                </Row>
              )
            },
            {
              key: 'ai',
              label: (
                <span>
                  <RobotOutlined />
                  AI 配置
                </span>
              ),
              children: <WorkingAIConfigurationPanel />
            }
          ]}
        />
      </Card>

      {/* 添加角色 Modal */}
      <Modal
        title="添加自定义角色"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => {
          setIsModalVisible(false)
          message.info('自定义角色功能待实现')
        }}
      >
        <Form layout="vertical">
          <Form.Item label="角色名称">
            <Input placeholder="输入角色名称" />
          </Form.Item>
          <Form.Item label="角色描述">
            <Input.TextArea placeholder="输入角色描述" rows={3} />
          </Form.Item>
          <Form.Item label="所属阵营">
            <Select placeholder="选择阵营">
              <Option value="werewolf">狼人阵营</Option>
              <Option value="villager">村民阵营</Option>
              <Option value="neutral">中立阵营</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ConfigurationPanel