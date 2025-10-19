<div align="center">

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

一个支持多种 LLM 模型的 AI 狼人杀游戏，拥有精致的终端界面（TUI）。

其他语言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特色功能

- 🎮 **完整游戏逻辑**：实现超过 20 个角色的完整狼人杀规则
- 🤖 **LLM 整合**：统一的代理接口，轻松接入任意 LLM（OpenAI、Anthropic、DeepSeek、本地模型等）
- 🖥️ **精美 TUI**：基于 Textual 打造的实时互动终端界面
- 👤 **真人玩家**：支持真人与 AI 混合对战
- ⚙️ **高度可配置**：通过 YAML 配置文件灵活调整玩家与游戏参数
- 📊 **事件系统**：完整的事件记录与游戏状态追踪
- 🧪 **充分测试**：高代码覆盖率与完备测试套件

## 快速开始

### 安装

```bash
# 复制仓库
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# 安装基础依赖
uv sync

# 可选：安装特定 LLM 提供商的依赖
uv sync --group llm-openai      # OpenAI 模型
uv sync --group llm-anthropic   # Claude 模型
uv sync --group llm-all         # 所有已支持的提供商
```

### 运行游戏

命令行入口（`llm-werewolf` 与 `werewolf`）会加载一个 YAML 配置文件，用于描述玩家与界面模式。

```bash
# 使用内建示例配置启动 TUI（使用 demo 代理）
uv run llm-werewolf configs/demo.yaml

# 启动包含 LLM 玩家的示例（需先配置 API 密钥）
uv run llm-werewolf configs/players.yaml

# 若已全局安装
llm-werewolf configs/demo.yaml

# 运行自定义配置
uv run llm-werewolf my-game.yaml

# 使用 werewolf 别名
uv run werewolf configs/demo.yaml
```

可以在 YAML 中调整以下界面选项：

- `game_type: tui` 启用交互式终端界面（默认）
- `game_type: console` 切换为纯文本日志模式
- `show_debug: true` 显示 TUI 调试面板（仅在 `tui` 模式有效）
- `preset: <preset-name>` 指定角色预设组合（如 `6-players`、`9-players`、`12-players`、`15-players`、`expert`、`chaos`）

### 环境配置

创建 `.env` 文件保存 LLM API 密钥：

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# xAI (Grok)
XAI_API_KEY=xai-...

# 本地模型（如 Ollama）无需 API 密钥
# 只需在 YAML 中设置 base_url
```

## 支持的角色

### 狼人阵营 🐺

- **普通狼人 (Werewolf)**：标准狼人，夜间结伴杀人
- **狼王 (AlphaWolf)**：被淘汰时可带走一名玩家
- **白狼王 (WhiteWolf)**：每隔一晚可杀死另一名狼人，成为独狼
- **狼美人 (WolfBeauty)**：魅惑一名玩家，狼美人被杀后该玩家同亡
- **守卫狼 (GuardianWolf)**：每晚可保护一名狼人
- **隐狼 (HiddenWolf)**：在预言家查验中显示为村民
- **血月使徒 (BloodMoonApostle)**：可以转化为狼人
- **梦魇狼 (NightmareWolf)**：封锁一名玩家的能力

### 村民阵营 👥

- **平民 (Villager)**：没有特殊能力的普通村民
- **预言家 (Seer)**：每晚可查验一名玩家的阵营
- **女巫 (Witch)**：拥有一瓶解药和一瓶毒药
- **猎人 (Hunter)**：被淘汰时可以带走一人
- **守卫 (Guard)**：每晚可保护一名玩家免受狼人攻击
- **白痴 (Idiot)**：被投票处决时翻牌存活但失去投票权
- **长老 (Elder)**：需要两次攻击才会死亡
- **骑士 (Knight)**：每局可以与一名玩家决斗一次
- **魔术师 (Magician)**：可以交换两名玩家的角色各一次
- **丘比特 (Cupid)**：首夜连结两名玩家成为恋人
- **乌鸦 (Raven)**：标记一名玩家，使其额外获得一票
- **守墓人 (GraveyardKeeper)**：可以查看死亡玩家的身份

### 中立角色 👻

- **盗贼 (Thief)**：首夜可以从两张额外角色牌中挑选一张
- **恋人 (Lover)**：由丘比特连结，一方死亡另一方殉情

## 配置

### 使用预设

在配置文件中设置 `preset` 字段即可应用内建角色组合：

- `6-players`：新手局（6 人）— 2 狼人 + 预言家、女巫、2 平民
- `9-players`：标准局（9 人）— 2 狼人 + 预言家、女巫、猎人、守卫、3 平民
- `12-players`：进阶局（12 人）— 3 狼人（含狼王）+ 预言家、女巫、猎人、守卫、丘比特、白痴、3 平民
- `15-players`：完整版（15 人）— 4 狼人（含狼王、白狼王）+ 预言家、女巫、猎人、守卫、丘比特、白痴、长老、乌鸦、3 平民
- `expert`：专家配置（12 人），包含多种特殊狼人
- `chaos`：混乱配置（10 人），适合进阶玩家的少见组合

### 自定义配置

#### 玩家配置文件

```bash
# 从示例配置开始（全部为 demo 代理）
cp configs/demo.yaml my-game.yaml

# 或从支持 LLM 的示例开始
cp configs/players.yaml my-game.yaml

# 编辑配置
# configs/players.yaml 包含字段说明与示例
```

示例 `my-game.yaml`：

```yaml
preset: 6-players        # 选择预设
game_type: tui           # 界面模式：tui 或 console
show_debug: false        # 是否显示调试面板

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

  - name: DeepSeek 思考者
    model: deepseek-reasoner
    base_url: https://api.deepseek.com/v1
    api_key_env: DEEPSEEK_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: 真人玩家
    model: human          # 玩家手动操作

  - name: 本地 Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # 本地模型无需 api_key_env

  - name: 测试机器人
    model: demo           # 测试用简易代理
```

**配置字段说明：**

- `preset`：必填，决定角色组合与玩家数量
- `game_type`：可选，默认为 `tui`
- `show_debug`：可选，默认为 `false`
- `players`：必填，玩家列表，数量需与预设的 `num_players` 相同

**玩家配置字段：**

- `name`：玩家显示名称
- `model`：模型类型
  - `human`：真人玩家（终端输入）
  - `demo`：测试用随机代理
  - LLM 模型名称：如 `gpt-4o`、`claude-3-5-sonnet-20241022`、`llama3`
- `base_url`：API 端点（LLM 模型必填）
- `api_key_env`：存放 API 密钥的环境变量名称（需要鉴权时必填）
- `temperature`：可选，默认 0.7
- `max_tokens`：可选，默认 500

**支持的模型类型：**

- **OpenAI 兼容 API**：任何遵循 OpenAI Chat Completions 协议的服务
- **真人玩家**：`model: human`
- **测试代理**：`model: demo`

**本地模型示例：**

使用本地模型（如 Ollama）时可省略 `api_key_env`：

```yaml
  - name: Ollama Llama3
    model: llama3
    base_url: http://localhost:11434/v1
    temperature: 0.7
    max_tokens: 500
```

## 代理系统

### 内建代理类型

项目内建三种代理：

1. **LLMAgent**：支持任何 OpenAI 兼容 API 的 LLM 模型
2. **HumanAgent**：真人玩家通过终端输入
3. **DemoAgent**：返回随机回应的测试代理

### 通过 YAML 配置代理

推荐在 YAML 配置文件中设置代理（见[配置](#%E9%85%8D%E7%BD%AE)章节）。

### 程序化使用代理

如果需要在 Python 代码中直接创建代理：

```python
from llm_werewolf.ai import LLMAgent, HumanAgent, DemoAgent, create_agent, PlayerConfig
from llm_werewolf.core import GameEngine
from llm_werewolf.config import get_preset_by_name

# 方法 1：直接实例化代理
llm_agent = LLMAgent(
    model_name="gpt-4o",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    temperature=0.7,
    max_tokens=500,
)

human_agent = HumanAgent(model_name="human")
demo_agent = DemoAgent(model_name="demo")

# 方法 2：通过配置对象创建（自动从环境变量读取 API 密钥）
player_config = PlayerConfig(
    name="GPT-4 玩家",
    model="gpt-4o",
    base_url="https://api.openai.com/v1",
    api_key_env="OPENAI_API_KEY",
    temperature=0.7,
    max_tokens=500,
)
agent = create_agent(player_config)

# 设置游戏
game_config = get_preset_by_name("9-players")
engine = GameEngine(game_config)

players = [
    ("player_1", "GPT-4 玩家", llm_agent),
    ("player_2", "真人玩家", human_agent),
    ("player_3", "测试机器人", demo_agent),
    # ... 更多玩家
]

roles = game_config.to_role_list()
engine.setup_game(players, roles)
result = engine.play_game()
```

### 支持的 LLM 提供商

由于实现基于 OpenAI 兼容 API，以下提供商均可使用：

- **OpenAI**：GPT-4、GPT-4o、GPT-3.5-turbo 等
- **Anthropic**：Claude 3.5 Sonnet、Claude 3 Opus、Claude 3 Haiku 等
- **DeepSeek**：DeepSeek-Reasoner、DeepSeek-Chat 等
- **xAI**：Grok 系列模型
- **本地模型**：Ollama、LM Studio、vLLM 等
- **其他兼容 API**：任何支持 OpenAI Chat Completions 协议的服务

### 实现自定义代理

可以通过实现简洁的代理接口来接入自定义提供商：

```python
class MyCustomAgent:
    """自定义代理实现示例。"""

    def __init__(self, client: YourLLMClient) -> None:
        self.client = client
        self.model_name = "my-custom-model"
        self._history: list[dict[str, str]] = []

    def get_response(self, message: str) -> str:
        """获取 LLM 回复。

        Args:
            message: 用户消息或游戏提示

        Returns:
            str: LLM 的回复
        """
        self._history.append({"role": "user", "content": message})
        reply = self.client.generate(message, history=self._history)
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        """可选：在新游戏开始前清空对话记录。"""
        self._history.clear()
```

**必须实现的接口：**

- `model_name`（属性）：模型名称
- `get_response(message: str) -> str`：接收消息并返回回复

**可选帮助方法：**

- `reset()`：清空内部状态（对话历史等）
- `add_to_history(role: str, content: str)`：手动追加历史记录
- `get_history() -> list[dict[str, str]]`：读取历史记录

自定义代理可以直接传入 `GameEngine.setup_game()`。

## TUI 界面

TUI（Terminal User Interface）基于 [Textual](https://textual.textualize.io/) 提供现代终端中的实时可视化体验。

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
│ Henry     demo       │ │            "我觉得 Bob │               │ 白天超时：300s                │
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

展示所有玩家信息：

- **名字**：玩家显示名称
- **模型**：所用 AI 模型或 `human`/`demo`
- **状态指示**：
  - ✓：存活
  - ✗：死亡
  - 🛡️：被守卫保护
  - ❤️：恋人关系
  - ☠️：被女巫下毒
  - 🔴：被乌鸦标记

#### 游戏面板（上方中央）

展示当前游戏状态：

- **回合与阶段**：
  - 🌙 夜晚阶段
  - ☀️ 白天讨论阶段
  - 🗳️ 投票阶段
  - 🏁 游戏结束
- **玩家统计**：按阵营统计存活玩家数
- **投票统计**：投票阶段显示票数

#### 对话面板（下方中央）

可滚动的事件日志，记录所有游戏事件与对话：

- 💬 **玩家发言**：AI 生成的讨论、指控与辩护
- 🎮 **游戏事件**：游戏开始、阶段切换等
- ⏰ **阶段变化**：夜晚、白天、投票等
- 💀 **死亡事件**：玩家死亡通知
- 🐺 **狼人行动**：夜间狼人讨论
- 🔮 **技能使用**：角色技能触发记录

事件根据重要程度进行颜色区分，便于快速识别关键信息。

#### 调试面板（右侧，可选）

按 `d` 键切换显示，包含：

- 会话 ID
- 配置文件来源
- 玩家数量与类型
- 角色分配
- 各阶段超时时间
- 错误追踪

### TUI 控制

- `q`：退出游戏
- `d`：切换调试面板
- `n`：手动进入下一步（调试）
- 鼠标滚轮：滚动对话历史
- 方向键：在可聚焦组件间移动

### Console 模式

若不想使用 TUI，可在配置中设置 `game_type: console`，游戏将以纯文本日志输出。

## 游戏流程

1. **准备阶段**：随机分配角色
2. **夜晚阶段**：具备夜行能力的角色按优先级行动
3. **白天讨论**：玩家交流信息并讨论
4. **白天投票**：玩家投票淘汰嫌疑人
5. **胜利判定**：检测是否满足胜利条件
6. 重复步骤 2–5 直至出现胜利阵营

## 胜利条件

每个阶段结束后都会检查胜利条件：

- **村民阵营获胜**：所有狼人被淘汰
- **狼人阵营获胜**：狼人数量 ≥ 村民数量
- **恋人获胜**：只剩两名恋人存活（优先级高于阵营胜利）

## 开发

### 开发环境

```bash
# 克隆项目
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# 安装全量依赖（包含开发与测试）
uv sync --all-groups

# 或按需安装
uv sync                     # 仅基础依赖
uv sync --group dev         # 开发工具
uv sync --group test        # 测试依赖
uv sync --group llm-all     # 全部 LLM 扩展
```

### 执行测试

```bash
# 运行全部测试
uv run pytest

# 带覆盖率报告
uv run pytest --cov=src --cov-report=term-missing

# 运行单个测试文件
uv run pytest tests/core/test_roles.py -v

# 运行单个测试函数
uv run pytest tests/core/test_roles.py::test_werewolf_role -v

# 并行执行测试（更快）
uv run pytest -n auto
```

### 代码质量

```bash
# 执行 Ruff 检查
uv run ruff check src/

# 自动修复可修复的问题
uv run ruff check --fix src/

# 格式化代码
uv run ruff format src/

# 类型检查（若已配置 mypy）
uv run mypy src/
```

### Pre-commit

项目提供 pre-commit 配置，在提交前自动检查代码质量：

```bash
# 安装 pre-commit 钩子
uv run pre-commit install

# 手动运行全部钩子
uv run pre-commit run --all-files
```

### Makefile 快捷命令

Makefile 提供常用命令封装：

```bash
# 查看可用命令
make help

# 清理生成的文件
make clean

# 格式化代码（调用 pre-commit）
make format

# 运行全部测试
make test

# 生成文档
make gen-docs
```

## 项目结构

项目采用模块化设计，职责划分清晰：

```
src/llm_werewolf/
├── cli.py                 # 命令行入口
├── ai/                    # 代理系统
│   ├── agents.py         # LLM/Human/Demo 代理实现
│   └── message.py        # 消息处理
├── config/               # 配置系统
│   ├── game_config.py    # 游戏配置模型
│   └── role_presets.py   # 角色预设配置
├── core/                 # 核心游戏逻辑
│   ├── game_engine.py    # 游戏引擎
│   ├── game_state.py     # 游戏状态管理
│   ├── player.py         # 玩家模型
│   ├── actions.py        # 行动系统
│   ├── events.py         # 事件系统
│   ├── victory.py        # 胜利条件判定
│   └── roles/            # 角色实现
│       ├── base.py       # 角色基类
│       ├── werewolf.py   # 狼人阵营角色
│       ├── villager.py   # 村民阵营角色
│       └── neutral.py    # 中立角色
├── ui/                   # 用户界面
│   ├── tui_app.py        # TUI 应用
│   ├── styles.py         # TUI 样式
│   └── components/       # TUI 组件
│       ├── player_panel.py
│       ├── game_panel.py
│       ├── chat_panel.py
│       └── debug_panel.py
└── utils/                # 工具函数
    └── validator.py      # 校验工具
```

### 模块说明

- **cli.py**：加载配置并启动游戏
- **ai/**：AI 代理与真人玩家接口实现
- **config/**：游戏参数与角色预设
- **core/**：核心逻辑，包含角色、玩家、状态、行动与事件系统
- **ui/**：基于 Textual 的终端界面组件
- **utils/**：通用工具函数

## 系统需求

- **Python**：3.10 或更高版本
- **操作系统**：Linux、macOS、Windows
- **终端**：支持 ANSI 色彩与 Unicode 的现代终端（用于 TUI）

### 主要依赖

- **pydantic** (≥2.12.3)：数据验证与配置管理
- **textual** (≥6.3.0)：TUI 框架
- **rich** (≥14.2.0)：终端渲染
- **openai** (≥2.5.0)：OpenAI API 客户端（用于 LLM 整合）
- **python-dotenv** (≥1.1.1)：环境变量管理
- **pyyaml** (≥6.0.3)：YAML 解析
- **fire** (≥0.7.1)：命令行接口
- **logfire** (≥4.13.2)：结构化日志

## 常见问题

### 如何增加玩家数量？

编辑 YAML 配置文件，选择匹配玩家数量的 `preset`，并在 `players` 列表中添加对应配置。请确保玩家数量与预设的 `num_players` 保持一致。

### 可以混用不同的 LLM 模型吗？

可以！同一局游戏中可以混合使用多个提供商与模型，例如同时使用 GPT-4、Claude 和本地 Llama 模型。

### 如何让真人玩家加入？

在 YAML 中将某个玩家的 `model` 设置为 `human`。游戏过程中该玩家会直接在终端输入回应。

### 如何配置本地模型（如 Ollama）？

确保 Ollama 正在运行，然后在 YAML 中设置：

```yaml
  - name: Ollama 玩家
    model: llama3
    base_url: http://localhost:11434/v1
```

无需设置 `api_key_env`。

### 游戏节奏太快或太慢怎么办？

可自定义 `GameConfig` 调整各阶段的时间限制：

```python
from llm_werewolf.config import GameConfig

config = GameConfig(
    num_players=9,
    role_names=[...],
    night_timeout=90,  # 夜晚阶段 90 秒
    day_timeout=600,  # 白天讨论 600 秒
    vote_timeout=90,  # 投票阶段 90 秒
)
```

### 如何自定义角色组合？

创建自定义 `GameConfig` 并指定需要的角色：

```python
from llm_werewolf.config import GameConfig

config = GameConfig(
    num_players=10,
    role_names=[
        "Werewolf",
        "AlphaWolf",
        "WhiteWolf",
        "Seer",
        "Witch",
        "Hunter",
        "Guard",
        "Villager",
        "Villager",
        "Villager",
    ],
)
```

## 授权

本项目使用 [MIT License](LICENSE) 授权。

## 贡献

欢迎贡献！你可以通过以下方式参与：

1. **反馈问题**：在 [Issues](https://github.com/Mai0313/LLMWereWolf/issues) 页面报告 bug 或提交功能建议
2. **提交 Pull Request**：修复问题或新增功能
3. **改进文档**：完善 README 与代码注释
4. **分享反馈**：告诉我们你的使用体验

### 贡献流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 发起 Pull Request

请确保你的改动：

- 遵循项目代码风格（使用 Ruff）
- 包含相应测试
- 更新相关文档

## 致谢

项目基于以下优秀的开源工具构建：

- [Pydantic](https://pydantic.dev/) — 数据验证与配置管理
- [Textual](https://textual.textualize.io/) — 现代化 TUI 框架
- [Rich](https://rich.readthedocs.io/) — 精美的终端输出
- [OpenAI Python SDK](https://github.com/openai/openai-python) — LLM API 客户端
- [uv](https://docs.astral.sh/uv/) — 高速 Python 包管理器
- [Ruff](https://github.com/astral-sh/ruff) — 极速 Python linter

## 相关链接

- [项目主页](https://github.com/Mai0313/LLMWereWolf)
- [问题追踪](https://github.com/Mai0313/LLMWereWolf/issues)
- [文档站点](https://mai0313.github.io/llm_werewolf)（建设中）

## 更新日志

请参阅 [Releases](https://github.com/Mai0313/LLMWereWolf/releases) 获取版本更新记录。
