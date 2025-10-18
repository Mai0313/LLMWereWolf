# LLM Werewolf 狼人殺遊戲套件實作計劃（含 TUI）

## 第一階段：專案重構與基礎架構

### 1.1 專案重命名

- 將 `src/repo_template/` 重命名為 `src/llm_werewolf/`
- 更新 `pyproject.toml` 中所有相關配置
- 新增 TUI 相關依賴：`rich`, `textual`

### 1.2 建立模組化目錄結構

```
src/llm_werewolf/
├── core/                    # 核心遊戲邏輯
│   ├── roles/              # 角色系統（base, werewolf, villager, neutral）
│   ├── player.py
│   ├── game_state.py
│   ├── game_engine.py
│   ├── actions.py
│   ├── events.py
│   └── victory.py
├── config/                  # 配置系統
│   ├── game_config.py
│   └── role_presets.py
├── ai/                      # AI 介面抽象層
│   ├── base_agent.py
│   ├── message.py
│   └── demo_agent.py       # 示範 Agent
├── ui/                      # TUI 使用者介面 ⭐ 新增
│   ├── tui_app.py          # Textual App 主程式
│   ├── components/         # UI 元件
│   │   ├── player_panel.py    # 玩家列表面板
│   │   ├── game_panel.py      # 遊戲狀態面板
│   │   ├── chat_panel.py      # 對話歷史面板
│   │   └── debug_panel.py     # 除錯資訊面板
│   └── styles.py           # TUI 樣式定義
├── utils/                   # 工具函數
│   ├── logger.py
│   └── validator.py
└── cli.py                   # CLI 入口
```

## 第二階段：核心遊戲邏輯實作

（與原計劃相同：角色、玩家、狀態、行動、事件、引擎、勝利條件）

## 第三階段：配置系統

（與原計劃相同）

## 第四階段：AI 介面抽象層

（與原計劃相同）

## 第五階段：TUI 介面實作 ⭐ 新增

### 5.1 TUI 主應用程式

**檔案：`src/llm_werewolf/ui/tui_app.py`**

- 使用 `Textual` 框架建立主應用程式
- 佈局設計：
  - 左側：玩家列表面板（顯示玩家名稱、模型、角色、狀態）
  - 中間：遊戲進度面板（顯示回合、階段、當前發言者）
  - 右側：除錯/系統資訊面板
  - 底部：對話歷史滾動面板
- 即時更新機制：遊戲事件觸發 UI 更新

### 5.2 玩家列表面板

**檔案：`src/llm_werewolf/ui/components/player_panel.py`**

- 顯示每個玩家：
  - 玩家名稱
  - 使用的 AI 模型（例如：gpt-4, claude-3）
  - 角色圖示（活著/死亡）
  - 特殊狀態（中毒、保護等）
- 使用 Rich 的 `Table` 或自定義 Widget

### 5.3 遊戲狀態面板

**檔案：`src/llm_werewolf/ui/components/game_panel.py`**

- 顯示遊戲資訊：
  - 當前回合數（Round X）
  - 當前階段（Day/Night）
  - 階段圖示（太陽/月亮）
  - 當前行動者
  - 倒數計時（如有設定）
- 投票結果視覺化（投票表格）

### 5.4 對話歷史面板

**檔案：`src/llm_werewolf/ui/components/chat_panel.py`**

- 滾動顯示所有對話：
  - 系統訊息（遊戲提示）
  - 玩家發言（發言者名稱 + 內容）
  - 行動結果（誰死了、誰被驗等）
- 支援語法高亮和顏色區分
- 自動滾動到最新訊息

### 5.5 除錯資訊面板

**檔案：`src/llm_werewolf/ui/components/debug_panel.py`**

- 顯示技術資訊：
  - Session ID
  - 遊戲配置
  - AI 回應時間
  - 錯誤日誌
- 可選顯示（透過 `--debug` 參數）

### 5.6 樣式與主題

**檔案：`src/llm_werewolf/ui/styles.py`**

- 定義 TUI 配色方案
- 角色顏色（狼人紅色、村民綠色等）
- 響應式佈局設定

## 第六階段：CLI 與整合

### 6.1 更新 CLI

**檔案：`src/llm_werewolf/cli.py`**

- 支援兩種模式：
  - `--tui`: 啟動 TUI 介面（預設）
  - `--no-tui`: 純命令列模式
- 參數：
  - `--players`: 玩家數量
  - `--config`: 配置檔案
  - `--preset`: 預設配置
  - `--debug`: 顯示除錯面板

### 6.2 遊戲引擎與 TUI 整合

- `GameEngine` 發出事件時，通知 TUI 更新
- 使用觀察者模式或回調函數
- 確保 TUI 在獨立執行緒運行，不阻塞遊戲邏輯

## 第七階段：測試

### 7.1 單元測試

- 所有核心模組測試（與原計劃相同）
- 新增 `tests/ui/test_components.py`: 測試 UI 元件渲染

### 7.2 整合測試

- `tests/integration/test_full_game.py`: 完整遊戲流程
- `tests/integration/test_tui_game.py`: TUI 模式下的遊戲測試

## 第八階段：文檔更新

### 8.1 使用者文檔

更新 README，新增：

- TUI 介面截圖或示意圖
- TUI 功能說明
- 快捷鍵說明（如有）

### 8.2 API 文檔

- 確保 TUI 元件也有完整 docstrings
- 生成 API 文檔

### 8.3 開發者文檔

- 新增 `docs/tui.md`：TUI 架構說明
- 說明如何擴展 UI 元件

## 實作順序建議

1. **階段 1.1-1.2**：專案重構（含 TUI 目錄）
2. **階段 2**：完成核心遊戲邏輯
3. **階段 3**：完成配置系統
4. **階段 4**：完成 AI 抽象層
5. **階段 5**：完成 TUI 介面 ⭐
6. **階段 6**：整合 CLI 與 TUI
7. **階段 7**：完成測試
8. **階段 8**：完成文檔

## 技術選擇

**TUI 框架：Textual**

- 優點：現代、強大、支援 Rich、響應式佈局
- 適合複雜的多面板介面
- 文檔完善，社群活躍

**替代方案：Rich + 自定義佈局**

- 更輕量，但需要更多手動工作

## TUI 特色功能

1. **即時更新**：遊戲事件即時反映在 UI 上
2. **多面板顯示**：同時查看玩家、遊戲、對話
3. **顏色編碼**：不同角色/陣營用不同顏色
4. **互動式**（未來擴展）：可用鍵盤控制、暫停、回放
5. **日誌導出**：可將遊戲記錄導出為文字檔

## 依賴項更新

在 `pyproject.toml` 新增：

```toml
dependencies = [
    "pydantic",
    "textual>=0.40.0",    # TUI 框架
    "rich>=13.0.0",       # 終端美化
]
```
