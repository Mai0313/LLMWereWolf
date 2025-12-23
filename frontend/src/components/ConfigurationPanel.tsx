import React, { useState } from 'react'
import { Form, Input, Select, Slider, Switch, Button, Row, Col, Badge } from 'antd'
import {
  PlayCircleOutlined,
  SettingOutlined,
  RobotOutlined,
  UsergroupAddOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import { useGameStore, setView } from '@store/gameStore'
import WorkingAIConfigurationPanel from './WorkingAIConfigurationPanel'
import { motion } from 'framer-motion'

const { Option } = Select

const ConfigurationPanel: React.FC = () => {
  const [form] = Form.useForm()
  const [activeTab, setActiveTab] = useState<'rules' | 'ai'>('rules')

  const handleStart = () => {
    setView('game')
  }

  // 侧边栏菜单项组件
  const MenuItem = ({ id, icon, label, active }: any) => (
    <div
      onClick={() => setActiveTab(id)}
      className={`
        group flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-300
        ${active
          ? 'bg-gradient-to-r from-mystic-accent/20 to-transparent border-l-2 border-mystic-accent text-white'
          : 'text-gray-400 hover:bg-white/5 hover:text-gray-200 border-l-2 border-transparent'}
      `}
    >
      <span className={`text-lg transition-transform group-hover:scale-110 ${active ? 'text-mystic-accent' : 'text-gray-500'}`}>
        {icon}
      </span>
      <span className="font-serif tracking-wide text-sm">{label}</span>
    </div>
  )

  return (
    <div className="w-full h-full flex items-center justify-center p-4 md:p-8">
      {/* 玻璃拟态主容器 */}
      <div className="w-full max-w-6xl h-[85vh] bg-[#0a0a0f]/80 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col md:flex-row">

        {/* 左侧导航栏 */}
        <div className="w-full md:w-64 bg-black/20 border-r border-white/5 p-6 flex flex-col">
          <div className="mb-8 pl-2">
            <div className="text-[10px] text-mystic-dim uppercase tracking-[0.2em] mb-1">System Configuration</div>
            <h2 className="text-2xl font-serif text-white font-bold">RITUAL SETUP</h2>
          </div>

          <div className="flex-1 space-y-2">
            <MenuItem
              id="rules"
              icon={<SettingOutlined />}
              label="Game Parameters"
              active={activeTab === 'rules'}
            />
            <MenuItem
              id="ai"
              icon={<RobotOutlined />}
              label="Artificial Intelligence"
              active={activeTab === 'ai'}
            />
          </div>

          {/* 底部预设 */}
          <div className="mt-auto pt-6 border-t border-white/5">
            <div className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Quick Presets</div>
            <div className="space-y-2">
              {['Standard 12 (4 Wolves)', 'Chaos 9 (3 Wolves)', 'Speed 6 (2 Wolves)'].map((preset, i) => (
                <div key={i} className="px-3 py-2 text-xs text-gray-400 bg-white/5 hover:bg-mystic-accent/20 hover:text-white rounded cursor-pointer transition-colors border border-transparent hover:border-mystic-accent/30">
                  {preset}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧内容区 */}
        <div className="flex-1 flex flex-col relative overflow-hidden bg-gradient-to-br from-transparent to-mystic-accent/5">
          {/* 顶部标题栏 */}
          <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-black/10">
            <div>
              <h3 className="text-xl text-white font-serif tracking-wide">
                {activeTab === 'rules' ? 'RULES OF ENGAGEMENT' : 'NEURAL NETWORK CONFIG'}
              </h3>
              <p className="text-xs text-gray-500 mt-1">
                {activeTab === 'rules' ? 'Configure time dilation and participant souls' : 'Manage LLM connections and parameters'}
              </p>
            </div>

            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={handleStart}
              className="bg-mystic-accent border-none hover:bg-mystic-accent/80 shadow-glow-sm h-10 px-8 font-serif tracking-widest rounded-full"
            >
              INITIATE
            </Button>
          </div>

          {/* 滚动内容区 */}
          <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
            {activeTab === 'rules' ? (
              <Form form={form} layout="vertical" className="max-w-3xl">

                {/* 第一部分：核心设置 */}
                <div className="mb-8">
                  <div className="flex items-center gap-2 mb-4 text-mystic-accent">
                    <UsergroupAddOutlined />
                    <span className="text-sm font-bold uppercase tracking-widest">Core Parameters</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Form.Item label={<span className="text-gray-400">SESSION NAME</span>} name="name" initialValue="Midnight Protocol">
                      <Input className="h-10 text-lg font-serif" placeholder="Enter session name" />
                    </Form.Item>

                    <Form.Item label={<span className="text-gray-400">PARTICIPANTS</span>} name="playerCount" initialValue={12}>
                      <Select className="h-10" dropdownClassName="bg-mystic-900 border border-white/10">
                        {[6, 9, 12, 16, 20].map(n => (
                          <Option key={n} value={n}>
                            <div className="flex justify-between items-center">
                              <span>{n} Souls</span>
                              <Badge status="processing" color={n > 12 ? '#f59e0b' : '#8b5cf6'} />
                            </div>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </div>

                  <Form.Item name="personality" valuePropName="checked" className="bg-white/5 p-4 rounded-lg border border-white/5">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium mb-1">Complex Personality Matrix</div>
                        <div className="text-xs text-gray-500">Enable deep psychological profiling and memory retention for agents</div>
                      </div>
                      <Switch />
                    </div>
                  </Form.Item>
                </div>

                {/* 第二部分：时间设置 */}
                <div className="mb-8">
                  <div className="flex items-center gap-2 mb-4 text-mystic-gold">
                    <ClockCircleOutlined />
                    <span className="text-sm font-bold uppercase tracking-widest">Time Dilation</span>
                  </div>

                  <div className="bg-black/20 p-6 rounded-xl border border-white/5 space-y-6">
                    <Form.Item label={<span className="text-gray-400 flex justify-between"><span>NIGHT DURATION</span> <span className="text-mystic-accent">30s</span></span>} name="nightTime">
                      <Slider
                        trackStyle={{ backgroundColor: '#8b5cf6' }}
                        handleStyle={{ borderColor: '#8b5cf6', backgroundColor: '#000', boxShadow: '0 0 10px #8b5cf6' }}
                        railStyle={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
                      />
                    </Form.Item>
                    <Form.Item label={<span className="text-gray-400 flex justify-between"><span>DAY DISCUSSION</span> <span className="text-mystic-gold">60s</span></span>} name="dayTime">
                      <Slider
                        trackStyle={{ backgroundColor: '#fbbf24' }}
                        handleStyle={{ borderColor: '#fbbf24', backgroundColor: '#000', boxShadow: '0 0 10px #fbbf24' }}
                        railStyle={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
                      />
                    </Form.Item>
                    <Form.Item label={<span className="text-gray-400 flex justify-between"><span>VOTING WINDOW</span> <span className="text-mystic-blood">30s</span></span>} name="voteTime">
                      <Slider
                        trackStyle={{ backgroundColor: '#ef4444' }}
                        handleStyle={{ borderColor: '#ef4444', backgroundColor: '#000', boxShadow: '0 0 10px #ef4444' }}
                        railStyle={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
                      />
                    </Form.Item>
                  </div>
                </div>
              </Form>
            ) : (
              <div className="max-w-4xl animate-fade-in">
                <WorkingAIConfigurationPanel />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConfigurationPanel