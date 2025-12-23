import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import { Badge, Avatar, Tooltip, Card } from 'antd'
import { UserOutlined, CrownOutlined } from '@ant-design/icons'
import { Player, GameState, Position } from '../../types/game'
import { useCircleLayout, useGameStore } from '@store/gameStore'

interface PlayerCircleProps {
  players: Player[]
  gameState: GameState
}

interface PlayerNodeProps {
  player: Player
  position: Position
  index: number
  isSelected: boolean
  isHovered: boolean
  onClick: () => void
  onHover: (hover: boolean) => void
}

const PlayerNode: React.FC<PlayerNodeProps> = ({
  player,
  position,
  index,
  isSelected,
  isHovered,
  onClick,
  onHover
}) => {
  const { playerAnimations } = useGameStore()

  // 获取状态样式
  const getStatusColor = (player: Player) => {
    if (!player.isAlive) return 'text-gray-400'
    if (player.status === 'protected') return 'text-blue-400'
    if (player.status === 'poisoned') return 'text-purple-400'
    if (player.status === 'charmed') return 'text-pink-400'
    return 'text-green-400'
  }

  const getStatusBorderColor = (player: Player) => {
    if (!player.isAlive) return 'border-gray-400'
    if (player.status === 'protected') return 'border-blue-400'
    if (player.status === 'poisoned') return 'border-purple-400'
    if (player.status === 'charmed') return 'border-pink-400'
    return 'border-green-400'
  }

  const getStatusAnimation = (player: Player) => {
    const animation = playerAnimations[player.id]
    if (animation?.death) return 'death-animation'
    if (animation?.targeted) return 'pulse-effect'
    if (animation?.protected) return 'pulse-effect'
    if (animation?.poisoned) return 'pulse-effect'
    return ''
  }

  return (
    <motion.div
      key={player.id}
      initial={{ opacity: 0, scale: 0 }}
      animate={{
        opacity: 1,
        scale: isSelected ? 1.2 : isHovered ? 1.1 : 1,
        x: position.x,
        y: position.y
      }}
      className="absolute cursor-pointer player-circle"
      style={{
        left: '50%',
        top: '50%',
        marginLeft: '-40px',
        marginTop: '-40px',
        width: '80px',
        height: '80px'
      }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      onMouseEnter={() => onHover(true)}
      onMouseLeave={() => onHover(false)}
    >
      <div className="relative w-full h-full flex flex-col items-center justify-center">
        {/* 玩家头像 */}
        <div className="relative">
          <Avatar
            size={60}
            icon={<UserOutlined />}
            className={`border-4 ${getStatusBorderColor(player)} ${getStatusAnimation(player)} transition-all duration-300`}
            style={{
              backgroundColor: player.isAlive ? player.role.camp === 'werewolf' ? '#dc2626' : '#1e40af' : '#6b7280'
            }}
          />

          {/* 状态指示器 */}
          {player.status !== 'alive' && player.isAlive && (
            <div
              className={`absolute -top-1 -right-1 w-4 h-4 rounded-full full-animation ${getStatusColor(player).replace('text-', 'bg-')}`}
            />
          )}

          {/* 警长徽章 */}
          {player.sheriff && (
            <Badge
              count={<CrownOutlined className="text-yellow-400" />}
              className="absolute -top-2 -right-2"
            />
          )}
        </div>

        {/* 玩家名字 */}
        <div className="mt-1 text-xs font-medium text-center max-w-[80px] truncate">
          {player.name}
        </div>

        {/* 身份标签（仅在游戏结束或特殊状态显示） */}
        {!player.isAlive && (
          <div className="absolute -bottom-6 text-xs text-gray-400 whitespace-nowrap">
            {player.role.name}
          </div>
        )}
      </div>
    </motion.div>
  )
}

const ConnectionLines: React.FC<{ players: Player[]; positions: Record<string, Position> }> = ({
  players,
  positions
}) => {
  const lovers = players.filter(p => p.lovers && p.lovers.length > 0)

  if (lovers.length === 0) return null

  return (
    <svg className="absolute inset-0 w-full h-full pointer-events-none">
      {lovers.map((player) => {
        const loverId = player.lovers?.[0]
        if (!loverId || player.position === undefined || !positions[player.position]) return null

        const lover = players.find(p => p.id === loverId)
        if (!lover || lover.position === undefined || !positions[lover.position]) return null

        const pos1 = positions[player.position]
        const pos2 = positions[lover.position]

        return (
          <motion.line
            key={`${player.id}-${loverId}`}
            x1={pos1.x}
            y1={pos1.y}
            x2={pos2.x}
            y2={pos2.y}
            stroke="#ec4899"
            strokeWidth="2"
            className="connection-line"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2 }}
          />
        )
      })}
    </svg>
  )
}

const PlayerCircle: React.FC<PlayerCircleProps> = ({ players, gameState }) => {
  const layout = useCircleLayout()
  const { selectedPlayer, selectPlayer, hoverPlayer } = useGameStore()

  // 确保布局已计算
  if (Object.keys(layout).length === 0) {
    return null
  }

  return (
    <div className="relative w-full h-full">
      {/* 连接线 */}
      <ConnectionLines players={players} positions={layout} />

      {/* 中心信息显示 */}
      <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
        <div className="text-center">
          <div className="text-2xl font-bold mb-2">
            {gameState.phase === 'night' ? '🌙' : '☀️'}
          </div>
          <div className="text-lg mb-1">
            {gameState.round} 轮
          </div>
          <div className="text-sm opacity-75">
            {gameState.phaseName}
          </div>

          {/* 阵营统计 */}
          <div className="flex space-x-4 mt-4 justify-center">
            <div className="text-center">
              <div className="text-2xl">🐺</div>
              <div className="text-sm">狼人</div>
              <div className="font-bold text-red-400">
                {players.filter(p => p.isAlive && p.role.camp === 'werewolf').length}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl">👥</div>
              <div className="text-sm">村民</div>
              <div className="font-bold text-blue-400">
                {players.filter(p => p.isAlive && p.role.camp === 'villager').length}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl">⚖️</div>
              <div className="text-sm">中立</div>
              <div className="font-bold text-gray-400">
                {players.filter(p => p.isAlive && p.role.camp === 'neutral').length}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 玩家节点 */}
      {players.map((player, index) => {
        const position = layout[player.position] || { x: 0, y: 0 }
        return (
          <PlayerNode
            key={player.id}
            player={player}
            position={position}
            index={index}
            isSelected={selectedPlayer?.id === player.id}
            isHovered={false} // 可以从 store 获取
            onClick={() => {
              selectPlayer(selectedPlayer?.id === player.id ? null : player)
            }}
            onHover={(hover) => {
              hoverPlayer(hover ? player : null)
            }}
          />
        )
      })}
    </div>
  )
}

export default PlayerCircle