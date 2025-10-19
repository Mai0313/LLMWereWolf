<center>

# LLM 狼人殺 🐺

[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/llm_werewolf/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/llm_werewolf/pulls)

</center>

一個支援多種 LLM 模型的 AI 狼人殺遊戲，具有精美的終端介面。

其他語言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特色功能

- 🎮 **完整遊戲邏輯**：包含 20+ 種角色的完整狼人殺規則實作
- 🤖 **LLM 整合**：抽象介面可輕鬆整合任何 LLM（OpenAI、Anthropic、本地模型等）
- 🖥️ **精美 TUI**：使用 Textual 框架的即時遊戲視覺化
- ⚙️ **可配置**：多種預設配置適用不同玩家數量
- 📊 **事件系統**：完整的事件記錄和遊戲狀態追蹤
- 🧪 **充分測試**：高程式碼覆蓋率與完整測試套件

## 快速開始

### 安裝

```bash
# 複製儲存庫
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# 安裝基礎依賴
uv sync

# 可選：安裝 LLM 提供商依賴
uv sync --group llm-openai      # 用於 OpenAI 模型
uv sync --group llm-anthropic   # 用於 Claude 模型
uv sync --group llm-all         # 用於所有支援的 LLM 提供商

# 使用 TUI 執行（預設，使用演示代理）
uv run llm-werewolf

# 使用命令列模式執行
uv run llm-werewolf --no-tui
```

### 環境配置

建立 `.env` 檔案配置 LLM API 金鑰：

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
# 啟動 9 人局 TUI 模式
uv run llm-werewolf --preset 9-players

# 啟動 6 人局命令列模式
uv run llm-werewolf --preset 6-players --no-tui

# 啟用除錯面板
uv run llm-werewolf --debug

# 查看說明
uv run llm-werewolf --help
```

## 支援的角色

### 狼人陣營 🐺

- **普通狼人**：在夜晚殺人的標準狼人
- **狼王**：被淘汰時可以開槍帶走一人
- **白狼王**：每隔一晚可以殺死另一個狼人
- **狼美人**：魅惑一名玩家，狼美人死亡時該玩家同死
- **守衛狼**：每晚可以保護一名狼人
- **隱狼**：預言家查驗顯示為村民
- **血月使徒**：可以轉化為狼人
- **夢魘**：可以封鎖玩家的能力

### 村民陣營 👥

- **平民**：沒有特殊能力的普通村民
- **預言家**：每晚可以查驗一名玩家的身分
- **女巫**：擁有解藥和毒藥（各一次性使用）
- **獵人**：被淘汰時可以開槍帶走一人
- **守衛**：每晚可以保護一名玩家
- **白痴**：被投票淘汰時存活但失去投票權
- **長老**：需要兩次攻擊才會死亡
- **騎士**：每局可以與一名玩家決鬥一次
- **魔術師**：可以交換兩名玩家的角色一次
- **丘比特**：第一晚將兩名玩家連結為戀人
- **烏鴉**：標記一名玩家獲得額外投票
- **守墓人**：可以查驗死亡玩家的身分

## 配置

### 使用預設配置

```bash
# 可用的預設配置
uv run llm-werewolf --preset 6-players   # 新手局（6 人）
uv run llm-werewolf --preset 9-players   # 標準局（9 人）
uv run llm-werewolf --preset 12-players  # 進階局（12 人）
uv run llm-werewolf --preset 15-players  # 完整局（15 人）
uv run llm-werewolf --preset expert      # 專家配置
uv run llm-werewolf --preset chaos       # 混亂角色組合
```

### 自訂配置

在 Python 中建立自訂配置：

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

## LLM 整合

### 使用內建 LLM 代理

套件提供多種主流 LLM 提供商的即用型代理：

```python
from llm_werewolf.ai import OpenAIAgent, AnthropicAgent, GenericLLMAgent, create_agent_from_config
from llm_werewolf import GameEngine
from llm_werewolf.config import get_preset

# 方法 1：直接建立代理
openai_agent = OpenAIAgent(model_name="gpt-4")
claude_agent = AnthropicAgent(model_name="claude-3-5-sonnet-20241022")
ollama_agent = GenericLLMAgent(model_name="llama2", base_url="http://localhost:11434/v1")

# 方法 2：從配置建立（自動從 .env 載入）
agent = create_agent_from_config(
    provider="openai",  # 或 "anthropic", "local", "xai" 等
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=500,
)

# 使用 LLM 代理設定遊戲
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

### 支援的 LLM 提供商

- **OpenAI**: GPT-4, GPT-3.5-turbo 等
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus 等
- **xAI**: Grok 模型
- **Local**: Ollama, LM Studio 或任何 OpenAI 相容端點
- **Azure OpenAI**: Azure 託管的 OpenAI 模型
- **Custom**: 任何 OpenAI 相容的 API

### 實作您自己的代理

對於自訂 LLM 整合，實作 `BaseAgent` 類別：

```python
from llm_werewolf.ai import BaseAgent


class MyLLMAgent(BaseAgent):
    def __init__(self, model_name: str = "my-model"):
        super().__init__(model_name)
        # 初始化您的 LLM 客戶端
        self.client = YourLLMClient()

    def get_response(self, message: str) -> str:
        """
        從您的 LLM 獲取回應。

        Args:
            message: 遊戲提示（角色資訊、遊戲狀態、行動請求等）

        Returns:
            str: LLM 的回應
        """
        # 加入到對話歷史（可選）
        self.add_to_history("user", message)

        # 呼叫您的 LLM API
        response = self.client.generate(message)

        # 加入回應到歷史（可選）
        self.add_to_history("assistant", response)

        return response
```

### 代理介面詳情

`BaseAgent` 提供：

- `get_response(message: str) -> str`：需要實作的主要方法（必需）
- `initialize()`：遊戲開始前呼叫的設定方法（可選）
- `reset()`：為新遊戲清除對話歷史（可選）
- `add_to_history(role: str, content: str)`：追蹤對話（可選）
- `get_history() -> list[dict]`：獲取對話歷史（可選）

## TUI 介面

TUI 提供現代化終端介面的即時視覺化：

### 介面預覽

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐺 Werewolf Game                                                    AI-Powered Werewolf  │
│ q 退出  d 切換除錯  n 下一步                                                 [00:02:34]   │
├──────────────────────┬─────────────────────────────────────────┬──────────────────────────┤
│                      │ ╭─────── 遊戲狀態 ─────────╮           │                          │
│    玩家              │ │ 🌙 第 2 回合 - 夜晚     │           │    除錯資訊              │
│ ──────────────────   │ │                             │        │ ──────────────────────   │
│ 名字      模型       │ │ 玩家總數：    8/9       │           │ 會話 ID:                 │
│           狀態       │ │ 狼人：        2         │           │   ww_20251019_163022     │
│ ──────────────────   │ │ 村民：        6         │           │                          │
│ Alice     gpt-4      │ ╰─────────────────────────────╯        │ 配置：players.yaml       │
│           ✓ 🛡️      │                                         │                          │
│ Bob       claude-3.5 │                                         │ 玩家：9                  │
│           ✓          │                                         │ AI: 6  真人: 1           │
│ Charlie   llama3     │                                         │                          │
│           ✓          │                                         │ 角色：                   │
│ David     gpt-3.5    │ ╭──── 事件聊天 ────────╮              │  - 狼人 x2               │
│           ✓ ❤️       │ │ [00:02:28] 🎮 遊戲開始│              │  - 預言家 x1             │
│ Eve       grok-beta  │ │ [00:02:29] ⏰ 階段：夜│              │  - 女巫 x1               │
│           ✓ ❤️       │ │ [00:02:30] 🐺 狼人討  │              │  - 獵人 x1               │
│ Frank     human      │ │           論目標      │              │  - 守衛 x1               │
│           ✓          │ │ [00:02:31] ⏰ 階段：白│              │  - 平民 x3               │
│ Grace     claude-3.5 │ │ [00:02:32] 💀 Iris死亡│              │                          │
│           ✓          │ │ [00:02:33] 💬 Alice：  │              │ 夜晚逾時：60s            │
│ Henry     demo       │ │           "我覺得Bob  │              │ 白天逾時：300s           │
│           ✓          │ │           行為可疑"   │              │                          │
│ Iris      demo       │ │ [00:02:34] 💬 Bob："我 │              │ 錯誤：0                  │
│           ✗          │ │           是村民！Alice│              │                          │
│                      │ │           在轉移焦點" │              │ 來源：YAML配置           │
│                      │ │ [00:02:35] 💬 Charlie: │              │                          │
│                      │ │           "昨晚的死亡  │              │                          │
│                      │ │           模式很奇怪..." │            │                          │
│                      │ ╰───────────────────────────╯          │                          │
│                      │                                         │                          │
└──────────────────────┴─────────────────────────────────────────┴──────────────────────────┘
```

### 面板說明

- **玩家面板**（左側）：顯示所有玩家的 AI 模型、狀態指示器和角色

  - ✓/✗：存活/死亡狀態
  - 🛡️：被守衛保護
  - ❤️：戀人關係
  - ☠️：被下毒
  - 🔴：被烏鴉標記

- **遊戲面板**（中央上方）：顯示當前回合、階段和即時統計資訊

  - 階段圖示：🌙 夜晚 | ☀️ 白天討論 | 🗳️ 投票 | 🏁 遊戲結束
  - 按陣營統計存活玩家數
  - 投票階段顯示票數統計

- **對話面板**（中央下方）：可捲動的事件日誌，顯示**完整的玩家討論和遊戲事件**

  - 💬 **玩家發言**：即時 AI 生成的討論、指控和辯護
  - 根據事件重要性進行顏色編碼
  - 事件圖示方便快速視覺掃描
  - 顯示白天討論階段的完整對話流程

- **除錯面板**（右側，可選）：顯示會話資訊、配置和錯誤追蹤

  - 按 'd' 鍵切換顯示
  - 顯示遊戲配置和執行時資訊

### TUI 控制

- `q`：退出應用程式
- `d`：切換除錯面板
- `n`：進入下一步（用於除錯）
- 滑鼠：捲動對話歷史

## 遊戲流程

1. **準備階段**：玩家被隨機分配角色
2. **夜晚階段**：具有夜晚能力的角色按優先順序行動
3. **白天討論**：玩家討論並分享資訊
4. **白天投票**：玩家投票淘汰嫌疑人
5. **檢查勝利**：遊戲檢查是否有陣營獲勝
6. 重複步驟 2-5 直到滿足勝利條件

## 勝利條件

- **村民獲勝**：所有狼人被淘汰
- **狼人獲勝**：狼人數量等於或超過村民
- **戀人獲勝**：只剩下兩個戀人存活

## 開發

### 執行測試

```bash
# 安裝測試依賴
uv sync --group test

# 執行所有測試
uv run pytest

# 執行並顯示覆蓋率
uv run pytest --cov=src

# 執行特定測試檔案
uv run pytest tests/core/test_roles.py -v
```

### 程式碼品質

```bash
# 安裝開發依賴
uv sync --group dev

# 執行 linter
uv run ruff check src/

# 格式化程式碼
uv run ruff format src/
```

## 架構

專案採用模組化架構：

- **Core**：遊戲邏輯（角色、玩家、狀態、引擎、勝利）
- **Config**：遊戲配置和預設
- **AI**：LLM 整合的抽象 agent 介面
- **UI**：TUI 元件（基於 Textual）
- **Utils**：輔助函數（logger、validator）

## 需求

- Python 3.10+
- 依賴：pydantic、textual、rich

## 授權

MIT License

## 貢獻

歡迎貢獻！請隨時提交 pull request 或開 issue。

## 致謝

使用以下工具建構：

- [Pydantic](https://pydantic.dev/) 用於資料驗證
- [Textual](https://textual.textualize.io/) 用於 TUI
- [Rich](https://rich.readthedocs.io/) 用於終端格式化
