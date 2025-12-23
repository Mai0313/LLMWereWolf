import { GamePhase, Role, Player, GameState, GameEvent, GameConfiguration, GameStatistics } from '../types/game'

// 模拟角色数据
const mockRoles: Role[] = [
  {
    id: 'werewolf',
    name: '狼人',
    camp: 'werewolf',
    description: '每晚可以选择击杀一名玩家',
    priority: 5,
    icon: '🐺'
  },
  {
    id: 'villager',
    name: '村民',
    camp: 'villager',
    description: '普通村民，没有特殊技能',
    priority: 999,
    icon: '👤'
  },
  {
    id: 'seer',
    name: '预言家',
    camp: 'villager',
    description: '每晚可以查验一名玩家的真实身份',
    priority: 6,
    icon: '🔮'
  },
  {
    id: 'witch',
    name: '女巫',
    camp: 'villager',
    description: '拥有一瓶解药和一瓶毒药',
    priority: 4,
    icon: '🧪'
  },
  {
    id: 'guard',
    name: '守卫',
    camp: 'villager',
    description: '每晚可以守护一名玩家免受狼人攻击',
    priority: 2,
    icon: '🛡️'
  },
  {
    id: 'hunter',
    name: '猎人',
    camp: 'villager',
    description: '死亡时可以开枪带走一名玩家',
    priority: 999,
    icon: '🏹'
  },
  {
    id: 'cupid',
    name: '丘比特',
    camp: 'neutral',
    description: '游戏开始时连接两名玩家成为情侣',
    priority: 0,
    icon: '💘'
  },
  {
    id: 'elder',
    name: '长老',
    camp: 'villager',
    description: '受到女巫毒药时不会死亡，但失去技能',
    priority: 999,
    icon: '👴'
  },
  {
    id: 'idiot',
    name: '白痴',
    camp: 'villager',
    description: '被投票出局时可以保留投票权',
    priority: 999,
    icon: '🤡'
  },
  {
    id: 'white_wolf',
    name: '白狼',
    camp: 'werewolf',
    description: '没有同伴的白狼，可以在白天自爆击杀一人',
    priority: 5,
    icon: '🐺‍⬛'
  },
  {
    id: 'alpha_wolf',
    name: '狼王',
    camp: 'werewolf',
    description: '狼人领袖，死亡时可以传递狼刀',
    priority: 5,
    icon: '👑'
  },
  {
    id: 'wolf_beauty',
    name: '狼美人',
    camp: 'werewolf',
    description: '每晚可以魅惑一名男性玩家',
    priority: 5,
    icon: '💋'
  }
]

// 生成模拟玩家
function generateMockPlayers(count: number): Player[] {
  const playerNames = [
    'DemoPlayer1', 'DemoPlayer2', 'DemoPlayer3', 'DemoPlayer4',
    'DemoPlayer5', 'DemoPlayer6', 'DemoPlayer7', 'DemoPlayer8',
    'DemoPlayer9', 'DemoPlayer10', 'DemoPlayer11', 'DemoPlayer12',
    'DemoPlayer13', 'DemoPlayer14', 'DemoPlayer15', 'DemoPlayer16',
    'DemoPlayer17', 'DemoPlayer18', 'DemoPlayer19', 'DemoPlayer20'
  ]

  const aiModels = ['gpt-4', 'claude-3', 'deepseek-chat', 'demo']

  // 简单的角色分配逻辑
  const roleDistribution = getRoleDistribution(count)

  return playerNames.slice(0, count).map((name, index) => ({
    id: `player_${index}`,
    name,
    role: roleDistribution[index],
    status: 'alive' as const,
    isAlive: index < count - 2, // 模拟前几个玩家已死
    position: index,
    agent: aiModels[index % aiModels.length],
    avatar: undefined,
    sheriff: index === 0, // 第一个玩家是警长
    lovers: index === 0 || index === 1 ? (index === 0 ? [`player_1`] : [`player_0`]) : undefined // 前两个是情侣
  }))
}

// 根据玩家数量分配角色
function getRoleDistribution(playerCount: number): Role[] {
  const roles: Role[] = []

  const roleTemplates = {
    6: { werewolf: 2, special: 2, villager: 2 },
    9: { werewolf: 3, special: 3, villager: 3 },
    12: { werewolf: 4, special: 4, villager: 4 },
    16: { werewolf: 5, special: 5, villager: 6 }
  }

  const template = roleTemplates[playerCount as keyof typeof roleTemplates] || roleTemplates[16]

  // 添加狼人
  for (let i = 0; i < template.werewolf; i++) {
    roles.push(mockRoles.find(r => r.id === 'werewolf') || mockRoles[0])
  }

  // 添加特殊角色
  const specialRoles = ['seer', 'witch', 'guard', 'hunter', 'cupid']
  for (let i = 0; i < Math.min(template.special, specialRoles.length); i++) {
    const role = mockRoles.find(r => r.id === specialRoles[i])
    if (role) roles.push(role)
  }

  // 填充村民
  while (roles.length < playerCount) {
    roles.push(mockRoles.find(r => r.id === 'villager') || mockRoles[1])
  }

  return roles.slice(0, playerCount)
}

// 生成模拟游戏事件
function generateMockEvents(): GameEvent[] {
  const eventTemplates = [
    {
      type: 'GAME_STARTED',
      message: '游戏开始！所有玩家请就坐。',
      phase: 'waiting' as GamePhase
    },
    {
      type: 'ROLE_ACTION',
      message: '狼人正在讨论击杀目标...',
      phase: 'night' as GamePhase
    },
    {
      type: 'ROLE_ACTION',
      message: '预言家正在查验玩家身份...',
      phase: 'night' as GamePhase
    },
    {
      type: 'ROLE_ACTION',
      message: '守卫正在守护目标玩家...',
      phase: 'night' as GamePhase
    },
    {
      type: 'POTION_USED',
      message: '女巫使用了解药/毒药...',
      phase: 'night' as GamePhase
    },
    {
      type: 'PLAYER_DIED',
      message: 'DemoPlayer7 被狼人击杀！',
      phase: 'night' as GamePhase,
      data: { target: 'DemoPlayer7', cause: 'werewolf_kill' }
    },
    {
      type: 'DAY_START',
      message: '天亮了，所有人请睁眼...',
      phase: 'day_discussion' as GamePhase
    },
    {
      type: 'DISCUSSION',
      message: 'DemoPlayer1: 我觉得昨天投票结果很可疑...',
      phase: 'day_discussion' as GamePhase
    },
    {
      type: 'DISCUSSION',
      message: 'DemoPlayer2: 我同意，我们需要重新分析。',
      phase: 'day_discussion' as GamePhase
    },
    {
      type: 'DISCUSSION',
      message: 'DemoPlayer3: 让我看看大家的发言pattern...',
      phase: 'day_discussion' as GamePhase
    },
    {
      type: 'VOTING_START',
      message: '投票开始！请选择要投票淘汰的玩家。',
      phase: 'day_voting' as GamePhase
    },
    {
      type: 'VOTING',
      message: 'DemoPlayer5 投票给 DemoPlayer8',
      phase: 'day_voting' as GamePhase
    },
    {
      type: 'PLAYER_ELIMINATED',
      message: 'DemoPlayer8 被投票淘汰！身份是：女巫',
      phase: 'day_voting' as GamePhase,
      data: { eliminated: 'DemoPlayer8', role: 'witch' }
    }
  ]

  return eventTemplates.map((template, index) => ({
    id: `event_${index}`,
    type: template.type,
    message: template.message,
    round: Math.floor(index / 5),
    phase: template.phase,
    timestamp: new Date(Date.now() - (eventTemplates.length - index) * 60000),
    data: template.data
  }))
}

// 生成模拟游戏状态
export function generateMockGame(): GameState {
  const playerCount = 16
  const players = generateMockPlayers(playerCount)
  const events = generateMockEvents()

  const gameConfig: GameConfiguration = {
    id: 'mock_game_1',
    name: 'Demo Game',
    playerCount,
    roles: players.map(p => p.role),
    timeout: {
      night: 30,
      dayDiscussion: 60,
      dayVoting: 30
    },
    language: 'zh-CN',
    enablePersonalitySystem: false,
    agents: []
  }

  const statistics: GameStatistics = {
    totalEvents: events.length,
    votesByPlayer: {
      'DemoPlayer1': 2,
      'DemoPlayer2': 1,
      'DemoPlayer3': 3,
      'DemoPlayer4': 2,
      'DemoPlayer5': 4
    },
    speakingEventsByPlayer: {
      'DemoPlayer1': 5,
      'DemoPlayer2': 8,
      'DemoPlayer3': 6,
      'DemoPlayer4': 4,
      'DemoPlayer5': 7
    },
    actionEventsByPlayer: {
      'DemoPlayer1': 2,
      'DemoPlayer2': 1,
      'DemoPlayer3': 3,
      'DemoPlayer4': 2,
      'DemoPlayer5': 1
    },
    phaseDurations: {
      'night': 120,
      'day_discussion': 300,
      'day_voting': 90
    },
    factionStatistics: {
      werewolf: {
        aliveCount: 4,
        deadCount: 1,
        totalKills: 3,
        totalVotes: 8
      },
      villager: {
        aliveCount: 8,
        deadCount: 3,
        totalKills: 0,
        totalVotes: 15
      },
      neutral: {
        aliveCount: 1,
        deadCount: 0,
        totalKills: 0,
        totalVotes: 2
      }
    }
  }

  return {
    id: 'game_session_1',
    round: 3,
    phase: 'day_discussion',
    phaseName: '白天讨论',
    players,
    events,
    isRunning: true,
    isPaused: false,
    configuration: gameConfig,
    startTime: new Date(Date.now() - 10 * 60 * 1000),
    statistics
  }
}

// 生成模拟配置列表
export function generateMockConfigurations(): GameConfiguration[] {
  return [
    {
      id: 'demo_16p',
      name: '16人标准局',
      playerCount: 16,
      roles: [],
      timeout: {
        night: 30,
        dayDiscussion: 60,
        dayVoting: 30
      },
      language: 'zh-CN',
      enablePersonalitySystem: false,
      agents: []
    },
    {
      id: 'personality_12p',
      name: '12人人格局',
      playerCount: 12,
      roles: [],
      timeout: {
        night: 45,
        dayDiscussion: 90,
        dayVoting: 45
      },
      language: 'zh-CN',
      enablePersonalitySystem: true,
      agents: []
    },
    {
      id: 'quick_6p',
      name: '6人快速局',
      playerCount: 6,
      roles: [],
      timeout: {
        night: 20,
        dayDiscussion: 40,
        dayVoting: 20
      },
      language: 'zh-CN',
      enablePersonalitySystem: false,
      agents: []
    }
  ]
}

// 格式化时间
export function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return minutes > 0 ? `${minutes}:${remainingSeconds.toString().padStart(2, '0')}` : `${remainingSeconds}s`
}

// 获取阵营颜色
export function getFactionColor(faction: string): string {
  switch (faction) {
    case 'werewolf': return '#dc2626'
    case 'villager': return '#1e40af'
    case 'neutral': return '#6b7280'
    default: return '#6b7280'
  }
}

// 获取阵营文本
export function getFactionText(faction: string): string {
  switch (faction) {
    case 'werewolf': return '狼人'
    case 'villager': return '村民'
    case 'neutral': return '中立'
    default: return '未知'
  }
}