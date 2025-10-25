from collections.abc import Callable

from llm_werewolf.core.types import EventType, ActionPriority
from llm_werewolf.core.locale import Locale
from llm_werewolf.core.game_state import GameState
from llm_werewolf.core.actions.base import Action
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


class ActionProcessorMixin:
    """Mixin for processing game actions."""

    game_state: GameState | None
    locale: Locale
    _log_event: Callable

    @staticmethod
    def _get_action_priority(action: Action) -> int:
        """Get action priority. Higher number = higher priority (executes first).

        Args:
            action: The action to get priority for.

        Returns:
            int: Priority value (higher executes first).
        """
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

    def _is_actor_blocked(self, action: Action) -> bool:
        """Check if actor is blocked by Nightmare Wolf.

        Args:
            action: The action to check.

        Returns:
            bool: True if actor is blocked, False otherwise.
        """
        if not self.game_state or not self.game_state.nightmare_blocked:
            return False

        if not hasattr(action, "actor"):
            return False

        if isinstance(action, NightmareWolfBlockAction):
            return False

        return action.actor.player_id == self.game_state.nightmare_blocked

    def _log_guard_action(self, action: GuardProtectAction) -> None:
        """Log guard protection action."""
        self._log_event(
            EventType.GUARD_PROTECTED,
            self.locale.get("guard_protected", target=action.target.name),
            data={"target_id": action.target.player_id},
        )
        if action.actor.agent and self.game_state:
            action.actor.agent.add_decision(
                f"Round {self.game_state.round_number}: Protected {action.target.name}"
            )

    def _log_witch_save_action(self, action: WitchSaveAction) -> None:
        """Log witch save action."""
        self._log_event(
            EventType.WITCH_SAVED,
            self.locale.get("witch_saved", target=action.target.name),
            data={"target_id": action.target.player_id},
        )
        if action.actor.agent and self.game_state:
            action.actor.agent.add_decision(
                f"Round {self.game_state.round_number}: Used save potion on {action.target.name}"
            )

    def _log_witch_poison_action(self, action: WitchPoisonAction) -> None:
        """Log witch poison action."""
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("witch_uses_poison", target=action.target.name),
            data={"target_id": action.target.player_id},
        )
        if action.actor.agent and self.game_state:
            action.actor.agent.add_decision(
                f"Round {self.game_state.round_number}: Used poison on {action.target.name}"
            )

    def _log_seer_action(self, action: SeerCheckAction) -> None:
        """Log seer check action."""
        result = action.target.get_camp()
        # HiddenWolf appears as villager to Seer
        if action.target.role.name == "HiddenWolf":
            result = "villager"
        # BloodMoonApostle (untransformed) appears as villager to Seer
        if action.target.role.name == "Blood Moon Apostle":
            if hasattr(action.target.role, "transformed") and not action.target.role.transformed:
                result = "villager"
        self._log_event(
            EventType.SEER_CHECKED,
            self.locale.get("seer_checked", target=action.target.name, result=result),
            data={"target_id": action.target.player_id, "result": result},
            visible_to=[action.actor.player_id],
        )
        if action.actor.agent and self.game_state:
            action.actor.agent.add_decision(
                f"Round {self.game_state.round_number}: Checked {action.target.name}, result: {result}"
            )

    def _log_cupid_action(self, action: CupidLinkAction) -> None:
        """Log cupid link action."""
        self._log_event(
            EventType.LOVERS_LINKED,
            self.locale.get(
                "cupid_links", player1=action.target1.name, player2=action.target2.name
            ),
            data={"player1_id": action.target1.player_id, "player2_id": action.target2.player_id},
        )
        if action.actor.agent and self.game_state:
            action.actor.agent.add_decision(
                f"Round {self.game_state.round_number}: Linked {action.target1.name} and {action.target2.name} as lovers"
            )

    def _log_white_wolf_action(self, action: WhiteWolfKillAction) -> None:
        """Log white wolf kill action."""
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("white_wolf_kills", target=action.target.name),
            data={"target_id": action.target.player_id},
        )

    def _log_wolf_beauty_action(self, action: WolfBeautyCharmAction) -> None:
        """Log wolf beauty charm action."""
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("wolf_beauty_charms", target=action.target.name),
            data={"target_id": action.target.player_id},
        )

    def _log_action_event(self, action: Action) -> None:
        """Log event for specific action types.

        Args:
            action: The action to log.
        """
        if isinstance(action, GuardProtectAction):
            self._log_guard_action(action)
        elif isinstance(action, WitchSaveAction):
            self._log_witch_save_action(action)
        elif isinstance(action, WitchPoisonAction):
            self._log_witch_poison_action(action)
        elif isinstance(action, SeerCheckAction):
            self._log_seer_action(action)
        elif isinstance(action, CupidLinkAction):
            self._log_cupid_action(action)
        elif isinstance(action, WhiteWolfKillAction):
            self._log_white_wolf_action(action)
        elif isinstance(action, WolfBeautyCharmAction):
            self._log_wolf_beauty_action(action)

    def process_actions(self, actions: list) -> list[str]:
        """Process a list of actions.

        Args:
            actions: List of Action objects to process.

        Returns:
            list[str]: Messages from processing actions.
        """
        messages = []

        # Sort by priority: higher priority value = executes first
        sorted_actions = sorted(actions, key=self._get_action_priority, reverse=True)

        for action in sorted_actions:
            # Check if actor is blocked by Nightmare Wolf
            if self._is_actor_blocked(action):
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
                self._log_action_event(action)
                messages.extend(result_messages)

        return messages
