import React from 'react'
import { Button, Tooltip } from 'antd'
import { PlayCircleOutlined, PauseCircleOutlined, ReloadOutlined } from '@ant-design/icons'
import { useGameState, usePlayers } from '@store/gameStore'

const StatItem: React.FC<{ label: string; value: string | number; color?: string }> = ({ label, value, color = 'text-white' }) => (
  <div className="flex flex-col items-center px-5 border-r border-white/10 last:border-0 min-w-[80px]">
    <span className="text-[9px] uppercase tracking-[0.2em] text-gray-500 mb-0.5 font-sans">{label}</span>
    <span className={`text-xl font-serif font-bold ${color} drop-shadow-md`}>{value}</span>
  </div>
)

const GameDashboard: React.FC = () => {
  const gameState = useGameState()
  const players = usePlayers()
  if (!gameState) return null

  const alive = players.filter(p => p.isAlive).length
  const wolves = players.filter(p => p.isAlive && p.role.camp === 'werewolf').length

  return (
    <div className="
      flex items-center gap-2 px-1 py-1 pr-6 rounded-full 
      bg-[#0a0a0f]/80 backdrop-blur-xl border border-white/10 shadow-[0_4px_20px_rgba(0,0,0,0.4)]
    ">

      {/* Phase Indicator Circle */}
      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-mystic-accent to-blue-600 flex items-center justify-center shadow-glow-sm">
        <span className="text-lg">
          {gameState.phase === 'night' ? '🌙' : gameState.phase.includes('day') ? '☀️' : '⏳'}
        </span>
      </div>

      {/* Stats */}
      <div className="flex items-center mx-2">
        <StatItem label="Alive" value={`${alive}/${players.length}`} />
        <StatItem label="Wolves" value={wolves} color="text-red-400" />
        <StatItem label="Round" value={gameState.round} color="text-mystic-accent" />
      </div>

      {/* Controls */}
      <div className="flex gap-1 ml-2 pl-4 border-l border-white/10">
        <Tooltip title={gameState.isRunning ? "Pause Ritual" : "Resume Ritual"}>
          <Button
            type="text"
            shape="circle"
            icon={gameState.isRunning ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            className="text-white hover:text-mystic-accent hover:bg-white/10"
            onClick={() => { }}
          />
        </Tooltip>
        <Tooltip title="Reset Timeline">
          <Button
            type="text"
            shape="circle"
            icon={<ReloadOutlined />}
            className="text-gray-400 hover:text-red-400 hover:bg-white/10"
            onClick={() => { }}
          />
        </Tooltip>
      </div>
    </div>
  )
}

export default GameDashboard