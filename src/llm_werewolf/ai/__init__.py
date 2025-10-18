"""AI agent interface for the Werewolf game."""

from llm_werewolf.ai.base_agent import BaseAgent, DemoAgent, HumanAgent
from llm_werewolf.ai.llm_agents import (
    AnthropicAgent,
    GenericLLMAgent,
    OpenAIAgent,
    create_agent_from_config,
)
from llm_werewolf.ai.message import GameMessage, MessageBuilder, MessageType

__all__ = [
    # Agent classes
    "BaseAgent",
    "DemoAgent",
    "HumanAgent",
    # LLM Agent classes
    "OpenAIAgent",
    "AnthropicAgent",
    "GenericLLMAgent",
    "create_agent_from_config",
    # Message classes
    "GameMessage",
    "MessageBuilder",
    "MessageType",
]
