"""LLM Werewolf - AI-powered Werewolf game with LLM integration."""

from importlib.metadata import version

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
from importlib.metadata import version
from pathlib import Path

package_name = Path(__file__).parent.name
__package__ = package_name
__version__ = version(package_name)

__all__ = [
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
