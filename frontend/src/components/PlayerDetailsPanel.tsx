import React from 'react'
import { Card, Tag, Avatar, Statistic, Row, Col, Timeline, Divider } from 'antd'
import {
  UserOutlined,
  CrownOutlined,
  HeartOutlined,
  EyeOutlined,
  MessageOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import { Player } from '../../types/game'
import { useGameEvents } from '@store/gameStore'

interface PlayerDetailsPanelProps {
  player: Player
}

const PlayerDetailsPanel: React.FC<PlayerDetailsPanelProps> = ({ player }) => {
  const events = useGameEvents()

  // 获取与玩家相关的事件
  const playerEvents = events.filter(event =>
    event.message.includes(player.name) ||
    event.actorId === player.id ||
    event.targetId === player.id
  ).slice(-10) // 最近10个事件

  // 统计数据
  const discussionEvents = playerEvents.filter(e => e.type === 'DISCUSSION').length
  const voteEvents = playerEvents.filter(e => e.type === 'VOTING').length
  const actionEvents = playerEvents.filter(e => e.type === 'ROLE_ACTION').length

  const getStatusColor = (player: Player) => {
    if (!player.isAlive) return 'default'
    if (player.status === 'protected') return 'blue'
    if (player.status === 'poisoned') return 'purple'
    if (player.status === 'charmed') return 'magenta'
    return 'green'
  }

  const getStatusText = (player: Player) => {
    if (!player.isAlive) return '已淘汰'
    if (player.status === 'protected') return '被保护'
    if (player.status === 'poisoned') return '中毒'
    if (player.status === 'charmed') return '被魅惑'
    return '存活'
  }

  const getFactionColor = (faction: string) => {
    switch (faction) {
      case 'werewolf': return 'red'
      case 'villager': return 'blue'
      case 'neutral': return 'default'
      default: return 'default'
    }
  }

  const getFactionText = (faction: string) => {
    switch (faction) {
      case 'werewolf': return '狼人阵营'
      case 'villager': return '村民阵营'
      case 'neutral': return '中立阵营'
      default: return '未知阵营'
    }
  }

  return (
    <div className="space-y-4">
      {/* 玩家基本信息 */}
      <Card size="small" title="玩家信息">
        <div className="flex items-center space-x-4 mb-4">
          <Avatar
            size={64}
            icon={<UserOutlined />}
            className={
              `border-4 ${
                getStatusColor(player) === 'default' ? 'border-gray-400' :
                getStatusColor(player) === 'blue' ? 'border-blue-400' :
                getStatusColor(player) === 'purple' ? 'border-purple-400' :
                getStatusColor(player) === 'magenta' ? 'border-pink-400' :
                'border-green-400'
              }`
            }
            style={{
              backgroundColor: player.isAlive ?
                (player.role.camp === 'werewolf' ? '#dc2626' : '#1e40af') :
                '#6b7280'
            }}
          />

          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-bold">{player.name}</h3>
              {player.sheriff && <CrownOutlined className="text-yellow-400" />}
            </div>

            <div className="space-y-1">
              <Tag color={getFactionColor(player.role.camp)}>
                {getFactionText(player.role.camp)}
              </Tag>
              <Tag color={getStatusColor(player)}>
                {getStatusText(player)}
              </Tag>
            </div>

            {!player.isAlive && (
              <div className="text-sm opacity-60">
                身份: {player.role.name}
              </div>
            )}
          </div>
        </div>

        {/* 详细状态 */}
        <Row gutter={[8, 8]}>
          <Col span={12}>
            <Statistic
              title="状态"
              value={getStatusText(player)}
              valueStyle={{
                color: getStatusColor(player) === 'default' ? '#9ca3af' :
                       getStatusColor(player) === 'blue' ? '#3b82f6' :
                       getStatusColor(player) === 'purple' ? '#8b5cf6' :
                       getStatusColor(player) === 'magenta' ? '#ec4899' :
                       '#10b981'
              }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="位置"
              value={`位置 ${player.position + 1}`}
              prefix={<ClockCircleOutlined />}
            />
          </Col>
        </Row>
      </Card>

      {/* 角色信息 */}
      <Card size="small" title="角色信息">
        <div className="space-y-3">
          <div>
            <div className="text-sm opacity-60">角色名称</div>
            <div className="font-medium">{player.role.name}</div>
          </div>
          <div>
            <div className="text-sm opacity-60">角色描述</div>
            <div className="text-sm">{player.role.description}</div>
          </div>
          <div>
            <div className="text-sm opacity-60">行动优先级</div>
            <div className="font-medium">{player.role.priority}</div>
          </div>
          <div>
            <div className="text-sm opacity-60">AI 模型</div>
            <div className="text-sm">{player.agent}</div>
          </div>
        </div>
      </Card>

      {/* 活动统计 */}
      <Card size="small" title="活动统计">
        <Row gutter={[16, 16]}>
          <Col span={8}>
            <Statistic
              title="发言次数"
              value={discussionEvents}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#f59e0b' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="投票次数"
              value={voteEvents}
              prefix={<VoteOutlined />}
              valueStyle={{ color: '#ef4444' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="技能使用"
              value={actionEvents}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#3b82f6' }}
            />
          </Col>
        </Row>
      </Card>

      {/* 特殊状态 */}
      {(player.status !== 'alive' || player.lovers?.length || player.sheriff) && (
        <Card size="small" title="特殊状态">
          <div className="space-y-2">
            {!player.isAlive && (
              <div className="flex items-center space-x-2">
                <HeartOutlined className="text-red-400" />
                <span>已被淘汰</span>
              </div>
            )}

            {player.status === 'protected' && (
              <div className="flex items-center space-x-2">
                <ShieldCheckOutlined className="text-blue-400" />
                <span>被守卫保护</span>
              </div>
            )}

            {player.status === 'poisoned' && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-purple-400" />
                <span>中了女巫毒药</span>
              </div>
            )}

            {player.status === 'charmed' && (
              <div className="flex items-center space-x-2">
                <HeartOutlined className="text-pink-400" />
                <span>被狼美人魅惑</span>
              </div>
            )}

            {player.sheriff && (
              <div className="flex items-center space-x-2">
                <CrownOutlined className="text-yellow-400" />
                <span>当前警长</span>
              </div>
            )}

            {player.lovers && player.lovers.length > 0 && (
              <div className="flex items-center space-x-2">
                <HeartOutlined className="text-pink-400" />
                <span>有情侣关系</span>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* 最近事件 */}
      <Card size="small" title={`最近事件 (${playerEvents.length})`}>
        <div className="max-h-64 overflow-y-auto">
          <Timeline mode="left" size="small">
            {playerEvents.map((event, index) => (
              <Timeline.Item
                key={`${event.id}-${index}`}
                color={
                  event.type === 'PLAYER_DIED' ? 'red' :
                  event.type === 'ROLE_ACTION' ? 'blue' :
                  event.type === 'DISCUSSION' ? 'gold' :
                  event.type === 'VOTING' ? 'orange' :
                  'gray'
                }
              >
                <div className="text-sm">
                  <div className="opacity-60 text-xs mb-1">
                    第{event.round}轮 • {event.phase}
                  </div>
                  <div>{event.message}</div>
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        </div>
      </Card>
    </div>
  )
}

export default PlayerDetailsPanel