## 重構 `./src/llm_werewolf/core` 代碼, 將整個代碼透過 `pydantic` 的 `BaseModel` 來完善結構化的代碼

當任務完成時 請務必記得透過 `uv run pre-commit run -a` 來確保代碼質量

## 解決循環導入問題

幫我檢查一下我的狼人殺遊戲邏輯 `./src/llm_werewolf/core`
我發現這個主要邏輯中有非常多循環導入的問題 我不希望透過 `TYPE_CHECKING`, `function` 內 `import`, 透過雙引號, 或透過 `from __future__ import annotations` 來解決循環問題
正確的做法應該是將代碼重構, 關於類型的東西應該放在 `./src/llm_werewolf/core/types` 資料夾中, 來避免循環導入的問題
應該從根本去解決 也就是將架構重構

## 更新規則

請查看 `./src/llm_werewolf/core` 這裡是我的狼人殺遊戲邏輯代碼
請幫我檢查是否有邏輯錯誤或規則錯誤的部分沒處理到
如果有需要可以參考 `rule.md`

## 請依照我代碼實際狀況去更新 `README.md`, `README.zh-TW.md`, 和 `README.zh-CN.md`

目前代碼經過很多迭代 但都沒有更新文檔 所以請你逐行檢查文件是否與代碼一致
如果不一致 請你更新文檔 讓文檔與代碼一致
並且在文檔中提供 tui / cli 指令的 preview 畫面

## 請幫我補齊測試

目前測試覆蓋率很低
你可以透過 `uv run pytest` 來進行查看
請幫我提升它的覆蓋率
測試時 如果需要執行 可以嘗試透過 `uv run python ./src/llm_werewolf/cli.py ./configs/demo.yaml` 來進行測試
