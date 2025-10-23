from __future__ import annotations

from llm_werewolf.core.types import ActionType, PlayerProtocol, GameStateProtocol
from llm_werewolf.core.actions.base import Action


class WerewolfVoteAction(Action):
    """Action for a werewolf to vote for a kill target."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the werewolf vote action.

        Args:
            actor: The werewolf casting the vote.
            target: The target player to vote for.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.WEREWOLF_KILL

    def validate(self) -> bool:
        """Validate the vote action."""
        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the werewolf vote."""
        self.game_state.werewolf_votes[self.actor.player_id] = self.target.player_id
        return []  # Don't reveal individual votes


class WerewolfKillAction(Action):
    """Action for werewolves to kill a player (legacy - kept for compatibility)."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the werewolf kill action.

        Args:
            actor: The werewolf performing the action.
            target: The target player to kill.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.WEREWOLF_KILL

    def validate(self) -> bool:
        """Validate the kill action."""
        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the werewolf kill."""
        self.game_state.werewolf_target = self.target.player_id
        return [f"Werewolves target {self.target.name}"]


class WhiteWolfKillAction(Action):
    """Action for White Wolf to kill another werewolf."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the white wolf kill action.

        Args:
            actor: The white wolf performing the action.
            target: The werewolf target to kill.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.WHITE_WOLF_KILL

    def validate(self) -> bool:
        """Validate the white wolf kill."""
        # Check if actor is WhiteWolf (by role name)
        if self.actor.role.name != "WhiteWolf":
            return False

        # White Wolf can only act on even rounds (2, 4, 6...)
        if self.game_state.round_number % 2 == 1:
            return False

        return (
            self.actor.is_alive()
            and self.target.is_alive()
            and self.target.get_camp() == "werewolf"
            and self.target.player_id != self.actor.player_id
        )

    def execute(self) -> list[str]:
        """Execute the white wolf kill."""
        if (
            hasattr(self.game_state, "guardian_wolf_protected")
            and self.game_state.guardian_wolf_protected == self.target.player_id
        ):
            return [
                f"White Wolf attempts to kill {self.target.name}, but they are protected by Guardian Wolf!"
            ]

        self.target.kill()
        self.game_state.night_deaths.add(self.target.player_id)
        self.game_state.death_causes[self.target.player_id] = "white_wolf"
        return [f"White Wolf kills werewolf {self.target.name}"]


class WolfBeautyCharmAction(Action):
    """Action for Wolf Beauty to charm a player."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the wolf beauty charm action.

        Args:
            actor: The wolf beauty performing the action.
            target: The target player to charm.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.WOLF_BEAUTY_CHARM

    def validate(self) -> bool:
        """Validate the wolf beauty charm."""
        # Check if actor has WolfBeauty abilities (charmed_player attribute)
        if not hasattr(self.actor.role, "charmed_player"):
            return False

        if self.actor.role.charmed_player:
            return False

        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the wolf beauty charm."""
        # Update WolfBeauty's charmed_player status
        if hasattr(self.actor.role, "charmed_player"):
            self.actor.role.charmed_player = self.target.player_id

        return [f"Wolf Beauty charms {self.target.name}"]


class GuardianWolfProtectAction(Action):
    """Action for Guardian Wolf to protect a werewolf."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the guardian wolf protect action.

        Args:
            actor: The guardian wolf performing the action.
            target: The werewolf to protect.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.GUARD_PROTECT

    def validate(self) -> bool:
        """Validate the guardian wolf protect."""
        return (
            self.actor.is_alive()
            and self.target.is_alive()
            and self.target.get_camp() == "werewolf"
        )

    def execute(self) -> list[str]:
        """Execute the guardian wolf protect."""
        self.game_state.guardian_wolf_protected = self.target.player_id
        return [f"Guardian Wolf protects {self.target.name}"]


class NightmareWolfBlockAction(Action):
    """Action for Nightmare Wolf to block a player's ability."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
        """Initialize the nightmare wolf block action.

        Args:
            actor: The nightmare wolf performing the action.
            target: The player to block.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.NIGHTMARE_BLOCK

    def validate(self) -> bool:
        """Validate the nightmare wolf block."""
        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the nightmare wolf block."""
        self.game_state.nightmare_blocked = self.target.player_id
        return [f"Nightmare Wolf blocks {self.target.name}"]
