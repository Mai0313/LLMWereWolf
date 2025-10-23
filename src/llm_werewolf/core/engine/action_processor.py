"""Action processing logic for the game engine."""

from typing import TYPE_CHECKING

from llm_werewolf.core.types import EventType

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.core.locale import Locale
    from llm_werewolf.core.actions import Action
    from llm_werewolf.core.game_state import GameState


class ActionProcessorMixin:
    """Mixin for processing game actions."""

    game_state: "GameState | None"
    locale: "Locale"
    _log_event: "Callable"

    @staticmethod
    def _get_action_priority(action: "Action") -> int:
        """Get action priority. Higher number = higher priority (executes first).

        Args:
            action: The action to get priority for.

        Returns:
            int: Priority value (higher executes first).
        """
        from llm_werewolf.core.types import ActionPriority

        # Priority map ordered from highest to lowest priority
        priority_map = {
            "CupidLinkAction": ActionPriority.CUPID.value,
            "NightmareWolfBlockAction": ActionPriority.NIGHTMARE_WOLF.value,
            "GuardProtectAction": ActionPriority.GUARD.value,
            "GuardianWolfProtectAction": ActionPriority.GUARD.value,
            "WerewolfVoteAction": ActionPriority.WEREWOLF.value,
            "WerewolfKillAction": ActionPriority.WEREWOLF.value,
            "WolfBeautyCharmAction": ActionPriority.WEREWOLF.value,
            "WhiteWolfKillAction": ActionPriority.WHITE_WOLF.value,
            "WitchSaveAction": ActionPriority.WITCH.value,
            "WitchPoisonAction": ActionPriority.WITCH.value,
            "SeerCheckAction": ActionPriority.SEER.value,
            "GraveyardKeeperCheckAction": ActionPriority.GRAVEYARD_KEEPER.value,
            "RavenMarkAction": ActionPriority.RAVEN.value,
        }
        return priority_map.get(action.__class__.__name__, 0)

    def process_actions(self, actions: list) -> list[str]:
        """Process a list of actions.

        Args:
            actions: List of Action objects to process.

        Returns:
            list[str]: Messages from processing actions.
        """
        from llm_werewolf.core.actions.villager import (
            CupidLinkAction,
            SeerCheckAction,
            WitchSaveAction,
            WitchPoisonAction,
            GuardProtectAction,
        )
        from llm_werewolf.core.actions.werewolf import (
            WhiteWolfKillAction,
            WolfBeautyCharmAction,
            NightmareWolfBlockAction,
        )

        messages = []

        # Sort by priority: higher priority value = executes first
        sorted_actions = sorted(actions, key=self._get_action_priority, reverse=True)

        for action in sorted_actions:
            # Check if actor is blocked by Nightmare Wolf
            if (
                self.game_state
                and self.game_state.nightmare_blocked
                and hasattr(action, "actor")
                and action.actor.player_id == self.game_state.nightmare_blocked
                and not isinstance(action, NightmareWolfBlockAction)
            ):
                self._log_event(
                    EventType.MESSAGE,
                    self.locale.get(
                        "nightmare_blocked",
                        player=action.actor.name,
                        role=action.actor.get_role_name(),
                    ),
                    data={
                        "player_id": action.actor.player_id,
                        "role": action.actor.get_role_name(),
                    },
                )
                continue

            if action.validate():
                result_messages = action.execute()

                # Log detailed events for different action types
                if isinstance(action, GuardProtectAction):
                    self._log_event(
                        EventType.GUARD_PROTECTED,
                        self.locale.get("guard_protected", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )
                    # Record decision
                    if action.actor.agent and self.game_state:
                        action.actor.agent.add_decision(
                            f"Round {self.game_state.round_number}: Protected {action.target.name}"
                        )
                elif isinstance(action, WitchSaveAction):
                    self._log_event(
                        EventType.WITCH_SAVED,
                        self.locale.get("witch_saved", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )
                    # Record decision (without revealing who attacked)
                    if action.actor.agent and self.game_state:
                        action.actor.agent.add_decision(
                            f"Round {self.game_state.round_number}: Used save potion on {action.target.name}"
                        )
                elif isinstance(action, WitchPoisonAction):
                    self._log_event(
                        EventType.MESSAGE,
                        self.locale.get("witch_uses_poison", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )
                    # Note: Actual death is handled in resolve_deaths()
                    # Record decision
                    if action.actor.agent and self.game_state:
                        action.actor.agent.add_decision(
                            f"Round {self.game_state.round_number}: Used poison on {action.target.name}"
                        )
                elif isinstance(action, SeerCheckAction):
                    result = action.target.get_camp()
                    # HiddenWolf appears as villager to Seer
                    if action.target.role.name == "HiddenWolf":
                        result = "villager"
                    self._log_event(
                        EventType.SEER_CHECKED,
                        self.locale.get("seer_checked", target=action.target.name, result=result),
                        data={"target_id": action.target.player_id, "result": result},
                        visible_to=[action.actor.player_id],  # Only seer sees this
                    )
                    # Record decision (safe summary without werewolf team info)
                    if action.actor.agent and self.game_state:
                        action.actor.agent.add_decision(
                            f"Round {self.game_state.round_number}: Checked {action.target.name}, result: {result}"
                        )
                elif isinstance(action, CupidLinkAction):
                    self._log_event(
                        EventType.LOVERS_LINKED,
                        self.locale.get(
                            "cupid_links", player1=action.target1.name, player2=action.target2.name
                        ),
                        data={
                            "player1_id": action.target1.player_id,
                            "player2_id": action.target2.player_id,
                        },
                    )
                    # Record decision
                    if action.actor.agent and self.game_state:
                        action.actor.agent.add_decision(
                            f"Round {self.game_state.round_number}: Linked {action.target1.name} and {action.target2.name} as lovers"
                        )
                elif isinstance(action, WhiteWolfKillAction):
                    self._log_event(
                        EventType.MESSAGE,
                        self.locale.get("white_wolf_kills", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )
                elif isinstance(action, WolfBeautyCharmAction):
                    self._log_event(
                        EventType.MESSAGE,
                        self.locale.get("wolf_beauty_charms", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )

                messages.extend(result_messages)

        return messages
