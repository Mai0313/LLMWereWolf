import React from 'react'
import { usePlayers, useGameEvents, useGameState } from '@store/gameStore'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from 'recharts'
import { CloseOutlined } from '@ant-design/icons'
import { Button } from 'antd'
import { useGameStore } from '@store/gameStore'

const COLORS = {
  werewolf: '#ef4444',
  villager: '#3b82f6',
  neutral: '#9ca3af'
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-black/90 border border-white/20 p-2 text-xs text-white uppercase tracking-widest shadow-xl rounded">
        {`${payload[0].name} : ${payload[0].value}`}
      </div>
    );
  }
  return null;
};

const StatCard: React.FC<{ title: string; value: string | number; sub?: string }> = ({ title, value, sub }) => (
  <div className="bg-white/5 border border-white/5 p-4 rounded-xl flex flex-col items-center justify-center relative overflow-hidden group hover:bg-white/10 transition-colors">
    <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 z-10">{title}</div>
    <div className="text-3xl font-serif font-bold text-white z-10">{value}</div>
    {sub && <div className="text-[10px] text-mystic-accent z-10 mt-1">{sub}</div>}
  </div>
)

const StatisticsPanel: React.FC = () => {
  const players = usePlayers()
  const events = useGameEvents()
  const gameState = useGameState()
  const { toggleStatistics } = useGameStore()

  // 数据计算
  const alive = players.filter(p => p.isAlive).length
  const werewolfCount = players.filter(p => p.isAlive && p.role.camp === 'werewolf').length
  const villagerCount = players.filter(p => p.isAlive && p.role.camp === 'villager').length

  const chartData = [
    { name: 'Werewolf', value: werewolfCount },
    { name: 'Villager', value: villagerCount },
    { name: 'Neutral', value: players.filter(p => p.isAlive && p.role.camp === 'neutral').length }
  ]

  // 活跃度数据
  const activityData = players.map(p => ({
    name: p.name,
    count: events.filter(e => e.message.includes(p.name)).length,
  })).sort((a, b) => b.count - a.count).slice(0, 5)

  return (
    <div className="h-full flex flex-col text-white p-6 md:p-10 relative overflow-y-auto custom-scrollbar">
      {/* 关闭按钮 */}
      <Button
        type="text"
        icon={<CloseOutlined />}
        onClick={toggleStatistics}
        className="absolute top-6 right-6 text-gray-400 hover:text-white z-50"
      />

      <div className="mb-8">
        <h1 className="text-3xl font-serif text-white tracking-[0.2em] uppercase mb-1">Analysis Protocol</h1>
        <div className="text-xs text-gray-500 uppercase tracking-widest">
          Session Data • Round {gameState?.round}
        </div>
      </div>

      {/* 顶部概览卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Souls" value={players.length} />
        <StatCard title="Survivors" value={alive} sub={`${((alive / players.length) * 100).toFixed(0)}% Alive`} />
        <StatCard title="Events Logged" value={events.length} />
        <StatCard title="Current Phase" value={gameState?.phaseName || 'Unknown'} />
      </div>

      <div className="grid grid-cols-1 gap-8">
        {/* 阵营平衡 */}
        <div className="bg-black/40 p-6 rounded-2xl border border-white/5">
          <h3 className="text-sm font-serif text-gray-300 mb-6 uppercase tracking-widest border-b border-white/5 pb-2">
            Faction Balance
          </h3>
          <div className="flex flex-col md:flex-row items-center justify-around h-64">
            <div className="w-full h-full md:w-1/2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? COLORS.werewolf : index === 1 ? COLORS.villager : COLORS.neutral} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-4 w-full md:w-auto mt-4 md:mt-0">
              {chartData.map((d, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: i === 0 ? COLORS.werewolf : i === 1 ? COLORS.villager : COLORS.neutral }} />
                  <div>
                    <div className="text-sm font-medium">{d.name}</div>
                    <div className="text-xs text-gray-500">{d.value} remaining</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 活跃度排行 */}
        <div className="bg-black/40 p-6 rounded-2xl border border-white/5">
          <h3 className="text-sm font-serif text-gray-300 mb-6 uppercase tracking-widest border-b border-white/5 pb-2">
            Most Active Subjects
          </h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activityData} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" hide />
                <YAxis
                  dataKey="name"
                  type="category"
                  width={100}
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={10} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatisticsPanel