from llm_werewolf.core.agent import DemoAgent


def test_demo_agent_response() -> None:
    """Demo agent should always return some canned text."""
    agent = DemoAgent(name="TestAgent", model="demo")
    assert agent.model == "demo"
    assert agent.name == "TestAgent"

    response = agent.get_response("Test message")
    assert isinstance(response, str)
    assert response


def test_demo_agent_repr() -> None:
    """Demo agent repr returns the agent name and model."""
    agent = DemoAgent(name="TestAgent", model="demo")
    assert repr(agent) == "TestAgent (demo)"
