import json

import httpx
from openai import OpenAI
import pytest

from llm_werewolf.core import agent as agent_module
from llm_werewolf.core.agent import LLMAgent, create_agent
from llm_werewolf.core.config import PlayerConfig


def test_create_agent_without_api_key_env_uses_keyless_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that a player without api_key_env talks to a keyless endpoint."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-must-not-be-sent")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-1",
                "object": "chat.completion",
                "created": 0,
                "model": "llama3",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": "I agree."},
                    }
                ],
            },
        )

    def local_openai(api_key: str, base_url: str) -> OpenAI:
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        )

    monkeypatch.setattr(agent_module, "OpenAI", local_openai)
    config = PlayerConfig(name="Local Llama", model="llama3", base_url="http://localhost:11434/v1")

    agent = create_agent(config)

    assert isinstance(agent, LLMAgent)
    assert agent.get_response("Who do you suspect?") == "I agree."
    assert len(requests) == 1
    assert "authorization" not in requests[0].headers


def test_create_agent_sends_configured_reasoning_effort(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that a player's reasoning_effort reaches the chat completion request."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-1",
                "object": "chat.completion",
                "created": 0,
                "model": "gpt-5",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": "I agree."},
                    }
                ],
            },
        )

    def local_openai(api_key: str, base_url: str) -> OpenAI:
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        )

    monkeypatch.setattr(agent_module, "OpenAI", local_openai)
    config = PlayerConfig(
        name="Thinker",
        model="gpt-5",
        base_url="http://localhost:11434/v1",
        reasoning_effort="high",
    )

    create_agent(config).get_response("Who do you suspect?")

    assert json.loads(requests[0].content).get("reasoning_effort") == "high"


def test_create_agent_with_unset_api_key_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that a player whose api_key_env names an unset variable fails at creation."""
    monkeypatch.delenv("LLM_WEREWOLF_TEST_API_KEY", raising=False)
    config = PlayerConfig(
        name="Cloud Player",
        model="gpt-5",
        base_url="https://api.openai.com/v1",
        api_key_env="LLM_WEREWOLF_TEST_API_KEY",
    )

    with pytest.raises(ValueError, match="LLM_WEREWOLF_TEST_API_KEY"):
        create_agent(config)
