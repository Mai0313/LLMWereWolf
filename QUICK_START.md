# ⚡ 快速开始 - 人格系统集成

## 🎯 5分钟体验人格系统

### 1. 立即体验（无需修改现有代码）

```bash
# 运行内置的人格系统演示
python scripts/demo_personality_system.py
```

这会展示：
- 不同人格的行为差异
- 信息裁剪效果
- 意图选择过程

### 2. 创建简单的人格游戏配置

创建 `/home/mystic/dist/LLMWereWolf/my_personality_game.yaml`：

```yaml
language: zh-TW

players:
  - name: 激进狼人
    model: demo
    personality_profile: aggressive_wolf
    enable_personality_system: true

  - name: 谨慎预言家
    model: demo
    personality_profile: cautious_seer
    enable_personality_system: true

  - name: 传统AI玩家
    model: demo
    # 不启用人格系统，保持原有行为

  - name: 传统AI玩家2
    model: demo
    # 不启用人格系统，保持原有行为

  - name: 传统AI玩家3
    model: demo
    # 不启用人格系统，保持原有行为

  - name: 传统AI玩家4
    model: demo
    # 不启用人格系统，保持原有行为
```

### 3. 运行游戏

```bash
# 运行带人格的游戏
uv run llm-werewolf my_personality_game.yaml
```

### 4. 对比效果

在这个配置中：
- ✅ **玩家1（激进狼人）**：会表现出发控欲强、高风险的行为
- ✅ **玩家2（谨慎预言家）**：会表现出逻辑分析、谨慎的特征
- ✅ **玩家3-6（传统AI）**：保持原有的随机行为

---

## 🔧 最小修改方案

如果你想在现有项目中少量修改来支持人格系统：

### 修改现有的配置文件

在你现有的配置文件中，为任意玩家添加人格参数：

```yaml
# 在你现有的配置文件中
players:
  - name: AI玩家1
    model: gpt-4
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    # 🆕 添加这两行
    personality_profile: aggressive_wolf
    enable_personality_system: true

  - name: AI玩家2
    model: claude-3-sonnet
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    # 🆕 保持不变，继续使用传统模式
```

### 只需要修改3个文件（可选）

如果你想要更完整的集成，只需要修改这三个关键文件（我们已经帮你改好了）：

1. `core/config/player_config.py` - 支持人格配置（✅ 已改）
2. `core/player.py` - 支持人格Agent（✅ 已改）
3. `cli.py` - 加载人格系统（✅ 已改）

**所有修改都是向后兼容的，不会影响现有功能！**

---

## 🎭 可用人格类型

| 人格名称 | 特点描述 | 适用场景 |
|---------|---------|---------|
| `aggressive_wolf` | 激进型狼人：高控制欲，高风险，善欺骗 | 狼人角色，进攻型玩家 |
| `cautious_seer` | 谨慎型预言家：高逻辑，低风险，重证据 | 神职角色，分析型玩家 |
| `emotional_witch` | 情绪化女巫：高社交压力，情感驱动 | 辅助角色，感性玩家 |
| `balanced_hunter` | 平衡型猎人：中庸稳健，理性决策 | 特殊能力者，平衡玩家 |
| `passive_villager` | 被动型平民：易受影响，保守谨慎 | 普通角色，跟随型玩家 |
| `chaotic_player` | 混乱型玩家：行为不可预测，爱冒险 | 任何角色，娱乐效果 |

---

## 🔍 效果对比

同样面对"怀疑玩家2"的情况：

### 传统AI响应：
```
"我觉得玩家2的行为有点奇怪，需要再观察。"
```

### 人格AI响应：

**激进狼人**：
```
"我强烈怀疑玩家2！他的行为逻辑完全混乱，绝对是狼人！必须立即处理！"
```

**谨慎预言家**：
```
"基于目前的观察，玩家2确实表现出一些值得关注的行为模式，但还需要更多信息来做出准确判断。"
```

**情绪化女巫**：
```
"我真的很难过，看到玩家2这样让我感到很不安，我希望能相信他但现实让我失望..."
```

---

## 🚀 生产级使用

### 1. 混合模式（推荐部分玩家启用人格）

```yaml
# 真实场景：部分AI启用人格，部分保持传统
players:
  - name: 主角AI
    model: gpt-4
    personality_profile: aggressive_wolf
    enable_personality_system: true
    api_key_env: OPENAI_API_KEY

  - name: 分析AI
    model: claude-3-opus
    personality_profile: cautious_seer
    enable_personality_system: true
    api_key_env: ANTHROPIC_API_KEY

  - name: 背景AI1
    model: demo
    # 传统模式，减少干扰

  - name: 背景AI2
    model: demo
    # 传统模式，减少干扰
```

### 2. 实验模式（全部启用人格）

```yaml
settings:
  enable_personality_system: true

players:
  - name: 激进狼人
    model: gpt-4
    personality_profile: aggressive_wolf
    enable_personality_system: true

  - name: 谨慎预言家
    model: claude-3-sonnet
    personality_profile: cautious_seer
    enable_personality_system: true

  - name: 情感女巫
    model: gpt-4
    personality_profile: emotional_witch
    enable_personality_system: true

  # ... 其他玩家
```

---

## 📋 验证步骤

1. **运行演示**：确认人格系统工作正常
2. **测试配置**：使用新配置文件跑一局游戏
3. **对比效果**：观察是否出现人格化行为
4. **性能检查**：确保运行流畅无错误

---

## ❓ 常见问题

**Q: 会不会影响现有的游戏？**
A: 完全不会！所有新功能都是可选的，默认关闭。

**Q: 需要API密钥吗？**
A: 人格系统本身不需要，但如果你用LLM模型还是需要的。

**Q: 可以自定义人格吗？**
A: 可以！在 `configs/personalities/` 目录下创建新配置。

**Q: 性能影响大吗？**
A: 影响很小，主要是额外的意图选择过程。

**Q: 如何回退？**
A: 直接删除 `personality_profile` 和 `enable_personality_system` 即可。

---

## 🎉 开始体验！

现在你已经了解了：

✅ 人格系统的基本概念
✅ 如何配置和使用
✅ 实际效果差异
✅ 最小修改方案

**快去试试吧！** 🚀

```bash
# 立即体验
python scripts/demo_personality_system.py

# 或创建自己的游戏
uv run llm-werewolf my_personality_game.yaml
```