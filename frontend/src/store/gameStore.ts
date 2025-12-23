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
  gameState: GameState | null
  gameHistory: GameEvent[]
  currentEvent: GameEvent | null
  votingData: Vote[]
  configuration: GameConfiguration | null
  availableConfigurations: GameConfiguration[]
  circleLayout: Record<string, Position>

  setGameState: (state: GameState) => void
  addEvent: (event: GameEvent) => void
  selectPlayer: (player: Player | null) => void
  togglePlayerDetails: () => void
  toggleStatistics: () => void
  setView: (view: UIState['currentView']) => void

  // 关键修复：坐标计算
  calculateCircleLayout: (playerCount: number) => void

  // ... 其他方法保持不变，为节省篇幅省略 ...
  updateGameState: (updates: Partial<GameState>) => void
  setCurrentEvent: (event: GameEvent | null) => void
  setVotingData: (votes: Vote[]) => void
  setGameSpeed: (speed: number) => void
  toggleAutoScroll: () => void
  setTheme: (theme: 'dark' | 'light') => void
  setPlayerAnimation: (playerId: string, animation: any) => void
  setConfiguration: (config: GameConfiguration) => void
  loadConfigurations: () => Promise<void>
  reset: () => void
}

export const useGameStore = create<GameStore>()(
  subscribeWithSelector((set, get) => ({
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

    setGameState: (state) => {
      set({ gameState: state })
      // 初始化时立即计算布局
      get().calculateCircleLayout(state.players.length)
    },

    // 修复：强制使用 800x800 容器的中心点 (400, 400)
    calculateCircleLayout: (playerCount) => {
      const positions: Record<string, Position> = {}
      const centerX = 400
      const centerY = 400
      const radius = 300 // 半径设为 300，留出边距

      const angleStep = (2 * Math.PI) / playerCount

      for (let i = 0; i < playerCount; i++) {
        // -PI/2 确保第一个玩家在正上方
        const angle = -Math.PI / 2 + (i * angleStep)
        const x = centerX + radius * Math.cos(angle)
        const y = centerY + radius * Math.sin(angle)
        positions[i] = { x, y }
      }

      set({ circleLayout: positions })
    },

    // ... 其他方法的实现保持不变 (直接复制原来的) ...
    updateGameState: (updates) => {
      const currentState = get().gameState
      if (currentState) { set({ gameState: { ...currentState, ...updates } }) }
    },
    addEvent: (event) => {
      set({ currentEvent: event })
      const history = get().gameHistory
      set({ gameHistory: [...history, event] })
    },
    setCurrentEvent: (event) => set({ currentEvent: event }),
    setVotingData: (votes) => set({ votingData: votes }),
    selectPlayer: (player) => set({ selectedPlayer: player }),
    hoverPlayer: (player) => set({ hoveredPlayer: player }),
    togglePlayerDetails: () => set((state) => ({ showPlayerDetails: !state.showPlayerDetails })),
    setGameSpeed: (speed) => set({ gameSpeed: speed }),
    toggleAutoScroll: () => set((state) => ({ autoScroll: !state.autoScroll })),
    setTheme: (theme) => set({ theme }),
    setView: (view) => set({ currentView: view }),
    toggleStatistics: () => set((state) => ({ showingStatistics: !state.showingStatistics })),
    setPlayerAnimation: (playerId, animation) => {
      const animations = get().playerAnimations
      set({ playerAnimations: { ...animations, [playerId]: animation } })
    },
    setConfiguration: (config) => set({ configuration: config }),
    loadConfigurations: async () => { /* ... */ },
    reset: () => {
      set({ gameState: null, gameHistory: [], currentEvent: null, votingData: [], circleLayout: {} })
    }
  }))
)

// Export Hooks
export const useGameState = () => useGameStore((state) => state.gameState)
export const usePlayers = () => useGameStore((state) => state.gameState?.players || [])
export const useGameEvents = () => useGameStore((state) => state.gameHistory)
export const useUIState = () => useGameStore((state) => ({
  selectedPlayer: state.selectedPlayer,
  showPlayerDetails: state.showPlayerDetails,
  showingStatistics: state.showingStatistics,
  currentView: state.currentView
}))
export const useCircleLayout = () => useGameStore((state) => state.circleLayout)
export const useAutoScroll = () => useGameStore((state) => state.autoScroll)
export const setView = (view: UIState['currentView']) => useGameStore.getState().setView(view)