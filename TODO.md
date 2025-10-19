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
目前這個任務已經完成一部份, 我不確定是否有完整改完 如果有遺漏 請幫我補上

## 遊戲玩法更改與確認

我想確認一件事情 目前我遊戲是不是九人之類的 我要去哪裡設定其中九人是哪些模型? 能不能支援真人也參與遊戲? 我想法中應該是設定時要設定九個模型的base url, model name, api key 我不確定有啥辦法可以做到

我感覺可以透過 yaml 檔案來設定 (我只寫了部分當作範例)
例如

```yaml
players:
  - name: gpt-5-chat
    model_url: https://api.openai.com/v1
    api_key: OPENAI_API_KEY  # 此為環境變數名稱
  - name: claude-sonnet-4-5-20250929
    model_url: https://api.anthropic.com
    api_key: ANTHROPIC_API_KEY  # 此為環境變數名稱
  - name: human-player-1
    model_url: human
    api_key:
```

這樣的設定方式也可以減少 .env.example 裡面的大量資訊 只需要保留 api key 這種敏感資訊即可
