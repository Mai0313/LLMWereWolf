from unittest.mock import patch

import pytest

from llm_werewolf.core.agent import BaseAgent, DemoAgent, HumanAgent


def test_demo_agent_response() -> None:
    """Demo agent should always return some canned text."""
    agent = DemoAgent(name="TestAgent", model="demo")
    assert agent.model == "demo"
    assert agent.name == "TestAgent"

    # get_response returns a string
    response = agent.get_response("Test message")
    assert isinstance(response, str)
    assert response


def test_demo_agent_repr() -> None:
    """Demo agent repr returns the agent name and model."""
    agent = DemoAgent(name="TestAgent", model="demo")
    assert repr(agent) == "TestAgent (demo)"


def test_demo_agent_add_decision() -> None:
    """Test that DemoAgent inherits default add_decision (does nothing)."""
    agent = DemoAgent(name="TestAgent", model="demo")
    # Should not raise any error
    agent.add_decision("Some decision")
    # DemoAgent doesn't track decisions
    context = agent.get_decision_context()
    assert context == ""


def test_demo_agent_get_decision_context() -> None:
    """Test that DemoAgent returns empty decision context."""
    agent = DemoAgent(name="TestAgent", model="demo")
    context = agent.get_decision_context()
    assert context == ""


def test_base_agent_get_response_not_implemented() -> None:
    """Test that BaseAgent.get_response raises NotImplementedError."""
    agent = BaseAgent(name="TestAgent", model="test")
    with pytest.raises(NotImplementedError, match="Subclass must implement get_response"):
        agent.get_response("Test message")


def test_human_agent_creation() -> None:
    """Test creating a human agent."""
    agent = HumanAgent(name="Human", model="human")
    assert agent.name == "Human"
    assert agent.model == "human"


def test_human_agent_repr() -> None:
    """Test human agent repr."""
    agent = HumanAgent(name="Player1")
    assert repr(agent) == "Player1 (human)"


@patch("builtins.input", return_value="I think it's Bob!")
def test_human_agent_get_response(mock_input: object) -> None:
    """Test getting response from human agent."""
    agent = HumanAgent(name="Human")
    response = agent.get_response("Who do you suspect?")

    assert response == "I think it's Bob!"
    mock_input.assert_called_once_with("Your response: ")


def test_human_agent_add_decision() -> None:
    """Test that HumanAgent inherits default add_decision."""
    agent = HumanAgent(name="Human")
    # Should not raise any error
    agent.add_decision("Voted for Alice")
    # HumanAgent doesn't track decisions
    context = agent.get_decision_context()
    assert context == ""
