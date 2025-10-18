<center>

# LLM 狼人杀 🐺

[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/llm_werewolf/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/llm_werewolf/pulls)

</center>

一个支持多种 LLM 模型的 AI 狼人杀游戏，具有精美的终端界面。

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
git clone <repository-url>
cd Werewolf

# 安装依赖
uv sync

# 使用 TUI 执行（默认）
uv run llm-werewolf

# 使用命令行模式执行
uv run llm-werewolf --no-tui
```

### 基本使用

```bash
# 启动 9 人局 TUI 模式
uv run llm-werewolf --preset 9-players

# 启动 6 人局命令行模式
uv run llm-werewolf --preset 6-players --no-tui

# 启用调试面板
uv run llm-werewolf --debug

# 查看说明
uv run llm-werewolf --help
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

```bash
# 可用的预设配置
uv run llm-werewolf --preset 6-players   # 新手局（6 人）
uv run llm-werewolf --preset 9-players   # 标准局（9 人）
uv run llm-werewolf --preset 12-players  # 进阶局（12 人）
uv run llm-werewolf --preset 15-players  # 完整局（15 人）
uv run llm-werewolf --preset expert      # 专家配置
uv run llm-werewolf --preset chaos       # 混乱角色组合
```

### 自定义配置

在 Python 中创建自定义配置：

```python
from llm_werewolf import GameConfig

config = GameConfig(
    num_players=9,
    role_names=[
        "Werewolf",
        "Werewolf",
        "Seer",
        "Witch",
        "Hunter",
        "Villager",
        "Villager",
        "Villager",
        "Villager",
    ],
    night_timeout=60,
    day_timeout=300,
)
```

## 整合您自己的 LLM

套件提供抽象的 `BaseAgent` 类，您可以为任何 LLM 实作：

```python
from llm_werewolf.ai import BaseAgent


class MyLLMAgent(BaseAgent):
    def __init__(self, model_name: str = "my-model"):
        super().__init__(model_name)
        # 在这里初始化您的 LLM 客户端

    def get_response(self, message: str) -> str:
        # 在这里调用您的 LLM API
        # message 包含游戏提示
        # 返回 LLM 的响应
        response = your_llm_api_call(message)
        return response


# 在游戏中使用
from llm_werewolf import GameEngine
from llm_werewolf.config import get_preset

config = get_preset(9)
engine = GameEngine(config)

players = [(f"player_{i}", f"AI Player {i}", MyLLMAgent()) for i in range(config.num_players)]

roles = config.to_role_list()
engine.setup_game(players, roles)
```

## TUI 界面

TUI 提供实时可视化：

- **玩家面板**（左侧）：显示所有玩家、AI 模型和状态
- **游戏面板**（中央上方）：显示当前回合、阶段和统计数据
- **对话面板**（中央下方）：显示游戏事件和消息
- **调试面板**（右侧）：显示会话信息、配置和错误（按 'd' 切换）

### TUI 控制

- `q`：退出应用程序
- `d`：切换调试面板
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
- **Utils**：辅助函数（logger、validator）

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
