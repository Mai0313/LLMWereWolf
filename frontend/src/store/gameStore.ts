import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import {
  GameState,
  GameEvent,
  Player,
  GameConfiguration,
  UIState,
  Vote,
  Position
} from '../types/game'

interface GameStore extends UIState {
  // 游戏状态
  gameState: GameState | null
  gameHistory: GameEvent[]
  currentEvent: GameEvent | null
  votingData: Vote[]

  // 配置
  configuration: GameConfiguration | null
  availableConfigurations: GameConfiguration[]

  // 玩家相关
  circleLayout: Record<string, Position>
  playerAnimations: Record<string, any>

  // 动作
  setGameState: (state: GameState) => void
  updateGameState: (updates: Partial<GameState>) => void
  addEvent: (event: GameEvent) => void
  setCurrentEvent: (event: GameEvent | null) => void
  setVotingData: (votes: Vote[]) => void

  // UI 控制
  selectPlayer: (player: Player | null) => void
  hoverPlayer: (player: Player | null) => void
  togglePlayerDetails: () => void
  setGameSpeed: (speed: number) => void
  toggleAutoScroll: () => void
  setTheme: (theme: 'dark' | 'light') => void
  setView: (view: UIState['currentView']) => void
  toggleStatistics: () => void

  // 布局计算
  calculateCircleLayout: (playerCount: number, centerX?: number, centerY?: number, radius?: number) => void
  setPlayerAnimation: (playerId: string, animation: any) => void

  // 配置管理
  setConfiguration: (config: GameConfiguration) => void
  loadConfigurations: () => Promise<void>

  // 重置和清理
  reset: () => void
}

export const useGameStore = create<GameStore>()(
  subscribeWithSelector((set, get) => ({
    // 初始状态
    gameState: null,
    gameHistory: [],
    currentEvent: null,
    votingData: [],

    configuration: null,
    availableConfigurations: [],

    circleLayout: {},
    playerAnimations: {},

    selectedPlayer: null,
    hoveredPlayer: null,
    showPlayerDetails: false,
    gameSpeed: 1,
    autoScroll: true,
    theme: 'dark',
    showingStatistics: false,
    currentView: 'game',

    // 游戏状态管理
    setGameState: (state) => {
      set({ gameState: state })
      get().calculateCircleLayout(state.players.length)
    },

    updateGameState: (updates) => {
      const currentState = get().gameState
      if (currentState) {
        set({
          gameState: { ...currentState, ...updates }
        })
      }
    },

    addEvent: (event) => {
      set({ currentEvent: event })
      const history = get().gameHistory
      set({ gameHistory: [...history, event] })

      // 如果有当前游戏状态，也更新到那里
      const gameState = get().gameState
      if (gameState) {
        set({
          gameState: {
            ...gameState,
            events: [...gameState.events, event]
          }
        })
      }
    },

    setCurrentEvent: (event) => set({ currentEvent: event }),
    setVotingData: (votes) => set({ votingData: votes }),

    // UI 控制
    selectPlayer: (player) => set({ selectedPlayer: player }),
    hoverPlayer: (player) => set({ hoveredPlayer: player }),
    togglePlayerDetails: () => set((state) => ({ showPlayerDetails: !state.showPlayerDetails })),
    setGameSpeed: (speed) => set({ gameSpeed: speed }),
    toggleAutoScroll: () => set((state) => ({ autoScroll: !state.autoScroll })),
    setTheme: (theme) => set({ theme }),
    setView: (view) => set({ currentView: view }),
    toggleStatistics: () => set((state) => ({ showingStatistics: !state.showingStatistics })),

    // 布局计算
    calculateCircleLayout: (playerCount, centerX = 400, centerY = 300, radius = 200) => {
      const positions: Record<string, Position> = {}
      const angleStep = (2 * Math.PI) / playerCount

      // 从顶部开始，顺时针排列
      for (let i = 0; i < playerCount; i++) {
        const angle = -Math.PI / 2 + (i * angleStep) // 从顶部开始
        const x = centerX + radius * Math.cos(angle)
        const y = centerY + radius * Math.sin(angle)
        positions[i] = { x, y }
      }

      set({ circleLayout: positions })
    },

    setPlayerAnimation: (playerId, animation) => {
      const animations = get().playerAnimations
      set({
        playerAnimations: {
          ...animations,
          [playerId]: animation
        }
      })
    },

    // 配置管理
    setConfiguration: (config) => set({ configuration: config }),

    loadConfigurations: async () => {
      try {
        // 这里将来会连接真实的API
        const mockConfigs: GameConfiguration[] = [
          {
            id: 'demo',
            name: 'Demo Game',
            playerCount: 16,
            roles: [],
            timeout: {
              night: 30,
              dayDiscussion: 60,
              dayVoting: 30
            },
            language: 'en-US',
            enablePersonalitySystem: false,
            agents: []
          },
          {
            id: 'personality',
            name: 'Personality Game',
            playerCount: 12,
            roles: [],
            timeout: {
              night: 45,
              dayDiscussion: 90,
              dayVoting: 45
            },
            language: 'en-US',
            enablePersonalitySystem: true,
            agents: []
          }
        ]

        set({ availableConfigurations: mockConfigs })
      } catch (error) {
        console.error('Failed to load configurations:', error)
      }
    },

    // 重置
    reset: () => {
      set({
        gameState: null,
        gameHistory: [],
        currentEvent: null,
        votingData: [],
        selectedPlayer: null,
        hoveredPlayer: null,
        circleLayout: {},
        playerAnimations: {}
      })
    }
  }))
)

// 选择器 Hooks
export const useGameState = () => useGameStore((state) => state.gameState)
export const usePlayers = () => useGameStore((state) => state.gameState?.players || [])
export const useCurrentEvent = () => useGameStore((state) => state.currentEvent)
export const useGameEvents = () => useGameStore((state) => state.gameHistory)
export const useSelectedPlayer = () => useGameStore((state) => state.selectedPlayer)
export const useConfiguration = () => useGameStore((state) => state.configuration)
export const useCircleLayout = () => useGameStore((state) => state.circleLayout)
export const useUIState = () => useGameStore((state) => ({
  selectedPlayer: state.selectedPlayer,
  hoveredPlayer: state.hoveredPlayer,
  showPlayerDetails: state.showPlayerDetails,
  gameSpeed: state.gameSpeed,
  autoScroll: state.autoScroll,
  theme: state.theme,
  showingStatistics: state.showingStatistics,
  currentView: state.currentView
}))
export const useAutoScroll = () => useGameStore((state) => state.autoScroll)
export const useAvailableConfigurations = () => useGameStore((state) => state.availableConfigurations)
export const toggleAutoScroll = () => useGameStore.getState().toggleAutoScroll()
export const setView = (view: UIState['currentView']) => useGameStore.getState().setView(view)
export const setVotingData = (votes: Vote[]) => useGameStore.getState().setVotingData(votes)
export const useVotingData = () => useGameStore((state) => state.votingData)