"""Protocol definitions for the LLM Werewolf game.

This module defines structural type protocols to avoid circular imports.
Protocols define the interface of objects without requiring actual imports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from llm_werewolf.core.types.enums import (
        Camp,
        GamePhase,
        ActionType,
        PlayerStatus,
        ActionPriority,
    )
    from llm_werewolf.core.types.models import PlayerInfo, RoleConfig


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol for agent objects."""

    name: str
    model: str

    def get_response(self, message: str) -> str:
        """Get a response from the agent.

        Args:
            message: The prompt message.

        Returns:
            str: The agent's response.
        """
        ...


@runtime_checkable
class RoleProtocol(Protocol):
    """Protocol for role objects."""

    player: PlayerProtocol
    ability_uses: int
    config: RoleConfig
    disabled: bool

    @property
    def name(self) -> str:
        """Get the role name."""
        ...

    @property
    def camp(self) -> Camp:
        """Get the role's camp."""
        ...

    @property
    def description(self) -> str:
        """Get the role description."""
        ...

    @property
    def priority(self) -> ActionPriority | None:
        """Get the action priority."""
        ...

    def get_config(self) -> RoleConfig:
        """Get the configuration for this role."""
        ...

    def can_act_tonight(self, player: PlayerProtocol, round_number: int) -> bool:
        """Check if this role can perform an action tonight."""
        ...

    def can_act_today(self, player: PlayerProtocol) -> bool:
        """Check if this role can perform an action today."""
        ...

    def night_action(self, game_state: GameStateProtocol) -> ActionProtocol | None:
        """Perform the role's night action."""
        ...


@runtime_checkable
class PlayerProtocol(Protocol):
    """Protocol for player objects."""

    player_id: str
    name: str
    role: RoleProtocol
    agent: AgentProtocol | None
    ai_model: str
    statuses: set[PlayerStatus]
    lover_partner_id: str | None
    can_vote_flag: bool

    def is_alive(self) -> bool:
        """Check if the player is alive."""
        ...

    def kill(self) -> None:
        """Mark the player as dead."""
        ...

    def revive(self) -> None:
        """Revive the player."""
        ...

    def add_status(self, status: PlayerStatus) -> None:
        """Add a status to the player."""
        ...

    def remove_status(self, status: PlayerStatus) -> None:
        """Remove a status from the player."""
        ...

    def has_status(self, status: PlayerStatus) -> bool:
        """Check if the player has a specific status."""
        ...

    def can_vote(self) -> bool:
        """Check if the player can vote."""
        ...

    def disable_voting(self) -> None:
        """Disable the player's voting rights."""
        ...

    def set_lover(self, partner_id: str) -> None:
        """Set this player as a lover with another player."""
        ...

    def is_lover(self) -> bool:
        """Check if the player is a lover."""
        ...

    def get_public_info(self) -> PlayerInfo:
        """Get public information about the player."""
        ...

    def get_role_name(self) -> str:
        """Get the player's role name."""
        ...

    def get_camp(self) -> str:
        """Get the player's camp."""
        ...


@runtime_checkable
class GameStateProtocol(Protocol):
    """Protocol for game state objects."""

    players: list[PlayerProtocol]
    player_dict: dict[str, PlayerProtocol]
    phase: GamePhase
    round_number: int
    night_deaths: set[str]
    day_deaths: set[str]
    death_abilities_used: set[str]
    death_causes: dict[str, str]
    werewolf_target: str | None
    werewolf_votes: dict[str, str]
    witch_save_used: bool
    witch_poison_used: bool
    witch_saved_target: str | None
    witch_poison_target: str | None
    guard_protected: str | None
    guardian_wolf_protected: str | None
    nightmare_blocked: str | None
    seer_checked: dict[int, str]
    votes: dict[str, str]
    raven_marked: str | None
    winner: str | None
    sheriff_id: str | None
    sheriff_election_done: bool
    sheriff_votes: dict[str, str]

    def reset_deaths(self) -> None:
        """Reset the death sets for a new round."""
        ...

    def get_phase(self) -> GamePhase:
        """Get the current game phase."""
        ...

    def set_phase(self, phase: GamePhase) -> None:
        """Set the game phase."""
        ...

    def next_phase(self) -> GamePhase:
        """Advance to the next game phase."""
        ...

    def get_alive_players(self) -> list[PlayerProtocol]:
        """Get all alive players."""
        ...

    def get_player(self, player_id: str) -> PlayerProtocol | None:
        """Get a player by ID."""
        ...

    def count_alive_by_camp(self, camp: Camp) -> int:
        """Count alive players in a specific camp."""
        ...


@runtime_checkable
class ActionProtocol(Protocol):
    """Protocol for action objects."""

    actor: PlayerProtocol
    game_state: GameStateProtocol

    def get_action_type(self) -> ActionType:
        """Get the type of this action."""
        ...

    def validate(self) -> bool:
        """Validate if the action can be performed."""
        ...

    def execute(self) -> list[str]:
        """Execute the action."""
        ...
