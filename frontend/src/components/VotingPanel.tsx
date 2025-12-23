import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useGameState, usePlayers } from '@store/gameStore'
import { Vote } from '@/types/game'

const VotingPanel: React.FC = () => {
  const gameState = useGameState()
  const players = usePlayers()
  const votingData = useVotingData()
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null)
  const [hasVoted, setHasVoted] = useState(false)
  const [timeLeft, setTimeLeft] = useState(30)

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(prev => prev - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [timeLeft])

  const voteCounts = votingData.reduce((acc: Record<string, number>, vote: Vote) => {
    acc[vote.targetId] = (acc[vote.targetId] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const handleVote = (targetId: string) => {
    if (hasVoted) return
    if (!gameState) return null
    const newVote: Vote = {
      voterId: 'current-user',
      targetId,
      round: gameState.round,
      phase: gameState.phase,
      timestamp: new Date()
    }
    setVotingData([...votingData, newVote])
    setSelectedTarget(targetId)
    setHasVoted(true)
  }

  // 排序：存活优先 -> 票数高优先
  const candidates = players
    .filter(p => p.isAlive)
    .sort((a, b) => (voteCounts[b.id] || 0) - (voteCounts[a.id] || 0))

  return (
    <div className="w-full bg-black/80 backdrop-blur-2xl border border-mystic-accent/30 rounded-2xl overflow-hidden shadow-2xl p-6">
      {/* Header */}
      <div className="flex justify-between items-end mb-6 border-b border-white/10 pb-4">
        <div>
          <h2 className="text-xl font-serif text-white tracking-widest flex items-center gap-2">
            <span className="text-mystic-gold">⚖️</span> JUDGEMENT
          </h2>
          <div className="text-xs text-gray-500 mt-1 uppercase tracking-wider">Cast your vote to exile a suspect</div>
        </div>
        <div className="text-right">
          <div className={`text-4xl font-serif font-bold ${timeLeft < 10 ? 'text-red-500 animate-pulse' : 'text-white'}`}>
            {timeLeft}s
          </div>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 max-h-[250px] overflow-y-auto custom-scrollbar p-1">
        {candidates.map(player => {
          const votes = voteCounts[player.id] || 0
          const isSelected = selectedTarget === player.id

          return (
            <motion.div
              key={player.id}
              whileHover={!hasVoted ? { scale: 1.02, y: -2 } : {}}
              whileTap={!hasVoted ? { scale: 0.98 } : {}}
              onClick={() => handleVote(player.id)}
              className={`
                relative p-3 rounded-xl border transition-all duration-300 cursor-pointer overflow-hidden
                flex flex-col items-center justify-center gap-2
                ${isSelected
                  ? 'border-mystic-gold bg-mystic-gold/10 shadow-[0_0_15px_rgba(251,191,36,0.2)]'
                  : 'border-white/5 bg-white/5 hover:bg-white/10 hover:border-white/20'}
                ${hasVoted && !isSelected ? 'opacity-30 grayscale' : 'opacity-100'}
              `}
            >
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold border
                ${isSelected ? 'border-mystic-gold text-mystic-gold' : 'border-white/20 text-gray-400'}
              `}>
                {player.position + 1}
              </div>

              <div className="text-sm font-medium text-white truncate w-full text-center">
                {player.name}
              </div>

              {/* 票数指示器 */}
              {votes > 0 && (
                <div className="absolute top-2 right-2 bg-mystic-accent text-white text-[10px] px-1.5 py-0.5 rounded font-bold shadow-sm">
                  {votes}
                </div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Status Footer */}
      {hasVoted && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 text-center p-3 bg-mystic-gold/10 border border-mystic-gold/20 rounded-lg text-mystic-gold text-xs tracking-widest uppercase font-bold"
        >
          Vote Confirmed • Fate Sealed
        </motion.div>
      )}
    </div>
  )
}

export default VotingPanel