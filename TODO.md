## 檢查專案代碼邏輯

修改確認範圍:

- 狼人殺遊戲邏輯是否正確
- 狼人殺規則完整性, 部分特殊角色能力未實現, 詳情可以參考 `rule.md`
- 保存/加載遊戲 - 使用 Pydantic 序列化 GameState
- 重構複雜函數 - 將 run_voting_phase 拆分為更小的函數
- 狼人協商機制 - 實現多隻狼人投票決定殺人目標

當任務完成時 請務必記得透過 `uv run pre-commit run -a` 來確保代碼質量

## 循環導入

幫我檢查一下我的狼人殺遊戲邏輯 `./src/llm_werewolf/core`
我發現這個主要邏輯中有非常多循環導入的問題 導致很多 `import` 沒有按照規定放在文件最上方 或是 要透過 `TYPE_CHECKING` 來避免循環導入
但我覺得正確的做法應該是將代碼重構, 關於類型的東西應該放在 `./src/llm_werewolf/core/types` 資料夾中
這樣應該可以避免循環導入的問題
我不希望透過 `TYPE_CHECKING` 或是 在 `function` 內 `import` 來解決循環問題 我認為應該從根本去解決 也就是將架構重構

## 確認遊戲邏輯中 夜間行動 是如何完成的

## 更新規則

請查看 `./src/llm_werewolf/core` 這裡是我的狼人殺遊戲邏輯代碼
請幫我將目前我這個專案的規則 透過繁體中文寫成 `rule.md`

我需要你參考真實的狼人殺規則與角色 與 我現在完成的規則與角色完成這份文件
如果有缺少的規則或角色 請另外標註出來

## 請依照我代碼實際狀況去更新 `README.md`, `README.zh-TW.md`, 和 `README.zh-CN.md`

目前代碼經過很多迭代 但都沒有更新文檔 所以請你逐行檢查文件是否與代碼一致
如果不一致 請你更新文檔 讓文檔與代碼一致
並且在文檔中提供 tui / cli 指令的 preview 畫面

## 請幫我補齊測試

目前測試覆蓋率很低
你可以透過 `uv run pytest` 來進行查看
這裡是目前覆蓋率

```
------------------------------------ generated xml file: /home/wei/repo/LLMWereWolf/.github/reports/.coverage.pytest.xml -------------------------------------
======================================================================= tests coverage =======================================================================
______________________________________________________ coverage: platform linux, python 3.10.18-final-0 ______________________________________________________

Name                                               Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------
src/llm_werewolf/ai/__init__.py                        2      2     0%   1-3
src/llm_werewolf/ai/agents.py                         78     78     0%   1-193
src/llm_werewolf/cli.py                               49     49     0%   1-88
src/llm_werewolf/core/action_selector.py             102     75    26%   34-61, 77-90, 117-118, 144-145, 171-200, 216-234, 264-291
src/llm_werewolf/core/actions/base.py                 18      4    78%   7, 30, 39, 48
src/llm_werewolf/core/actions/common.py               26     13    50%   20-21, 25, 29, 33-34, 50-51, 55, 59, 63-65
src/llm_werewolf/core/actions/villager.py            132     83    37%   25, 30-36, 41-44, 60-61, 65, 70-72, 79-82, 103, 107, 111-118, 139, 144-150, 155-159, 180-182, 186, 191-197, 206-213, 229-230, 234, 238, 242-243, 259-260, 264, 268, 272-274, 292-293, 297, 302-308, 312-327
src/llm_werewolf/core/actions/werewolf.py             82     47    43%   25, 29, 33-34, 50-51, 55, 59, 63-64, 80-81, 85, 90-96, 105-116, 132-133, 137, 142-148, 153-156, 172-173, 177, 181, 189-190, 206-207, 211, 215, 219-220
src/llm_werewolf/core/agent.py                        21      2    90%   87-88
src/llm_werewolf/core/config/presets.py               44      8    82%   41, 54, 56, 58, 60, 77-79
src/llm_werewolf/core/engine/action_processor.py      45     37    18%   8-12, 31-120
src/llm_werewolf/core/engine/base.py                 131     63    52%   19, 57-61, 75, 109-110, 121, 160, 179-182, 190-193, 201, 209, 217-240, 244-271, 282-288, 304-307
src/llm_werewolf/core/engine/day_phase.py             59     48    19%   8-11, 32-68, 76-147
src/llm_werewolf/core/engine/death_handler.py        136    122    10%   9-12, 28-35, 47-55, 65-72, 87-133, 141-229, 237-297
src/llm_werewolf/core/engine/night_phase.py           92     77    16%   9-13, 33-132, 140-167, 175-234
src/llm_werewolf/core/engine/voting_phase.py         107     87    19%   10-14, 38-71, 79-118, 126-129, 148-166, 180-224, 232-265
src/llm_werewolf/core/events.py                       26     11    58%   62-67, 78, 92-97, 101, 109
src/llm_werewolf/core/game_state.py                   93     45    52%   45-48, 56, 72-94, 107, 116, 120, 153, 161, 172, 181, 189-198, 206-207, 222
src/llm_werewolf/core/locale.py                       20      7    65%   210, 228-231, 239-241
src/llm_werewolf/core/player.py                       50      3    94%   151-152, 160
src/llm_werewolf/core/role_registry.py                23      2    91%   93, 119
src/llm_werewolf/core/roles/base.py                   56     22    61%   7, 34, 61, 70, 82-91, 102-105, 117, 143-154, 169, 173
src/llm_werewolf/core/roles/neutral.py                29     15    48%   21-23, 31-34, 38, 62-64, 71, 79, 103, 110, 114
src/llm_werewolf/core/roles/villager.py              173     82    53%   48, 75, 81, 88-90, 94, 110, 144, 167-168, 176-194, 207, 211, 256, 262, 268-270, 289, 300-301, 305, 320, 332-333, 337, 352, 364-365, 369, 373, 396-397, 411-416, 420, 444-445, 449-488, 492, 516-539, 543, 565-594, 598
src/llm_werewolf/core/roles/werewolf.py              117     75    36%   48, 54, 61, 87, 99, 103, 127-163, 167, 190-191, 195-227, 231, 253-282, 286, 308, 312, 335-336, 341-381, 385, 409-438, 442
src/llm_werewolf/core/serialization.py               148    148     0%   1-325
src/llm_werewolf/core/types/models.py                 44      4    91%   67-69, 77
src/llm_werewolf/core/types/protocols.py             118     32    73%   29, 44, 49, 54, 59, 63, 67, 71, 75, 93, 97, 101, 105, 109, 113, 117, 121, 125, 129, 133, 137, 141, 172, 176, 180, 184, 188, 192, 196, 208, 212, 216
src/llm_werewolf/core/victory.py                      54     18    67%   23, 27, 49-50, 95-96, 113, 121, 129, 137-141, 153-158
src/llm_werewolf/tui.py                               24     24     0%   1-46
src/llm_werewolf/ui/__init__.py                        3      3     0%   1-4
src/llm_werewolf/ui/components/__init__.py             4      4     0%   1-5
src/llm_werewolf/ui/components/chat_panel.py          46     46     0%   1-102
src/llm_werewolf/ui/components/game_panel.py          62     62     0%   1-111
src/llm_werewolf/ui/components/player_panel.py        43     43     0%   1-90
src/llm_werewolf/ui/styles.py                         19     19     0%   1-140
src/llm_werewolf/ui/tui_app.py                        70     70     0%   1-184
--------------------------------------------------------------------------------
TOTAL                                               2505   1530    39%
```

請幫我提升它的覆蓋率
測試時 如果需要執行 可以嘗試透過 `uv run python ./src/llm_werewolf/cli.py ./configs/demo.yaml` 來進行測試
