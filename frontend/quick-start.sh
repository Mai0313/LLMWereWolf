#!/bin/bash

echo "🚀 快速启动 LLM Werewolf React UI"
echo "================================="

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 请先安装 Node.js (https://nodejs.org/)"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"

# 进入目录
cd "$(dirname "$0")"

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 创建环境文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "📝 创建环境配置..."
    cat > .env << 'EOF'
# API 配置
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws

# 公司 LLM API 服务器
REACT_APP_LLM_SERVER_1=http://100.80.20.5:4000/v1
REACT_APP_LLM_SERVER_2=http://100.82.5.110:30001
REACT_APP_DEFAULT_MODEL=meta-llama/Llama-3.3-70B-Instruct

# 开发配置
GENERATE_SOURCEMAP=true
PORT=3000
REACT_APP_ENABLE_MOCK_DATA=true
REACT_APP_ENABLE_DEBUG=true
EOF
fi

# 启动开发服务器
echo "🚀 启动开发服务器..."
echo "访问地址: http://localhost:3000"
echo "按 Ctrl+C 停止服务器"
echo ""

npm run dev