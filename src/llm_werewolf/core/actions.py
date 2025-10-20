from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from llm_werewolf.core.types import ActionType

if TYPE_CHECKING:
    from llm_werewolf.core.player import Player
    from llm_werewolf.core.game_state import GameState


class Action(ABC):
    """Abstract base class for all game actions."""

    def __init__(self, actor: Player, game_state: GameState) -> None:
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


class WerewolfVoteAction(Action):
    """Action for a werewolf to vote for a kill target."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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


class WitchSaveAction(Action):
    """Action for witch to save a player."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
        """Initialize the witch save action.

        Args:
            actor: The witch performing the action.
            target: The target player to save.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.WITCH_SAVE

    def validate(self) -> bool:
        """Validate the save action."""
        from llm_werewolf.core.roles.villager import Witch

        if not isinstance(self.actor.role, Witch):
            return False

        if self.game_state.werewolf_target != self.target.player_id:
            return False

        return self.actor.is_alive() and self.actor.role.has_save_potion

    def execute(self) -> list[str]:
        """Execute the witch save."""
        from llm_werewolf.core.roles.villager import Witch

        if isinstance(self.actor.role, Witch):
            self.actor.role.has_save_potion = False
        self.game_state.witch_saved_target = self.target.player_id
        return [f"Witch saves {self.target.name}"]


class WitchPoisonAction(Action):
    """Action for witch to poison a player."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
        """Initialize the witch poison action.

        Args:
            actor: The witch performing the action.
            target: The target player to poison.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.WITCH_POISON

    def validate(self) -> bool:
        """Validate the poison action."""
        from llm_werewolf.core.roles.villager import Witch

        if not isinstance(self.actor.role, Witch):
            return False
        return (
            self.actor.is_alive() and self.actor.role.has_poison_potion and self.target.is_alive()
        )

    def execute(self) -> list[str]:
        """Execute the witch poison."""
        from llm_werewolf.core.roles.villager import Witch

        if isinstance(self.actor.role, Witch):
            self.actor.role.has_poison_potion = False
        self.game_state.witch_poison_target = self.target.player_id
        return [f"Witch poisons {self.target.name}"]


class SeerCheckAction(Action):
    """Action for seer to check a player."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
        """Initialize the seer check action.

        Args:
            actor: The seer performing the action.
            target: The target player to check.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.SEER_CHECK

    def validate(self) -> bool:
        """Validate the seer check."""
        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the seer check."""
        from llm_werewolf.core.roles.werewolf import HiddenWolf

        result = self.target.get_camp()

        if isinstance(self.target.role, HiddenWolf):
            result = "villager"

        self.game_state.seer_checked[self.game_state.round_number] = self.target.player_id
        return [f"Seer checks {self.target.name}: {result}"]


class GuardProtectAction(Action):
    """Action for guard to protect a player."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
        """Initialize the guard protect action.

        Args:
            actor: The guard performing the action.
            target: The target player to protect.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.GUARD_PROTECT

    def validate(self) -> bool:
        """Validate the guard protect."""
        from llm_werewolf.core.roles.villager import Guard

        if not isinstance(self.actor.role, Guard):
            return False

        if self.actor.role.last_protected == self.target.player_id:
            return False

        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the guard protect."""
        from llm_werewolf.core.roles.villager import Guard

        if isinstance(self.actor.role, Guard):
            self.actor.role.last_protected = self.target.player_id

        self.game_state.guard_protected = self.target.player_id
        return [f"Guard protects {self.target.name}"]


class VoteAction(Action):
    """Action for voting during the day."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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


class CupidLinkAction(Action):
    """Action for Cupid to link two players as lovers."""

    def __init__(
        self, actor: Player, target1: Player, target2: Player, game_state: GameState
    ) -> None:
        """Initialize the cupid link action.

        Args:
            actor: The cupid performing the action.
            target1: First player to link.
            target2: Second player to link.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target1 = target1
        self.target2 = target2

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.CUPID_LINK

    def validate(self) -> bool:
        """Validate the cupid link."""
        from llm_werewolf.core.roles.villager import Cupid

        if not isinstance(self.actor.role, Cupid):
            return False

        if self.actor.role.has_linked:
            return False

        return (
            self.actor.is_alive()
            and self.target1.is_alive()
            and self.target2.is_alive()
            and self.target1.player_id != self.target2.player_id
        )

    def execute(self) -> list[str]:
        """Execute the cupid link."""
        from llm_werewolf.core.roles.villager import Cupid

        self.target1.set_lover(self.target2.player_id)
        self.target2.set_lover(self.target1.player_id)

        if isinstance(self.actor.role, Cupid):
            self.actor.role.has_linked = True

        return [f"Cupid links {self.target1.name} and {self.target2.name} as lovers"]


class RavenMarkAction(Action):
    """Action for Raven to mark a player for extra votes."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
        """Initialize the raven mark action.

        Args:
            actor: The raven performing the action.
            target: The target player to mark.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.RAVEN_MARK

    def validate(self) -> bool:
        """Validate the raven mark."""
        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the raven mark."""
        self.game_state.raven_marked = self.target.player_id
        return [f"Raven marks {self.target.name}"]


class WhiteWolfKillAction(Action):
    """Action for White Wolf to kill another werewolf."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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
        from llm_werewolf.core.roles.werewolf import WhiteWolf

        if not isinstance(self.actor.role, WhiteWolf):
            return False

        if self.game_state.round_number % 2 == 0:
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

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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
        from llm_werewolf.core.roles.werewolf import WolfBeauty

        if not isinstance(self.actor.role, WolfBeauty):
            return False

        if self.actor.role.charmed_player:
            return False

        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the wolf beauty charm."""
        from llm_werewolf.core.roles.werewolf import WolfBeauty

        if isinstance(self.actor.role, WolfBeauty):
            self.actor.role.charmed_player = self.target.player_id

        return [f"Wolf Beauty charms {self.target.name}"]


class GuardianWolfProtectAction(Action):
    """Action for Guardian Wolf to protect a werewolf."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
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


class GraveyardKeeperCheckAction(Action):
    """Action for Graveyard Keeper to check a dead player."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
        """Initialize the graveyard keeper check action.

        Args:
            actor: The graveyard keeper performing the action.
            target: The dead player to check.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.SEER_CHECK

    def validate(self) -> bool:
        """Validate the graveyard keeper check."""
        return self.actor.is_alive() and not self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the graveyard keeper check."""
        camp = self.target.get_camp()
        role_name = self.target.get_role_name()
        return [
            f"Graveyard Keeper checks {self.target.name}: They were a {role_name} ({camp} camp)"
        ]


class KnightDuelAction(Action):
    """Action for Knight to duel a player during the day."""

    def __init__(self, actor: Player, target: Player, game_state: GameState) -> None:
        """Initialize the knight duel action.

        Args:
            actor: The knight performing the action.
            target: The target player to duel.
            game_state: The current game state.
        """
        super().__init__(actor, game_state)
        self.target = target

    def get_action_type(self) -> ActionType:
        """Get the action type."""
        return ActionType.KNIGHT_DUEL

    def validate(self) -> bool:
        """Validate the knight duel."""
        from llm_werewolf.core.roles.villager import Knight

        if not isinstance(self.actor.role, Knight):
            return False

        if self.actor.role.has_dueled:
            return False

        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the knight duel."""
        from llm_werewolf.core.roles.villager import Knight

        messages = []

        if self.target.get_camp() == "werewolf":
            self.target.kill()
            self.game_state.day_deaths.add(self.target.player_id)
            messages.append(f"Knight {self.actor.name} duels and defeats {self.target.name}!")
        else:
            self.actor.kill()
            self.game_state.day_deaths.add(self.actor.player_id)
            messages.append(f"Knight {self.actor.name} loses the duel and dies!")

        if isinstance(self.actor.role, Knight):
            self.actor.role.has_dueled = True

        return messages
