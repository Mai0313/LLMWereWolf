from typing import TYPE_CHECKING

from pydantic import Field, BaseModel

from llm_werewolf.core.game_state import GameState

if TYPE_CHECKING:
    from llm_werewolf.core.player import Player


class VictoryResult(BaseModel):
    """Result of a victory check."""

    has_winner: bool = Field(..., description="Whether there is a winner")
    winner_camp: str | None = Field(None, description="The winning camp")
    winner_ids: list[str] = Field(default_factory=list, description="IDs of winning players")
    reason: str = Field(..., description="Reason for the victory")


class VictoryChecker:
    """Checks for victory conditions in the Werewolf game."""

    def __init__(self, game_state: GameState) -> None:
        """Initialize the victory checker.

        Args:
            game_state: The current game state.
        """
        self.game_state = game_state

    def check_victory(self) -> VictoryResult:
        """Check if any victory condition has been met.

        Returns:
            VictoryResult: The victory check result.
        """
        # Check for lover victory first (highest priority)
        lover_result = self.check_lover_victory()
        if lover_result.has_winner:
            return lover_result

        # Check werewolf victory
        werewolf_result = self.check_werewolf_victory()
        if werewolf_result.has_winner:
            return werewolf_result

        # Check villager victory
        villager_result = self.check_villager_victory()
        if villager_result.has_winner:
            return villager_result

        # No winner yet
        return VictoryResult(has_winner=False, reason="Game continues")

    def check_werewolf_victory(self) -> VictoryResult:
        """Check if werewolves have won.

        Werewolves win when they equal or outnumber the villagers.

        Returns:
            VictoryResult: The victory check result.
        """
        alive_players = self.game_state.get_alive_players()

        werewolf_count = sum(1 for p in alive_players if p.get_camp() == "werewolf")
        villager_count = sum(1 for p in alive_players if p.get_camp() == "villager")

        if werewolf_count >= villager_count and werewolf_count > 0:
            werewolf_ids = [p.player_id for p in alive_players if p.get_camp() == "werewolf"]
            return VictoryResult(
                has_winner=True,
                winner_camp="werewolf",
                winner_ids=werewolf_ids,
                reason=f"Werewolves ({werewolf_count}) equal or outnumber villagers ({villager_count})",
            )

        return VictoryResult(has_winner=False, reason="Werewolves have not won")

    def check_villager_victory(self) -> VictoryResult:
        """Check if villagers have won.

        Villagers win when all werewolves are eliminated.

        Returns:
            VictoryResult: The victory check result.
        """
        alive_players = self.game_state.get_alive_players()

        werewolf_count = sum(1 for p in alive_players if p.get_camp() == "werewolf")

        if werewolf_count == 0:
            villager_ids = [p.player_id for p in alive_players if p.get_camp() == "villager"]
            return VictoryResult(
                has_winner=True,
                winner_camp="villager",
                winner_ids=villager_ids,
                reason="All werewolves have been eliminated",
            )

        return VictoryResult(has_winner=False, reason="Villagers have not won")

    def check_lover_victory(self) -> VictoryResult:
        """Check if lovers have won.

        Lovers win when only the two lovers remain alive.

        Returns:
            VictoryResult: The victory check result.
        """
        alive_players = self.game_state.get_alive_players()

        # Find all lovers
        lovers = [p for p in alive_players if p.is_lover()]

        # Lovers win if only they remain and both are alive
        if len(lovers) == 2 and len(alive_players) == 2:
            lover_ids = [p.player_id for p in lovers]
            return VictoryResult(
                has_winner=True,
                winner_camp="lover",
                winner_ids=lover_ids,
                reason="Only the lovers remain alive",
            )

        return VictoryResult(has_winner=False, reason="Lovers have not won")

    def check_special_victory(self) -> VictoryResult:
        """Check for special victory conditions.

        This can be extended for custom game modes or special roles.

        Returns:
            VictoryResult: The victory check result.
        """
        # Placeholder for future special victory conditions
        return VictoryResult(has_winner=False, reason="No special victory")

    def get_winner(self) -> VictoryResult:
        """Get the current winner if any.

        Returns:
            VictoryResult: The victory result.
        """
        return self.check_victory()

    def is_game_over(self) -> bool:
        """Check if the game is over.

        Returns:
            bool: True if the game has ended.
        """
        return self.check_victory().has_winner

    def get_winning_players(self) -> list["Player"]:
        """Get the list of winning players.

        Returns:
            list[Player]: List of winning players, or empty list if no winner.
        """
        result = self.check_victory()
        if not result.has_winner:
            return []

        return [
            self.game_state.get_player(player_id)
            for player_id in result.winner_ids
            if self.game_state.get_player(player_id) is not None
        ]

    def get_losing_players(self) -> list["Player"]:
        """Get the list of losing players.

        Returns:
            list[Player]: List of losing players, or empty list if no winner.
        """
        result = self.check_victory()
        if not result.has_winner:
            return []

        winning_ids = set(result.winner_ids)
        return [p for p in self.game_state.players if p.player_id not in winning_ids]
