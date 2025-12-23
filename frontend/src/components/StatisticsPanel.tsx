import React from 'react'
import { Card, Row, Col, Statistic, Table, Tag } from 'antd'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts'
import {
  UserOutlined,
  MessageOutlined,
  VoteOutlined,
  ThunderboltOutlined,
  TrophyOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import { usePlayers, useGameState, useGameEvents } from '@store/gameStore'

const COLORS = {
  werewolf: '#dc2626',
  villager: '#1e40af',
  neutral: '#6b7280'
}

const StatisticsPanel: React.FC = () => {
  const players = usePlayers()
  const gameState = useGameState()
  const events = useGameEvents()

  // 基础统计数据
  const alivePlayers = players.filter(p => p.isAlive)
  const deadPlayers = players.filter(p => !p.isAlive)

  const factionData = [
    {
      name: '狼人',
      value: alivePlayers.filter(p => p.role.camp === 'werewolf').length,
      color: COLORS.werewolf,
      totalDead: deadPlayers.filter(p => p.role.camp === 'werewolf').length
    },
    {
      name: '村民',
      value: alivePlayers.filter(p => p.role.camp === 'villager').length,
      color: COLORS.villager,
      totalDead: deadPlayers.filter(p => p.role.camp === 'villager').length
    },
    {
      name: '中立',
      value: alivePlayers.filter(p => p.role.camp === 'neutral').length,
      color: COLORS.neutral,
      totalDead: deadPlayers.filter(p => p.role.camp === 'neutral').length
    }
  ]

  // 玩家活跃度统计
  const playerActivityData = players.map(player => {
    const playerEvents = events.filter(e =>
      e.message.includes(player.name) || e.actorId === player.id
    )

    const discussionEvents = playerEvents.filter(e => e.type === 'DISCUSSION').length
    const voteEvents = playerEvents.filter(e => e.type === 'VOTING').length
    const actionEvents = playerEvents.filter(e => e.type === 'ROLE_ACTION').length

    return {
      name: player.name,
      alive: player.isAlive,
      discussion: discussionEvents,
      voting: voteEvents,
      actions: actionEvents,
      total: discussionEvents + voteEvents + actionEvents
    }
  }).sort((a, b) => b.total - a.total)

  // 时间线数据（模拟）
  const timelineData = Array.from({ length: gameState.round + 1 }, (_, i) => ({
    round: i,
    werewolf: Math.max(0, players.filter(p => p.role.camp === 'werewolf').length - i),
    villager: Math.max(0, players.filter(p => p.role.camp === 'villager').length - Math.floor(i * 0.8))
  }))

  // 事件类型分布
  const eventTypeData = [
    { type: '讨论', count: events.filter(e => e.type === 'DISCUSSION').length, color: '#f59e0b' },
    { type: '投票', count: events.filter(e => e.type === 'VOTING').length, color: '#ef4444' },
    { type: '技能', count: events.filter(e => e.type === 'ROLE_ACTION').length, color: '#3b82f6' },
    { type: '死亡', count: events.filter(e => e.type === 'PLAYER_DIED').length, color: '#dc2626' }
  ]

  // 表格列定义
  const columns = [
    {
      title: '玩家',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <div className="flex items-center space-x-2">
          <span>{name}</span>
          {!record.alive && <Tag color="default">已淘汰</Tag>}
        </div>
      )
    },
    {
      title: '发言次数',
      dataIndex: 'discussion',
      key: 'discussion',
      render: (count: number) => <span className="text-yellow-400">{count}</span>
    },
    {
      title: '投票次数',
      dataIndex: 'voting',
      key: 'voting',
      render: (count: number) => <span className="text-orange-400">{count}</span>
    },
    {
      title: '技能使用',
      dataIndex: 'actions',
      key: 'actions',
      render: (count: number) => <span className="text-blue-400">{count}</span>
    },
    {
      title: '总活跃度',
      dataIndex: 'total',
      key: 'total',
      render: (count: number) => (
        <span className="font-bold text-green-400">{count}</span>
      )
    }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* 概览统计 */}
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="存活玩家"
              value={alivePlayers.length}
              suffix={`/ ${players.length}`}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#10b981' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="总事件数"
              value={events.length}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#f59e0b' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="当前回合"
              value={gameState.round}
              suffix="轮"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#3b82f6' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          {gameState.phase === 'ended' && gameState.winner && (
            <Card size="small">
              <Statistic
                title="获胜阵营"
                value={gameState.winner === 'werewolf' ? '狼人' : gameState.winner === 'villager' ? '村民' : '中立'}
                prefix={<TrophyOutlined />}
                valueStyle={{
                  color: gameState.winner === 'werewolf' ? COLORS.werewolf :
                         gameState.winner === 'villager' ? COLORS.villager :
                         COLORS.neutral
                }}
              />
            </Card>
          )}
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]}>
        {/* 阵营分布饼图 */}
        <Col span={8}>
          <Card title="阵营分布" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={factionData.map(d => ({ name: d.name, value: d.value }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {factionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* 事件类型分布 */}
        <Col span={8}>
          <Card title="事件类型分布" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={eventTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#0ea5e9">
                  {eventTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* 人数变化趋势 */}
        <Col span={8}>
          <Card title="阵营人数变化" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="round" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="werewolf" stroke={COLORS.werewolf} name="狼人" />
                <Line type="monotone" dataKey="villager" stroke={COLORS.villager} name="村民" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 玩家活跃度分析 */}
      <Card title="玩家活跃度分析" size="small">
        <Table
          columns={columns}
          dataSource={playerActivityData}
          pagination={false}
          size="small"
          rowKey="name"
        />
      </Card>

      {/* 历史数据分析 */}
      {gameState.phase === 'ended' && (
        <Card title="游戏总结" size="small">
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <h4>死亡顺序分析</h4>
              <div className="space-y-2">
                {deadPlayers.map((player, index) => (
                  <div key={player.id} className="flex items-center space-x-2">
                    <span className="text-gray-400">第{index + 1}个:</span>
                    <span>{player.name}</span>
                    <Tag color={player.role.camp === 'werewolf' ? 'red' : 'blue'}>
                      {player.role.name}
                    </Tag>
                  </div>
                ))}
              </div>
            </Col>
            <Col span={12}>
              <h4>关键统计</h4>
              <div className="space-y-2 text-sm">
                <div>游戏持续时间: {gameState.round} 轮</div>
                <div>狼人击杀率: {((factionData[0].totalDead / players.length) * 100).toFixed(1)}%</div>
                <div>村民存活率: {((factionData[1].value / players.filter(p => p.role.camp === 'villager').length) * 100).toFixed(1)}%</div>
                <div>平均每轮事件: {(events.length / (gameState.round || 1)).toFixed(1)}</div>
              </div>
            </Col>
          </Row>
        </Card>
      )}
    </div>
  )
}

export default StatisticsPanel