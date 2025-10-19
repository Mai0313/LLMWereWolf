"""Tests for simplified AI agents."""

from llm_werewolf.ai import DemoAgent, LLMAgent


def test_demo_agent_response():
    """Demo agent should always return some canned text."""
    agent = DemoAgent()
    assert agent.model_name == "demo-random"

    response = agent.get_response("Test message")
    assert isinstance(response, str)
    assert response


def test_demo_agent_repr():
    """Demo agent repr includes the model name."""
    agent = DemoAgent()
    assert "DemoAgent" in repr(agent)
    assert "demo-random" in repr(agent)


def test_llm_agent_history_helpers():
    """LLM agent exposes conversation history helpers."""
    agent = LLMAgent(model_name="dummy-model")

    agent.add_to_history("user", "Hello")
    agent.add_to_history("assistant", "Hi there")

    history = agent.get_history()
    assert history[0]["role"] == "user"
    assert history[1]["content"] == "Hi there"

    agent.reset()
    assert agent.get_history() == []
