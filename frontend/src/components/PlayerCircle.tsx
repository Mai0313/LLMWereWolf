import React from 'react'
import { motion } from 'framer-motion'
import { Player, GameState, Position } from '@/types/game'
import { useCircleLayout, useGameStore } from '@store/gameStore'

interface PlayerCircleProps {
  players: Player[]
  gameState: GameState
}

const PlayerNode: React.FC<{
  player: Player
  position: Position
  isSelected: boolean
  onClick: () => void
}> = ({ player, position, isSelected, onClick }) => {
  // 安全检查
  if (!position) return null;

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{
        scale: isSelected ? 1.2 : 1,
        opacity: 1,
        // 直接使用 store 计算的绝对坐标
        left: position.x,
        top: position.y
      }}
      // 关键样式：absolute, transform 居中 (-translate-x-1/2)
      className="absolute w-20 h-20 -ml-10 -mt-10 flex flex-col items-center justify-center cursor-pointer z-10 group"
      onClick={onClick}
    >
      {/* 选中光环 */}
      {isSelected && (
        <div className="absolute inset-[-8px] rounded-full border border-mystic-accent animate-pulse" />
      )}

      {/* 头像圆圈 */}
      <div className={`
        relative w-14 h-14 rounded-full border-2 flex items-center justify-center
        transition-all duration-300 backdrop-blur-sm
        ${player.isAlive
          ? 'bg-black/40 border-blue-400/50 shadow-[0_0_15px_rgba(59,130,246,0.4)]'
          : 'bg-black/60 border-gray-700 grayscale opacity-50'}
      `}>
        <span className="text-xl">{player.isAlive ? '👤' : '💀'}</span>

        {/* 警长 */}
        {player.sheriff && <span className="absolute -top-3 text-lg">👑</span>}

        {/* 编号 */}
        <div className="absolute -bottom-2 bg-black border border-white/20 px-1 rounded text-[9px] text-gray-300 font-mono">
          {String(player.position + 1).padStart(2, '0')}
        </div>
      </div>

      {/* 名字 */}
      <div className="mt-2 text-[10px] text-gray-400 font-serif tracking-widest bg-black/50 px-2 rounded">
        {player.name}
      </div>
    </motion.div>
  )
}

const PlayerCircle: React.FC<PlayerCircleProps> = ({ players, gameState }) => {
  const layout = useCircleLayout()
  const { selectedPlayer, selectPlayer } = useGameStore()

  return (
    // 强制 w-full h-full 填满 800x800 的父容器
    <div className="relative w-full h-full">
      {/* 背景装饰：魔法阵 */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
        <div className="w-[500px] h-[500px] border border-mystic-accent/30 rounded-full animate-pulse" />
        <div className="w-[300px] h-[300px] border border-blue-500/20 rounded-full" />
      </div>

      {/* 中心文字 */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-0">
        <div className="text-6xl font-serif font-bold text-white/5">{gameState.round}</div>
        <div className="text-xl font-serif text-mystic-accent tracking-[0.2em] mt-2">
          {gameState.phase.toUpperCase().replace('_', ' ')}
        </div>
      </div>

      {/* 玩家节点 */}
      {players.map((player) => (
        <PlayerNode
          key={player.id}
          player={player}
          position={layout[player.position]}
          isSelected={selectedPlayer?.id === player.id}
          onClick={() => selectPlayer(selectedPlayer?.id === player.id ? null : player)}
        />
      ))}
    </div>
  )
}

export default PlayerCircle