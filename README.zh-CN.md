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
uv run llm-werewolf-tui configs/gpt-5-chaos.yaml

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

### 环境配置

将 [`.env.example`](.env.example) 复制为 `.env`，并填入玩家所使用提供商的 API 密钥：

```bash
cp .env.example .env
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

### 自动角色分配

游戏会根据玩家人数（6-20 人）自动生成平衡的角色配置，无需手动设置预设组合！

各玩家人数对应的角色与时间限制定义于 [`presets.py`](src/llm_werewolf/core/config/presets.py)。

### 自定义配置

#### 玩家配置文件

```bash
# 由演示配置开始（全部为 demo 代理）
cp configs/demo.yaml my-game.yaml

# 或由支持 LLM 的样板开始
cp configs/gpt-5-chaos.yaml my-game.yaml

# 编辑配置文件
```

范例 `my-game.yaml`：

```yaml
language: zh-CN          # 语言代码（en-US, zh-TW, zh-CN）

players:
  # 游戏会根据玩家人数自动分配角色

  - name: GPT-4o 侦探
    model: gpt-4o
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: GPT-4o-mini 玩家
    model: gpt-4o-mini
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: GPT-4 分析师
    model: gpt-4
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: Claude Sonnet
    model: claude-sonnet-4-20250514
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY

  - name: DeepSeek 思考者
    model: deepseek-reasoner
    base_url: https://api.deepseek.com/v1
    api_key_env: DEEPSEEK_API_KEY

  - name: Claude Haiku
    model: claude-haiku-4-5-20251001
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY

  - name: 人类玩家
    model: human          # 真人玩家

  - name: 本地 Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # 本地模型不需要 api_key_env

  - name: 测试机器人
    model: demo           # 测试用的简单代理
```

所有字段及其默认值、是否必填，均定义于 [`player_config.py`](src/llm_werewolf/core/config/player_config.py)。

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
```

## TUI 界面

TUI (Terminal User Interface) 提供现代化终端界面的实时游戏可视化，使用 [Textual](https://textual.textualize.io/) 框架构建。

### 面板说明

#### 玩家面板（左上方）

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

#### 游戏面板（右上方）

显示当前游戏状态：

- **回合与阶段**：
    - 🌙 夜晚阶段
    - ☀️ 白天讨论阶段
    - 🗳️ 投票阶段
    - 🏁 游戏结束
- **玩家统计**：按阵营统计存活玩家数
- **投票计数**（投票阶段）：显示各玩家得票数

#### 对话面板（下方）

可滚动的事件日志，显示游戏中的所有事件和对话：

- 💬 **玩家发言**：AI 生成的讨论、指控、辩护
- 🎮 **游戏事件**：游戏开始、阶段切换等
- ⏰ **阶段变化**：夜晚、白天、投票等
- 💀 **死亡事件**：玩家死亡通知
- 🐺 **狼人行动**：狼人夜晚讨论
- 🔮 **技能使用**：各角色技能的使用记录

事件根据重要性进行颜色编码，便于快速识别关键信息。

### TUI 控制

- **q**：退出游戏
- **鼠标滚轮**：滚动对话历史
- **方向键**：在可聚焦组件间移动

游戏启动后会自动执行，无需手动干预。

### Console 模式

如果不想使用 TUI，可以使用 `llm-werewolf` 或 `werewolf` 命令，游戏将以纯文本日志形式自动执行并输出到终端。

Console 模式会显示实时状态提示，让你了解游戏进度：

- 🎬 **夜晚阶段**：显示每个角色正在行动（例如：`🎬 Seer（gpt-4）正在行动...`）
- 💬 **白天讨论**：显示每个玩家正在思考发言（例如：`💬 Alice（gpt-4）正在思考发言...`）
- 🗳️ **投票阶段**：显示每个玩家正在思考投票（例如：`🗳️ Bob（gpt-4）正在思考投票...`）

这些提示能帮助你了解游戏正在等待 LLM API 响应，而非卡住。LLM 响应通常需要数秒至数十秒不等。

**Console 模式范例输出：**

```
🎮 游戏开始，共 9 名玩家...
📋 角色分配完成
   - Werewolf x2
   - Seer x1
   - Witch x1
   - Hunter x1
   - Guard x1
   - Villager x3

🌙 === 第 1 回合：夜晚阶段 ===
🐺 狼人正在讨论目标...
🎬 Guard(gpt-4o) 正在行动...
   → 守卫保护了 Alice
🎬 Seer(claude-sonnet) 正在行动...
   → 预言家查验 Bob：村民
🎬 Werewolf(gpt-4o-mini) 正在行动...
   → 狼人杀死了 Charlie
🎬 Witch(deepseek-reasoner) 正在行动...
   → 女巫对 Charlie 使用解药

☀️ === 第 1 回合：白天阶段 ===
💬 Alice(gpt-4o) 正在思考...
💬 Alice：「昨晚很平静，但我们需要找出狼人。」
💬 Bob(claude-sonnet) 正在思考...
💬 Bob：「我注意到 David 昨天行为可疑。」
...

🗳️ === 投票阶段 ===
🗳️ Alice(gpt-4o) 正在思考投票...
   → Alice 投票给 David
🗳️ Bob(claude-sonnet) 正在思考投票...
   → Bob 投票给 David
...

📊 投票结果：
   David: 5 票
   Eve: 3 票
   Frank: 1 票

💀 David 被淘汰（村民）

🏁 === 游戏结束 ===
🎉 狼人阵营获胜！
   存活：Werewolf x2, Villager x2
```

## 游戏流程

1. **准备阶段**：玩家被随机分配角色
2. **夜晚阶段**：
    - 🌙 **旁白**：「天黑请闭眼...」
    - 🐺 **狼人讨论**：多个狼人之间可以讨论要投票杀谁（如果只有一个狼人则跳过）
    - 🐺 **狼人投票**：狼人投票选择目标
    - 🎬 **其他角色行动**：其他具有夜晚能力的角色按优先顺序行动（预言家、女巫、守卫等）
    - 🌙 **旁白**：「狼人请闭眼...」
3. **警长选举**（仅限第一轮）：
    - 🎖️ 玩家决定是否参选，候选人依次发表竞选演说
    - 🗳️ 所有人投票选出警长，此后警长的一票算 1.5 票
4. **白天讨论**：
    - ☀️ **旁白**：「天亮了，所有人请睁眼...」
    - 💬 玩家依序发言，讨论并分享信息
5. **白天投票**：
    - 🗳️ 玩家投票淘汰嫌疑人
6. **检查胜利**：游戏检查是否有阵营获胜
7. 重复步骤 2-6 直到满足胜利条件

## 胜利条件

游戏会在每个阶段结束后检查胜利条件：

- **村民阵营获胜**：所有狼人被淘汰
- **狼人阵营获胜**：狼人数量 ≥ 村民数量
- **恋人获胜**：只剩下两个恋人存活（恋人胜利优先于阵营胜利）

## 系统需求

- **Python**：3.10 或更高版本
- **操作系统**：Linux、macOS、Windows
- **终端**：支持 ANSI 颜色和 Unicode 的现代终端（用于 TUI）

### 主要依赖

请参阅 [`pyproject.toml`](pyproject.toml) 中的 `dependencies`。

## 常见问题

### 如何新增更多玩家？

编辑您的 YAML 配置文件，在 `players` 列表中新增玩家配置。游戏会根据玩家总数（支持 6-20 人）自动生成平衡的角色配置。

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

游戏会根据玩家人数（6-20 人）自动生成平衡的角色配置。角色分配和时间限制会随玩家数量增加而自动调整。如需高级自定义角色生成逻辑，请参阅 `src/llm_werewolf/core/config/presets.py` 中的 `create_game_config_from_player_count()` 函数。

## 授权

本项目采用 [MIT License](LICENSE) 授权。

## 开发

开发环境设置、测试、贡献流程、架构概览与 TUI 截图方式请见 [CONTRIBUTING.md](./.github/CONTRIBUTING.md)。

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
