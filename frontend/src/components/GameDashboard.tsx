import React from 'react'
import { Card, Row, Col, Statistic, Progress, Tag, Button, Space, Tooltip } from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  ReloadOutlined,
  ForwardOutlined
} from '@ant-design/icons'
import { motion } from 'framer-motion'
import { useGameState, usePlayers } from '@store/gameStore'
import { GamePhase } from '../../types/game'

const GameDashboard: React.FC = () => {
  const gameState = useGameState()
  const players = usePlayers()

  if (!gameState) return null

  const alivePlayers = players.filter(p => p.isAlive)
  const deadPlayers = players.filter(p => !p.isAlive)

  const werewolfCount = alivePlayers.filter(p => p.role.camp === 'werewolf').length
  const villagerCount = alivePlayers.filter(p => p.role.camp === 'villager').length
  const neutralCount = alivePlayers.filter(p => p.role.camp === 'neutral').length

  const getPhaseIcon = (phase: GamePhase) => {
    switch (phase) {
      case 'night': return '🌙'
      case 'day_discussion': return '☀️'
      case 'day_voting': return '🗳️'
      case 'ended': return '🏆'
      default: return '⏳'
    }
  }

  const getPhaseColor = (phase: GamePhase) => {
    switch (phase) {
      case 'night': return '#7c3aed'
      case 'day_discussion': return '#f59e0b'
      case 'day_voting': return '#ef4444'
      case 'ended': return '#10b981'
      default: return '#6b7280'
    }
  }

  const getGameProgress = () => {
    if (!gameState.startTime) return 0
    if (!gameState.endTime) {
      const elapsed = Date.now() - gameState.startTime.getTime()
      return Math.min((elapsed / (10 * 60 * 1000)) * 100, 100) // 假设标准游戏10分钟
    }
    return 100
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-6xl"
    >
      <Card
        size="small"
        className="shadow-lg"
        style={{
          background: 'rgba(30, 41, 59, 0.95)',
          backdropFilter: 'blur(10px)'
        }}
      >
        {/* 主要信息行 */}
        <Row gutter={[16, 16]}>
          {/* 游戏状态 */}
          <Col span={6}>
            <Statistic
              title="游戏状态"
              value={gameState.phaseName}
              prefix={getPhaseIcon(gameState.phase)}
              valueStyle={{
                color: getPhaseColor(gameState.phase)
              }}
            />
          </Col>

          {/* 当前回合 */}
          <Col span={6}>
            <Statistic
              title="当前回合"
              value={gameState.round}
              suffix="轮"
              prefix={<ClockCircleOutlined />}
            />
          </Col>

          {/* 存活玩家 */}
          <Col span={6}>
            <Statistic
              title="存活玩家"
              value={alivePlayers.length}
              suffix={`/ ${players.length}`}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#10b981' }}
            />
          </Col>

          {/* 游戏进度 */}
          <Col span={6}>
            <div>
              <div className="text-sm mb-2 opacity-75">游戏进度</div>
              <Progress
                percent={Math.round(getGameProgress())}
                strokeColor={{
                  '0%': '#10b981',
                  '50%': '#f59e0b',
                  '100%': '#ef4444',
                }}
                size="small"
                showInfo={false}
              />
              <div className="text-xs opacity-60 mt-1">
                {Math.round(getGameProgress())}%
              </div>
            </div>
          </Col>
        </Row>

        {/* 阵营统计 */}
        <Row gutter={[8, 8]} className="mt-4">
          <Col span={8}>
            <div className="text-center p-3 rounded-lg bg-red-900/20 border border-red-500/30">
              <div className="text-2xl mb-1">🐺</div>
              <div className="text-sm text-red-400">狼人阵营</div>
              <div className="text-2xl font-bold text-red-400">{werewolfCount}</div>
            </div>
          </Col>
          <Col span={8}>
            <div className="text-center p-3 rounded-lg bg-blue-900/20 border border-blue-500/30">
              <div className="text-2xl mb-1">👥</div>
              <div className="text-sm text-blue-400">村民阵营</div>
              <div className="text-2xl font-bold text-blue-400">{villagerCount}</div>
            </div>
          </Col>
          <Col span={8}>
            <div className="text-center p-3 rounded-lg bg-gray-700/20 border border-gray-500/30">
              <div className="text-2xl mb-1">⚖️</div>
              <div className="text-sm text-gray-400">中立角色</div>
              <div className="text-2xl font-bold text-gray-400">{neutralCount}</div>
            </div>
          </Col>
        </Row>

        {/* 控制按钮 */}
        <Row className="mt-4">
          <Col span={24}>
            <Space>
              <Tooltip title={gameState.isRunning ? "暂停游戏" : "继续游戏"}>
                <Button
                  type={gameState.isRunning ? "default" : "primary"}
                  icon={gameState.isRunning ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                  size="small"
                >
                  {gameState.isRunning ? "暂停" : "继续"}
                </Button>
              </Tooltip>

              <Tooltip title="快进到下一阶段">
                <Button
                  icon={<ForwardOutlined />}
                  size="small"
                >
                  快进
                </Button>
              </Tooltip>

              <Tooltip title="重新开始游戏">
                <Button
                  icon={<ReloadOutlined />}
                  size="small"
                  danger
                >
                  重新开始
                </Button>
              </Tooltip>

              {/* 阶段标签 */}
              <Tag
                color={getPhaseColor(gameState.phase)}
                className="ml-auto"
              >
                {getPhaseIcon(gameState.phase)} {gameState.phaseName}
              </Tag>
            </Space>
          </Col>
        </Row>

        {/* 游戏结束信息 */}
        {gameState.phase === 'ended' && gameState.winner && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-4 text-center p-4 rounded-lg bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border border-yellow-500/30"
          >
            <div className="flex items-center justify-center space-x-2">
              <TrophyOutlined className="text-2xl text-yellow-400" />
              <span className="text-xl font-bold text-yellow-400">
                {gameState.winner === 'werewolf' ? '狼人' : gameState.winner === 'villager' ? '村民' : '中立'} 阵营获胜！
              </span>
              <TrophyOutlined className="text-2xl text-yellow-400" />
            </div>
          </motion.div>
        )}
      </Card>
    </motion.div>
  )
}

export default GameDashboard