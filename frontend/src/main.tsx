import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import { GameProvider } from './contexts/GameContext'
import './index.css'

// Ant Design 主题配置
const antTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    // 主色调
    colorPrimary: '#0ea5e9',
    colorSuccess: '#22c55e',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    colorInfo: '#3b82f6',

    // 背景色
    colorBgContainer: 'rgba(30, 41, 59, 0.8)',
    colorBgElevated: 'rgba(30, 41, 59, 0.9)',
    colorBgLayout: 'transparent',

    // 文字颜色
    colorText: '#f1f5f9',
    colorTextSecondary: '#cbd5e1',
    colorTextTertiary: '#94a3b8',

    // 边框
    colorBorder: 'rgba(148, 163, 184, 0.2)',
    colorBorderSecondary: 'rgba(148, 163, 184, 0.1)',

    // 阴影
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
    boxShadowSecondary: '0 1px 3px 0 rgba(0, 0, 0, 0.2)',

    // 圆角
    borderRadius: 8,
  },
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      theme={antTheme}
      locale={zhCN}
    >
      <BrowserRouter>
        <GameProvider>
          <App />
        </GameProvider>
      </BrowserRouter>
    </ConfigProvider>
  </React.StrictMode>,
)