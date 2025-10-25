from llm_werewolf.core.types import ActionType, PlayerProtocol, GameStateProtocol
from llm_werewolf.core.actions.base import Action


class VoteAction(Action):
    """Action for voting during the day."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the vote action.

        Args:
            actor: The player voting.
            target: The player being voted for.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.VOTE

    def validate(self) -> bool:
        """Validate the vote."""
        return self.actor.can_vote() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the vote."""
        self.game_state.add_vote(self.actor.player_id, self.target.player_id)
        return [f"{self.actor.name} votes for {self.target.name}"]


class HunterShootAction(Action):
    """Action for hunter to shoot when dying."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the hunter shoot action.

        Args:
            actor: The hunter performing the action.
            target: The target player to shoot.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.HUNTER_SHOOT

    def validate(self) -> bool:
        """Validate the hunter shoot."""
        return not self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the hunter shoot."""
        self.target.kill()
        self.game_state.night_deaths.add(self.target.player_id)
        return [f"Hunter {self.actor.name} shoots {self.target.name}"]
