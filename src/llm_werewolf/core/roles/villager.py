import random
from typing import TYPE_CHECKING

from llm_werewolf.core.actions import (
    Action,
    CupidLinkAction,
    RavenMarkAction,
    SeerCheckAction,
    WitchSaveAction,
    WitchPoisonAction,
    GuardProtectAction,
)
from llm_werewolf.core.roles.base import Camp, Role, RoleConfig, ActionPriority

if TYPE_CHECKING:
    from llm_werewolf.core.player import Player
    from llm_werewolf.core.game_state import GameState


class Villager(Role):
    """Standard Villager role.

    An ordinary villager with no special abilities.
    Can only vote during the day phase.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Villager role."""
        return RoleConfig(
            name="Villager",
            camp=Camp.VILLAGER,
            description=(
                "You are a Villager. You have no special abilities, but you can vote "
                "during the day to eliminate suspected werewolves. Use your deduction "
                "and persuasion skills to help the village win!"
            ),
            priority=None,
            can_act_night=False,
            can_act_day=False,
        )

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Villager has no night actions."""
        return []


class Seer(Role):
    """Seer role.

    Can check one player each night to see if they are a werewolf or villager.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Seer role."""
        return RoleConfig(
            name="Seer",
            camp=Camp.VILLAGER,
            description=(
                "You are the Seer (Prophet). Each night, you can check one player "
                "to learn their true identity (werewolf or villager). Use this information "
                "wisely to guide the village, but be careful not to reveal yourself too early."
            ),
            priority=ActionPriority.SEER,
            can_act_night=True,
            can_act_day=False,
        )

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Get the night actions for the Seer role."""
        if not self.player.is_alive():
            return []

        possible_targets = [
            p for p in game_state.get_alive_players() if p.player_id != self.player.player_id
        ]
        if not possible_targets:
            return []

        # In a real implementation, the agent would choose the target.
        # For now, we'll randomly choose one.
        target = random.choice(possible_targets)  # noqa: S311
        return [SeerCheckAction(self.player, target, game_state)]


class Witch(Role):
    """Witch role.

    Has two potions: one to save someone who was killed, one to poison someone.
    Each potion can only be used once per game.
    """

    def __init__(self, player: "Player") -> None:
        """Initialize the Witch role."""
        super().__init__(player)
        self.has_save_potion = True
        self.has_poison_potion = True

    def get_config(self) -> RoleConfig:
        """Get configuration for the Witch role."""
        return RoleConfig(
            name="Witch",
            camp=Camp.VILLAGER,
            description=(
                "You are the Witch. You have two potions: a save potion to resurrect someone "
                "killed by werewolves, and a poison potion to kill any player. "
                "Each potion can only be used once per game. Use them wisely!"
            ),
            priority=ActionPriority.WITCH,
            can_act_night=True,
            can_act_day=False,
        )

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Get the night actions for the Witch role."""
        if not self.player.is_alive():
            return []

        actions = []
        # Decide whether to use save potion
        if self.has_save_potion and game_state.werewolf_target:
            target = game_state.get_player(game_state.werewolf_target)
            if target and random.random() < 0.5:  # noqa: S311
                actions.append(WitchSaveAction(self.player, target, game_state))
                self.has_save_potion = False
                return actions

        # Decide whether to use poison potion
        if self.has_poison_potion:
            possible_targets = [
                p for p in game_state.get_alive_players() if p.player_id != self.player.player_id
            ]
            if possible_targets and random.random() < 0.5:  # noqa: S311
                target = random.choice(possible_targets)  # noqa: S311
                actions.append(WitchPoisonAction(self.player, target, game_state))
                self.has_poison_potion = False

        return actions


class Hunter(Role):
    """Hunter role.

    When eliminated (by werewolves or voting), can shoot and eliminate another player.
    """

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Hunter has no night actions."""
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Hunter role."""
        return RoleConfig(
            name="Hunter",
            camp=Camp.VILLAGER,
            description=(
                "You are the Hunter. When you are eliminated (by werewolves at night or "
                "by voting during the day), you can immediately shoot and eliminate another "
                "player before you die. Choose your target carefully!"
            ),
            priority=None,
            can_act_night=False,
            can_act_day=True,  # Acts when dying
            max_uses=1,
        )


class Guard(Role):
    """Guard role.

    Can protect one player each night from werewolf attacks.
    Cannot protect the same player two nights in a row.
    """

    def __init__(self, player: "Player") -> None:
        """Initialize the Guard role."""
        super().__init__(player)
        self.last_protected: str | None = None

    def get_config(self) -> RoleConfig:
        """Get configuration for the Guard role."""
        return RoleConfig(
            name="Guard",
            camp=Camp.VILLAGER,
            description=(
                "You are the Guard. Each night, you can protect one player from werewolf attacks. "
                "The protected player cannot be killed by werewolves that night. "
                "However, you cannot protect the same player two nights in a row."
            ),
            priority=ActionPriority.GUARD,
            can_act_night=True,
            can_act_day=False,
        )

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Get the night actions for the Guard role."""
        if not self.player.is_alive():
            return []

        possible_targets = [
            p for p in game_state.get_alive_players() if p.player_id != self.last_protected
        ]
        if not possible_targets:
            return []

        # In a real implementation, the agent would choose the target.
        # For now, we'll randomly choose one.
        target = random.choice(possible_targets)  # noqa: S311
        self.last_protected = target.player_id
        return [GuardProtectAction(self.player, target, game_state)]


class Idiot(Role):
    """Idiot role.

    When voted out, reveals identity and survives but loses voting rights.
    """

    def __init__(self, player: "Player") -> None:
        """Initialize the Idiot role."""
        super().__init__(player)
        self.revealed = False

    def get_config(self) -> RoleConfig:
        """Get configuration for the Idiot role."""
        return RoleConfig(
            name="Idiot",
            camp=Camp.VILLAGER,
            description=(
                "You are the Idiot. If you are voted out during the day, you reveal your "
                "identity card and survive the elimination. However, you lose your right to vote "
                "for the rest of the game. You can still be killed by werewolves at night."
            ),
            priority=None,
            can_act_night=False,
            can_act_day=False,
        )


class Elder(Role):
    """Elder role.

    Takes two werewolf attacks to kill. If killed by villagers, all villagers
    with special abilities lose their powers.
    """

    def __init__(self, player: "Player") -> None:
        """Initialize the Elder role."""
        super().__init__(player)
        self.lives = 2

    def get_config(self) -> RoleConfig:
        """Get configuration for the Elder role."""
        return RoleConfig(
            name="Elder",
            camp=Camp.VILLAGER,
            description=(
                "You are the Elder. You have two lives and can survive one werewolf attack. "
                "However, if you are eliminated by voting during the day, all villagers with "
                "special abilities lose their powers as punishment for killing an elder."
            ),
            priority=None,
            can_act_night=False,
            can_act_day=False,
        )


class Knight(Role):
    """Knight role.

    Once per game, can duel a player during the day. If the target is a werewolf,
    they die. If not, the Knight dies.
    """

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Knight has no night actions."""
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Knight role."""
        return RoleConfig(
            name="Knight",
            camp=Camp.VILLAGER,
            description=(
                "You are the Knight. Once per game during the day, you can challenge a player "
                "to a duel before voting. If they are a werewolf, they die immediately. "
                "If they are not a werewolf, you die instead. Use this power wisely!"
            ),
            priority=None,
            can_act_night=False,
            can_act_day=True,
            max_uses=1,
        )


class Magician(Role):
    """Magician role.

    Once per game, can swap two players' roles at night.
    """

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Get the night actions for the Magician role."""
        # TODO: Implement magician logic
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Magician role."""
        return RoleConfig(
            name="Magician",
            camp=Camp.VILLAGER,
            description=(
                "You are the Magician. Once per game, you can swap the roles of two players "
                "at night. The players will not be aware of the swap initially. "
                "Use this to confuse the werewolves or save valuable roles!"
            ),
            priority=ActionPriority.GUARD,
            can_act_night=True,
            can_act_day=False,
            max_uses=1,
        )


class Cupid(Role):
    """Cupid role.

    On the first night, chooses two players to become lovers.
    Lovers win together or die together.
    """

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Get the night actions for the Cupid role."""
        if game_state.round_number == 1:
            possible_targets = game_state.get_alive_players()
            if len(possible_targets) >= 2:
                target1, target2 = random.sample(possible_targets, 2)
                return [CupidLinkAction(self.player, target1, target2, game_state)]
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Cupid role."""
        return RoleConfig(
            name="Cupid",
            camp=Camp.VILLAGER,
            description=(
                "You are Cupid. On the first night only, you choose two players to become lovers. "
                "The lovers will learn each other's identities. If one lover dies, the other dies "
                "immediately from heartbreak. Lovers win together regardless of their original camps."
            ),
            priority=ActionPriority.CUPID,
            can_act_night=True,
            can_act_day=False,
            max_uses=1,
        )


class Raven(Role):
    """Raven role.

    Each night, can mark a player to receive an extra vote against them
    during the next day's voting.
    """

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Get the night actions for the Raven role."""
        if not self.player.is_alive():
            return []

        possible_targets = game_state.get_alive_players()
        if not possible_targets:
            return []

        target = random.choice(possible_targets)  # noqa: S311
        return [RavenMarkAction(self.player, target, game_state)]

    def get_config(self) -> RoleConfig:
        """Get configuration for the Raven role."""
        return RoleConfig(
            name="Raven",
            camp=Camp.VILLAGER,
            description=(
                "You are the Raven. Each night, you can mark a player with a curse. "
                "During the next day's voting, that player will have one extra vote against them "
                "from the start. Use this to help eliminate werewolves!"
            ),
            priority=ActionPriority.RAVEN,
            can_act_night=True,
            can_act_day=False,
        )


class GraveyardKeeper(Role):
    """Graveyard Keeper role.

    Each night, can check if a dead player was a werewolf or villager.
    """

    def get_night_actions(self, game_state: "GameState") -> list["Action"]:
        """Get the night actions for the GraveyardKeeper role."""
        # TODO: Implement GraveyardKeeper logic
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Graveyard Keeper role."""
        return RoleConfig(
            name="Graveyard Keeper",
            camp=Camp.VILLAGER,
            description=(
                "You are the Graveyard Keeper. Each night, you can check the true identity "
                "of one dead player (werewolf or villager). This helps you piece together "
                "who the remaining werewolves might be."
            ),
            priority=ActionPriority.GRAVEYARD_KEEPER,
            can_act_night=True,
            can_act_day=False,
        )
