import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Player } from '../../types/game'

interface PlayerDeathAnimationProps {
  player: Player
  trigger: boolean
  onComplete?: () => void
}

const PlayerDeathAnimation: React.FC<PlayerDeathAnimationProps> = ({
  player,
  trigger,
  onComplete
}) => {
  if (!trigger) return null

  return (
    <AnimatePresence onExitComplete={onComplete}>
      <motion.div
        key={`death-${player.id}`}
        className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* 死亡特效背景 */}
        <motion.div
          className="absolute inset-0 bg-red-900/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        />

        {/* 中心动画 */}
        <motion.div
          className="relative"
          initial={{ scale: 0, rotate: 0 }}
          animate={{
            scale: [0, 1.2, 0.8],
            rotate: [0, 180, 360]
          }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{
            duration: 1.2,
            times: [0, 0.6, 1],
            type: 'spring',
            stiffness: 60,
            damping: 15
          }}
        >
          {/* 死亡图标 */}
          <motion.div
            className="relative w-32 h-32 rounded-full bg-red-600/20 border-4 border-red-500/50 flex items-center justify-center"
            animate={{
              boxShadow: [
                '0 0 20px rgba(239, 68, 68, 0.5)',
                '0 0 40px rgba(239, 68, 68, 0.8)',
                '0 0 60px rgba(239, 68, 68, 0.4)'
              ]
            }}
            transition={{ duration: 1, repeat: 2 }}
          >
            <span className="text-4xl">💀</span>

            {/* 内部漩涡效果 */}
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-red-400/30"
              animate={{ rotate: 360 }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear'
              }}
            />

            <motion.div
              className="absolute inset-2 rounded-full border border-red-300/20"
              animate={{ rotate: -360 }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'linear'
              }}
            />
          </motion.div>

          {/* 爆炸粒子效果 */}
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(8)].map((_, i) => {
              const angle = (i * 45) * Math.PI / 180
              const distance = 100

              return (
                <motion.div
                  key={`particle-${i}`}
                  className="absolute w-2 h-2 bg-red-500 rounded-full"
                  style={{
                    left: '50%',
                    top: '50%',
                    marginLeft: '-4px',
                    marginTop: '-4px'
                  }}
                  initial={{
                    x: 0,
                    y: 0,
                    opacity: 1,
                    scale: 0
                  }}
                  animate={{
                    x: Math.cos(angle) * distance,
                    y: Math.sin(angle) * distance,
                    opacity: 0,
                    scale: [0, 1, 0]
                  }}
                  transition={{
                    duration: 1,
                    delay: i * 0.05,
                    type: 'tween',
                    ease: 'easeOut'
                  }}
                />
              )
            })}
          </div>
        </motion.div>

        {/* 警告文字 */}
        <motion.div
          className="absolute -bottom-20 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ delay: 0.3 }}
        >
          <motion.h2
            className="text-2xl font-bold text-red-400 mb-2"
            animate={{
              color: ['#ef4444', '#dc2626', '#991b1b', '#dc2626', '#ef4444'],
              textShadow: [
                '0 0 10px rgba(239, 68, 68, 0.8)',
                '0 0 20px rgba(239, 68, 68, 1)',
                '0 0 30px rgba(239, 68, 68, 1.2)',
                '0 0 20px rgba(239, 68, 68, 1)',
                '0 0 10px rgba(239, 68, 68, 0.8)'
              ]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatType: 'reverse'
            }}
          >
            玩家死亡
          </motion.h2>

          <motion.p
            className="text-lg text-gray-300"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {player.name} 被淘汰了
          </motion.p>

          {/* 死亡原因 */}
          {player.role && (
            <motion.p
              className="text-sm text-gray-400 mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              身份: {player.role.name}
            </motion.p>
          )}
        </motion.div>

        {/* 屏幕震动效果 */}
        <motion.div
          className="fixed inset-0 pointer-events-none"
          animate={{
            x: [0, -5, 5, -3, 3, -2, 2, 0],
            y: [0, -3, 3, -2, 2, -1, 1, 0]
          }}
          transition={{
            duration: 0.5,
            type: 'tween',
            ease: 'easeOut'
          }}
        />
      </motion.div>
    </AnimatePresence>
  )
}

export default PlayerDeathAnimation