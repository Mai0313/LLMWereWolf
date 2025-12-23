# 🐺 LLM Werewolf React UI

一个漂亮的 2D 可视化界面，用于展示 LLM Werewolf 狼人杀游戏过程。

## ✨ 功能特色

### 🎮 核心功能
- **实时游戏可视化** - 圆形玩家布局，实时显示游戏状态
- **事件流时间轴** - 详细记录每个游戏事件
- **投票交互界面** - 直观的投票体验
- **统计数据分析** - 多维度数据可视化
- **游戏配置管理** - 灵活的游戏参数配置

### 🎨 视觉效果
- **暗色/亮色主题** - 自适应用户偏好
- **流畅动画过渡** - 基于Framer Motion的动画效果
- **2.5D视觉效果** - CSS transforms营造空间感
- **响应式设计** - 适配桌面、平板、手机

### 🤖 AI集成
- **多模型支持** - GPT、Claude、DeepSeek等
- **人格系统** - 可视化AI性格特征
- **决策透明化** - AI思考过程展示

## 🚀 快速开始

### 环境要求
- Node.js 18+
- npm 或 yarn

### 安装依赖
```bash
cd frontend
npm install
```

### 开发模式
```bash
npm run dev
```
访问 http://localhost:3000

### 构建生产版本
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 🏗️ 技术架构

### 前端技术栈
- **React 18** - 组件化UI框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Tailwind CSS** - 现代CSS框架
- **Ant Design** - 组件库
- **Framer Motion** - 动画库
- **Zustand** - 轻量级状态管理
- **Recharts** - 数据可视化
- **Axios** - HTTP客户端

### 状态管理
```
store/
├── gameStore.ts          # 主要游戏状态
├── uiStore.ts           # UI状态管理
└── configurationStore.ts # 配置状态管理
```

### 组件结构
```
components/
├── GameLayout.tsx       #主布局
├── PlayerCircle.tsx     #玩家圆桌视图
├── EventFeed.tsx        #事件流
├── VotingPanel.tsx      #投票界面
├── StatisticsPanel.tsx  #统计面板
├── GameDashboard.tsx    #游戏仪表板
├── PlayerDetailsPanel.tsx #玩家详情
├── ConfigurationPanel.tsx #配置面板
└── animations/         #动画组件
    ├── PhaseTransition.tsx
    └── PlayerDeathAnimation.tsx
```

## 🎯 功能说明

### 游戏主界面
1. **圆桌视图** - 以圆形方式展示所有玩家
2. **实时状态** - 显示存活/死亡/特殊状态
3. **交互操作** - 点击查看玩家详情
4. **阶段指示** - 当前游戏阶段和进度

### 事件时间轴
- **实时更新** - 游戏事件实时显示
- **分类展示** - 不同类型事件用不同颜色标记
- **自动滚动** - 新事件自动滚动到底部
- **详情查看** - 点击展开事件详细信息

### 投票系统
- **进度显示** - 实时投票进度
- **结果预览** - 当前得票最多的玩家
- **倒计时** - 投票时间限制显示
- **交互投票** - 点击选择投票目标

### 统计分析
- **阵营分布** - 饼图展示各阵营人数
- **事件统计** - 柱状图显示各类事件数量
- **趋势分析** - 折线图展示人数变化趋势
- **玩家活跃度** - 表格排名玩家活动情况

## 🔧 配置选项

### 游戏配置
- **玩家人数** - 6-20人可选
- **时间设置** - 各阶段时间自定义
- **角色配置** - 灵活的角色分配
- **AI模型** - 选择不同的AI模型

### 界面配置
- **主题切换** - 暗色/亮色主题
- **动画速度** - 调整动画播放速度
- **自动滚动** - 事件流自动滚动设置
- **语言选择** - 中英文界面切换

## 🔌 API集成

### RESTful API
```typescript
// 游戏控制
POST   /api/games/start      # 开始游戏
POST   /api/games/{id}/pause # 暂停游戏
GET    /api/games/{id}       # 获取游戏状态

// 配置管理
GET    /api/configurations   # 获取配置列表
POST   /api/configurations   # 保存配置
PUT    /api/configurations/{id} # 更新配置
```

### WebSocket实时通信
```typescript
// 连接游戏房间
ws://localhost:8000/ws?gameId=xxx

// 消息类型
- game_update    # 游戏状态更新
- event          # 新游戏事件
- phase_change   # 阶段切换
- statistics     # 统计数据更新
```

## 🎨 自定义样式

### 主题变量
```css
:root {
  --color-primary: #0ea5e9;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --bg-dark: #0f172a;
  --bg-light: #f8fafc;
}
```

### 动画配置
```javascript
const animations = {
  fadeIn: { duration: 0.5, ease: "easeInOut" },
  slideUp: { duration: 0.3, stiffness: 200 },
  pulse: { duration: 2, repeat: Infinity },
  bounce: { type: "spring", stiffness: 400 }
}
```

## 🚀 部署指南

### 生产环境配置
1. 设置环境变量：
```bash
REACT_APP_API_BASE_URL=https://your-api-server.com/api
REACT_APP_WS_URL=wss://your-api-server.com/ws
```

2. 构建优化：
```bash
npm run build
```

3. 部署到静态服务器（Nginx、Apache等）

### Docker部署
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🐛 故障排除

### 常见问题
1. **白屏问题** - 检查控制台错误，确保所有依赖已安装
2. **连接失败** - 检查后端API服务和环境变量配置
3. **动画卡顿** - 尝试关闭硬件加速或降低动画质量
4. **响应式问题** - 检查CSS媒体查询和容器查询

### 调试工具
- **Redux DevTools** - 调试状态管理
- **React DevTools** - 调试组件状态
- **Network面板** - 调试API请求
- **Performance面板** - 分析性能问题

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [React](https://reactjs.org/) - UI框架
- [Framer Motion](https://www.framer.com/motion/) - 动画库
- [Ant Design](https://ant.design/) - 组件库
- [Recharts](https://recharts.org/) - 图表库
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架