from importlib.metadata import version
from pathlib import Path

from llm_werewolf.ai import AgentType, DemoAgent, GameMessage, MessageBuilder
from llm_werewolf.config import GameConfig, get_preset
from llm_werewolf.core import (
    GameEngine,
    GamePhase,
    GameState,
    Player,
    VictoryChecker,
)
from llm_werewolf.core.roles import Camp, Role

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
    # AI
    "AgentType",
    "DemoAgent",
    "GameMessage",
    "MessageBuilder",
]
