<div align="center" markdown="1">

# LLM 狼人殺 🐺

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

一個支援多種 LLM 模型的 AI 狼人殺遊戲，具有精美的終端介面 (TUI)。

其他語言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特色功能

- 🎮 **完整遊戲邏輯**：包含 20+ 種角色的完整狼人殺規則實作
- 🤖 **LLM 整合**：統一的代理介面，輕鬆整合任何 LLM（OpenAI、Anthropic、DeepSeek、本地模型等）
- 🖥️ **精美 TUI**：使用 Textual 框架的即時遊戲視覺化，支援互動式終端介面
- 👤 **真人玩家**：支援真人玩家與 AI 混合遊戲
- ⚙️ **可配置**：透過 YAML 配置檔案靈活設定玩家和遊戲參數
- 📊 **事件系統**：完整的事件記錄和遊戲狀態追蹤
- 🧪 **充分測試**：高程式碼覆蓋率與完整測試套件

## 快速開始

### 安裝

```bash
# 複製儲存庫
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# 安裝依賴
uv sync
```

### 執行遊戲

專案提供兩種執行模式,透過不同的命令列入口來選擇:

**TUI 模式（互動式終端介面）：**

```bash
# 使用內建示範配置啟動 TUI（使用 demo 代理測試）
uv run llm-werewolf-tui configs/demo.yaml

# 使用 LLM 玩家配置（需先設定 API 金鑰）
uv run llm-werewolf-tui configs/gpt-5-chaos.yaml

# 若已全域安裝套件
llm-werewolf-tui configs/demo.yaml

# 使用 werewolf-tui 別名
uv run werewolf-tui configs/demo.yaml
```

**Console 模式（純文字日誌）：**

```bash
# 使用 Console 模式（自動執行）
uv run llm-werewolf configs/demo.yaml

# 或使用別名
uv run werewolf configs/demo.yaml
```

### 環境配置

將 [`.env.example`](.env.example) 複製為 `.env`，並填入玩家所使用提供商的 API 金鑰：

```bash
cp .env.example .env
```

## 支援的角色

### 狼人陣營 🐺

- **普通狼人 (Werewolf)**：在夜晚集體殺人的標準狼人
- **狼王 (AlphaWolf)**：被淘汰時可以開槍帶走一人
- **白狼王 (WhiteWolf)**：每隔一晚可以殺死另一個狼人，成為獨狼
- **狼美人 (WolfBeauty)**：魅惑一名玩家，狼美人死亡時該玩家同死
- **守衛狼 (GuardianWolf)**：每晚可以保護一名狼人
- **隱狼 (HiddenWolf)**：預言家查驗顯示為村民
- **血月使徒 (BloodMoonApostle)**：可以轉化為狼人
- **夢魘狼 (NightmareWolf)**：可以封鎖玩家的能力

### 村民陣營 👥

- **平民 (Villager)**：沒有特殊能力的普通村民
- **預言家 (Seer)**：每晚可以查驗一名玩家的身分（狼人或村民）
- **女巫 (Witch)**：擁有解藥和毒藥（各一次性使用）
- **獵人 (Hunter)**：被淘汰時可以開槍帶走一人
- **守衛 (Guard)**：每晚可以保護一名玩家免於狼人攻擊
- **白痴 (Idiot)**：被投票淘汰時翻牌存活但失去投票權
- **長老 (Elder)**：需要兩次攻擊才會死亡
- **騎士 (Knight)**：每局可以與一名玩家決鬥一次
- **魔術師 (Magician)**：可以交換兩名玩家的角色一次
- **丘比特 (Cupid)**：第一晚將兩名玩家連結為戀人
- **烏鴉 (Raven)**：標記一名玩家獲得額外投票
- **守墓人 (GraveyardKeeper)**：可以查驗死亡玩家的身分

### 中立角色 👻

- **盜賊 (Thief)**：第一晚可以從兩張額外角色卡中選擇一個
- **戀人 (Lover)**：由丘比特連結，一人死亡另一人殉情
- **白狼戀人 (WhiteLoverWolf)**：可以建立戀人關係的特殊狼人變體

## 配置

### 自動角色分配

遊戲會根據玩家人數（6-20 人）自動產生平衡的角色配置，無需手動設定預設組合！

各玩家人數對應的角色與時間限制定義於 [`presets.py`](src/llm_werewolf/core/config/presets.py)。

### 自訂配置

#### 玩家配置檔案

```bash
# 由示範配置開始（全部為 demo 代理）
cp configs/demo.yaml my-game.yaml

# 或由支援 LLM 的樣板開始
cp configs/gpt-5-chaos.yaml my-game.yaml

# 編輯設定檔
```

範例 `my-game.yaml`：

```yaml
language: zh-TW          # 語言代碼（en-US, zh-TW, zh-CN）

players:
  # 遊戲會根據玩家人數自動分配角色

  - name: GPT-4o 偵探
    model: gpt-4o
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: GPT-4o-mini 玩家
    model: gpt-4o-mini
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: GPT-4 分析師
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

  - name: 人類玩家
    model: human          # 真人玩家

  - name: 本地 Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # 本地模型不需要 api_key_env

  - name: 測試機器人
    model: demo           # 測試用的簡單代理
```

所有欄位及其預設值、是否必填，皆定義於 [`player_config.py`](src/llm_werewolf/core/config/player_config.py)。

**支援的模型類型：**

- **OpenAI 相容 API**：任何支援 OpenAI Chat Completions 格式的模型
- **真人玩家**：`model: human`
- **測試代理**：`model: demo`

**本地模型範例：**

若使用 Ollama 等本地模型，可省略 `api_key_env`：

```yaml
  - name: Ollama Llama3
    model: llama3
    base_url: http://localhost:11434/v1
```

## TUI 介面

TUI (Terminal User Interface) 提供現代化終端介面的即時遊戲視覺化，使用 [Textual](https://textual.textualize.io/) 框架構建。

### 面板說明

#### 玩家面板（左上方）

顯示所有玩家的資訊：

- **名字**：玩家顯示名稱
- **模型**：使用的 AI 模型或 `human`/`demo`
- **狀態指示器**：
    - ✓：存活
    - ✗：死亡
    - 🛡️：被守衛保護
    - ❤️：戀人關係
    - ☠️：被女巫下毒
    - 🔴：被烏鴉標記

#### 遊戲面板（右上方）

顯示當前遊戲狀態：

- **回合與階段**：
    - 🌙 夜晚階段
    - ☀️ 白天討論階段
    - 🗳️ 投票階段
    - 🏁 遊戲結束
- **玩家統計**：按陣營統計存活玩家數
- **投票計數**（投票階段）：顯示各玩家得票數

#### 對話面板（下方）

可捲動的事件日誌，顯示遊戲中的所有事件和對話：

- 💬 **玩家發言**：AI 生成的討論、指控、辯護
- 🎮 **遊戲事件**：遊戲開始、階段切換等
- ⏰ **階段變化**：夜晚、白天、投票等
- 💀 **死亡事件**：玩家死亡通知
- 🐺 **狼人行動**：狼人夜晚討論
- 🔮 **技能使用**：各角色技能的使用記錄

事件根據重要性進行顏色編碼，便於快速識別關鍵資訊。

### TUI 控制

- **q**：退出遊戲
- **滑鼠滾輪**：捲動對話歷史
- **方向鍵**：在可聚焦元件間移動

遊戲啟動後會自動執行，無需手動介入。

### Console 模式

如果不想使用 TUI，可以使用 `llm-werewolf` 或 `werewolf` 命令，遊戲將以純文字日誌形式自動執行並輸出到終端。

Console 模式會顯示即時狀態提示，讓你了解遊戲進度：

- 🎬 **夜晚階段**：顯示每個角色正在行動（例如：`🎬 Seer（gpt-4）正在行動...`）
- 💬 **白天討論**：顯示每個玩家正在思考發言（例如：`💬 Alice（gpt-4）正在思考發言...`）
- 🗳️ **投票階段**：顯示每個玩家正在思考投票（例如：`🗳️ Bob（gpt-4）正在思考投票...`）

這些提示能幫助你了解遊戲正在等待 LLM API 回應，而非卡住。LLM 回應通常需要數秒至數十秒不等。

**Console 模式範例輸出：**

```
🎮 遊戲開始，共 9 名玩家...
📋 角色分配完成
   - Werewolf x2
   - Seer x1
   - Witch x1
   - Hunter x1
   - Guard x1
   - Villager x3

🌙 === 第 1 回合：夜晚階段 ===
🐺 狼人正在討論目標...
🎬 Guard(gpt-4o) 正在行動...
   → 守衛保護了 Alice
🎬 Seer(claude-sonnet) 正在行動...
   → 預言家查驗 Bob：村民
🎬 Werewolf(gpt-4o-mini) 正在行動...
   → 狼人殺死了 Charlie
🎬 Witch(deepseek-reasoner) 正在行動...
   → 女巫對 Charlie 使用解藥

☀️ === 第 1 回合：白天階段 ===
💬 Alice(gpt-4o) 正在思考...
💬 Alice：「昨晚很平靜，但我們需要找出狼人。」
💬 Bob(claude-sonnet) 正在思考...
💬 Bob：「我注意到 David 昨天行為可疑。」
...

🗳️ === 投票階段 ===
🗳️ Alice(gpt-4o) 正在思考投票...
   → Alice 投票給 David
🗳️ Bob(claude-sonnet) 正在思考投票...
   → Bob 投票給 David
...

📊 投票結果：
   David: 5 票
   Eve: 3 票
   Frank: 1 票

💀 David 被淘汰（村民）

🏁 === 遊戲結束 ===
🎉 狼人陣營獲勝！
   存活：Werewolf x2, Villager x2
```

## 遊戲流程

1. **準備階段**：玩家被隨機分配角色
2. **夜晚階段**：
    - 🌙 **旁白**：「天黑請閉眼...」
    - 🐺 **狼人討論**：多個狼人之間可以討論要投票殺誰（如果只有一個狼人則跳過）
    - 🐺 **狼人投票**：狼人投票選擇目標
    - 🎬 **其他角色行動**：其他具有夜晚能力的角色按優先順序行動（預言家、女巫、守衛等）
    - 🌙 **旁白**：「狼人請閉眼...」
3. **警長選舉**（僅限第一輪）：
    - 🎖️ 玩家決定是否參選，候選人依序發表競選演說
    - 🗳️ 所有人投票選出警長，此後警長的一票算 1.5 票
4. **白天討論**：
    - ☀️ **旁白**：「天亮了，所有人請睜眼...」
    - 💬 玩家依序發言，討論並分享資訊
5. **白天投票**：
    - 🗳️ 玩家投票淘汰嫌疑人
6. **檢查勝利**：遊戲檢查是否有陣營獲勝
7. 重複步驟 2-6 直到滿足勝利條件

## 勝利條件

遊戲會在每個階段結束後檢查勝利條件：

- **村民陣營獲勝**：所有狼人被淘汰
- **狼人陣營獲勝**：狼人數量 ≥ 村民數量
- **戀人獲勝**：只剩下兩個戀人存活（戀人勝利優先於陣營勝利）

## 系統需求

- **Python**：3.10 或更高版本
- **作業系統**：Linux、macOS、Windows
- **終端**：支援 ANSI 顏色和 Unicode 的現代終端（用於 TUI）

### 主要依賴

請參閱 [`pyproject.toml`](pyproject.toml) 中的 `dependencies`。

## 常見問題

### 如何新增更多玩家？

編輯您的 YAML 配置檔案，在 `players` 列表中新增玩家配置。遊戲會根據玩家總數（支援 6-20 人）自動生成平衡的角色配置。

### 可以混合不同的 LLM 模型嗎？

可以！您可以在同一場遊戲中使用不同的 LLM 提供商和模型，例如同時使用 GPT-4、Claude 和本地 Llama 模型。

### 如何讓真人玩家參與遊戲？

在 YAML 配置中，將某個玩家的 `model` 設定為 `human`。遊戲進行時，該玩家需要透過終端輸入來回應。

### 本地模型（Ollama）如何設定？

確保 Ollama 正在執行，然後在 YAML 中設定：

```yaml
  - name: Ollama 玩家
    model: llama3
    base_url: http://localhost:11434/v1
```

不需要設定 `api_key_env`。

### 如何自訂遊戲設定？

遊戲會根據玩家人數（6-20 人）自動生成平衡的角色配置。角色分配和時間限制會隨玩家數量增加而自動調整。如需進階自訂角色生成邏輯，請參閱 `src/llm_werewolf/core/config/presets.py` 中的 `create_game_config_from_player_count()` 函數。

## 授權

本專案採用 [MIT License](LICENSE) 授權。

## 開發

開發環境設定、測試、貢獻流程、架構概覽與 TUI 截圖方式請見 [CONTRIBUTING.md](./.github/CONTRIBUTING.md)。

## 致謝

本專案使用以下優秀的開源工具構建：

- [Pydantic](https://pydantic.dev/) - 資料驗證和設定管理
- [Textual](https://textual.textualize.io/) - 現代化 TUI 框架
- [Rich](https://rich.readthedocs.io/) - 精美的終端輸出
- [OpenAI Python SDK](https://github.com/openai/openai-python) - LLM API 客戶端
- [uv](https://docs.astral.sh/uv/) - 快速的 Python 套件管理器
- [Ruff](https://github.com/astral-sh/ruff) - 極速 Python linter

## 相關連結

- [專案首頁](https://github.com/Mai0313/LLMWereWolf)
- [問題追蹤](https://github.com/Mai0313/LLMWereWolf/issues)

## 更新日誌

請參閱 [Releases](https://github.com/Mai0313/LLMWereWolf/releases) 頁面查看版本更新記錄。
