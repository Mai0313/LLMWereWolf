from enum import Enum
from typing import TYPE_CHECKING

from pydantic import Field, BaseModel

if TYPE_CHECKING:
    from llm_werewolf.core.player import Player
    from llm_werewolf.core.game_state import GameState


class MessageType(str, Enum):
    """Enum representing different types of messages."""

    SYSTEM = "system"  # System messages (game rules, instructions)
    ROLE_INFO = "role_info"  # Information about player's role
    NIGHT_ACTION = "night_action"  # Prompt for night action
    DAY_DISCUSSION = "day_discussion"  # Day discussion
    VOTING = "voting"  # Voting prompt
    GAME_UPDATE = "game_update"  # Game state updates
    DEATH_ANNOUNCEMENT = "death_announcement"  # Death announcements
    VICTORY = "victory"  # Victory announcement


class GameMessage(BaseModel):
    """Represents a message in the game."""

    message_type: MessageType = Field(..., description="Type of the message")
    content: str = Field(..., description="The message content")
    metadata: dict = Field(default_factory=dict, description="Additional message metadata")
    sender: str | None = Field(None, description="Sender of the message (if applicable)")
    visible_to: list[str] | None = Field(None, description="Player IDs who can see this message")

    def is_visible_to(self, player_id: str) -> bool:
        """Check if this message is visible to a specific player.

        Args:
            player_id: The player ID to check.

        Returns:
            bool: True if the message is visible to the player.
        """
        if self.visible_to is None:
            return True
        return player_id in self.visible_to


class MessageBuilder:
    """Builds messages for AI agents."""

    @staticmethod
    def build_role_assignment(player: "Player") -> str:
        """Build a role assignment message.

        Args:
            player: The player receiving their role.

        Returns:
            str: The role assignment message.
        """
        return (
            f"You are {player.name}. Your role is: {player.get_role_name()}\n\n"
            f"{player.role.description}\n\n"
            f"Your camp: {player.get_camp()}\n"
            f"Your goal is to help your camp win the game."
        )

    @staticmethod
    def build_night_prompt(
        player: "Player", game_state: "GameState", available_targets: list["Player"]
    ) -> str:
        """Build a prompt for night action.

        Args:
            player: The player who needs to act.
            game_state: The current game state.
            available_targets: List of players that can be targeted.

        Returns:
            str: The night action prompt.
        """
        base_prompt = player.role.get_action_prompt(player, game_state)

        targets_str = ", ".join([p.name for p in available_targets])

        return (
            f"{base_prompt}\n\n"
            f"It is Night {game_state.round_number}. You must choose your action.\n"
            f"Available targets: {targets_str}\n\n"
            f"Please respond with the name of your target player."
        )

    @staticmethod
    def build_day_discussion_prompt(
        player: "Player", game_state: "GameState", recent_events: list[str]
    ) -> str:
        """Build a prompt for day discussion.

        Args:
            player: The player participating in discussion.
            game_state: The current game state.
            recent_events: Recent game events to inform the discussion.

        Returns:
            str: The day discussion prompt.
        """
        alive_players = game_state.get_alive_players()
        alive_names = ", ".join([p.name for p in alive_players if p.player_id != player.player_id])

        events_str = "\n".join(recent_events) if recent_events else "Nothing significant happened."

        return (
            f"It is Day {game_state.round_number}. Time for discussion.\n\n"
            f"Recent events:\n{events_str}\n\n"
            f"Alive players: {alive_names}\n\n"
            f"You may speak your thoughts, accusations, or defenses. "
            f"What would you like to say?"
        )

    @staticmethod
    def build_voting_prompt(player: "Player", game_state: "GameState") -> str:
        """Build a voting prompt.

        Args:
            player: The player who needs to vote.
            game_state: The current game state.

        Returns:
            str: The voting prompt.
        """
        alive_players = game_state.get_alive_players()
        candidates = [p.name for p in alive_players if p.player_id != player.player_id]
        candidates_str = ", ".join(candidates)

        return (
            f"It is time to vote for elimination.\n\n"
            f"Candidates: {candidates_str}\n\n"
            f"Who do you vote to eliminate? Please respond with their name."
        )

    @staticmethod
    def build_game_state_summary(game_state: "GameState", for_player: "Player") -> str:
        """Build a summary of the current game state.

        Args:
            game_state: The current game state.
            for_player: The player receiving the summary.

        Returns:
            str: The game state summary.
        """
        alive = game_state.get_alive_players()
        dead = game_state.get_dead_players()

        alive_names = ", ".join([p.name for p in alive])
        dead_names = ", ".join([p.name for p in dead]) if dead else "None"

        return (
            f"=== Game Status ===\n"
            f"Round: {game_state.round_number}\n"
            f"Phase: {game_state.phase.value}\n"
            f"Alive players ({len(alive)}): {alive_names}\n"
            f"Dead players: {dead_names}\n"
        )

    @staticmethod
    def build_death_announcement(dead_players: list["Player"], show_roles: bool = True) -> str:
        """Build a death announcement message.

        Args:
            dead_players: List of players who died.
            show_roles: Whether to show the roles of dead players.

        Returns:
            str: The death announcement.
        """
        if not dead_players:
            return "No one died."

        announcements = []
        for player in dead_players:
            if show_roles:
                announcements.append(
                    f"{player.name} has died. They were a {player.get_role_name()}."
                )
            else:
                announcements.append(f"{player.name} has died.")

        return "\n".join(announcements)

    @staticmethod
    def build_victory_announcement(winner_camp: str, winners: list["Player"]) -> str:
        """Build a victory announcement.

        Args:
            winner_camp: The winning camp.
            winners: List of winning players.

        Returns:
            str: The victory announcement.
        """
        winner_names = ", ".join([p.name for p in winners])

        return (
            f"\n{'=' * 50}\n"
            f"GAME OVER!\n"
            f"{'=' * 50}\n\n"
            f"The {winner_camp.upper()} camp has won!\n\n"
            f"Winners: {winner_names}\n"
            f"{'=' * 50}\n"
        )
