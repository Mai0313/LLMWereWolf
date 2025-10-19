## 請幫我把 src/llm_werewolf/ai 的內容簡化 因為目前我會用到的所有模型都會支援 ChatCompletion

所以只需要使用 openai 套件就好, 主要差別在於不同的模型需要 init 不同的 client
可以簡化 src/llm_werewolf/ai 和 src/llm_werewolf/config/llm_config.py
裡面有一大堆預設值我認為不需要

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
