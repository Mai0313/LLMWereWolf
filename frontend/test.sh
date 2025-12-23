#!/bin/bash

# LLM Werewolf React UI 测试脚本

echo "🧪 测试 LLM Werewolf React UI"
echo "==========================="

# 测试1: 检查 Node.js
echo "1️⃣ 检查 Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js 未安装"
    exit 1
fi

# 测试2: 检查依赖
echo "2️⃣ 检查依赖..."
if [ -f "package.json" ]; then
    echo "✅ package.json 存在"
else
    echo "❌ package.json 不存在"
    exit 1
fi

if [ -d "node_modules" ]; then
    echo "✅ node_modules 存在"
else
    echo "❌ node_modules 不存在，请先运行 npm install"
    exit 1
fi

# 测试3: 检查 TypeScript 编译
echo "3️⃣ 测试 TypeScript 编译..."
npx tsc --noEmit --skipLibCheck
if [ $? -eq 0 ]; then
    echo "✅ TypeScript 编译通过"
else
    echo "❌ TypeScript 编译错误"
    exit 1
fi

# 测试4: 检查构建
echo "4️⃣ 测试构建..."
npm run build
if [ $? -eq 0 ]; then
    echo "✅ 构建成功"
else
    echo "❌ 构建失败"
    exit 1
fi

# 测试5: 检查关键文件
echo "5️⃣ 检查关键文件..."
key_files=(
    "src/App.tsx"
    "src/components/GameLayout.tsx"
    "src/components/PlayerCircle.tsx"
    "src/components/EventFeed.tsx"
    "src/components/VotingPanel.tsx"
    "src/components/StatisticsPanel.tsx"
    "src/store/gameStore.ts"
    "src/types/game.ts"
)

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done

# 清理测试构建文件
rm -rf dist

echo ""
echo "🎉 所有测试通过！"
echo "可以运行 ./start.sh 启动开发服务器"