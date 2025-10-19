<center>

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

</center>

一个支持多种 LLM 模型的 AI 狼人杀游戏，具有精美的终端界面。

其他语言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特色功能

- 🎮 **完整游戏逻辑**：包含 20+ 种角色的完整狼人杀规则实作
- 🤖 **LLM 整合**：抽象接口可轻松整合任何 LLM（OpenAI、Anthropic、本地模型等）
- 🖥️ **精美 TUI**：使用 Textual 框架的实时游戏可视化
- ⚙️ **可配置**：多种预设配置适用不同玩家数量
- 📊 **事件系统**：完整的事件记录和游戏状态追踪
- 🧪 **充分测试**：高代码覆盖率与完整测试套件

## 快速开始

### 安装

```bash
# 复制仓库
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# 安装基础依赖
uv sync

# 可选：安装 LLM 提供商依赖
uv sync --group llm-openai      # 用于 OpenAI 模型
uv sync --group llm-anthropic   # 用于 Claude 模型
uv sync --group llm-all         # 用于所有支持的 LLM 提供商
```

### 运行游戏

命令行入口（`llm-werewolf` 与 `werewolf`）需要读取一个 YAML 配置文件，其中定义玩家与界面模式。

```bash
# 使用内建演示配置启动 TUI
uv run llm-werewolf configs/demo.yaml

# 如果已全局安装套件
llm-werewolf configs/demo.yaml

# 运行自定义配置
uv run llm-werewolf my-game.yaml
```

在 YAML 中可以控制界面模式：

- `game_type: tui` 开启交互式终端界面
- `game_type: console` 使用纯命令行输出
- `show_debug: true` 在 TUI 中显示调试面板（仅 `tui` 模式有效）

### 环境配置

创建 `.env` 文件配置 LLM API 密钥：

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# xAI (Grok)
XAI_API_KEY=xai-...
XAI_MODEL=grok-beta

# 本地模型（Ollama 等）
LOCAL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL=llama2
```

### 基本使用

```bash
# 运行任何配置（界面模式由 YAML 决定）
uv run llm-werewolf my-game.yaml

# 使用别名 werewolf
uv run werewolf my-game.yaml

# 直接运行模块
uv run python -m llm_werewolf.cli my-game.yaml
```

## 支持的角色

### 狼人阵营 🐺

- **普通狼人**：在夜晚杀人的标准狼人
- **狼王**：被淘汰时可以开枪带走一人
- **白狼王**：每隔一晚可以杀死另一个狼人
- **狼美人**：魅惑一名玩家，狼美人死亡时该玩家同死
- **守卫狼**：每晚可以保护一名狼人
- **隐狼**：预言家查验显示为村民
- **血月使徒**：可以转化为狼人
- **梦魇**：可以封锁玩家的能力

### 村民阵营 👥

- **平民**：没有特殊能力的普通村民
- **预言家**：每晚可以查验一名玩家的身份
- **女巫**：拥有解药和毒药（各一次性使用）
- **猎人**：被淘汰时可以开枪带走一人
- **守卫**：每晚可以保护一名玩家
- **白痴**：被投票淘汰时存活但失去投票权
- **长老**：需要两次攻击才会死亡
- **骑士**：每局可以与一名玩家决斗一次
- **魔术师**：可以交换两名玩家的角色一次
- **丘比特**：第一晚将两名玩家连结为恋人
- **乌鸦**：标记一名玩家获得额外投票
- **守墓人**：可以查验死亡玩家的身份

## 配置

### 使用预设配置

在配置文件中设置 `preset` 字段即可使用内建的角色组合，可选值包括：

- `6-players`：新手局（6 人）
- `9-players`：标准局（9 人）
- `12-players`：进阶局（12 人）
- `15-players`：完整局（15 人）
- `expert`：专家级组合
- `chaos`：混乱角色组合

### 自定义配置

```bash
# 从演示配置开始（全部为 demo 代理）
cp configs/demo.yaml my-game.yaml

# 或从支持 LLM 的范例开始
cp configs/players.yaml my-game.yaml

# 编辑配置文件
# configs/players.yaml 内含字段说明
```

范例 `players.yaml`：

```yaml
preset: 9-players
game_type: tui
show_debug: false

players:
  - name: GPT-4 侦探
    model: gpt-4o
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: Claude 分析师
    model: claude-3-5-sonnet-20241022
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: 人类玩家
    model: human

  - name: 本地 Llama
    model: llama3
    base_url: http://localhost:11434/v1
```

支持的模型类型：

- 任意兼容 OpenAI Chat Completions 的模型（需要 `model` + `base_url` + `api_key_env`）
- `human`：通过控制台输入的真人玩家
- `demo`：用于测试的演示机器人

对不需要认证的本地端点，可以省略 `api_key_env`。

## LLM 整合

### 使用内置 LLM 代理

套件提供多种主流 LLM 提供商的即用型代理：

```python
from llm_werewolf.ai import OpenAIAgent, AnthropicAgent, GenericLLMAgent, create_agent_from_config
from llm_werewolf import GameEngine
from llm_werewolf.config import get_preset

# 方法 1：直接创建代理
openai_agent = OpenAIAgent(model_name="gpt-4")
claude_agent = AnthropicAgent(model_name="claude-3-5-sonnet-20241022")
ollama_agent = GenericLLMAgent(model_name="llama2", base_url="http://localhost:11434/v1")

# 方法 2：从配置创建（自动从 .env 加载）
agent = create_agent_from_config(
    provider="openai",  # 或 "anthropic", "local", "xai" 等
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=500,
)

# 使用 LLM 代理设置游戏
config = get_preset("9-players")
engine = GameEngine(config)

players = [
    ("p1", "GPT-4 玩家", OpenAIAgent("gpt-4")),
    ("p2", "Claude 玩家", AnthropicAgent("claude-3-5-sonnet-20241022")),
    ("p3", "Llama 玩家", GenericLLMAgent("llama2")),
    # ... 更多玩家
]

roles = config.to_role_list()
engine.setup_game(players, roles)
```

### 支持的 LLM 提供商

- **OpenAI**: GPT-4, GPT-3.5-turbo 等
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus 等
- **xAI**: Grok 模型
- **Local**: Ollama, LM Studio 或任何 OpenAI 兼容端点
- **Azure OpenAI**: Azure 托管的 OpenAI 模型
- **Custom**: 任何 OpenAI 兼容的 API

### 实现您自己的代理

自定义提供者只需遵守一个轻量协议：代理需要 `model_name` 属性与 `get_response(message: str) -> str` 方法。

```python
class MyLLMAgent:
    def __init__(self, client: YourLLMClient) -> None:
        self.client = client
        self.model_name = "my-llm"
        self._history: list[dict[str, str]] = []

    def get_response(self, message: str) -> str:
        self._history.append({"role": "user", "content": message})
        reply = self.client.generate(message)
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        """可选：在新游戏前清空状态。"""
        self._history.clear()
```

可以直接把自定义代理传入 `GameEngine.setup_game`，或扩展 `create_agent()` 以便通过 YAML 配置加载。

### 代理协议

代理可以根据需要补充以下辅助方法：

- `reset()`：在新游戏前清理内部状态
- `add_to_history(role: str, content: str)`：预先载入对话
- `get_history() -> list[dict[str, str]]`：查看缓存的消息
- `initialize()`：第一次响应前执行延迟初始化

## TUI 界面

TUI 提供现代化终端界面的实时可视化：

### 界面预览

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐺 Werewolf Game                                                    AI-Powered Werewolf  │
│ q 退出  d 切换调试  n 下一步                                                 [00:02:34]   │
├──────────────────────┬─────────────────────────────────────────┬──────────────────────────┤
│                      │ ╭─────── 游戏状态 ─────────╮           │                          │
│    玩家              │ │ 🌙 第 2 回合 - 夜晚     │           │    调试信息              │
│ ──────────────────   │ │                             │        │ ──────────────────────   │
│ 名字      模型       │ │ 玩家总数：    8/9       │           │ 会话 ID:                 │
│           状态       │ │ 狼人：        2         │           │   ww_20251019_163022     │
│ ──────────────────   │ │ 村民：        6         │           │                          │
│ Alice     gpt-4      │ ╰─────────────────────────────╯        │ 配置：players.yaml       │
│           ✓ 🛡️      │                                         │                          │
│ Bob       claude-3.5 │                                         │ 玩家：9                  │
│           ✓          │                                         │ AI: 6  真人: 1           │
│ Charlie   llama3     │                                         │                          │
│           ✓          │                                         │ 角色：                   │
│ David     gpt-3.5    │ ╭──── 事件聊天 ────────╮              │  - 狼人 x2               │
│           ✓ ❤️       │ │ [00:02:28] 🎮 游戏开始│              │  - 预言家 x1             │
│ Eve       grok-beta  │ │ [00:02:29] ⏰ 阶段：夜│              │  - 女巫 x1               │
│           ✓ ❤️       │ │ [00:02:30] 🐺 狼人讨  │              │  - 猎人 x1               │
│ Frank     human      │ │           论目标      │              │  - 守卫 x1               │
│           ✓          │ │ [00:02:31] ⏰ 阶段：白│              │  - 平民 x3               │
│ Grace     claude-3.5 │ │ [00:02:32] 💀 Iris死亡│              │                          │
│           ✓          │ │ [00:02:33] 💬 Alice：  │              │ 夜晚超时：60s            │
│ Henry     demo       │ │           "我觉得Bob  │              │ 白天超时：300s           │
│           ✓          │ │           行为可疑"   │              │                          │
│ Iris      demo       │ │ [00:02:34] 💬 Bob："我 │              │ 错误：0                  │
│           ✗          │ │           是村民！Alice│              │                          │
│                      │ │           在转移焦点" │              │ 来源：YAML配置           │
│                      │ │ [00:02:35] 💬 Charlie: │              │                          │
│                      │ │           "昨晚的死亡  │              │                          │
│                      │ │           模式很奇怪..." │            │                          │
│                      │ ╰───────────────────────────╯          │                          │
│                      │                                         │                          │
└──────────────────────┴─────────────────────────────────────────┴──────────────────────────┘
```

### 面板说明

- **玩家面板**（左侧）：显示所有玩家的 AI 模型、状态指示器和角色

  - ✓/✗：存活/死亡状态
  - 🛡️：被守卫保护
  - ❤️：恋人关系
  - ☠️：被下毒
  - 🔴：被乌鸦标记

- **游戏面板**（中央上方）：显示当前回合、阶段和实时统计信息

  - 阶段图标：🌙 夜晚 | ☀️ 白天讨论 | 🗳️ 投票 | 🏁 游戏结束
  - 按阵营统计存活玩家数
  - 投票阶段显示票数统计

- **对话面板**（中央下方）：可滚动的事件日志，显示**完整的玩家讨论和游戏事件**

  - 💬 **玩家发言**：实时 AI 生成的讨论、指控和辩护
  - 根据事件重要性进行颜色编码
  - 事件图标方便快速视觉扫描
  - 显示白天讨论阶段的完整对话流程

- **调试面板**（右侧，可选）：显示会话信息、配置和错误追踪

  - 按 'd' 键切换显示
  - 显示游戏配置和运行时信息

### TUI 控制

- `q`：退出应用程序
- `d`：切换调试面板
- `n`：进入下一步（用于调试）
- 鼠标：滚动对话历史

## 游戏流程

1. **准备阶段**：玩家被随机分配角色
2. **夜晚阶段**：具有夜晚能力的角色按优先顺序行动
3. **白天讨论**：玩家讨论并分享信息
4. **白天投票**：玩家投票淘汰嫌疑人
5. **检查胜利**：游戏检查是否有阵营获胜
6. 重复步骤 2-5 直到满足胜利条件

## 胜利条件

- **村民获胜**：所有狼人被淘汰
- **狼人获胜**：狼人数量等于或超过村民
- **恋人获胜**：只剩下两个恋人存活

## 开发

### 执行测试

```bash
# 安装测试依赖
uv sync --group test

# 执行所有测试
uv run pytest

# 执行并显示覆盖率
uv run pytest --cov=src

# 执行特定测试文件
uv run pytest tests/core/test_roles.py -v
```

### 代码质量

```bash
# 安装开发依赖
uv sync --group dev

# 执行 linter
uv run ruff check src/

# 格式化代码
uv run ruff format src/
```

## 架构

项目采用模块化架构：

- **Core**：游戏逻辑（角色、玩家、状态、引擎、胜利）
- **Config**：游戏配置和预设
- **AI**：LLM 整合的抽象 agent 接口
- **UI**：TUI 组件（基于 Textual）
- **Utils**：辅助函数（校验器）

## 需求

- Python 3.10+
- 依赖：pydantic、textual、rich

## 授权

MIT License

## 贡献

欢迎贡献！请随时提交 pull request 或开 issue。

## 致谢

使用以下工具构建：

- [Pydantic](https://pydantic.dev/) 用于数据验证
- [Textual](https://textual.textualize.io/) 用于 TUI
- [Rich](https://rich.readthedocs.io/) 用于终端格式化
