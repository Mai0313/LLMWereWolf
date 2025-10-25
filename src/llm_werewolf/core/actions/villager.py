from llm_werewolf.core.types import ActionType, PlayerProtocol, GameStateProtocol
from llm_werewolf.core.actions.base import Action


class WitchSaveAction(Action):
    """Action for witch to save a player."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
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
        # Check if actor has Witch abilities (has_save_potion attribute)
        if not hasattr(self.actor.role, "has_save_potion"):
            return False

        if self.game_state.werewolf_target != self.target.player_id:
            return False

        return self.actor.is_alive() and self.actor.role.has_save_potion

    def execute(self) -> list[str]:
        """Execute the witch save."""
        # Update Witch's save potion status
        if hasattr(self.actor.role, "has_save_potion"):
            self.actor.role.has_save_potion = False
        self.game_state.witch_saved_target = self.target.player_id
        return [f"Witch saves {self.target.name}"]


class WitchPoisonAction(Action):
    """Action for witch to poison a player."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
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
        # Check if actor has Witch abilities (has_poison_potion attribute)
        if not hasattr(self.actor.role, "has_poison_potion"):
            return False
        return (
            self.actor.is_alive() and self.actor.role.has_poison_potion and self.target.is_alive()
        )

    def execute(self) -> list[str]:
        """Execute the witch poison."""
        # Update Witch's poison potion status
        if hasattr(self.actor.role, "has_poison_potion"):
            self.actor.role.has_poison_potion = False
        self.game_state.witch_poison_target = self.target.player_id
        return [f"Witch poisons {self.target.name}"]


class SeerCheckAction(Action):
    """Action for seer to check a player."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
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
        result = self.target.get_camp()

        # HiddenWolf appears as villager to Seer (check by role name)
        if self.target.role.name == "HiddenWolf":
            result = "villager"

        # BloodMoonApostle (untransformed) appears as villager to Seer
        if self.target.role.name == "Blood Moon Apostle":
            if hasattr(self.target.role, "transformed") and not self.target.role.transformed:
                result = "villager"

        self.game_state.seer_checked[self.game_state.round_number] = self.target.player_id
        return [f"Seer checks {self.target.name}: {result}"]


class GuardProtectAction(Action):
    """Action for guard to protect a player."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
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
        # Check if actor has Guard abilities (last_protected attribute)
        if not hasattr(self.actor.role, "last_protected"):
            return False

        if self.actor.role.last_protected == self.target.player_id:
            return False

        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the guard protect."""
        # Update Guard's last protected target
        if hasattr(self.actor.role, "last_protected"):
            self.actor.role.last_protected = self.target.player_id

        self.game_state.guard_protected = self.target.player_id
        return [f"Guard protects {self.target.name}"]


class CupidLinkAction(Action):
    """Action for Cupid to link two players as lovers."""

    def __init__(
        self,
        actor: PlayerProtocol,
        target1: PlayerProtocol,
        target2: PlayerProtocol,
        game_state: GameStateProtocol,
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
        # Check if actor has Cupid abilities (has_linked attribute)
        if not hasattr(self.actor.role, "has_linked"):
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
        self.target1.set_lover(self.target2.player_id)
        self.target2.set_lover(self.target1.player_id)

        # Update Cupid's has_linked status
        if hasattr(self.actor.role, "has_linked"):
            self.actor.role.has_linked = True

        return [f"Cupid links {self.target1.name} and {self.target2.name} as lovers"]


class RavenMarkAction(Action):
    """Action for Raven to mark a player for extra votes."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
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


class GraveyardKeeperCheckAction(Action):
    """Action for Graveyard Keeper to check a dead player."""

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
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
        return ActionType.GRAVEYARD_KEEPER_CHECK

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

    def __init__(
        self, actor: PlayerProtocol, target: PlayerProtocol, game_state: GameStateProtocol
    ) -> None:
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
        # Check if actor has Knight abilities (has_dueled attribute)
        if not hasattr(self.actor.role, "has_dueled"):
            return False

        if self.actor.role.has_dueled:
            return False

        return self.actor.is_alive() and self.target.is_alive()

    def execute(self) -> list[str]:
        """Execute the knight duel."""
        messages = []

        if self.target.get_camp() == "werewolf":
            self.target.kill()
            self.game_state.day_deaths.add(self.target.player_id)
            messages.append(f"Knight {self.actor.name} duels and defeats {self.target.name}!")
        else:
            self.actor.kill()
            self.game_state.day_deaths.add(self.actor.player_id)
            messages.append(f"Knight {self.actor.name} loses the duel and dies!")

        # Update Knight's has_dueled status
        if hasattr(self.actor.role, "has_dueled"):
            self.actor.role.has_dueled = True

        return messages
