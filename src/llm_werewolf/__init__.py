"""LLM Werewolf - AI-powered Werewolf game with LLM integration."""

__version__ = "0.1.0"

from llm_werewolf.ai import BaseAgent, DemoAgent, GameMessage, MessageBuilder
from llm_werewolf.config import GameConfig, get_preset, list_preset_names
from llm_werewolf.core import (
    GameEngine,
    GamePhase,
    GameState,
    Player,
    VictoryChecker,
)
from llm_werewolf.core.roles import Camp, Role

__all__ = [
    "__version__",
    # Core classes
    "GameEngine",
    "GameState",
    "GamePhase",
    "Player",
    "VictoryChecker",
    # Roles
    "Role",
    "Camp",
    # Config
    "GameConfig",
    "get_preset",
    "list_preset_names",
    # AI
    "BaseAgent",
    "DemoAgent",
    "GameMessage",
    "MessageBuilder",
]
