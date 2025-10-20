from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_werewolf.core.types import Camp, RoleConfig, ActionPriority
    from llm_werewolf.core.player import Player
    from llm_werewolf.core.actions import Action
    from llm_werewolf.core.game_state import GameState


class Role(ABC):
    """Abstract base class for all roles in the Werewolf game."""

    def __init__(self, player: Player) -> None:
        """Initialize the role."""
        self.player = player
        self.ability_uses = 0
        self.config = self.get_config()
        self.disabled = False  # If True, role abilities are disabled

    @abstractmethod
    def get_config(self) -> RoleConfig:
        """Get the configuration for this role.

        Returns:
            RoleConfig: The role's configuration.
        """
        pass

    @property
    def name(self) -> str:
        """Get the role name.

        Returns:
            str: The role name.
        """
        return self.config.name

    @property
    def camp(self) -> Camp:
        """Get the role's camp.

        Returns:
            Camp: The camp this role belongs to.
        """
        return self.config.camp

    @property
    def description(self) -> str:
        """Get the role description.

        Returns:
            str: Description of the role's abilities.
        """
        return self.config.description

    @property
    def priority(self) -> ActionPriority | None:
        """Get the action priority.

        Returns:
            ActionPriority | None: The priority of night actions, or None if no night action.
        """
        return self.config.priority

    def can_act_tonight(self, player: Player, round_number: int) -> bool:
        """Check if this role can perform an action tonight.

        Args:
            player: The player with this role.
            round_number: The current round number.

        Returns:
            bool: True if the role can act tonight.
        """
        if self.disabled:
            return False

        if not self.config.can_act_night:
            return False

        if not player.is_alive():
            return False

        return not (self.config.max_uses is not None and self.ability_uses >= self.config.max_uses)

    def can_act_today(self, player: Player) -> bool:
        """Check if this role can perform an action today.

        Args:
            player: The player with this role.

        Returns:
            bool: True if the role can act today.
        """
        if not self.config.can_act_day:
            return False

        return player.is_alive()

    def get_action_prompt(self, player: Player, game_state: object) -> str:
        """Get the prompt for the AI agent when this role needs to act.

        Args:
            player: The player with this role.
            game_state: The current game state.

        Returns:
            str: The prompt string for the AI agent.
        """
        return f"You are {player.name}, a {self.name}. {self.description}"

    @abstractmethod
    def get_night_actions(self, game_state: GameState) -> list[Action]:
        """Get the night actions for this role.

        Args:
            game_state: The current game state.

        Returns:
            list[Action]: A list of actions to perform.
        """

    def has_night_action(self, game_state: GameState) -> bool:
        """Check if the role has a night action.

        Args:
            game_state: The current game state.

        Returns:
            bool: True if the role has a night action.
        """
        if self.disabled:
            return False
        return self.config.can_act_night

    def validate_action(self, actor: Player, target: Player | None, action_data: dict) -> bool:
        """Validate if an action is legal.

        Args:
            actor: The player performing the action.
            target: The target player (if any).
            action_data: Additional action data.

        Returns:
            bool: True if the action is valid.
        """
        return True

    def use_ability(self) -> None:
        """Mark that the ability has been used."""
        self.ability_uses += 1

    def __str__(self) -> str:
        """String representation of the role.

        Returns:
            str: The role name.
        """
        return self.name

    def __repr__(self) -> str:
        """Repr of the role.

        Returns:
            str: The role representation.
        """
        return f"{self.__class__.__name__}()"
