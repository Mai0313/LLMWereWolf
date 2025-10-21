from llm_werewolf.ai import LLMAgent
from llm_werewolf.core.agent import DemoAgent


def test_demo_agent_response() -> None:
    """Demo agent should always return some canned text."""
    agent = DemoAgent()
    assert agent.model_name == "demo"

    response = agent.get_response("Test message")
    assert isinstance(response, str)
    assert response


def test_demo_agent_repr() -> None:
    """Demo agent repr returns the model name."""
    agent = DemoAgent()
    assert repr(agent) == "demo"


def test_llm_agent_history_helpers() -> None:
    """LLM agent exposes conversation history helpers."""
    agent = LLMAgent(model_name="dummy-model")

    agent.add_to_history("user", "Hello")
    agent.add_to_history("assistant", "Hi there")

    history = agent.get_history()
    assert history[0]["role"] == "user"
    assert history[1]["content"] == "Hi there"

    agent.reset()
    assert agent.get_history() == []
