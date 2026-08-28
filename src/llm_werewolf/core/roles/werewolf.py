from llm_werewolf.core.types import (
    Camp,
    RoleConfig,
    ActionPriority,
    ActionProtocol,
    PlayerProtocol,
    GameStateProtocol,
)
from llm_werewolf.core.actions import (
    WerewolfVoteAction,
    WhiteWolfKillAction,
    WolfBeautyCharmAction,
    NightmareWolfBlockAction,
    GuardianWolfProtectAction,
)
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

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the Werewolf role.

        All werewolves vote on a target, and the majority vote determines the kill.
        """
        if not self.player.is_alive():
            return []

        # Get all alive werewolves
        werewolves = [w for w in game_state.get_players_by_camp(Camp.WEREWOLF) if w.is_alive()]

        if not werewolves:
            return []

        # Get possible targets (non-werewolf players)
        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if not possible_targets:
            return []

        # Get target from AI agent (each werewolf votes)
        if self.player.agent:
            # Build context for werewolves
            werewolf_names = [w.name for w in werewolves]
            context = (
                f"You are working with these werewolves: {', '.join(werewolf_names)}.\n"
                f"All werewolves will vote on who to eliminate tonight.\n"
                f"Choose a villager to vote for."
            )

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Werewolf",
                action_description="Vote for a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                return [WerewolfVoteAction(self.player, target, game_state)]

        return []


class AlphaWolf(Role):
    """Alpha Wolf (Wolf King) role.

    Similar to a standard werewolf, but when eliminated (by vote or hunter),
    can take another player down with them.
    """

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the Alpha Wolf role.

        Alpha Wolf participates in the standard werewolf vote.
        """
        if not self.player.is_alive():
            return []

        # Get possible targets (non-werewolf players)
        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if not possible_targets:
            return []

        # Get target from AI agent (participate in werewolf vote)
        if self.player.agent:
            # Build context for werewolves
            werewolves = [w for w in game_state.get_players_by_camp(Camp.WEREWOLF) if w.is_alive()]
            werewolf_names = [w.name for w in werewolves]
            context = (
                f"You are working with these werewolves: {', '.join(werewolf_names)}.\n"
                f"All werewolves will vote on who to eliminate tonight.\n"
                f"Choose a villager to vote for."
            )

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Alpha Wolf",
                action_description="Vote for a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                return [WerewolfVoteAction(self.player, target, game_state)]

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

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the White Wolf role.

        White Wolf participates in the standard werewolf vote every night,
        and can kill another werewolf on even rounds.
        """
        if not self.player.is_alive():
            return []

        actions: list[ActionProtocol] = []

        # 1. Participate in standard werewolf vote (every night)
        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if possible_targets and self.player.agent:
            # Build context for werewolves
            werewolves = [w for w in game_state.get_players_by_camp(Camp.WEREWOLF) if w.is_alive()]
            werewolf_names = [w.name for w in werewolves]
            context = (
                f"You are working with these werewolves: {', '.join(werewolf_names)}.\n"
                f"All werewolves will vote on who to eliminate tonight.\n"
                f"Choose a villager to vote for."
            )

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="White Wolf",
                action_description="Vote for a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                actions.append(WerewolfVoteAction(self.player, target, game_state))

        # 2. Special ability: Kill another werewolf on odd rounds (1, 3, 5...)
        if game_state.round_number % 2 == 1:
            werewolf_targets = [
                p
                for p in game_state.get_players_by_camp("werewolf")
                if p.is_alive() and p.player_id != self.player.player_id
            ]

            if werewolf_targets and self.player.agent:
                target = ActionSelector.get_target_from_agent(
                    agent=self.player.agent,
                    role_name="White Wolf",
                    action_description="Choose a werewolf to kill (or skip)",
                    possible_targets=werewolf_targets,
                    allow_skip=True,
                    additional_context=(
                        "You can kill another werewolf tonight. "
                        "This is optional - you may skip if you prefer."
                    ),
                    fallback_random=False,  # White Wolf can skip
                    round_number=game_state.round_number,
                    phase="Night",
                )

                if target:
                    actions.append(WhiteWolfKillAction(self.player, target, game_state))

        return actions

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

    def __init__(self, player: PlayerProtocol) -> None:
        """Initialize the Wolf Beauty role."""
        super().__init__(player)
        self.charmed_player: str | None = None

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the Wolf Beauty role.

        Wolf Beauty participates in the standard werewolf vote every night,
        and can charm one player (once per game).
        """
        if not self.player.is_alive():
            return []

        actions: list[ActionProtocol] = []

        # 1. Participate in standard werewolf vote (every night)
        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if possible_targets and self.player.agent:
            # Build context for werewolves
            werewolves = [w for w in game_state.get_players_by_camp(Camp.WEREWOLF) if w.is_alive()]
            werewolf_names = [w.name for w in werewolves]
            context = (
                f"You are working with these werewolves: {', '.join(werewolf_names)}.\n"
                f"All werewolves will vote on who to eliminate tonight.\n"
                f"Choose a villager to vote for."
            )

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Wolf Beauty",
                action_description="Vote for a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                actions.append(WerewolfVoteAction(self.player, target, game_state))

        # 2. Special ability: Charm a player (once per game)
        if not self.charmed_player:
            charm_targets = game_state.get_alive_players()

            if charm_targets and self.player.agent:
                target = ActionSelector.get_target_from_agent(
                    agent=self.player.agent,
                    role_name="Wolf Beauty",
                    action_description="Choose a player to charm",
                    possible_targets=charm_targets,
                    allow_skip=False,
                    additional_context=(
                        "If you die, the charmed player will die with you immediately. "
                        "Choose wisely - you can only charm one player for the entire game."
                    ),
                    round_number=game_state.round_number,
                    phase="Night",
                )

                if target:
                    actions.append(WolfBeautyCharmAction(self.player, target, game_state))

        return actions

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

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the Guardian Wolf role.

        Guardian Wolf participates in the standard werewolf vote every night,
        and can protect one werewolf from elimination.
        """
        if not self.player.is_alive():
            return []

        actions: list[ActionProtocol] = []

        # 1. Participate in standard werewolf vote (every night)
        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if possible_targets and self.player.agent:
            # Build context for werewolves
            werewolves = [w for w in game_state.get_players_by_camp(Camp.WEREWOLF) if w.is_alive()]
            werewolf_names = [w.name for w in werewolves]
            context = (
                f"You are working with these werewolves: {', '.join(werewolf_names)}.\n"
                f"All werewolves will vote on who to eliminate tonight.\n"
                f"Choose a villager to vote for."
            )

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Guardian Wolf",
                action_description="Vote for a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                actions.append(WerewolfVoteAction(self.player, target, game_state))

        # 2. Special ability: Protect a werewolf
        werewolf_targets = [p for p in game_state.get_players_by_camp("werewolf") if p.is_alive()]

        if werewolf_targets and self.player.agent:
            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Guardian Wolf",
                action_description="Choose a werewolf to protect tonight",
                possible_targets=werewolf_targets,
                allow_skip=True,
                additional_context=(
                    "You can protect one werewolf from elimination tonight. "
                    "This protection works against White Wolf kills and other threats."
                ),
                fallback_random=False,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                actions.append(GuardianWolfProtectAction(self.player, target, game_state))

        return actions

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

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the Hidden Wolf role.

        Hidden Wolf participates in the standard werewolf vote.
        Special ability: Appears as villager when checked by Seer (handled elsewhere).
        """
        if not self.player.is_alive():
            return []

        # Get possible targets (non-werewolf players)
        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if not possible_targets:
            return []

        # Get target from AI agent (participate in werewolf vote)
        if self.player.agent:
            # Build context for werewolves
            werewolves = [w for w in game_state.get_players_by_camp(Camp.WEREWOLF) if w.is_alive()]
            werewolf_names = [w.name for w in werewolves]
            context = (
                f"You are working with these werewolves: {', '.join(werewolf_names)}.\n"
                f"All werewolves will vote on who to eliminate tonight.\n"
                f"Choose a villager to vote for."
            )

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Hidden Wolf",
                action_description="Vote for a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                return [WerewolfVoteAction(self.player, target, game_state)]

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

    def __init__(self, player: PlayerProtocol) -> None:
        """Initialize the Blood Moon Apostle role."""
        super().__init__(player)
        self.transformed = False

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the Blood Moon Apostle role."""
        # Only act if transformed into a werewolf
        if not self.transformed:
            # Check if all regular werewolves are dead
            werewolves = [
                p
                for p in game_state.get_players_by_camp("werewolf")
                if p.is_alive()
                and p.player_id != self.player.player_id
                and not isinstance(p.role, BloodMoonApostle)
            ]

            if not werewolves and self.player.is_alive():
                # Transform into werewolf
                self.transformed = True
                return []

        # After transformation, can vote like normal werewolf
        if self.transformed and self.player.is_alive():
            possible_targets = [
                p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
            ]
            if not possible_targets:
                return []

            if self.player.agent:
                target = ActionSelector.get_target_from_agent(
                    agent=self.player.agent,
                    role_name="Blood Moon Apostle",
                    action_description="Vote for a player to kill tonight",
                    possible_targets=possible_targets,
                    allow_skip=False,
                    additional_context=(
                        "You have transformed into a werewolf! Vote for who to eliminate tonight."
                    ),
                    round_number=game_state.round_number,
                    phase="Night",
                )

                if target:
                    return [WerewolfVoteAction(self.player, target, game_state)]

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
            priority=ActionPriority.WEREWOLF,  # Acts with werewolves after transformation
            can_act_night=True,  # Needs to check transformation condition every night
            can_act_day=False,
            max_uses=None,  # Can act every night after transformation
        )


class NightmareWolf(Role):
    """Nightmare Wolf role.

    A werewolf who can block a player from using their ability for one night.
    """

    def get_night_actions(self, game_state: GameStateProtocol) -> list[ActionProtocol]:
        """Get the night actions for the Nightmare Wolf role.

        Nightmare Wolf participates in the standard werewolf vote every night,
        and can block one player's ability.
        """
        if not self.player.is_alive():
            return []

        actions: list[ActionProtocol] = []

        # 1. Participate in standard werewolf vote (every night)
        possible_targets = [
            p for p in game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]
        if possible_targets and self.player.agent:
            # Build context for werewolves
            werewolves = [w for w in game_state.get_players_by_camp(Camp.WEREWOLF) if w.is_alive()]
            werewolf_names = [w.name for w in werewolves]
            context = (
                f"You are working with these werewolves: {', '.join(werewolf_names)}.\n"
                f"All werewolves will vote on who to eliminate tonight.\n"
                f"Choose a villager to vote for."
            )

            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Nightmare Wolf",
                action_description="Vote for a player to kill tonight",
                possible_targets=possible_targets,
                allow_skip=False,
                additional_context=context,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                actions.append(WerewolfVoteAction(self.player, target, game_state))

        # 2. Special ability: Block a player's ability
        block_targets = game_state.get_alive_players(except_ids=[self.player.player_id])

        if block_targets and self.player.agent:
            target = ActionSelector.get_target_from_agent(
                agent=self.player.agent,
                role_name="Nightmare Wolf",
                action_description="Choose a player to block tonight",
                possible_targets=block_targets,
                allow_skip=True,
                additional_context=(
                    "You can block one player's ability tonight. "
                    "They will not be able to use their role ability this night."
                ),
                fallback_random=False,
                round_number=game_state.round_number,
                phase="Night",
            )

            if target:
                actions.append(NightmareWolfBlockAction(self.player, target, game_state))

        return actions

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
