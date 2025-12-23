// 游戏核心类型定义
export type GamePhase = 'waiting' | 'night' | 'day_discussion' | 'day_voting' | 'ended'
export type Faction = 'werewolf' | 'villager' | 'neutral'
export type PlayerStatus = 'alive' | 'dead' | 'protected' | 'poisoned' | 'charmed'

export interface Role {
  id: string
  name: string
  camp: Faction
  description: string
  priority: number
  icon: string
}

export interface Player {
  id: string
  name: string
  role: Role
  status: PlayerStatus
  isAlive: boolean
  position: number
  x?: number
  y?: number
  agent: string
  avatar?: string
  sheriff?: boolean
  lovers?: string[] // 情侣ID数组
}

export interface GameEvent {
  id: string
  type: string
  message: string
  round: number
  phase: GamePhase
  timestamp: Date
  data?: Record<string, any>
  actorId?: string
  targetId?: string
}

export interface GameState {
  id: string
  round: number
  phase: GamePhase
  phaseName: string
  players: Player[]
  events: GameEvent[]
  isRunning: boolean
  isPaused: boolean
  configuration: GameConfiguration
  startTime?: Date
  endTime?: Date
  winner?: Faction
  statistics: GameStatistics
}

export interface GameConfiguration {
  id: string
  name: string
  playerCount: number
  roles: Role[]
  timeout: {
    night: number
    dayDiscussion: number
    dayVoting: number
  }
  language: string
  enablePersonalitySystem: boolean
  agents: AgentConfig[]
}

export interface AgentConfig {
  model: string
  apiKey?: string
  personalityProfile?: string
  description: string
}

export interface GameStatistics {
  totalEvents: number
  votesByPlayer: Record<string, number>
  speakingEventsByPlayer: Record<string, number>
  actionEventsByPlayer: Record<string, number>
  phaseDurations: Record<string, number>
  factionStatistics: Record<Faction, FactionStats>
}

export interface FactionStats {
  aliveCount: number
  deadCount: number
  totalKills: number
  totalVotes: number
}

// 投票相关类型
export interface Vote {
  voterId: string
  targetId: string
  round: number
  phase: GamePhase
  timestamp: Date
}

export interface VotingResult {
  round: number
  votes: Vote[]
  eliminatedPlayer?: Player
  tie: boolean
  statistics: {
    totalVotes: number
    invalidVotes: number
    topCandidates: Array<{ playerId: string; votes: number }>
  }
}

// UI 特定类型
export interface Position {
  x: number
  y: number
}

export interface CircleLayout {
  center: Position
  radius: number
  positions: Position[]
}

export interface PlayerAnimations {
  death?: boolean
  targeted?: boolean
  protected?: boolean
  poisoned?: boolean
  speaking?: boolean
  voting?: boolean
}

export interface UIState {
  selectedPlayer: Player | null
  hoveredPlayer: Player | null
  showPlayerDetails: boolean
  gameSpeed: number
  autoScroll: boolean
  theme: 'dark' | 'light'
  showingStatistics: boolean
  currentView: 'game' | 'statistics' | 'configuration'
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface GameListResponse {
  games: Array<{
    id: string
    name: string
    status: string
    playerCount: number
    createTime: Date
  }>
}

// WebSocket 消息类型
export interface WebSocketMessage {
  type: 'game_update' | 'event' | 'state_change' | 'error' | 'statistics'
  gameId: string
  data: any
  timestamp: Date
}