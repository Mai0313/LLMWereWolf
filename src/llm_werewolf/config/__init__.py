from llm_werewolf.ai.agents import (
    PlayerConfig,
    PlayersConfig,
    create_agent,
    load_config,
)
from llm_werewolf.config.game_config import GameConfig
from llm_werewolf.config.role_presets import (
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
    # Config classes
    "GameConfig",
    "PlayerConfig",
    "PlayersConfig",
    # Player config functions
    "create_agent_from_player_config",
    "create_agent",
    "load_config",
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


# Backward compatibility alias
create_agent_from_player_config = create_agent
