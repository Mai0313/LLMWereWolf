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
