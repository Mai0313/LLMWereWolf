<div align="center" markdown="1">

# LLM 狼人杀 🐺

[![PyPI version](https://img.shields.io/pypi/v/llm_werewolf.svg)](https://pypi.org/project/llm_werewolf/)
[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/LLMWereWolf/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/LLMWereWolf/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/LLMWereWolf/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/LLMWereWolf/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/LLMWereWolf/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/LLMWereWolf/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/LLMWereWolf.svg)](https://github.com/Mai0313/LLMWereWolf/graphs/contributors)

</div>

一个支持多种 LLM 模型的 AI 狼人杀游戏，具有精美的终端界面 (TUI)。

其他语言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特色功能

- 🎮 **完整游戏逻辑**：包含 20+ 种角色的完整狼人杀规则实现
- 🤖 **LLM 整合**：统一的代理界面，轻松整合任何 LLM（OpenAI、Anthropic、DeepSeek、本地模型等）
- 🖥️ **精美 TUI**：使用 Textual 框架的实时游戏可视化，支持交互式终端界面
- 👤 **真人玩家**：支持真人玩家与 AI 混合游戏
- ⚙️ **可配置**：通过 YAML 配置文件灵活设置玩家和游戏参数
- 📊 **事件系统**：完整的事件记录和游戏状态追踪
- 🧪 **充分测试**：高代码覆盖率与完整测试套件

## 快速开始

### 安装

```bash
# 复制存储库
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# 安装依赖
uv sync
```

### 执行游戏

项目提供两种执行模式,通过不同的命令行入口来选择:

**TUI 模式（交互式终端界面）：**

```bash
# 使用内置演示配置启动 TUI（使用 demo 代理测试）
uv run llm-werewolf-tui configs/demo.yaml

# 使用 LLM 玩家配置（需先设置 API 密钥）
uv run llm-werewolf-tui configs/players.yaml

# 显示调试面板
uv run llm-werewolf-tui configs/demo.yaml --debug

# 若已全局安装套件
llm-werewolf-tui configs/demo.yaml

# 使用 werewolf-tui 别名
uv run werewolf-tui configs/demo.yaml
```

**Console 模式（纯文本日志）：**

```bash
# 使用 Console 模式（自动执行）
uv run llm-werewolf configs/demo.yaml

# 或使用别名
uv run werewolf configs/demo.yaml
```

YAML 配置文件选项：

- `preset: <preset-name>` 指定角色预设配置（如 `6-players`、`9-players`、`12-players`、`15-players`、`expert`、`chaos`）
- `show_debug: true` 显示 TUI 调试面板（可被命令行 `--debug` 参数覆盖）
- `language: <language-code>` 设置游戏语言（如 `en-US`、`zh-TW`、`zh-CN`）。默认：`en-US`
- `players: [...]` 定义玩家列表

### 环境配置

创建 `.env` 文件配置 LLM API 密钥：

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# xAI (Grok)
XAI_API_KEY=xai-...

# 本地模型（Ollama 等）不需要 API 密钥
# 只需在 YAML 中设置 base_url 即可
```

## 支持的角色

### 狼人阵营 🐺

- **普通狼人 (Werewolf)**：在夜晚集体杀人的标准狼人
- **狼王 (AlphaWolf)**：被淘汰时可以开枪带走一人
- **白狼王 (WhiteWolf)**：每隔一晚可以杀死另一个狼人，成为独狼
- **狼美人 (WolfBeauty)**：魅惑一名玩家，狼美人死亡时该玩家同死
- **守卫狼 (GuardianWolf)**：每晚可以保护一名狼人
- **隐狼 (HiddenWolf)**：预言家查验显示为村民
- **血月使徒 (BloodMoonApostle)**：可以转化为狼人
- **梦魇狼 (NightmareWolf)**：可以封锁玩家的能力

### 村民阵营 👥

- **平民 (Villager)**：没有特殊能力的普通村民
- **预言家 (Seer)**：每晚可以查验一名玩家的身份（狼人或村民）
- **女巫 (Witch)**：拥有解药和毒药（各一次性使用）
- **猎人 (Hunter)**：被淘汰时可以开枪带走一人
- **守卫 (Guard)**：每晚可以保护一名玩家免于狼人攻击
- **白痴 (Idiot)**：被投票淘汰时翻牌存活但失去投票权
- **长老 (Elder)**：需要两次攻击才会死亡
- **骑士 (Knight)**：每局可以与一名玩家决斗一次
- **魔术师 (Magician)**：可以交换两名玩家的角色一次
- **丘比特 (Cupid)**：第一晚将两名玩家连结为恋人
- **乌鸦 (Raven)**：标记一名玩家获得额外投票
- **守墓人 (GraveyardKeeper)**：可以查验死亡玩家的身份

### 中立角色 👻

- **盗贼 (Thief)**：第一晚可以从两张额外角色卡中选择一个
- **恋人 (Lover)**：由丘比特连结，一人死亡另一人殉情
- **白狼恋人 (WhiteLoverWolf)**：可以建立恋人关系的特殊狼人变体

## 配置

### 使用预设配置

在配置文件中调整 `preset` 字段即可应用内置角色组合，可选项：

- `6-players`：新手局（6 人）- 2 狼人 + 预言家、女巫、2 平民
- `9-players`：标准局（9 人）- 2 狼人 + 预言家、女巫、猎人、守卫、3 平民
- `12-players`：进阶局（12 人）- 3 狼人（2 狼人 + 狼王）+ 预言家、女巫、猎人、守卫、丘比特、白痴、3 平民
- `15-players`：完整局（15 人）- 4 狼人（2 狼人 + 狼王 + 白狼王）+ 预言家、女巫、猎人、守卫、丘比特、白痴、长老、乌鸦、3 平民
- `expert`：专家配置（12 人）- 3 狼人（狼人 + 狼王 + 白狼王）+ 预言家、女巫、猎人、守卫、丘比特、骑士、魔术师、长老、平民
- `chaos`：混乱角色组合（10 人）- 3 特殊狼人（白狼王 + 狼美人 + 隐狼）+ 预言家、女巫、猎人、白痴、长老、乌鸦、平民

### 自定义配置

#### 玩家配置文件

```bash
# 由演示配置开始（全部为 demo 代理）
cp configs/demo.yaml my-game.yaml

# 或由支持 LLM 的样板开始
cp configs/players.yaml my-game.yaml

# 编辑配置文件
# configs/players.yaml 含有字段说明与范例
```

范例 `my-game.yaml`：

```yaml
preset: 6-players        # 选择预设配置
show_debug: false        # 是否显示调试面板（TUI 模式适用）
language: zh-CN          # 语言代码（en-US, zh-TW, zh-CN）

players:
  - name: GPT-4o 侦探
    model: gpt-4o
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0.7
    max_tokens:

  - name: GPT-4o-mini 玩家
    model: gpt-4o-mini
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0.7
    max_tokens:

  - name: GPT-4 分析师
    model: gpt-4
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0.7
    max_tokens:

  - name: Claude Sonnet
    model: claude-sonnet-4-20250514
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: DeepSeek 思考者
    model: deepseek-reasoner
    base_url: https://api.deepseek.com/v1
    api_key_env: DEEPSEEK_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: Claude Haiku
    model: claude-haiku-4-5-20251001
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: 人类玩家
    model: human          # 真人玩家

  - name: 本地 Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # 本地模型不需要 api_key_env

  - name: 测试机器人
    model: demo           # 测试用的简单代理
```

**配置说明：**

- `preset`：必填，决定游戏的角色配置和玩家数量
- `show_debug`：选填，默认为 `false`，用于 TUI 模式显示调试面板
- `language`：选填，默认为 `en-US`，设置游戏语言（如 `en-US`、`zh-TW`、`zh-CN`）
- `players`：必填，玩家列表，数量必须与 preset 的 `num_players` 一致

**玩家配置字段：**

- `name`：玩家显示名称
- `model`：模型类型
  - `human`：真人玩家（通过终端输入）
  - `demo`：测试用简单代理（随机回应）
  - LLM 模型名称：如 `gpt-4o`、`gpt-4o-mini`、`claude-sonnet-4-20250514`、`claude-haiku-4-20250514`、`deepseek-reasoner`、`llama3` 或任何 OpenAI 兼容模型
- `base_url`：API 端点（LLM 模型必填）
- `api_key_env`：环境变量名称（有验证的端点必填）
- `temperature`：选填，默认 0.7
- `max_tokens`：选填，默认 `null`（无限制）
- `reasoning_effort`：选填，支持推理的模型的推理努力等级（如 "low"、"medium"、"high"）

**支持的模型类型：**

- **OpenAI 兼容 API**：任何支持 OpenAI Chat Completions 格式的模型
- **真人玩家**：`model: human`
- **测试代理**：`model: demo`

**本地模型范例：**

若使用 Ollama 等本地模型，可省略 `api_key_env`：

```yaml
  - name: Ollama Llama3
    model: llama3
    base_url: http://localhost:11434/v1
    temperature: 0.7
    max_tokens: 500
```

## 代理系统

### 代理类型

本项目提供三种内置代理类型：

1. **LLMAgent**：支持任何 OpenAI 兼容 API 的 LLM 模型（GPT-4、Claude、DeepSeek、Grok、本地模型等）
2. **HumanAgent**：真人玩家通过终端输入
3. **DemoAgent**：测试用的简单代理（随机回应）

所有代理都通过 YAML 配置文件设置（参见[配置](#%E9%85%8D%E7%BD%AE)章节）。游戏支持在同一局中混合使用不同类型的代理。

## TUI 界面

TUI (Terminal User Interface) 提供现代化终端界面的实时游戏可视化，使用 [Textual](https://textual.textualize.io/) 框架构建。

### 界面预览

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐺 Werewolf Game                                                       AI-Powered Werewolf     │
│ q 退出  d 切换调试  n 下一步                                                    [00:02:34]     │
├──────────────────────┬─────────────────────────────────────────┬───────────────────────────────┤
│                      │ ╭───── 游戏状态 ─────╮                 │                               │
│    玩家              │ │ 🌙 第 2 回合 - 夜晚 │                 │    调试信息                   │
│ ──────────────────   │ │                     │                 │ ───────────────────────────   │
│ 名字      模型       │ │ 玩家总数： 8/9      │                 │ 会话 ID:                      │
│           状态       │ │ 狼人：     2        │                 │   ww_20251019_163022          │
│ ──────────────────   │ │ 村民：     6        │                 │                               │
│ Alice     gpt-4o     │ ╰─────────────────────╯                 │ 配置：players.yaml            │
│           ✓ 🛡️      │                                          │                               │
│ Bob       claude     │                                          │ 玩家：9                       │
│           ✓          │                                          │ AI: 7  真人: 1  Demo: 1       │
│ Charlie   llama3     │                                          │                               │
│           ✓          │                                          │ 角色：                        │
│ David     deepseek   │ ╭──── 事件 / 对话 ────╮                │  - Werewolf x2                │
│           ✓ ❤️       │ │ [00:02:28] 🎮 游戏开始│                │  - Seer x1                    │
│ Eve       grok       │ │ [00:02:29] ⏰ 阶段：夜│                │  - Witch x1                   │
│           ✓ ❤️       │ │ [00:02:30] 🐺 狼人讨论│                │  - Hunter x1                  │
│ Frank     human      │ │            目标       │                │  - Guard x1                   │
│           ✓          │ │ [00:02:31] ⏰ 阶段：白│                │  - Villager x3                │
│ Grace     claude     │ │ [00:02:32] 💀 Iris 死亡│               │                               │
│           ✓          │ │ [00:02:33] 💬 Alice：  │               │ 夜晚超时：60s                 │
│ Henry     demo       │ │            "我觉得Bob │               │ 白天超时：300s                │
│           ✓          │ │            行为可疑"  │               │ 投票超时：60s                 │
│ Iris      demo       │ │ [00:02:34] 💬 Bob：    │               │                               │
│           ✗          │ │            "我是村民！│               │ 错误：0                       │
│                      │ │            Alice 在转 │               │                               │
│                      │ │            移焦点"    │               │ 来源：YAML 配置               │
│                      │ │ [00:02:35] 💬 Charlie: │               │                               │
│                      │ │            "昨晚的死亡│               │                               │
│                      │ │            模式很奇怪"│               │                               │
│                      │ ╰───────────────────────╯               │                               │
│                      │                                          │                               │
└──────────────────────┴──────────────────────────────────────────┴───────────────────────────────┘
```

### 面板说明

#### 玩家面板（左侧）

显示所有玩家的信息：

- **名字**：玩家显示名称
- **模型**：使用的 AI 模型或 `human`/`demo`
- **状态指示器**：
  - ✓：存活
  - ✗：死亡
  - 🛡️：被守卫保护
  - ❤️：恋人关系
  - ☠️：被女巫下毒
  - 🔴：被乌鸦标记

#### 游戏面板（中央上方）

显示当前游戏状态：

- **回合与阶段**：
  - 🌙 夜晚阶段
  - ☀️ 白天讨论阶段
  - 🗳️ 投票阶段
  - 🏁 游戏结束
- **玩家统计**：按阵营统计存活玩家数
- **投票计数**（投票阶段）：显示各玩家得票数

#### 对话面板（中央下方）

可滚动的事件日志，显示游戏中的所有事件和对话：

- 💬 **玩家发言**：AI 生成的讨论、指控、辩护
- 🎮 **游戏事件**：游戏开始、阶段切换等
- ⏰ **阶段变化**：夜晚、白天、投票等
- 💀 **死亡事件**：玩家死亡通知
- 🐺 **狼人行动**：狼人夜晚讨论
- 🔮 **技能使用**：各角色技能的使用记录

事件根据重要性进行颜色编码，便于快速识别关键信息。

#### 调试面板（右侧，可选）

按 'd' 键切换显示，包含：

- 会话 ID
- 配置文件来源
- 玩家数量与类型统计
- 角色分配
- 时间限制设置
- 错误追踪

### TUI 控制

- **q**：退出游戏
- **d**：切换调试面板显示/隐藏（或使用 `--debug` 参数默认开启）
- **n**：手动进入下一步（调试用）
- **鼠标滚轮**：滚动对话历史
- **方向键**：在可聚焦组件间移动

### Console 模式

如果不想使用 TUI，可以使用 `llm-werewolf` 或 `werewolf` 命令，游戏将以纯文本日志形式自动执行并输出到终端。

## 游戏流程

1. **准备阶段**：玩家被随机分配角色
2. **夜晚阶段**：具有夜晚能力的角色按优先顺序行动
3. **白天讨论**：玩家讨论并分享信息
4. **白天投票**：玩家投票淘汰嫌疑人
5. **检查胜利**：游戏检查是否有阵营获胜
6. 重复步骤 2-5 直到满足胜利条件

## 胜利条件

游戏会在每个阶段结束后检查胜利条件：

- **村民阵营获胜**：所有狼人被淘汰
- **狼人阵营获胜**：狼人数量 ≥ 村民数量
- **恋人获胜**：只剩下两个恋人存活（恋人胜利优先于阵营胜利）

## 项目架构

项目采用模块化架构，各模块职责清晰：

```
src/llm_werewolf/
├── cli.py                 # 命令行入口（控制台模式）
├── tui.py                 # TUI 入口（交互模式）
├── ai/                    # 代理系统
│   └── agents.py         # LLM 代理实现和配置模型
├── core/                 # 核心游戏逻辑
│   ├── agent.py          # 基础代理、HumanAgent 和 DemoAgent
│   ├── game_engine.py    # 游戏引擎
│   ├── game_state.py     # 游戏状态管理
│   ├── player.py         # 玩家类
│   ├── action_selector.py # 动作选择逻辑
│   ├── events.py         # 事件系统
│   ├── victory.py        # 胜利条件检查
│   ├── serialization.py  # 序列化工具
│   ├── role_registry.py  # 角色注册与验证
│   ├── actions/          # 动作系统
│   │   ├── base.py       # 基础动作类
│   │   ├── common.py     # 通用动作
│   │   ├── villager.py   # 村民阵营动作
│   │   └── werewolf.py   # 狼人阵营动作
│   ├── config/           # 配置系统
│   │   ├── game_config.py    # 游戏配置模型
│   │   └── presets.py        # 角色预设配置
│   ├── types/            # 类型定义
│   │   ├── enums.py      # 枚举（阵营、阶段、状态等）
│   │   ├── models.py     # 数据模型
│   │   └── protocols.py  # 协议定义
│   └── roles/            # 角色实现
│       ├── base.py       # 角色基类
│       ├── werewolf.py   # 狼人阵营角色
│       ├── villager.py   # 村民阵营角色
│       └── neutral.py    # 中立角色
└── ui/                   # 用户界面
    ├── tui_app.py        # TUI 应用程序
    ├── styles.py         # TUI 样式
    └── components/       # TUI 组件
        ├── player_panel.py
        ├── game_panel.py
        ├── chat_panel.py
        └── debug_panel.py
```

### 模块说明

- **cli.py**：控制台模式的命令行界面，负责加载配置并自动启动游戏
- **tui.py**：交互模式的 TUI 入口，提供终端用户界面
- **ai/**：LLM 代理实现和配置模型（PlayerConfig、PlayersConfig）
- **core/agent.py**：基础代理协议和内置代理（HumanAgent、DemoAgent）
- **core/actions/**：动作系统，包含基础类和阵营特定动作
- **core/config/**：配置系统，包含游戏参数和角色预设
- **core/types/**：类型定义，包含枚举、数据模型和协议定义
- **core/**：游戏核心逻辑，包含角色、玩家、游戏状态、动作选择、事件和胜利检查
- **ui/**：基于 Textual 框架的终端用户界面

## 系统需求

- **Python**：3.10 或更高版本
- **操作系统**：Linux、macOS、Windows
- **终端**：支持 ANSI 颜色和 Unicode 的现代终端（用于 TUI）

### 主要依赖

- **pydantic** (≥2.12.3)：数据验证和设定管理
- **textual** (≥6.3.0)：TUI 框架
- **rich** (≥14.2.0)：终端格式化
- **openai** (≥2.5.0)：OpenAI API 客户端（用于 LLM 整合）
- **python-dotenv** (≥1.1.1)：环境变量管理
- **pyyaml** (≥6.0.3)：YAML 配置文件解析
- **fire** (≥0.7.1)：命令行界面
- **logfire** (≥4.13.2)：结构化日志记录

## 常见问题

### 如何新增更多玩家？

编辑您的 YAML 配置文件，调整 `preset` 以匹配玩家数量，并在 `players` 列表中新增玩家配置。记得玩家数量必须与 preset 的 `num_players` 一致。

### 可以混合不同的 LLM 模型吗？

可以！您可以在同一场游戏中使用不同的 LLM 提供商和模型，例如同时使用 GPT-4、Claude 和本地 Llama 模型。

### 如何让真人玩家参与游戏？

在 YAML 配置中，将某个玩家的 `model` 设置为 `human`。游戏进行时，该玩家需要通过终端输入来回应。

### 本地模型（Ollama）如何设定？

确保 Ollama 正在执行，然后在 YAML 中设定：

```yaml
  - name: Ollama 玩家
    model: llama3
    base_url: http://localhost:11434/v1
```

不需要设定 `api_key_env`。

### 如何自定义游戏设定？

游戏使用在 YAML 文件中定义的预设配置（如 `6-players`、`9-players` 等）。每个预设包含预定义的角色组合和时间限制。要调整设定，您可以修改预设配置或创建自定义配置。如需高级自定义，请参阅项目的配置系统 `src/llm_werewolf/core/config/`。

## 授权

本项目采用 [MIT License](LICENSE) 授权。

## 贡献

欢迎贡献！您可以通过以下方式参与：

1. **回报问题**：在 [Issues](https://github.com/Mai0313/LLMWereWolf/issues) 页面回报 bug 或提出功能建议
2. **提交 Pull Request**：修复 bug 或新增功能
3. **改进文档**：帮助改善 README 和代码注解
4. **分享反馈**：告诉我们您的使用体验

### 贡献流程

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

请确保您的代码：

- 遵循项目的代码风格（使用 Ruff）
- 包含适当的测试
- 更新相关文档

## 致谢

本项目使用以下优秀的开源工具构建：

- [Pydantic](https://pydantic.dev/) - 数据验证和设定管理
- [Textual](https://textual.textualize.io/) - 现代化 TUI 框架
- [Rich](https://rich.readthedocs.io/) - 精美的终端输出
- [OpenAI Python SDK](https://github.com/openai/openai-python) - LLM API 客户端
- [uv](https://docs.astral.sh/uv/) - 快速的 Python 包管理器
- [Ruff](https://github.com/astral-sh/ruff) - 极速 Python linter

## 相关链接

- [项目首页](https://github.com/Mai0313/LLMWereWolf)
- [问题追踪](https://github.com/Mai0313/LLMWereWolf/issues)

## 更新日志

请参阅 [Releases](https://github.com/Mai0313/LLMWereWolf/releases) 页面查看版本更新记录。
