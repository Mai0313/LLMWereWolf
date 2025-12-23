import React from 'react'
import { Button, Tooltip } from 'antd'
import { SettingOutlined, BarChartOutlined, CloseOutlined } from '@ant-design/icons'
import { useUIState, useGameStore } from '@store/gameStore'
import GameLayout from '@components/GameLayout'
import StatisticsPanel from '@components/StatisticsPanel'
import ConfigurationPanel from '@components/ConfigurationPanel'
import { motion, AnimatePresence } from 'framer-motion'

const App: React.FC = () => {
  const { showingStatistics, currentView } = useUIState()
  const { setView, toggleStatistics } = useGameStore()

  // 渲染当前视图
  const renderContent = () => {
    return (
      <AnimatePresence mode="wait">
        {currentView === 'configuration' && (
          <motion.div
            key="config"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            className="absolute inset-0 z-40"
          >
            <ConfigurationPanel />
          </motion.div>
        )}

        {currentView === 'game' && (
          <motion.div
            key="game"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-0"
          >
            <GameLayout />
          </motion.div>
        )}
      </AnimatePresence>
    )
  }

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-bg-dark font-sans selection:bg-mystic-accent selection:text-white">
      {/* 动态背景层 */}
      <div className="absolute inset-0 bg-radial-mystic pointer-events-none z-0" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none z-0 mix-blend-overlay" />

      {/* 顶部导航栏 (悬浮) */}
      <div className="absolute top-0 left-0 w-full z-50 p-6 flex justify-between items-start pointer-events-none">
        {/* Logo/标题区域 */}
        <div className="pointer-events-auto">
          {currentView === 'game' && (
            <div className="flex flex-col">
              <h1 className="text-2xl font-serif font-bold text-transparent bg-clip-text bg-gradient-to-r from-mystic-accent to-blue-400 tracking-widest drop-shadow-sm">
                MIDNIGHT PROTOCOL
              </h1>
              <span className="text-[10px] text-mystic-dim uppercase tracking-[0.3em]">AI Werewolf Simulation</span>
            </div>
          )}
        </div>

        {/* 右上角控制按钮 */}
        <div className="pointer-events-auto flex gap-3">
          {currentView === 'game' && (
            <>
              <Tooltip title="Statistics" placement="bottom">
                <Button
                  type="text"
                  icon={<BarChartOutlined />}
                  className={`
                    w-10 h-10 rounded-full border border-white/10 backdrop-blur-md transition-all duration-300
                    ${showingStatistics ? 'bg-mystic-accent text-white shadow-glow-sm' : 'bg-black/20 text-mystic-dim hover:bg-white/10 hover:text-white'}
                  `}
                  onClick={toggleStatistics}
                />
              </Tooltip>
              <Tooltip title="Configuration" placement="bottom">
                <Button
                  type="text"
                  icon={<SettingOutlined />}
                  className="w-10 h-10 rounded-full border border-white/10 bg-black/20 backdrop-blur-md text-mystic-dim hover:bg-white/10 hover:text-white transition-all duration-300"
                  onClick={() => setView('configuration')}
                />
              </Tooltip>
            </>
          )}

          {/* 在配置页面显示的关闭按钮 */}
          {currentView === 'configuration' && (
            <Tooltip title="Back to Game" placement="bottom">
              <Button
                type="text"
                icon={<CloseOutlined />}
                className="w-10 h-10 rounded-full border border-white/10 bg-black/40 backdrop-blur-md text-white hover:bg-white/10 hover:rotate-90 transition-all duration-300"
                onClick={() => setView('game')}
              />
            </Tooltip>
          )}
        </div>
      </div>

      {/* 统计面板覆盖层 */}
      <AnimatePresence>
        {showingStatistics && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute top-0 right-0 bottom-0 w-full md:w-[600px] z-40 bg-black/80 backdrop-blur-xl border-l border-white/10 shadow-2xl"
          >
            <StatisticsPanel />
          </motion.div>
        )}
      </AnimatePresence>

      {/* 主内容区域 */}
      {renderContent()}
    </div>
  )
}

export default App