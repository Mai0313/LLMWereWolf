"""Tests for AI agent interface."""

from llm_werewolf.ai import DemoAgent


def test_demo_agent_creation():
    """Test creating a demo agent."""
    agent = DemoAgent()
    assert agent.model_name == "demo-random"


def test_demo_agent_response():
    """Test demo agent response."""
    agent = DemoAgent()
    response = agent.get_response("Test message")

    assert isinstance(response, str)
    assert len(response) > 0


def test_agent_history():
    """Test agent conversation history."""
    agent = DemoAgent()

    agent.add_to_history("user", "Hello")
    agent.add_to_history("assistant", "Hi there")

    history = agent.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_agent_reset():
    """Test agent reset."""
    agent = DemoAgent()

    agent.add_to_history("user", "Test")
    assert len(agent.get_history()) == 1

    agent.reset()
    assert len(agent.get_history()) == 0


def test_agent_repr():
    """Test agent string representation."""
    agent = DemoAgent()
    assert "DemoAgent" in repr(agent)
    assert "demo-random" in repr(agent)
