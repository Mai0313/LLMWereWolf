## 檢查專案代碼邏輯

修改確認範圍:

- 狼人殺遊戲邏輯是否正確
- 代碼是否需要優化, 例如是否有充分利用 `pydantic` 來實現更好的結構化和驗證
- 狼人殺規則完整性, 部分特殊角色能力未實現, 詳情可以參考 `rule.md`
- 保存/加載遊戲 - 使用 Pydantic 序列化 GameState
- 重構複雜函數 - 將 run_voting_phase 拆分為更小的函數
- 狼人協商機制 - 實現多隻狼人投票決定殺人目標

當任務完成時 請務必記得透過 `uv run pre-commit run -a` 來確保代碼質量

## 循環導入

幫我檢查一下我的專案的 import, 我認為目前的 import 很亂
另外 import 應該放在檔案最上面 而不是透過延遲import 來規避循環導入

我認為應該從根源上處理 而不是像現在這樣

而且不需要每個功能都往外開放, 只需要將這個專案理解為三種分開的功能

- ai (控制參與玩家 或 參與AI)
- 狼人殺遊戲核心邏輯
- ui (tui)

這部分應該要重新規劃

## 請幫我使用 TypeAlias

請幫我找一下 Codebase 中是否有類似這種 `AgentType = DemoAgent | HumanAgent | LLMAgent`
我希望可以改成透過 `TypeAlias`, `Annotated` 最後再用 `PropertyInfo(discriminator="type")` 來處理

## 確認遊戲邏輯中 夜間行動 是如何完成的

## 更新規則

請查看 `./src/llm_werewolf/core` 這裡是我的狼人殺遊戲邏輯代碼
請幫我將目前我這個專案的規則 透過繁體中文寫成 `rule.md`

我需要你參考真實的狼人殺規則與角色 與 我現在完成的規則與角色完成這份文件
如果有缺少的規則或角色 請另外標註出來

## 請依照我代碼實際狀況去更新 `README.md`, `README.zh-TW.md`, 和 `README.zh-CN.md`

目前代碼經過很多迭代 但都沒有更新文檔 所以請你逐行檢查文件是否與代碼一致
如果不一致 請你更新文檔 讓文檔與代碼一致
