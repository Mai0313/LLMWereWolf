## 完成 AI 玩狼人殺

我想透過 python來寫一個狼人殺的套件, 未來希望接入多個不同的 LLM 模型來實現 AI 玩狼人殺
但我希望從狼人殺的遊戲邏輯開始做起, 你能幫我設計一個狼人殺遊戲的基本架構嗎? 包含角色設定, 遊戲流程, 以及勝利條件等
腳色我希望是完整版, 遊戲規則則是標準, 規模則是可配置
專案名稱可以是 LLMWereWolf 之類的

我希望還要有類似的UI來顯示這些資訊 例如 參與玩家 (模型名稱) 和 一些遊戲正在執行的資訊, 這部分我覺得可以透過TUI來完成

後續我計畫透過一個 function, 可能是 OpenAI ChatCompletion 或是其他的 function 來完成所謂的 "參與玩家"

有一點要注意的是, 這個 function 不一定是 OpenAI ChatCompletion, 所以未來這個 function 會稍微有點抽象
input 是 message (string), output 則是 result (string), 這樣未來會比較好完成
另外 目前的專案代碼是一個 python 專案模板, 所以請幫我將全部修改
