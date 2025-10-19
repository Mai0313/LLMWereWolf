from llm_werewolf.config.game_config import GameConfig

# 6-player preset (beginner friendly)
PRESET_6_PLAYERS = GameConfig(
    num_players=6,
    role_names=["Werewolf", "Werewolf", "Seer", "Witch", "Villager", "Villager"],
    night_timeout=45,
    day_timeout=180,
    vote_timeout=45,
)

# 9-player preset (standard game)
PRESET_9_PLAYERS = GameConfig(
    num_players=9,
    role_names=[
        "Werewolf",
        "Werewolf",
        "Seer",
        "Witch",
        "Hunter",
        "Guard",
        "Villager",
        "Villager",
        "Villager",
    ],
    night_timeout=60,
    day_timeout=300,
    vote_timeout=60,
)

# 12-player preset (advanced game with more roles)
PRESET_12_PLAYERS = GameConfig(
    num_players=12,
    role_names=[
        "Werewolf",
        "Werewolf",
        "AlphaWolf",
        "Seer",
        "Witch",
        "Hunter",
        "Guard",
        "Cupid",
        "Idiot",
        "Villager",
        "Villager",
        "Villager",
    ],
    night_timeout=60,
    day_timeout=400,
    vote_timeout=60,
)

# 15-player preset (full game with complex roles)
PRESET_15_PLAYERS = GameConfig(
    num_players=15,
    role_names=[
        "Werewolf",
        "Werewolf",
        "AlphaWolf",
        "WhiteWolf",
        "Seer",
        "Witch",
        "Hunter",
        "Guard",
        "Cupid",
        "Idiot",
        "Elder",
        "Raven",
        "Villager",
        "Villager",
        "Villager",
    ],
    night_timeout=90,
    day_timeout=500,
    vote_timeout=90,
)

# Expert preset with many special roles
PRESET_EXPERT = GameConfig(
    num_players=12,
    role_names=[
        "Werewolf",
        "AlphaWolf",
        "WhiteWolf",
        "Seer",
        "Witch",
        "Hunter",
        "Guard",
        "Cupid",
        "Knight",
        "Magician",
        "Elder",
        "Villager",
    ],
    night_timeout=90,
    day_timeout=400,
    vote_timeout=60,
)

# Chaos preset with unusual role combinations
PRESET_CHAOS = GameConfig(
    num_players=10,
    role_names=[
        "WhiteWolf",
        "WolfBeauty",
        "HiddenWolf",
        "Seer",
        "Witch",
        "Hunter",
        "Idiot",
        "Elder",
        "Raven",
        "Villager",
    ],
    night_timeout=90,
    day_timeout=400,
    vote_timeout=60,
)


def get_preset(num_players: int) -> GameConfig:
    """Get a preset configuration for a given number of players.

    Args:
        num_players: Number of players in the game.

    Returns:
        GameConfig: A preset configuration.

    Raises:
        ValueError: If no preset exists for the given player count.
    """
    presets = {
        6: PRESET_6_PLAYERS,
        9: PRESET_9_PLAYERS,
        12: PRESET_12_PLAYERS,
        15: PRESET_15_PLAYERS,
    }

    if num_players in presets:
        return presets[num_players]

    # Try to scale an existing preset
    if num_players < 6:
        msg = "Minimum 6 players required"
        raise ValueError(msg)
    if num_players > 20:
        msg = "Maximum 20 players supported"
        raise ValueError(msg)

    # For other counts, recommend closest preset
    closest = min(presets.keys(), key=lambda x: abs(x - num_players))
    msg = (
        f"No preset for {num_players} players. "
        f"Try using the {closest}-player preset and customize it."
    )
    raise ValueError(msg)


def get_all_presets() -> dict[str, GameConfig]:
    """Get all available presets.

    Returns:
        dict[str, GameConfig]: Dictionary of preset names to configs.
    """
    return {
        "6-players": PRESET_6_PLAYERS,
        "9-players": PRESET_9_PLAYERS,
        "12-players": PRESET_12_PLAYERS,
        "15-players": PRESET_15_PLAYERS,
        "expert": PRESET_EXPERT,
        "chaos": PRESET_CHAOS,
    }


def get_preset_by_name(name: str) -> GameConfig:
    """Get a preset by name.

    Args:
        name: Name of the preset.

    Returns:
        GameConfig: The preset configuration.

    Raises:
        ValueError: If preset name is not found.
    """
    presets = get_all_presets()
    if name not in presets:
        available = ", ".join(presets.keys())
        msg = f"Preset '{name}' not found. Available presets: {available}"
        raise ValueError(msg)
    return presets[name]
