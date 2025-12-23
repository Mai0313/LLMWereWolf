import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Progress, Button, Tag, Divider, Avatar, Statistic } from 'antd'
import { motion, AnimatePresence } from 'framer-motion'
import { UserOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { useGameState, usePlayers, useVotingData, setVotingData } from '@store/gameStore'
import { Vote } from '../../types/game'

interface VotingPlayerProps {
  player: any
  isTarget: boolean
  voteCount: number
  onVote: (playerId: string) => void
  disabled?: boolean
}

const VotingPlayer: React.FC<VotingPlayerProps> = ({
  player,
  isTarget,
  voteCount,
  onVote,
  disabled = false
}) => {
  const totalVotes = 16 // 这里应该从游戏状态获取总数
  const votePercentage = totalVotes > 0 ? (voteCount / totalVotes) * 100 : 0

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={disabled ? 'opacity-50' : ''}
    >
      <Card
        size="small"
        className={`cursor-pointer transition-all duration-200 ${
          isTarget ? 'border-2 border-blue-400' : 'border-gray-600'
        }`}
        style={{
          background: isTarget ? 'rgba(59, 130, 246, 0.1)' : 'rgba(30, 41, 59, 0.8)'
        }}
        onClick={() => !disabled && onVote(player.id)}
      >
        <div className="flex items-center space-x-3">
          <Avatar
            size="large"
            icon={<UserOutlined />}
            className={`${player.isAlive ? 'border-green-400' : 'border-gray-400'}`}
          />
          <div className="flex-1">
            <div className="font-medium">{player.name}</div>
            {player.isAlive ? (
              <Tag color="green" size="small">存活</Tag>
            ) : (
              <Tag color="default" size="small">已淘汰</Tag>
            )}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{voteCount}</div>
            <div className="text-xs opacity-60">票</div>
          </div>
        </div>

        {/* 投票进度条 */}
        <div className="mt-3">
          <Progress
            percent={votePercentage}
            strokeColor={
              isTarget ? '#3b82f6' :
              votePercentage > 50 ? '#ef4444' :
              votePercentage > 25 ? '#f59e0b' : '#10b981'
            }
            size="small"
            showInfo={false}
          />
        </div>
      </Card>
    </motion.div>
  )
}

const VotingPanel: React.FC = () => {
  const gameState = useGameState()
  const players = usePlayers()
  const votingData = useVotingData()
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null)
  const [hasVoted, setHasVoted] = useState(false)
  const [timeRemaining, setTimeRemaining] = useState(30)

  // 模拟投票倒计时
  useEffect(() => {
    if (timeRemaining > 0 && gameState.phase === 'day_voting') {
      const timer = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [timeRemaining, gameState.phase])

  // 计算每个玩家的投票数
  const voteCounts = votingData.reduce((acc, vote) => {
    acc[vote.targetId] = (acc[vote.targetId] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // 按投票数排序的玩家列表
  const sortedPlayers = [...players]
    .filter(p => p.isAlive) // 只显示存活玩家
    .sort((a, b) => (voteCounts[b.id] || 0) - (voteCounts[a.id] || 0))

  // 处理投票
  const handleVote = (targetId: string) => {
    if (hasVoted) return

    // 模拟投票
    const newVote: Vote = {
      voterId: 'current-user', // 应该从用户状态获取
      targetId,
      round: gameState.round,
      phase: gameState.phase,
      timestamp: new Date()
    }

    setVotingData([...votingData, newVote])
    setSelectedTarget(targetId)
    setHasVoted(true)
  }

  // 获取领先者
  const getLeadingPlayer = () => {
    if (sortedPlayers.length === 0) return null
    const maxVotes = Math.max(...sortedPlayers.map(p => voteCounts[p.id] || 0))
    return sortedPlayers.find(p => voteCounts[p.id] === maxVotes)
  }

  const leadingPlayer = getLeadingPlayer()

  if (gameState.phase !== 'day_voting') {
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      className="w-full max-w-6xl mx-auto"
    >
      <Card
        className="shadow-2xl"
        style={{
          background: 'rgba(30, 41, 59, 0.95)',
          backdropFilter: 'blur(10px)'
        }}
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <VoteOutlined className="text-orange-400" />
              <span>投票阶段</span>
              <Tag color="orange">{votingData.length} 票已投</Tag>
            </div>
            <div className="flex items-center space-x-2">
              <ClockCircleOutlined />
              <span className={timeRemaining <= 10 ? 'text-red-400' : ''}>
                {timeRemaining}s
              </span>
            </div>
          </div>
        }
      >
        {/* 投票统计 */}
        <Row gutter={[16, 16]} className="mb-4">
          <Col span={6}>
            <Statistic
              title="参与人数"
              value={players.filter(p => p.isAlive).length}
              suffix={`/ ${players.length}`}
              prefix={<UserOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="已投票数"
              value={votingData.length}
              prefix={<VoteOutlined />}
              valueStyle={{ color: '#f59e0b' }}
            />
          </Col>
          <Col span={12}>
            <div>
              <div className="text-sm mb-2 opacity-75">投票进度</div>
              <Progress
                percent={Math.round((votingData.length / players.filter(p => p.isAlive).length) * 100)}
                strokeColor="#f59e0b"
                size="small"
              />
            </div>
          </Col>
        </Row>

        <Divider />

        {/* 投票选项 */}
        <Row gutter={[12, 12]}>
          {sortedPlayers.map((player, index) => (
            <Col xs={24} sm={12} md={8} lg={6} key={player.id}>
              <VotingPlayer
                player={player}
                isTarget={selectedTarget === player.id}
                voteCount={voteCounts[player.id] || 0}
                onVote={handleVote}
                disabled={hasVoted || !player.isAlive}
              />
            </Col>
          ))}
        </Row>

        {/* 当前领先者提示 */}
        {leadingPlayer && voteCounts[leadingPlayer.id] > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 text-center p-3 rounded-lg bg-blue-900/20 border border-blue-500/30"
          >
            <div className="text-sm text-blue-400">
              当前领先: <strong>{leadingPlayer.name}</strong> ({voteCounts[leadingPlayer.id]} 票)
            </div>
          </motion.div>
        )}

        {/* 用户投票状态 */}
        {hasVoted && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-4 text-center p-3 rounded-lg bg-green-900/20 border border-green-500/30"
          >
            <div className="text-sm text-green-400">
              ✅ 你已投票给 <strong>{players.find(p => p.id === selectedTarget)?.name}</strong>
            </div>
          </motion.div>
        )}
      </Card>
    </motion.div>
  )
}

export default VotingPanel