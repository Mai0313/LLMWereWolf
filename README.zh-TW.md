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
uv run llm-werewolf-tui configs/players.yaml

# 顯示除錯面板
uv run llm-werewolf-tui configs/demo.yaml --debug

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

YAML 設定檔選項：

- `preset: <preset-name>` 指定角色預設配置（如 `6-players`、`9-players`、`12-players`、`15-players`、`expert`、`chaos`）
- `show_debug: true` 顯示 TUI 除錯面板（可被命令列 `--debug` 參數覆蓋）
- `language: <language-code>` 設定遊戲語言（如 `en-US`、`zh-TW`、`zh-CN`）。預設：`en-US`
- `players: [...]` 定義玩家列表

### 環境配置

建立 `.env` 檔案配置 LLM API 金鑰：

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# xAI (Grok)
XAI_API_KEY=xai-...

# 本地模型（Ollama 等）不需要 API 金鑰
# 只需在 YAML 中設定 base_url 即可
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

### 使用預設配置

在設定檔中調整 `preset` 欄位即可套用內建角色組合，可選項目：

- `6-players`：新手局（6 人）- 2 狼人 + 預言家、女巫、2 平民
- `9-players`：標準局（9 人）- 2 狼人 + 預言家、女巫、獵人、守衛、3 平民
- `12-players`：進階局（12 人）- 3 狼人（2 狼人 + 狼王）+ 預言家、女巫、獵人、守衛、丘比特、白痴、3 平民
- `15-players`：完整局（15 人）- 4 狼人（2 狼人 + 狼王 + 白狼王）+ 預言家、女巫、獵人、守衛、丘比特、白痴、長老、烏鴉、3 平民
- `expert`：專家配置（12 人）- 3 狼人（狼人 + 狼王 + 白狼王）+ 預言家、女巫、獵人、守衛、丘比特、騎士、魔術師、長老、平民
- `chaos`：混亂角色組合（10 人）- 3 特殊狼人（白狼王 + 狼美人 + 隱狼）+ 預言家、女巫、獵人、白痴、長老、烏鴉、平民

### 自訂配置

#### 玩家配置檔案

```bash
# 由示範配置開始（全部為 demo 代理）
cp configs/demo.yaml my-game.yaml

# 或由支援 LLM 的樣板開始
cp configs/players.yaml my-game.yaml

# 編輯設定檔
# configs/players.yaml 含有欄位說明與範例
```

範例 `my-game.yaml`：

```yaml
preset: 6-players        # 選擇預設配置
show_debug: false        # 是否顯示除錯面板（TUI 模式適用）
language: zh-TW          # 語言代碼（en-US, zh-TW, zh-CN）

players:
  - name: GPT-4o 偵探
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

  - name: GPT-4 分析師
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

  - name: 人類玩家
    model: human          # 真人玩家

  - name: 本地 Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # 本地模型不需要 api_key_env

  - name: 測試機器人
    model: demo           # 測試用的簡單代理
```

**配置說明：**

- `preset`：必填，決定遊戲的角色配置和玩家數量
- `show_debug`：選填，預設為 `false`，用於 TUI 模式顯示除錯面板
- `language`：選填，預設為 `en-US`，設定遊戲語言（如 `en-US`、`zh-TW`、`zh-CN`）
- `players`：必填，玩家列表，數量必須與 preset 的 `num_players` 一致

**玩家配置欄位：**

- `name`：玩家顯示名稱
- `model`：模型類型
  - `human`：真人玩家（透過終端輸入）
  - `demo`：測試用簡單代理（隨機回應）
  - LLM 模型名稱：如 `gpt-4o`、`gpt-4o-mini`、`claude-sonnet-4-20250514`、`claude-haiku-4-20250514`、`deepseek-reasoner`、`llama3` 或任何 OpenAI 相容模型
- `base_url`：API 端點（LLM 模型必填）
- `api_key_env`：環境變數名稱（有驗證的端點必填）
- `temperature`：選填，預設 0.7
- `max_tokens`：選填，預設 `null`（無限制）
- `reasoning_effort`：選填，支援推理的模型的推理努力等級（如 "low"、"medium"、"high"）

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
    temperature: 0.7
    max_tokens: 500
```

## 代理系統

### 代理類型

本專案提供三種內建代理類型：

1. **LLMAgent**：支援任何 OpenAI 相容 API 的 LLM 模型（GPT-4、Claude、DeepSeek、Grok、本地模型等）
2. **HumanAgent**：真人玩家透過終端輸入
3. **DemoAgent**：測試用的簡單代理（隨機回應）

所有代理都透過 YAML 配置檔案設定（參見[配置](#%E9%85%8D%E7%BD%AE)章節）。遊戲支援在同一局中混合使用不同類型的代理。

## TUI 介面

TUI (Terminal User Interface) 提供現代化終端介面的即時遊戲視覺化，使用 [Textual](https://textual.textualize.io/) 框架構建。

### 介面預覽

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐺 Werewolf Game                                                       AI-Powered Werewolf     │
│ q 退出  d 切換除錯  n 下一步                                                    [00:02:34]     │
├──────────────────────┬─────────────────────────────────────────┬───────────────────────────────┤
│                      │ ╭───── 遊戲狀態 ─────╮                 │                               │
│    玩家              │ │ 🌙 第 2 回合 - 夜晚 │                 │    除錯資訊                   │
│ ──────────────────   │ │                     │                 │ ───────────────────────────   │
│ 名字      模型       │ │ 玩家總數： 8/9      │                 │ 會話 ID:                      │
│           狀態       │ │ 狼人：     2        │                 │   ww_20251019_163022          │
│ ──────────────────   │ │ 村民：     6        │                 │                               │
│ Alice     gpt-4o     │ ╰─────────────────────╯                 │ 配置：players.yaml            │
│           ✓ 🛡️      │                                          │                               │
│ Bob       claude     │                                          │ 玩家：9                       │
│           ✓          │                                          │ AI: 7  真人: 1  Demo: 1       │
│ Charlie   llama3     │                                          │                               │
│           ✓          │                                          │ 角色：                        │
│ David     deepseek   │ ╭──── 事件 / 對話 ────╮                │  - Werewolf x2                │
│           ✓ ❤️       │ │ [00:02:28] 🎮 遊戲開始│                │  - Seer x1                    │
│ Eve       grok       │ │ [00:02:29] ⏰ 階段：夜│                │  - Witch x1                   │
│           ✓ ❤️       │ │ [00:02:30] 🐺 狼人討論│                │  - Hunter x1                  │
│ Frank     human      │ │            目標       │                │  - Guard x1                   │
│           ✓          │ │ [00:02:31] ⏰ 階段：白│                │  - Villager x3                │
│ Grace     claude     │ │ [00:02:32] 💀 Iris 死亡│               │                               │
│           ✓          │ │ [00:02:33] 💬 Alice：  │               │ 夜晚逾時：60s                 │
│ Henry     demo       │ │            "我覺得Bob │               │ 白天逾時：300s                │
│           ✓          │ │            行為可疑"  │               │ 投票逾時：60s                 │
│ Iris      demo       │ │ [00:02:34] 💬 Bob：    │               │                               │
│           ✗          │ │            "我是村民！│               │ 錯誤：0                       │
│                      │ │            Alice 在轉 │               │                               │
│                      │ │            移焦點"    │               │ 來源：YAML 配置               │
│                      │ │ [00:02:35] 💬 Charlie: │               │                               │
│                      │ │            "昨晚的死亡│               │                               │
│                      │ │            模式很奇怪"│               │                               │
│                      │ ╰───────────────────────╯               │                               │
│                      │                                          │                               │
└──────────────────────┴──────────────────────────────────────────┴───────────────────────────────┘
```

### 面板說明

#### 玩家面板（左側）

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

#### 遊戲面板（中央上方）

顯示當前遊戲狀態：

- **回合與階段**：
  - 🌙 夜晚階段
  - ☀️ 白天討論階段
  - 🗳️ 投票階段
  - 🏁 遊戲結束
- **玩家統計**：按陣營統計存活玩家數
- **投票計數**（投票階段）：顯示各玩家得票數

#### 對話面板（中央下方）

可捲動的事件日誌，顯示遊戲中的所有事件和對話：

- 💬 **玩家發言**：AI 生成的討論、指控、辯護
- 🎮 **遊戲事件**：遊戲開始、階段切換等
- ⏰ **階段變化**：夜晚、白天、投票等
- 💀 **死亡事件**：玩家死亡通知
- 🐺 **狼人行動**：狼人夜晚討論
- 🔮 **技能使用**：各角色技能的使用記錄

事件根據重要性進行顏色編碼，便於快速識別關鍵資訊。

#### 除錯面板（右側，可選）

按 'd' 鍵切換顯示，包含：

- 會話 ID
- 配置檔案來源
- 玩家數量與類型統計
- 角色分配
- 時間限制設定
- 錯誤追蹤

### TUI 控制

- **q**：退出遊戲
- **d**：切換除錯面板顯示/隱藏（或使用 `--debug` 參數預設開啟）
- **n**：手動進入下一步（除錯用）
- **滑鼠滾輪**：捲動對話歷史
- **方向鍵**：在可聚焦元件間移動

### Console 模式

如果不想使用 TUI，可以使用 `llm-werewolf` 或 `werewolf` 命令，遊戲將以純文字日誌形式自動執行並輸出到終端。

## 遊戲流程

1. **準備階段**：玩家被隨機分配角色
2. **夜晚階段**：具有夜晚能力的角色按優先順序行動
3. **白天討論**：玩家討論並分享資訊
4. **白天投票**：玩家投票淘汰嫌疑人
5. **檢查勝利**：遊戲檢查是否有陣營獲勝
6. 重複步驟 2-5 直到滿足勝利條件

## 勝利條件

遊戲會在每個階段結束後檢查勝利條件：

- **村民陣營獲勝**：所有狼人被淘汰
- **狼人陣營獲勝**：狼人數量 ≥ 村民數量
- **戀人獲勝**：只剩下兩個戀人存活（戀人勝利優先於陣營勝利）

## 專案架構

專案採用模組化架構，各模組職責清晰：

```
src/llm_werewolf/
├── cli.py                 # 命令列入口（主控台模式）
├── tui.py                 # TUI 入口（互動模式）
├── ai/                    # 代理系統
│   └── agents.py         # LLM 代理實作和配置模型
├── core/                 # 核心遊戲邏輯
│   ├── agent.py          # 基礎代理、HumanAgent 和 DemoAgent
│   ├── game_engine.py    # 遊戲引擎
│   ├── game_state.py     # 遊戲狀態管理
│   ├── player.py         # 玩家類
│   ├── action_selector.py # 動作選擇邏輯
│   ├── events.py         # 事件系統
│   ├── victory.py        # 勝利條件檢查
│   ├── serialization.py  # 序列化工具
│   ├── role_registry.py  # 角色註冊與驗證
│   ├── actions/          # 動作系統
│   │   ├── base.py       # 基礎動作類別
│   │   ├── common.py     # 通用動作
│   │   ├── villager.py   # 村民陣營動作
│   │   └── werewolf.py   # 狼人陣營動作
│   ├── config/           # 配置系統
│   │   ├── game_config.py    # 遊戲配置模型
│   │   └── presets.py        # 角色預設配置
│   ├── types/            # 類型定義
│   │   ├── enums.py      # 列舉（陣營、階段、狀態等）
│   │   ├── models.py     # 資料模型
│   │   └── protocols.py  # 協議定義
│   └── roles/            # 角色實作
│       ├── base.py       # 角色基類
│       ├── werewolf.py   # 狼人陣營角色
│       ├── villager.py   # 村民陣營角色
│       └── neutral.py    # 中立角色
└── ui/                   # 使用者介面
    ├── tui_app.py        # TUI 應用程式
    ├── styles.py         # TUI 樣式
    └── components/       # TUI 元件
        ├── player_panel.py
        ├── game_panel.py
        ├── chat_panel.py
        └── debug_panel.py
```

### 模組說明

- **cli.py**：主控台模式的命令列介面，負責載入配置並自動啟動遊戲
- **tui.py**：互動模式的 TUI 入口，提供終端使用者介面
- **ai/**：LLM 代理實作和配置模型（PlayerConfig、PlayersConfig）
- **core/agent.py**：基礎代理協定和內建代理（HumanAgent、DemoAgent）
- **core/actions/**：動作系統，包含基礎類別和陣營特定動作
- **core/config/**：配置系統，包含遊戲參數和角色預設
- **core/types/**：類型定義，包含列舉、資料模型和協議定義
- **core/**：遊戲核心邏輯，包含角色、玩家、遊戲狀態、動作選擇、事件和勝利檢查
- **ui/**：基於 Textual 框架的終端使用者介面

## 系統需求

- **Python**：3.10 或更高版本
- **作業系統**：Linux、macOS、Windows
- **終端**：支援 ANSI 顏色和 Unicode 的現代終端（用於 TUI）

### 主要依賴

- **pydantic** (≥2.12.3)：資料驗證和設定管理
- **textual** (≥6.3.0)：TUI 框架
- **rich** (≥14.2.0)：終端格式化
- **openai** (≥2.5.0)：OpenAI API 客戶端（用於 LLM 整合）
- **python-dotenv** (≥1.1.1)：環境變數管理
- **pyyaml** (≥6.0.3)：YAML 配置檔案解析
- **fire** (≥0.7.1)：命令列介面
- **logfire** (≥4.13.2)：結構化日誌記錄

## 常見問題

### 如何新增更多玩家？

編輯您的 YAML 配置檔案，調整 `preset` 以匹配玩家數量，並在 `players` 列表中新增玩家配置。記得玩家數量必須與 preset 的 `num_players` 一致。

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

遊戲使用在 YAML 檔案中定義的預設配置（如 `6-players`、`9-players` 等）。每個預設包含預定義的角色組合和時間限制。要調整設定，您可以修改預設配置或建立自訂配置。如需進階自訂，請參閱專案的配置系統 `src/llm_werewolf/core/config/`。

## 授權

本專案採用 [MIT License](LICENSE) 授權。

## 貢獻

歡迎貢獻！您可以透過以下方式參與：

1. **回報問題**：在 [Issues](https://github.com/Mai0313/LLMWereWolf/issues) 頁面回報 bug 或提出功能建議
2. **提交 Pull Request**：修復 bug 或新增功能
3. **改進文件**：幫助改善 README 和程式碼註解
4. **分享反饋**：告訴我們您的使用體驗

### 貢獻流程

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

請確保您的程式碼：

- 遵循專案的程式碼風格（使用 Ruff）
- 包含適當的測試
- 更新相關文件

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
