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
git clone <repository-url>
cd Werewolf

# 安裝依賴
uv sync

# 使用 TUI 執行（預設）
uv run llm-werewolf

# 使用命令列模式執行
uv run llm-werewolf --no-tui
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

## 整合您自己的 LLM

套件提供抽象的 `BaseAgent` 類別，您可以為任何 LLM 實作：

```python
from llm_werewolf.ai import BaseAgent


class MyLLMAgent(BaseAgent):
    def __init__(self, model_name: str = "my-model"):
        super().__init__(model_name)
        # 在這裡初始化您的 LLM 客戶端

    def get_response(self, message: str) -> str:
        # 在這裡呼叫您的 LLM API
        # message 包含遊戲提示
        # 回傳 LLM 的回應
        response = your_llm_api_call(message)
        return response


# 在遊戲中使用
from llm_werewolf import GameEngine
from llm_werewolf.config import get_preset

config = get_preset(9)
engine = GameEngine(config)

players = [(f"player_{i}", f"AI Player {i}", MyLLMAgent()) for i in range(config.num_players)]

roles = config.to_role_list()
engine.setup_game(players, roles)
```

## TUI 介面

TUI 提供即時視覺化：

- **玩家面板**（左側）：顯示所有玩家、AI 模型和狀態
- **遊戲面板**（中央上方）：顯示當前回合、階段和統計資料
- **對話面板**（中央下方）：顯示遊戲事件和訊息
- **除錯面板**（右側）：顯示會話資訊、配置和錯誤（按 'd' 切換）

### TUI 控制

- `q`：退出應用程式
- `d`：切換除錯面板
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
