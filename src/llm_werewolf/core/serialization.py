from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from pathlib import Path

from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from llm_werewolf.core.types import PlayerProtocol, GameStateProtocol
    from llm_werewolf.core.game_state import GameState


class PlayerSnapshot(BaseModel):
    """Serializable snapshot of a player's state."""

    player_id: str
    name: str
    role_name: str
    role_data: dict[str, Any] = Field(default_factory=dict)
    is_alive: bool
    statuses: list[str] = Field(default_factory=list)
    lover_partner_id: str | None = None
    can_vote_flag: bool = True
    ai_model: str = "unknown"


class GameStateSnapshot(BaseModel):
    """Serializable snapshot of the game state."""

    players: list[PlayerSnapshot]

    phase: str
    round_number: int

    night_deaths: list[str] = Field(default_factory=list)
    day_deaths: list[str] = Field(default_factory=list)
    death_abilities_used: list[str] = Field(default_factory=list)
    death_causes: dict[str, str] = Field(default_factory=dict)

    werewolf_target: str | None = None
    werewolf_votes: dict[str, str] = Field(default_factory=dict)
    witch_save_used: bool = False
    witch_poison_used: bool = False
    witch_saved_target: str | None = None
    witch_poison_target: str | None = None
    guard_protected: str | None = None
    guardian_wolf_protected: str | None = None
    nightmare_blocked: str | None = None
    seer_checked: dict[str, str] = Field(default_factory=dict)

    # Voting tracking
    votes: dict[str, str] = Field(default_factory=dict)
    raven_marked: str | None = None

    # Winner
    winner: str | None = None


def serialize_player(player: PlayerProtocol) -> PlayerSnapshot:
    """Serialize a player to a snapshot.

    Args:
        player: The player to serialize.

    Returns:
        PlayerSnapshot: Serialized player data.
    """
    from llm_werewolf.core.roles.neutral import Thief
    from llm_werewolf.core.roles.villager import (
        Cupid,
        Elder,
        Guard,
        Idiot,
        Witch,
        Knight,
        Magician,
    )
    from llm_werewolf.core.roles.werewolf import WhiteWolf, WolfBeauty, BloodMoonApostle

    # Serialize role-specific data
    role_data: dict[str, Any] = {}

    if isinstance(player.role, Witch):
        role_data["has_save_potion"] = player.role.has_save_potion
        role_data["has_poison_potion"] = player.role.has_poison_potion
    elif isinstance(player.role, Guard):
        role_data["last_protected"] = player.role.last_protected
    elif isinstance(player.role, Elder):
        role_data["lives"] = player.role.lives
    elif isinstance(player.role, Idiot):
        role_data["revealed"] = player.role.revealed
    elif isinstance(player.role, WolfBeauty):
        role_data["charmed_player"] = player.role.charmed_player
    elif isinstance(player.role, Knight):
        role_data["has_dueled"] = player.role.has_dueled
    elif isinstance(player.role, Cupid):
        role_data["has_linked"] = player.role.has_linked
    elif isinstance(player.role, BloodMoonApostle):
        role_data["transformed"] = player.role.transformed
    elif isinstance(player.role, Magician):
        role_data["has_swapped"] = player.role.has_swapped
    elif isinstance(player.role, Thief):
        role_data["has_chosen"] = player.role.has_chosen
    elif isinstance(player.role, WhiteWolf):
        # WhiteWolf doesn't have additional state to save
        pass

    return PlayerSnapshot(
        player_id=player.player_id,
        name=player.name,
        role_name=player.get_role_name(),
        role_data=role_data,
        is_alive=player.is_alive(),
        statuses=[s.value for s in player.statuses],
        lover_partner_id=player.lover_partner_id,
        can_vote_flag=player.can_vote_flag,
        ai_model=player.ai_model,
    )


def serialize_game_state(game_state: GameStateProtocol) -> GameStateSnapshot:
    """Serialize a game state to a snapshot.

    Args:
        game_state: The game state to serialize.

    Returns:
        GameStateSnapshot: Serialized game state data.
    """
    return GameStateSnapshot(
        players=[serialize_player(p) for p in game_state.players],
        phase=game_state.phase.value,
        round_number=game_state.round_number,
        night_deaths=list(game_state.night_deaths),
        day_deaths=list(game_state.day_deaths),
        death_abilities_used=list(game_state.death_abilities_used),
        death_causes=game_state.death_causes,
        werewolf_target=game_state.werewolf_target,
        werewolf_votes=game_state.werewolf_votes,
        witch_save_used=game_state.witch_save_used,
        witch_poison_used=game_state.witch_poison_used,
        witch_saved_target=game_state.witch_saved_target,
        witch_poison_target=game_state.witch_poison_target,
        guard_protected=game_state.guard_protected,
        guardian_wolf_protected=game_state.guardian_wolf_protected,
        nightmare_blocked=game_state.nightmare_blocked,
        seer_checked={str(k): v for k, v in game_state.seer_checked.items()},
        votes=game_state.votes,
        raven_marked=game_state.raven_marked,
        winner=game_state.winner,
    )


def save_game_state(game_state: GameStateProtocol, file_path: str | Path) -> None:
    """Save game state to a JSON file.

    Args:
        game_state: The game state to save.
        file_path: Path to the save file.
    """
    snapshot = serialize_game_state(game_state)
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        f.write(snapshot.model_dump_json(indent=2))


def load_game_state_snapshot(file_path: str | Path) -> GameStateSnapshot:
    """Load a game state snapshot from a JSON file.

    Args:
        file_path: Path to the save file.

    Returns:
        GameStateSnapshot: The loaded game state snapshot.

    Note:
        This only loads the snapshot. To restore a full GameState with agents,
        you need to use restore_game_state() which requires agent factory.
    """
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return GameStateSnapshot.model_validate(data)


def restore_game_state(
    snapshot: GameStateSnapshot, agent_factory: dict[str, Any] | None = None
) -> GameState:
    """Restore a GameState from a snapshot.

    Args:
        snapshot: The game state snapshot.
        agent_factory: Optional dictionary mapping player_id to agent instances.
                      If not provided, players will have no agents.

    Returns:
        GameState: The restored game state.

    Note:
        Agents cannot be serialized, so they must be recreated manually.
        Pass a dictionary mapping player_id to agent instances to restore agents.
    """
    from llm_werewolf.core.types import GamePhase, PlayerStatus
    from llm_werewolf.core.player import Player
    from llm_werewolf.core.game_state import GameState
    from llm_werewolf.core.role_registry import RoleRegistry

    agent_factory = agent_factory or {}

    # Restore players
    players: list[Player] = []
    for p_snap in snapshot.players:
        # Get role class from registry
        role_class = RoleRegistry.get_role(p_snap.role_name)
        if not role_class:
            msg = f"Unknown role: {p_snap.role_name}"
            raise ValueError(msg)

        # Get agent for this player (if available)
        agent = agent_factory.get(p_snap.player_id)

        # Create player
        player = Player(
            player_id=p_snap.player_id,
            name=p_snap.name,
            role=role_class,
            agent=agent,
            ai_model=p_snap.ai_model,
        )

        # Restore player state
        if not p_snap.is_alive:
            player.kill()

        player.statuses = {PlayerStatus(s) for s in p_snap.statuses}
        player.lover_partner_id = p_snap.lover_partner_id
        player.can_vote_flag = p_snap.can_vote_flag

        # Restore role-specific data
        from llm_werewolf.core.roles.neutral import Thief
        from llm_werewolf.core.roles.villager import (
            Cupid,
            Elder,
            Guard,
            Idiot,
            Witch,
            Knight,
            Magician,
        )
        from llm_werewolf.core.roles.werewolf import WolfBeauty, BloodMoonApostle

        if isinstance(player.role, Witch):
            player.role.has_save_potion = p_snap.role_data.get("has_save_potion", True)
            player.role.has_poison_potion = p_snap.role_data.get("has_poison_potion", True)
        elif isinstance(player.role, Guard):
            player.role.last_protected = p_snap.role_data.get("last_protected")
        elif isinstance(player.role, Elder):
            player.role.lives = p_snap.role_data.get("lives", 2)
        elif isinstance(player.role, Idiot):
            player.role.revealed = p_snap.role_data.get("revealed", False)
        elif isinstance(player.role, WolfBeauty):
            player.role.charmed_player = p_snap.role_data.get("charmed_player")
        elif isinstance(player.role, Knight):
            player.role.has_dueled = p_snap.role_data.get("has_dueled", False)
        elif isinstance(player.role, Cupid):
            player.role.has_linked = p_snap.role_data.get("has_linked", False)
        elif isinstance(player.role, BloodMoonApostle):
            player.role.transformed = p_snap.role_data.get("transformed", False)
        elif isinstance(player.role, Magician):
            player.role.has_swapped = p_snap.role_data.get("has_swapped", False)
        elif isinstance(player.role, Thief):
            player.role.has_chosen = p_snap.role_data.get("has_chosen", False)

        players.append(player)

    # Create game state
    game_state = GameState(players)

    # Restore game state fields
    game_state.phase = GamePhase(snapshot.phase)
    game_state.round_number = snapshot.round_number

    game_state.night_deaths = set(snapshot.night_deaths)
    game_state.day_deaths = set(snapshot.day_deaths)
    game_state.death_abilities_used = set(snapshot.death_abilities_used)
    game_state.death_causes = snapshot.death_causes

    game_state.werewolf_target = snapshot.werewolf_target
    game_state.werewolf_votes = snapshot.werewolf_votes
    game_state.witch_save_used = snapshot.witch_save_used
    game_state.witch_poison_used = snapshot.witch_poison_used
    game_state.witch_saved_target = snapshot.witch_saved_target
    game_state.witch_poison_target = snapshot.witch_poison_target
    game_state.guard_protected = snapshot.guard_protected
    game_state.guardian_wolf_protected = snapshot.guardian_wolf_protected
    game_state.nightmare_blocked = snapshot.nightmare_blocked
    game_state.seer_checked = {int(k): v for k, v in snapshot.seer_checked.items()}

    game_state.votes = snapshot.votes
    game_state.raven_marked = snapshot.raven_marked

    game_state.winner = snapshot.winner

    return game_state


def load_game_state(
    file_path: str | Path, agent_factory: dict[str, Any] | None = None
) -> GameState:
    """Load a game state from a JSON file.

    Args:
        file_path: Path to the save file.
        agent_factory: Optional dictionary mapping player_id to agent instances.

    Returns:
        GameState: The restored game state.
    """
    snapshot = load_game_state_snapshot(file_path)
    return restore_game_state(snapshot, agent_factory)
