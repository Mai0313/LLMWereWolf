"""Core game configuration module."""

from llm_werewolf.core.config.game_config import GameConfig
from llm_werewolf.core.config.presets import (
    get_all_presets,
    get_preset,
    get_preset_by_name,
)

__all__ = [
    # Config class
    "GameConfig",
    # Preset functions
    "get_preset",
    "get_all_presets",
    "get_preset_by_name",
]
