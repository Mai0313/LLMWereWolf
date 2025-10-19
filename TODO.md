## 檢查專案代碼邏輯

修改確認範圍:

- 狼人殺遊戲邏輯是否正確
- 代碼是否需要優化, 例如是否有充分利用 `pydantic` 來實現更好的結構化和驗證
- 遊戲邏輯是否與實際 進行遊戲的 代碼充分切開
  - 遊戲規則 和 遊戲邏輯應該放在 `./src/llm_werewolf/core` 裡面, 遊戲實際運行則是放在 `./src/llm_werewolf/cli.py` 和 `./src/llm_werewolf/tui.py`
- 狼人殺規則完整性, 部分特殊角色能力未實現
- AI 整合, 夜間行動應調用 AI 而非隨機選擇
- 函數複雜度, 部分函數過長, 建議拆分
- 所有 import 都應該放在檔案最上方 而不是放在 function 內部進行 import

當任務完成時 請務必記得透過 `uv run pre-commit run -a` 來確保代碼質量
