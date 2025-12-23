import React, { useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import PlayerCircle from './PlayerCircle'
import EventFeed from './EventFeed'
import VotingPanel from './VotingPanel'
import PlayerDetailsPanel from './PlayerDetailsPanel'
import GameDashboard from './GameDashboard'
import { useGameState, usePlayers, useUIState, useGameStore } from '@store/gameStore'
import { generateMockGame } from '@utils/mockData'

const GameLayout: React.FC = () => {
  const players = usePlayers()
  const gameState = useGameState()
  const uiState = useUIState()
  const { setGameState, calculateCircleLayout } = useGameStore()

  useEffect(() => {
    // 初始化游戏数据
    if (!gameState) {
      setGameState(generateMockGame())
    }
  }, []) // 只在挂载时运行一次

  // 监听玩家数量变化，重新计算布局
  useEffect(() => {
    if (players.length > 0) {
      calculateCircleLayout(players.length)
    }
  }, [players.length, calculateCircleLayout])

  if (!gameState) return <div className="w-full h-full bg-black" />

  return (
    <div className="relative w-full h-full flex overflow-hidden bg-bg-dark">

      {/* 左侧：日志栏 */}
      <aside className="w-80 flex-shrink-0 z-10 flex flex-col border-r border-white/10 bg-black/40 backdrop-blur-md">
        <EventFeed />
      </aside>

      {/* 中间：主舞台 */}
      <main className="flex-1 relative flex flex-col bg-radial-mystic">

        {/* 顶部仪表盘 */}
        <div className="absolute top-6 left-0 right-0 z-20 flex justify-center pointer-events-none">
          <div className="pointer-events-auto">
            <GameDashboard />
          </div>
        </div>

        {/* 仪式圆环区域 - 强制居中 */}
        <div className="flex-1 flex items-center justify-center overflow-hidden">
          {/* 这里强制设定容器大小，与 Store 中的计算逻辑(800x800)对应 */}
          <div className="w-[800px] h-[800px] relative flex items-center justify-center">
            <PlayerCircle players={players} gameState={gameState} />
          </div>
        </div>

        {/* 底部投票栏 */}
        <AnimatePresence>
          {gameState.phase === 'day_voting' && (
            <motion.div
              initial={{ y: 200, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 200, opacity: 0 }}
              className="absolute bottom-8 left-0 right-0 z-30 flex justify-center pointer-events-none"
            >
              <div className="pointer-events-auto w-full max-w-3xl px-4">
                <VotingPanel />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* 右侧：详情面板 */}
      <AnimatePresence>
        {uiState.showPlayerDetails && uiState.selectedPlayer && (
          <motion.aside
            initial={{ x: 350, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 350, opacity: 0 }}
            className="absolute right-0 top-0 bottom-0 w-80 z-40 border-l border-white/10 bg-black/80 backdrop-blur-xl shadow-2xl"
          >
            <PlayerDetailsPanel player={uiState.selectedPlayer} />
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  )
}

export default GameLayout