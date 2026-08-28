import json
from typing import Any
from pathlib import Path

from pydantic import Field, BaseModel

from llm_werewolf.core.types import GamePhase, PlayerStatus, PlayerProtocol, GameStateProtocol
from llm_werewolf.core.player import Player
from llm_werewolf.core.game_state import GameState
from llm_werewolf.core.role_registry import get_role_map
from llm_werewolf.core.roles.neutral import Thief
from llm_werewolf.core.roles.villager import Cupid, Elder, Guard, Idiot, Witch, Knight, Magician
from llm_werewolf.core.roles.werewolf import WolfBeauty, BloodMoonApostle


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


def _extract_witch_data(role: Witch) -> dict[str, Any]:
    """Extract Witch role data."""
    return {"has_save_potion": role.has_save_potion, "has_poison_potion": role.has_poison_potion}


def _extract_role_data(player: PlayerProtocol) -> dict[str, Any]:
    """Extract role-specific data for serialization.

    Args:
        player: The player whose role data to extract.

    Returns:
        dict[str, Any]: Role-specific data.
    """
    role = player.role
    role_data: dict[str, Any] = {}

    # Use dictionary mapping for simpler roles
    simple_extractors = {
        Guard: lambda r: {"last_protected": r.last_protected},
        Elder: lambda r: {"lives": r.lives},
        Idiot: lambda r: {"revealed": r.revealed},
        WolfBeauty: lambda r: {"charmed_player": r.charmed_player},
        Knight: lambda r: {"has_dueled": r.has_dueled},
        Cupid: lambda r: {"has_linked": r.has_linked},
        BloodMoonApostle: lambda r: {"transformed": r.transformed},
        Magician: lambda r: {"has_swapped": r.has_swapped},
        Thief: lambda r: {"has_chosen": r.has_chosen},
    }

    # Special handling for Witch
    if isinstance(role, Witch):
        return _extract_witch_data(role)

    # Check simple extractors
    for role_class, extractor in simple_extractors.items():
        if isinstance(role, role_class):
            return extractor(role)

    return role_data


def serialize_player(player: PlayerProtocol) -> PlayerSnapshot:
    """Serialize a player to a snapshot.

    Args:
        player: The player to serialize.

    Returns:
        PlayerSnapshot: Serialized player data.
    """
    return PlayerSnapshot(
        player_id=player.player_id,
        name=player.name,
        role_name=player.get_role_name(),
        role_data=_extract_role_data(player),
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


def _restore_witch_data(role: Witch, role_data: dict[str, Any]) -> None:
    """Restore Witch role data."""
    role.has_save_potion = role_data.get("has_save_potion", True)
    role.has_poison_potion = role_data.get("has_poison_potion", True)


def _restore_role_data(player: Player, role_data: dict[str, Any]) -> None:
    """Restore role-specific data to a player's role.

    Args:
        player: The player whose role to restore.
        role_data: The role-specific data to restore.
    """
    role = player.role

    # Use dictionary mapping for simpler roles
    simple_restorers = {
        Guard: lambda r, d: setattr(r, "last_protected", d.get("last_protected")),
        Elder: lambda r, d: setattr(r, "lives", d.get("lives", 2)),
        Idiot: lambda r, d: setattr(r, "revealed", d.get("revealed", False)),
        WolfBeauty: lambda r, d: setattr(r, "charmed_player", d.get("charmed_player")),
        Knight: lambda r, d: setattr(r, "has_dueled", d.get("has_dueled", False)),
        Cupid: lambda r, d: setattr(r, "has_linked", d.get("has_linked", False)),
        BloodMoonApostle: lambda r, d: setattr(r, "transformed", d.get("transformed", False)),
        Magician: lambda r, d: setattr(r, "has_swapped", d.get("has_swapped", False)),
        Thief: lambda r, d: setattr(r, "has_chosen", d.get("has_chosen", False)),
    }

    # Special handling for Witch
    if isinstance(role, Witch):
        _restore_witch_data(role, role_data)
        return

    # Check simple restorers
    for role_class, restorer in simple_restorers.items():
        if isinstance(role, role_class):
            restorer(role, role_data)
            return


def _restore_players(snapshot: GameStateSnapshot, agent_factory: dict[str, Any]) -> list[Player]:
    """Restore players from snapshot.

    Args:
        snapshot: The game state snapshot.
        agent_factory: Dictionary mapping player_id to agent instances.

    Returns:
        list[Player]: List of restored players.

    Raises:
        ValueError: If an unknown role is encountered.
    """
    players: list[Player] = []
    role_map = get_role_map()

    for p_snap in snapshot.players:
        # Get role class from registry
        role_class = role_map.get(p_snap.role_name)
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
        _restore_role_data(player, p_snap.role_data)

        players.append(player)

    return players


def _restore_game_state_fields(game_state: GameState, snapshot: GameStateSnapshot) -> None:
    """Restore game state fields from snapshot.

    Args:
        game_state: The game state to restore fields to.
        snapshot: The snapshot containing the fields to restore.
    """
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


def restore_game_state(
    snapshot: GameStateSnapshot, agent_factory: dict[str, Any] | None = None
) -> GameState:
    """Restore a GameState from a snapshot.

    Args:
        snapshot: The game state snapshot.
        agent_factory: Optional dictionary mapping player_id to agent instances. If not provided, players will have no agents.

    Returns:
        GameState: The restored game state.

    Note:
        Agents cannot be serialized, so they must be recreated manually.
        Pass a dictionary mapping player_id to agent instances to restore agents.
    """
    agent_factory = agent_factory or {}

    # Restore players
    players = _restore_players(snapshot, agent_factory)

    # Create game state
    game_state = GameState(players)

    # Restore game state fields
    _restore_game_state_fields(game_state, snapshot)

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
