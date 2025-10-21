"""Type definitions for the LLM Werewolf game.

This package contains all type definitions including enums, models, and protocols
to avoid circular import issues throughout the codebase.
"""

# Export all enums
from llm_werewolf.core.types.enums import (
    Camp,
    EventType,
    GamePhase,
    ActionType,
    PlayerStatus,
    ActionPriority,
)

# Export all models
from llm_werewolf.core.types.models import Event, PlayerInfo, RoleConfig, GameStateInfo

# Export all protocols
from llm_werewolf.core.types.protocols import (
    RoleProtocol,
    AgentProtocol,
    ActionProtocol,
    PlayerProtocol,
    GameStateProtocol,
)

__all__ = [
    # Enums
    "ActionPriority",
    # Protocols
    "ActionProtocol",
    "ActionType",
    "AgentProtocol",
    "Camp",
    # Models
    "Event",
    "EventType",
    "GamePhase",
    "GameStateInfo",
    "GameStateProtocol",
    "PlayerInfo",
    "PlayerProtocol",
    "PlayerStatus",
    "RoleConfig",
    "RoleProtocol",
]
