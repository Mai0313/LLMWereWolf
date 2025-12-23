/** @type {import('tailwindcss').Config} */
import { theme } from 'antd'

export default {
  // 关键修正：确保包含所有组件路径
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['serif'], // 暂时移除 Cinzel，防止字体加载失败导致回退样式丑陋
      },
      colors: {
        'bg-dark': '#050505',
        mystic: {
          950: '#050505',
          900: '#0a0a0f',
          text: '#e2e8f0',
          dim: '#64748b',
          accent: '#8b5cf6', // 紫色
          gold: '#fbbf24',
          blood: '#ef4444',
          soul: '#3b82f6',
        }
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(139, 92, 246, 0.3)',
      },
      backgroundImage: {
        'radial-mystic': 'radial-gradient(circle at center, #1e1b4b 0%, #020617 80%)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-fast': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 10s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}