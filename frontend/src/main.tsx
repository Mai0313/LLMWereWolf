import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import { GameProvider } from './contexts/GameContext'
import './index.css'

// 深色主题配置
const antTheme = {
  algorithm: theme.darkAlgorithm, // 开启暗黑模式算法
  token: {
    colorPrimary: '#8b5cf6', // mystic-accent
    colorInfo: '#3b82f6',
    colorSuccess: '#22c55e',
    colorWarning: '#fbbf24',
    colorError: '#ef4444',
    colorBgContainer: '#0f172a', // 深色背景
    colorBgElevated: '#1e293b',  // 浮层背景
    colorText: '#e2e8f0',
    colorBorder: 'rgba(255, 255, 255, 0.1)',
    fontFamily: 'Inter, sans-serif',
    borderRadius: 8,
  },
  components: {
    Button: {
      colorPrimary: '#8b5cf6',
      algorithm: true,
    },
    Slider: {
      colorPrimary: '#8b5cf6',
      handleSize: 8,
    },
    Switch: {
      colorPrimary: '#8b5cf6',
    }
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider theme={antTheme} locale={zhCN}>
      <BrowserRouter>
        <GameProvider>
          <App />
        </GameProvider>
      </BrowserRouter>
    </ConfigProvider>
  </React.StrictMode>,
)