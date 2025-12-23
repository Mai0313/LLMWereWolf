import React from 'react'
import { Player } from '@/types/game'
import { useGameEvents, useGameStore } from '@store/gameStore'
import { CloseOutlined, UserOutlined } from '@ant-design/icons'
import { Button, Tag } from 'antd'

const PlayerDetailsPanel: React.FC<{ player: Player }> = ({ player }) => {
  const events = useGameEvents()
  const { togglePlayerDetails } = useGameStore()
  const playerEvents = events.filter(e => e.message.includes(player.name)).slice(-10)

  return (
    <div className="h-full flex flex-col relative">
      {/* Close Button */}
      <Button
        type="text"
        icon={<CloseOutlined />}
        className="absolute top-4 right-4 text-gray-400 hover:text-white z-10"
        onClick={togglePlayerDetails}
      />

      {/* Header Profile */}
      <div className="p-8 pb-6 border-b border-white/5 bg-gradient-to-b from-mystic-accent/10 to-transparent">
        <div className="w-20 h-20 rounded-full border-2 border-mystic-accent/30 flex items-center justify-center bg-black/40 mb-4 mx-auto shadow-glow-sm relative">
          {player.isAlive ? (
            <span className="text-3xl">👤</span>
          ) : (
            <span className="text-3xl grayscale opacity-50">💀</span>
          )}
          <div className="absolute -bottom-2 px-2 py-0.5 bg-black border border-white/20 rounded text-[10px] text-gray-300">
            NO.{player.position + 1}
          </div>
        </div>

        <h2 className="text-2xl font-serif text-white font-bold text-center mb-1">{player.name}</h2>
        <div className="flex justify-center gap-2 mb-4">
          <Tag color={player.isAlive ? '#3b82f6' : '#262626'} className="border-none m-0">
            {player.isAlive ? 'ALIVE' : 'ELIMINATED'}
          </Tag>
          <Tag color="purple" className="border-none m-0 bg-mystic-accent/20 text-mystic-accent">
            {player.role.name}
          </Tag>
        </div>
      </div>

      {/* Stats / AI Info */}
      <div className="p-6 grid grid-cols-2 gap-4 border-b border-white/5">
        <div className="bg-white/5 p-3 rounded-lg">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Model</div>
          <div className="text-xs text-blue-300 font-mono truncate" title={player.agent}>{player.agent}</div>
        </div>
        <div className="bg-white/5 p-3 rounded-lg">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Role Camp</div>
          <div className="text-xs text-gray-200 capitalize">{player.role.camp}</div>
        </div>
      </div>

      {/* Activity Log */}
      <div className="flex-1 overflow-hidden flex flex-col p-6">
        <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span className="w-1 h-1 bg-mystic-accent rounded-full"></span>
          Behavior Analysis
        </div>
        <div className="space-y-4 overflow-y-auto pr-2 custom-scrollbar flex-1">
          {playerEvents.length > 0 ? playerEvents.map((e, i) => (
            <div key={i} className="relative pl-4 border-l border-white/10 pb-4 last:pb-0">
              <div className="absolute -left-[5px] top-1.5 w-2.5 h-2.5 rounded-full bg-black border border-white/20"></div>
              <div className="text-[10px] text-gray-500 mb-1">{new Date(e.timestamp).toLocaleTimeString()}</div>
              <div className="text-sm text-gray-300 font-light leading-snug">
                {e.message.replace(player.name, 'Target')}
              </div>
            </div>
          )) : (
            <div className="text-center text-gray-600 text-xs py-10 italic">No activity recorded yet</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PlayerDetailsPanel