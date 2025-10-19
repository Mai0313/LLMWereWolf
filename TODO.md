## 修正遊戲無法開始的問題

目前遊戲的主要流程是在 `src/llm_werewolf/cli.py` 和 `src/llm_werewolf/ui/tui_app.py` 來處理的
所有設置都會由 `configs` 裡面的 `yaml` 文件來處理
但我有點分不清楚 game_type 的 tui 和 console 差異在哪了
因為我的 TUI 似乎沒辦法開始遊戲
console 也沒有真正開始遊戲 反而跳出了一個TUI介面

我測試時是透過 `poe main configs/demo.yaml` 執行的

而且我覺得 tui 的東西應該完全切開 所以應該要有兩份檔案
- ./src/llm_werewolf/cli.py
- ./src/llm_werewolf/tui.py

而不是透過 config 的設定來處理 就是統一調用狼人殺的遊戲核心等等去處理
這樣的話才能更加清楚簡潔好維護
目前狀態有點混在一起的感覺
