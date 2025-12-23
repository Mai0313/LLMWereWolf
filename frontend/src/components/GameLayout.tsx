import React, { useEffect, useRef } from 'react'
import { Layout, Row, Col, Card, Empty, Spin } from 'antd'
import { motion, AnimatePresence } from 'framer-motion'
import PlayerCircle from './PlayerCircle'
import EventFeed from './EventFeed'
import GameDashboard from './GameDashboard'
import VotingPanel from './VotingPanel'
import PlayerDetailsPanel from './PlayerDetailsPanel'
import { useGameState, usePlayers, useCurrentEvent, useUIState, useGameStore } from '@store/gameStore'
import { generateMockGame } from '@utils/mockData'

const { Content, Sider } = Layout

const GameLayout: React.FC = () => {
  const players = usePlayers()
  const gameState = useGameState()
  const currentEvent = useCurrentEvent()
  const uiState = useUIState()
  const { setGameState, addEvent } = useGameStore()

  // 如果没有游戏状态，生成模拟数据
  useEffect(() => {
    if (!gameState) {
      const mockGame = generateMockGame()
      setGameState(mockGame)

      // 模拟事件流
      const eventInterval = setInterval(() => {
        if (mockGame.events.length > 0) {
          const randomEvent = mockGame.events[
            Math.floor(Math.random() * Math.min(mockGame.events.length, 10))
          ]
          addEvent({ ...randomEvent, id: Date.now().toString(), timestamp: new Date() })
        }
      }, 3000)

      return () => clearInterval(eventInterval)
    }
  }, [gameState, setGameState, addEvent])

  if (!gameState) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <Layout className="h-full">
      {/* 左侧边栏 - 事件流 */}
      <Sider
        width={350}
        className="p-4 overflow-hidden"
        style={{
          background: 'transparent',
          borderRight: uiState.theme === 'light' ?
            '1px solid rgba(0, 0, 0, 0.1)' :
            '1px solid rgba(148, 163, 184, 0.1)'
        }}
      >
        <EventFeed />
      </Sider>

      {/* 主内容区 - 游戏桌面 */}
      <Content className="relative overflow-hidden">
        {/* 游戏仪表板 */}
        <div className="absolute top-4 left-4 z-10">
          <GameDashboard />
        </div>

        {/* 圆形玩家布局 */}
        <div className="relative w-full h-full flex items-center justify-center">
          <AnimatePresence>
            {currentEvent && (
              <motion.div
                key={currentEvent.id}
                initial={{ opacity: 0, y: 50, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -50, scale: 0.9 }}
                className="absolute top-20 left-1/2 transform -translate-x-1/2 z-20"
              >
                <Card
                  className="shadow-2xl"
                  style={{
                    background: uiState.theme === 'light' ?
                      'rgba(255, 255, 255, 0.95)' :
                      'rgba(30, 41, 59, 0.95)',
                    backdropFilter: 'blur(10px)',
                    minWidth: '300px'
                  }}
                  size="small"
                >
                  <div className="text-center">
                    <div className="text-sm opacity-75 mb-1">
                      {currentEvent.round} 轮 • {currentEvent.phase}
                    </div>
                    <div className="font-medium">
                      {currentEvent.message}
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          <PlayerCircle
            players={players}
            gameState={gameState}
          />
        </div>

        {/* 投票面板 */}
        {gameState.phase === 'day_voting' && (
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
            <VotingPanel />
          </div>
        )}
      </Content>

      {/* 右侧边栏 - 玩家详情 */}
      {uiState.showPlayerDetails && uiState.selectedPlayer && (
        <Sider
          width={320}
          className="p-4"
          style={{
            background: 'transparent',
            borderLeft: uiState.theme === 'light' ?
              '1px solid rgba(0, 0, 0, 0.1)' :
              '1px solid rgba(148, 163, 184, 0.1)'
          }}
        >
          <PlayerDetailsPanel player={uiState.selectedPlayer} />
        </Sider>
      )}
    </Layout>
  )
}

export default GameLayout