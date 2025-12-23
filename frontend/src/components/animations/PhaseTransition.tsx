import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GamePhase } from '../../types/game'

interface PhaseTransitionProps {
  from: GamePhase
  to: GamePhase
  onComplete?: () => void
}

const phaseConfig = {
  night: {
    icon: '🌙',
    title: '黑夜阶段',
    description: '狼人行动时间',
    color: '#7c3aed',
    bgColor: 'from-purple-900/20 to-indigo-900/20'
  },
  day_discussion: {
    icon: '☀️',
    title: '白天讨论',
    description: '所有人讨论推理',
    color: '#f59e0b',
    bgColor: 'from-yellow-900/20 to-orange-900/20'
  },
  day_voting: {
    icon: '🗳️',
    title: '投票阶段',
    description: '投票淘汰可疑玩家',
    color: '#ef4444',
    bgColor: 'from-red-900/20 to-rose-900/20'
  },
  waiting: {
    icon: '⏳',
    title: '等待开始',
    description: '游戏准备中',
    color: '#6b7280',
    bgColor: 'from-gray-900/20 to-slate-900/20'
  },
  ended: {
    icon: '🏆',
    title: '游戏结束',
    description: '查看最终结果',
    color: '#10b981',
    bgColor: 'from-green-900/20 to-emerald-900/20'
  }
}

const PhaseTransition: React.FC<PhaseTransitionProps> = ({ from, to, onComplete }) => {
  const toConfig = phaseConfig[to] || phaseConfig.waiting

  return (
    <AnimatePresence onExitComplete={onComplete}>
      <motion.div
        key={`phase-${to}`}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <motion.div
          className={`relative p-8 rounded-2xl bg-gradient-to-br ${toConfig.bgColor} border border-white/10 backdrop-blur-lg shadow-2xl`}
          initial={{ scale: 0.8, y: 50, opacity: 0 }}
          animate={{ scale: 1, y: 0, opacity: 1 }}
          exit={{ scale: 0.8, y: 50, opacity: 0 }}
          transition={{
            duration: 0.5,
            type: 'spring',
            stiffness: 200,
            damping: 20
          }}
          style={{ minWidth: '350px' }}
        >
          {/* 背景动画 */}
          <motion.div
            className="absolute inset-0 rounded-2xl"
            style={{
              background: `
                radial-gradient(circle at 20% 50%, ${toConfig.color}20 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, ${toConfig.color}20 0%, transparent 50%)
              `
            }}
            animate={{
              opacity: [0.5, 0.8, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatType: 'reverse'
            }}
          />

          {/* 主要内容 */}
          <div className="relative flex flex-col items-center text-center space-y-4">
            {/* 图标动画 */}
            <motion.div
              className="text-6xl"
              initial={{ rotate: 0, scale: 0 }}
              animate={{ rotate: 360, scale: 1 }}
              transition={{
                duration: 0.8,
                delay: 0.2,
                type: 'spring',
                stiffness: 100
              }}
            >
              {toConfig.icon}
            </motion.div>

            {/* 标题 */}
            <motion.h2
              className="text-2xl font-bold"
              style={{ color: toConfig.color }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              {toConfig.title}
            </motion.h2>

            {/* 描述 */}
            <motion.p
              className="text-gray-300 opacity-80"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              {toConfig.description}
            </motion.p>

            {/* 装饰性动画 */}
            <motion.div
              className="flex space-x-2 mt-4"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.8 }}
            >
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: toConfig.color }}
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.2
                  }}
                />
              ))}
            </motion.div>
          </div>

          {/* 边框光效 */}
          <motion.div
            className="absolute inset-0 rounded-2xl pointer-events-none"
            style={{
              border: `2px solid ${toConfig.color}`,
              opacity: 0.3
            }}
            animate={{
              scale: [1, 1.05, 1],
              opacity: [0.3, 0.6, 0.3]
            }}
            transition={{
              duration: 2,
              repeat: Infinity
            }}
          />
        </motion.div>

        {/* 延迟消失的提示 */}
        <motion.div
          className="absolute bottom-8 text-white/60 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <motion.div
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            点击任意位置继续...
          </motion.div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default PhaseTransition