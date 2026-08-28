from llm_werewolf.core.config.game_config import GameConfig


def _validate_player_count(num_players: int) -> None:
    """Validate player count is within acceptable range.

    Args:
        num_players: Number of players to validate.

    Raises:
        ValueError: If player count is outside valid range (6-20).
    """
    if num_players < 6:
        msg = "Minimum 6 players required"
        raise ValueError(msg)
    if num_players > 20:
        msg = "Maximum 20 players supported"
        raise ValueError(msg)


def _allocate_werewolf_roles(num_players: int) -> list[str]:
    """Allocate werewolf roles based on player count.

    Args:
        num_players: Total number of players.

    Returns:
        list[str]: List of werewolf role names.
    """
    if num_players <= 8:
        return ["Werewolf", "Werewolf"]
    if num_players <= 11:
        return ["Werewolf", "Werewolf", "AlphaWolf"]
    if num_players <= 14:
        return ["Werewolf", "Werewolf", "AlphaWolf", "WhiteWolf"]
    return ["Werewolf", "Werewolf", "AlphaWolf", "WhiteWolf", "WolfBeauty"]


def _allocate_villager_roles(num_players: int) -> list[str]:
    """Allocate villager roles based on player count.

    Args:
        num_players: Total number of players.

    Returns:
        list[str]: List of villager role names.
    """
    # Core divine roles (always present)
    roles = ["Seer", "Witch"]

    # Additional divine roles based on player count
    if num_players >= 7:
        roles.append("Guard")
    if num_players >= 9:
        roles.append("Hunter")
    if num_players >= 11:
        roles.append("Cupid")
    if num_players >= 13:
        roles.append("Idiot")
    if num_players >= 15:
        roles.append("Elder")
    if num_players >= 17:
        roles.append("Knight")
    if num_players >= 19:
        roles.append("Raven")

    return roles


def _get_timeouts(num_players: int) -> tuple[int, int, int]:
    """Get timeout values based on player count.

    Args:
        num_players: Total number of players.

    Returns:
        tuple[int, int, int]: (night_timeout, day_timeout, vote_timeout)
    """
    if num_players <= 8:
        return (45, 180, 45)
    if num_players <= 12:
        return (60, 300, 60)
    return (90, 400, 90)


def create_game_config_from_player_count(num_players: int) -> GameConfig:
    """Automatically generate game configuration based on number of players.

    This function creates a balanced role composition by scaling the number of
    werewolves and special roles based on the total player count.

    Args:
        num_players: Number of players in the game (6-20).

    Returns:
        GameConfig: Generated game configuration with balanced roles.

    Raises:
        ValueError: If player count is outside valid range (6-20).
    """
    _validate_player_count(num_players)

    # Allocate werewolf and villager roles
    role_names = _allocate_werewolf_roles(num_players)
    role_names.extend(_allocate_villager_roles(num_players))

    # Fill remaining slots with villagers
    num_special_roles = len(role_names)
    num_villagers = num_players - num_special_roles
    role_names.extend(["Villager"] * num_villagers)

    # Get timeouts
    night_timeout, day_timeout, vote_timeout = _get_timeouts(num_players)

    return GameConfig(
        num_players=num_players,
        role_names=role_names,
        night_timeout=night_timeout,
        day_timeout=day_timeout,
        vote_timeout=vote_timeout,
    )
