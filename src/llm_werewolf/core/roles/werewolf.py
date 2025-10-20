from llm_werewolf.core.types import Camp, RoleConfig, ActionPriority
from llm_werewolf.core.player import Player
from llm_werewolf.core.actions import (
    Action,
    WerewolfKillAction,
    WhiteWolfKillAction,
    WolfBeautyCharmAction,
)
from llm_werewolf.core.game_state import GameState
from llm_werewolf.core.roles.base import Role
from llm_werewolf.core.action_selector import ActionSelector


class Werewolf(Role):
    """Standard Werewolf role.

    Werewolves wake up at night and collectively choose a victim to kill.
    They win when werewolves equal or outnumber villagers.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Werewolf role."""
        return RoleConfig(
            name="Werewolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are a Werewolf. Each night, you wake up with other werewolves "
                "and collectively choose a villager to eliminate. Your goal is to "
                "outnumber the villagers."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Get the night actions for the Werewolf role."""
        # In a real game, werewolves would need to coordinate.
        # For now, we'll have one werewolf act.
        # Let's find the first alive werewolf to act.
        werewolves = game_state.get_players_by_camp(Camp.WEREWOLF)
        acting_werewolf = None
        for werewolf in werewolves:
            if werewolf.is_alive():
                acting_werewolf = werewolf
                break

        if not acting_werewolf:
            return []

        # Only the first werewolf in the list will propose a kill
        if self.player.player_id != acting_werewolf.player_id:
            return []

        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if not possible_targets:
            return []

        # Get target from AI agent
        if self.player.agent:
            # Build context for werewolves
            werewolf_names = [w.name for w in werewolves if w.is_alive()]
            context = f"You are working with these werewolves: {', '.join(werewolf_names)}. Choose a villager to eliminate tonight."

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Werewolf",
                action_description="Choose a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
            )

            if target:
                return [WerewolfKillAction(self.player, target, game_state)]

        return []


class AlphaWolf(Role):
    """Alpha Wolf (Wolf King) role.

    Similar to a standard werewolf, but when eliminated (by vote or hunter),
    can take another player down with them.
    """

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Alpha Wolf has no special night actions beyond the standard werewolf kill."""
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Alpha Wolf role."""
        return RoleConfig(
            name="Alpha Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Alpha Wolf. You wake up with other werewolves each night "
                "to kill a villager. When you are eliminated (by voting or hunter), "
                "you can immediately shoot and eliminate another player before you die."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=True,  # Can shoot when dying
        )


class WhiteWolf(Role):
    """White Wolf role.

    A werewolf who can kill another werewolf once every two nights.
    This makes the white wolf a lone wolf trying to be the last werewolf standing.
    """

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Get the night actions for the White Wolf role."""
        # Can only kill every other night (odd rounds)
        if game_state.round_number % 2 == 0:
            return []

        if not self.player.is_alive():
            return []

        # Get other werewolves as possible targets
        possible_targets = [
            p
            for p in game_state.get_players_by_camp("werewolf")
            if p.is_alive() and p.player_id != self.player.player_id
        ]

        if not possible_targets:
            return []

        # Get target from AI agent or skip
        if self.player.agent:
            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="White Wolf",
                action_description="Choose a werewolf to kill (or skip)",
                possible_targets=possible_targets,
                allow_skip=True,
                additional_context=(
                    f"It is round {game_state.round_number}. You can kill another werewolf tonight. "
                    "This is optional - you may skip if you prefer."
                ),
                fallback_random=False,  # White Wolf can skip
            )

            if target:
                return [WhiteWolfKillAction(self.player, target, game_state)]

        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the White Wolf role."""
        return RoleConfig(
            name="White Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the White Wolf. You wake up with other werewolves to kill villagers. "
                "Additionally, every other night, you wake up alone and can choose to kill "
                "another werewolf. Your ultimate goal may be to be the last werewolf standing."
            ),
            priority=ActionPriority.WHITE_WOLF,
            can_act_night=True,
            can_act_day=False,
        )


class WolfBeauty(Role):
    """Wolf Beauty role.

    A werewolf who charms a player each night. If the Wolf Beauty dies,
    the charmed player dies too.
    """

    def __init__(self, player: Player) -> None:
        """Initialize the Wolf Beauty role."""
        super().__init__(player)
        self.charmed_player: str | None = None

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Get the night actions for the Wolf Beauty role."""
        if not self.player.is_alive():
            return []

        # Can only charm if not already charmed someone
        if self.charmed_player:
            return []

        # Get possible targets (all alive players)
        possible_targets = game_state.get_alive_players()

        if not possible_targets:
            return []

        # Get target from AI agent
        if self.player.agent:
            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Wolf Beauty",
                action_description="Choose a player to charm",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=(
                    "If you die, the charmed player will die with you immediately. "
                    "Choose wisely - you can only charm one player for the entire game."
                ),
            )

            if target:
                return [WolfBeautyCharmAction(self.player, target, game_state)]

        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Wolf Beauty role."""
        return RoleConfig(
            name="Wolf Beauty",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Wolf Beauty. You wake up with other werewolves to kill villagers. "
                "Each night, you can also charm a player. If you die, the charmed player "
                "dies with you immediately."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )


class GuardianWolf(Role):
    """Guardian Wolf role.

    A werewolf who can protect one werewolf from elimination each night.
    """

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Get the night actions for the Guardian Wolf role."""
        # TODO: Implement Guardian Wolf logic
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Guardian Wolf role."""
        return RoleConfig(
            name="Guardian Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Guardian Wolf. You wake up with other werewolves to kill villagers. "
                "Additionally, you can choose to protect one werewolf each night. "
                "The protected werewolf cannot be eliminated that night."
            ),
            priority=ActionPriority.GUARD,
            can_act_night=True,
            can_act_day=False,
        )


class HiddenWolf(Role):
    """Hidden Wolf role.

    A werewolf who appears as a villager when checked by the Seer.
    """

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Hidden Wolf has no special night actions beyond the standard werewolf kill."""
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Hidden Wolf role."""
        return RoleConfig(
            name="Hidden Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Hidden Wolf. You wake up with other werewolves to kill villagers. "
                "Your special ability is that you appear as a villager when checked by the Seer. "
                "This makes you much harder to detect."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )


class BloodMoonApostle(Role):
    """Blood Moon Apostle role.

    A werewolf supporter who doesn't wake up with other wolves but wins with them.
    Once per game, can turn into a real werewolf.
    """

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Get the night actions for the Blood Moon Apostle role."""
        # TODO: Implement Blood Moon Apostle logic
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Blood Moon Apostle role."""
        return RoleConfig(
            name="Blood Moon Apostle",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Blood Moon Apostle. You support the werewolves but don't wake up "
                "with them initially. Once per game, if all werewolves are dead, you transform "
                "into a werewolf and can start killing. You appear as a villager to the Seer "
                "until transformed."
            ),
            priority=None,  # No night action until transformed
            can_act_night=False,
            can_act_day=False,
            max_uses=1,  # Can only transform once
        )


class NightmareWolf(Role):
    """Nightmare Wolf role.

    A werewolf who can block a player from using their ability for one night.
    """

    def get_night_actions(self, game_state: GameState) -> list["Action"]:
        """Get the night actions for the Nightmare Wolf role."""
        # TODO: Implement Nightmare Wolf logic
        return []

    def get_config(self) -> RoleConfig:
        """Get configuration for the Nightmare Wolf role."""
        return RoleConfig(
            name="Nightmare Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Nightmare Wolf. You wake up with other werewolves to kill villagers. "
                "Additionally, you can choose one player each night to block their ability. "
                "That player cannot use their role ability that night."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )
