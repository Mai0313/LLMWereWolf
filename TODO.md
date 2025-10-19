## 修正遊戲無法開始的問題

目前遊戲的主要流程是在 `src/llm_werewolf/cli.py` 和 `src/llm_werewolf/ui/tui_app.py` 來處理的
所有設置都會由 `configs` 裡面的 `yaml` 文件來處理
但我有點分不清楚 game_type 的 tui 和 console 差異在哪了
因為我的 TUI 似乎沒辦法開始遊戲
console 也沒有真正開始遊戲 反而跳出了一個TUI介面

我測試時是透過 `poe main configs/demo.yaml` 執行的
