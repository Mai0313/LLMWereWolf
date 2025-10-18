"""Validation utilities for the Werewolf game."""

from llm_werewolf.core.player import Player
from llm_werewolf.core.game_state import GameState


def validate_player_action(
    actor: Player, target: Player | None, action_type: str, game_state: GameState
) -> tuple[bool, str]:
    """Validate if a player can perform an action.

    Args:
        actor: The player performing the action.
        target: The target player (if any).
        action_type: Type of action being performed.
        game_state: Current game state.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
    """
    # Actor must be alive (except hunter revenge)
    if not actor.is_alive() and action_type != "hunter_shoot":
        return False, f"{actor.name} is dead and cannot perform actions"

    # Target validation
    if target is not None:
        if actor.player_id == target.player_id:
            return False, "Cannot target yourself"

        # Most actions require target to be alive
        if action_type not in ["graveyard_check", "hunter_shoot"] and not target.is_alive():
            return False, f"{target.name} is already dead"

    return True, ""


def validate_vote(voter: Player, target: Player, game_state: GameState) -> tuple[bool, str]:
    """Validate if a vote is valid.

    Args:
        voter: The player voting.
        target: The player being voted for.
        game_state: Current game state.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
    """
    # Voter must be alive and able to vote
    if not voter.is_alive():
        return False, f"{voter.name} is dead and cannot vote"

    if not voter.can_vote():
        return False, f"{voter.name} has lost voting rights"

    # Target must be alive
    if not target.is_alive():
        return False, f"{target.name} is dead and cannot be voted for"

    # Cannot vote for yourself
    if voter.player_id == target.player_id:
        return False, "Cannot vote for yourself"

    # Must be in voting phase
    if game_state.phase.value != "day_voting":
        return False, "Not in voting phase"

    return True, ""


def validate_game_config(num_players: int, role_names: list[str]) -> tuple[bool, str]:
    """Validate game configuration.

    Args:
        num_players: Number of players.
        role_names: List of role names.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
    """
    # Check player count
    if num_players < 6:
        return False, "Minimum 6 players required"
    if num_players > 20:
        return False, "Maximum 20 players allowed"

    # Check role count matches players
    if len(role_names) != num_players:
        return False, f"Number of roles ({len(role_names)}) must match players ({num_players})"

    # Check for at least one werewolf
    werewolf_roles = {
        "Werewolf",
        "AlphaWolf",
        "WhiteWolf",
        "WolfBeauty",
        "GuardianWolf",
        "HiddenWolf",
        "NightmareWolf",
        "BloodMoonApostle",
    }
    werewolf_count = sum(1 for role in role_names if role in werewolf_roles)
    if werewolf_count == 0:
        return False, "At least one werewolf role is required"

    # Check werewolf ratio (shouldn't be more than 1/3 of players)
    if werewolf_count > num_players // 3 + 1:
        return (
            False,
            f"Too many werewolves ({werewolf_count}). "
            f"Should be at most {num_players // 3 + 1} for {num_players} players",
        )

    return True, ""


def sanitize_player_name(name: str) -> str:
    """Sanitize a player name.

    Args:
        name: The player name to sanitize.

    Returns:
        str: Sanitized name.
    """
    # Remove leading/trailing whitespace
    name = name.strip()

    # Limit length
    max_length = 20
    if len(name) > max_length:
        name = name[:max_length]

    # Replace empty name
    if not name:
        name = "Player"

    return name


def validate_player_id(player_id: str) -> bool:
    """Validate a player ID format.

    Args:
        player_id: The player ID to validate.

    Returns:
        bool: True if valid.
    """
    # Check if non-empty string
    if not player_id or not isinstance(player_id, str):
        return False

    # Check reasonable length
    return not len(player_id) > 100
