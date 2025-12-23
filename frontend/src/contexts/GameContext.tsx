import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { useGameStore } from '../store/gameStore'

interface GameContextType {
  // 这里可以添加额外的游戏上下文功能
  isConnected: boolean
  connect: () => void
  disconnect: () => void
}

const GameContext = createContext<GameContextType | undefined>(undefined)

interface GameProviderProps {
  children: ReactNode
}

export const GameProvider: React.FC<GameProviderProps> = ({ children }) => {
  const loadConfigurations = useGameStore((state) => state.loadConfigurations)

  useEffect(() => {
    // 初始化配置
    loadConfigurations()
  }, [loadConfigurations])

  const contextValue: GameContextType = {
    isConnected: true, // 暂时设为 true，将来连接 WebSocket
    connect: () => {
      console.log('Connecting to game server...')
    },
    disconnect: () => {
      console.log('Disconnecting from game server...')
    }
  }

  return (
    <GameContext.Provider value={contextValue}>
      {children}
    </GameContext.Provider>
  )
}

export const useGameContext = () => {
  const context = useContext(GameContext)
  if (context === undefined) {
    throw new Error('useGameContext must be used within a GameProvider')
  }
  return context
}