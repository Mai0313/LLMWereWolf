import React from 'react'
import { Layout, Switch, Button, Space, Tooltip } from 'antd'
import {
  SettingOutlined,
  BarChartOutlined,
  SunOutlined,
  MoonOutlined
} from '@ant-design/icons'
import { useUIState, useGameStore, useGameState } from '@store/gameStore'
import GameLayout from '@components/GameLayout'
import StatisticsPanel from '@components/StatisticsPanel'
import ConfigurationPanel from '@components/ConfigurationPanel'

const { Header, Content } = Layout

const App: React.FC = () => {
  const uiState = useUIState()
  const { gameSpeed, setGameSpeed, setTheme, setView, toggleStatistics } = useGameStore()
  const gameState = useGameState()

  const { theme, showingStatistics, currentView } = uiState

  const handleSpeedChange = (speed: number) => {
    setGameSpeed(speed)
  }

  const handleThemeToggle = (checked: boolean) => {
    setTheme(checked ? 'light' : 'dark')
    // 切换 document 类名
    if (checked) {
      document.body.classList.add('theme-light')
      document.body.classList.remove('game-container')
    } else {
      document.body.classList.add('game-container')
      document.body.classList.remove('theme-light')
    }
  }

  const renderContent = () => {
    if (showingStatistics) {
      return <StatisticsPanel />
    }

    if (currentView === 'configuration') {
      return <ConfigurationPanel />
    }

    return <GameLayout />
  }

  return (
    <Layout className={`game-container ${theme === 'light' ? 'theme-light' : ''}`}>
      {/* Header */}
      <Header
        className="fixed top-0 left-0 right-0 z-50 px-6 flex items-center justify-between"
        style={{
          background: theme === 'light' ?
            'rgba(255, 255, 255, 0.9)' :
            'rgba(15, 23, 42, 0.9)',
          backdropFilter: 'blur(10px)',
          borderBottom: theme === 'light' ?
            '1px solid rgba(0, 0, 0, 0.1)' :
            '1px solid rgba(148, 163, 184, 0.1)'
        }}
      >
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold">
            🐺 LLM Werewolf
          </h1>
          {gameState && (
            <div className="flex items-center space-x-2">
              <span className="text-sm opacity-75">
                回合 {gameState.round} • {gameState.phaseName}
              </span>
              <div className={`w-2 h-2 rounded-full ${
                gameState.isRunning ?
                'bg-green-500 animate-pulse' :
                'bg-yellow-500'
              }`} />
            </div>
          )}
        </div>

        <Space size="middle">
          {/* 游戏速度控制 */}
          <div className="flex items-center space-x-2">
            <span className="text-sm">速度:</span>
            <div className="flex space-x-1">
              {[0.5, 1, 2, 4].map((speed) => (
                <Button
                  key={speed}
                  size="small"
                  type={gameSpeed === speed ? 'primary' : 'default'}
                  onClick={() => handleSpeedChange(speed)}
                >
                  {speed}x
                </Button>
              ))}
            </div>
          </div>

          {/* 控制按钮 */}
          <Space>
            <Tooltip title="统计面板">
              <Button
                type={showingStatistics ? 'primary' : 'default'}
                icon={<BarChartOutlined />}
                onClick={toggleStatistics}
              />
            </Tooltip>

            <Tooltip title="游戏配置">
              <Button
                type={currentView === 'configuration' ? 'primary' : 'default'}
                icon={<SettingOutlined />}
                onClick={() => setView(currentView === 'configuration' ? 'game' : 'configuration')}
              />
            </Tooltip>

            <Tooltip title={theme === 'dark' ? '切换到亮色主题' : '切换到暗色主题'}>
              <Switch
                checked={theme === 'light'}
                onChange={handleThemeToggle}
                checkedChildren={<SunOutlined />}
                unCheckedChildren={<MoonOutlined />}
              />
            </Tooltip>
          </Space>
        </Space>
      </Header>

      {/* Main Content */}
      <Content
        className="mt-16"
        style={{ minHeight: 'calc(100vh - 64px)' }}
      >
        {renderContent()}
      </Content>
    </Layout>
  )
}

export default App