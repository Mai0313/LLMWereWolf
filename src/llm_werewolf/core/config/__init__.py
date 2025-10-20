"""Core game configuration module."""

from llm_werewolf.core.config.game_config import GameConfig
from llm_werewolf.core.config.presets import (
    PRESET_12_PLAYERS,
    PRESET_15_PLAYERS,
    PRESET_6_PLAYERS,
    PRESET_9_PLAYERS,
    PRESET_CHAOS,
    PRESET_EXPERT,
    get_all_presets,
    get_preset,
    get_preset_by_name,
)

__all__ = [
    # Config class
    "GameConfig",
    # Presets
    "PRESET_6_PLAYERS",
    "PRESET_9_PLAYERS",
    "PRESET_12_PLAYERS",
    "PRESET_15_PLAYERS",
    "PRESET_EXPERT",
    "PRESET_CHAOS",
    # Preset functions
    "get_preset",
    "get_all_presets",
    "get_preset_by_name",
]
