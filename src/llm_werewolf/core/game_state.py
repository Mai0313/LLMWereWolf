from enum import Enum
from typing import TYPE_CHECKING

from pydantic import Field, BaseModel

from llm_werewolf.core.events import Event

if TYPE_CHECKING:
    from llm_werewolf.core.player import Player


class GamePhase(str, Enum):
    """Enum representing the different phases of the game."""

    SETUP = "setup"  # Game initialization
    NIGHT = "night"  # Night phase (role actions)
    DAY_DISCUSSION = "day_discussion"  # Day phase (discussion)
    DAY_VOTING = "day_voting"  # Day phase (voting)
    ENDED = "ended"  # Game has ended


class GameStateInfo(BaseModel):
    """Public information about the game state."""

    phase: GamePhase = Field(..., description="Current game phase")
    round_number: int = Field(..., description="Current round number")
    total_players: int = Field(..., description="Total number of players")
    alive_players: int = Field(..., description="Number of alive players")
    werewolves_alive: int = Field(..., description="Number of alive werewolves")
    villagers_alive: int = Field(..., description="Number of alive villagers")


class GameState:
    """Manages the current state of the Werewolf game."""

    def __init__(self, players: list["Player"]) -> None:
        """Initialize the game state.

        Args:
            players: List of all players in the game.
        """
        self.players = players
        self.player_dict = {p.player_id: p for p in players}

        self.phase = GamePhase.SETUP
        self.round_number = 0

        self.event_history: list[Event] = []
        self.night_deaths: set[str] = set()  # Player IDs who died this night
        self.day_deaths: set[str] = set()  # Player IDs who died this day

        # Night action tracking
        self.werewolf_target: str | None = None
        self.witch_save_used = False
        self.witch_poison_used = False
        self.witch_saved_target: str | None = None
        self.witch_poison_target: str | None = None
        self.guard_protected: str | None = None
        self.seer_checked: dict[int, str] = {}  # round -> player_id

        # Voting tracking
        self.votes: dict[str, str] = {}  # voter_id -> target_id
        self.raven_marked: str | None = None

        self.winner: str | None = None

    def reset_deaths(self) -> None:
        """Reset the death sets for a new round."""
        self.night_deaths.clear()
        self.day_deaths.clear()

    def get_phase(self) -> GamePhase:
        """Get the current game phase.

        Returns:
            GamePhase: The current phase.
        """
        return self.phase

    def set_phase(self, phase: GamePhase) -> None:
        """Set the game phase.

        Args:
            phase: The new phase to set.
        """
        self.phase = phase

    def next_phase(self) -> GamePhase:
        """Advance to the next game phase.

        Returns:
            GamePhase: The new phase.
        """
        if self.phase == GamePhase.SETUP:
            self.phase = GamePhase.NIGHT
            self.round_number = 1
        elif self.phase == GamePhase.NIGHT:
            self.phase = GamePhase.DAY_DISCUSSION
        elif self.phase == GamePhase.DAY_DISCUSSION:
            self.phase = GamePhase.DAY_VOTING
        elif self.phase == GamePhase.DAY_VOTING:
            self.phase = GamePhase.NIGHT
            self.round_number += 1
            # Clear temporary data for new round
            self.night_deaths.clear()
            self.day_deaths.clear()
            self.votes.clear()
            self.werewolf_target = None
            self.witch_saved_target = None
            self.witch_poison_target = None
            self.guard_protected = None
            self.raven_marked = None

        return self.phase

    def get_alive_players(self, except_ids: list[str] | None = None) -> list["Player"]:
        """Get all alive players.

        Args:
            except_ids: Optional list of player IDs to exclude.

        Returns:
            list[Player]: List of alive players.
        """
        alive = [p for p in self.players if p.is_alive()]
        if except_ids:
            alive = [p for p in alive if p.player_id not in except_ids]
        return alive

    def get_dead_players(self) -> list["Player"]:
        """Get all dead players.

        Returns:
            list[Player]: List of dead players.
        """
        return [p for p in self.players if not p.is_alive()]

    def get_players_with_night_actions(self) -> list["Player"]:
        """Get all alive players that have night actions."""
        return [p for p in self.get_alive_players() if p.role.has_night_action(self)]

    def get_player(self, player_id: str) -> "Player | None":
        """Get a player by ID.

        Args:
            player_id: The player's ID.

        Returns:
            Player | None: The player, or None if not found.
        """
        return self.player_dict.get(player_id)

    def get_players_by_camp(self, camp: str) -> list["Player"]:
        """Get all players in a specific camp.

        Args:
            camp: The camp name.

        Returns:
            list[Player]: List of players in the camp.
        """
        return [p for p in self.players if p.get_camp() == camp]

    def count_alive_by_camp(self, camp: str) -> int:
        """Count alive players in a specific camp.

        Args:
            camp: The camp name.

        Returns:
            int: Number of alive players in the camp.
        """
        return sum(1 for p in self.get_alive_players() if p.get_camp() == camp)

    def record_event(self, event: Event) -> None:
        """Record a game event in history.

        Args:
            event: The event to record.
        """
        self.event_history.append(event)

    def get_recent_events(self, count: int = 10) -> list[Event]:
        """Get the most recent events.

        Args:
            count: Number of events to retrieve.

        Returns:
            list[Event]: Recent events.
        """
        return self.event_history[-count:]

    def add_vote(self, voter_id: str, target_id: str) -> None:
        """Record a vote.

        Args:
            voter_id: ID of the player voting.
            target_id: ID of the player being voted for.
        """
        self.votes[voter_id] = target_id

    def get_vote_counts(self) -> dict[str, int]:
        """Get the vote count for each player.

        Returns:
            dict[str, int]: Mapping of player_id to vote count.
        """
        vote_counts: dict[str, int] = {}
        for target_id in self.votes.values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1

        # Add raven curse (extra vote)
        if self.raven_marked and self.raven_marked in vote_counts:
            vote_counts[self.raven_marked] += 1
        elif self.raven_marked:
            vote_counts[self.raven_marked] = 1

        return vote_counts

    def get_public_info(self) -> GameStateInfo:
        """Get public information about the game state.

        Returns:
            GameStateInfo: Public game state information.
        """
        alive = self.get_alive_players()
        return GameStateInfo(
            phase=self.phase,
            round_number=self.round_number,
            total_players=len(self.players),
            alive_players=len(alive),
            werewolves_alive=self.count_alive_by_camp("werewolf"),
            villagers_alive=self.count_alive_by_camp("villager"),
        )

    def __repr__(self) -> str:
        """Repr of the game state.

        Returns:
            str: Game state representation.
        """
        return (
            f"GameState(phase={self.phase.value}, round={self.round_number}, "
            f"alive={len(self.get_alive_players())}/{len(self.players)})"
        )
