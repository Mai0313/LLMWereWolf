from llm_werewolf.core.config.game_config import GameConfig


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
    if num_players < 6:
        msg = "Minimum 6 players required"
        raise ValueError(msg)
    if num_players > 20:
        msg = "Maximum 20 players supported"
        raise ValueError(msg)

    # Determine number of werewolves and special roles based on player count
    role_names = []

    # Werewolf allocation
    if num_players <= 8:
        # 6-8 players: 2 werewolves
        role_names.extend(["Werewolf", "Werewolf"])
    elif num_players <= 11:
        # 9-11 players: 2 werewolves + 1 special werewolf
        role_names.extend(["Werewolf", "Werewolf", "AlphaWolf"])
    elif num_players <= 14:
        # 12-14 players: 2 werewolves + 2 special werewolves
        role_names.extend(["Werewolf", "Werewolf", "AlphaWolf", "WhiteWolf"])
    else:
        # 15+ players: 2 werewolves + 3 special werewolves
        role_names.extend(["Werewolf", "Werewolf", "AlphaWolf", "WhiteWolf", "WolfBeauty"])

    # Core divine roles (always present)
    role_names.extend(["Seer", "Witch"])

    # Additional divine roles based on player count
    if num_players >= 7:
        role_names.append("Guard")
    if num_players >= 9:
        role_names.append("Hunter")
    if num_players >= 11:
        role_names.append("Cupid")
    if num_players >= 13:
        role_names.append("Idiot")
    if num_players >= 15:
        role_names.append("Elder")
    if num_players >= 17:
        role_names.append("Knight")
    if num_players >= 19:
        role_names.append("Raven")

    # Fill remaining slots with villagers
    num_special_roles = len(role_names)
    num_villagers = num_players - num_special_roles
    role_names.extend(["Villager"] * num_villagers)

    # Set timeouts based on player count
    if num_players <= 8:
        night_timeout = 45
        day_timeout = 180
        vote_timeout = 45
    elif num_players <= 12:
        night_timeout = 60
        day_timeout = 300
        vote_timeout = 60
    else:
        night_timeout = 90
        day_timeout = 400
        vote_timeout = 90

    return GameConfig(
        num_players=num_players,
        role_names=role_names,
        night_timeout=night_timeout,
        day_timeout=day_timeout,
        vote_timeout=vote_timeout,
    )
