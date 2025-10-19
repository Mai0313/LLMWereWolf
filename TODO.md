## 請幫我簡化 src/llm_werewolf/cli.py

你可以看到 src/llm_werewolf/ai/agents.py 裡面有一個叫做 DemoAgent

請透過這個來幫我創建一個 demo.yaml 到 configs 裡面 這樣應該就能完成 create_demo_game 了

run_console_mode 和 run_tui_mode 都可以透過在 config 中新增 game_type 來完成 (tui, etc)

我覺得不應該有這麼多 function, 應該完全透過 config 來控制就好 我有點不確定 console 和 tui 之間的差別在哪
因為目前感覺看不出差異 console 應該是單純把每一輪的對話 和 投票等等結果印出來就好
