## 請幫我把 src/llm_werewolf/ai 的內容簡化 因為目前我會用到的所有模型都會支援 ChatCompletion

所以只需要使用 openai 套件就好, 主要差別在於不同的模型需要 init 不同的 client
例如
OpenAI Model:

```python
from openai import OpenAI

client = OpenAI(api_key=..., base_url=...)

completion = client.chat.completions.create(
    model="gpt-5", messages=[{"role": "user", "content": "..."}]
)
print(completion.choices[0].message)
```

Anthropic Model:

```python
from openai import OpenAI

client = OpenAI(api_key=..., base_url=...)
completion = client.chat.completions.create(
    model="claude-haiku-4-5-20251001", messages=[{"role": "user", "content": "..."}]
)
print(completion.choices[0].message)
```

他們的 output 基本上都是下面這種格式

```json
{
  "id": "chatcmpl-B9MBs8CjcvOU2jLn4n570S5qMJKcT",
  "object": "chat.completion",
  "created": 1741569952,
  "model": "...",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "...",
        "refusal": null,
        "annotations": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 10,
    "total_tokens": 29,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "audio_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "service_tier": "default"
}
```

我目前的想法是可以透過類似 `hydra` 的做法來 init client

例如

```yaml
preset: 6-players

players:
  name: gpt-4o
    target: openai.OpenAI
    model: gpt-4o
    base_url: https://api.openai.com/v1
    api_key: sk-...
    temperature: 0.7
    max_tokens: 500
```

target 就是我需要 init 的 class, 其餘 fields 則是該 class 需要的參數

我印象中 這樣做法就可以透過 `hydra.instantiate` 來初始化
但有個地方要注意的是 這樣的話 `configs/players.yaml` 可能就不能被 git trace, 並且要留一個 `configs/players.yaml.example` 來當作範例 因為 api key 將會從 .env 的方式 轉換成直接明文寫在 `configs/players.yaml`
