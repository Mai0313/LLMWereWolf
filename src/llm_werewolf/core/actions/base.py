from abc import ABC, abstractmethod

from llm_werewolf.core.types import ActionType, PlayerProtocol, GameStateProtocol


class Action(ABC):
    """Abstract base class for all game actions."""

    def __init__(self, actor: PlayerProtocol, game_state: GameStateProtocol) -> None:
        """Initialize the action.

        Args:
            actor: The player performing the action.
            game_state: The current game state.
        """
        self.actor = actor
        self.game_state = game_state

    @abstractmethod
    def get_action_type(self) -> ActionType:
        """Get the type of this action.

        Returns:
            ActionType: The action type.
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate if the action can be performed.

        Returns:
            bool: True if the action is valid.
        """
        pass

    @abstractmethod
    def execute(self) -> list[str]:
        """Execute the action.

        Returns:
            list[str]: Messages describing the action results.
        """
        pass
