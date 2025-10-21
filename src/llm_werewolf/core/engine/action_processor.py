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
        from llm_werewolf.core.actions.werewolf import WhiteWolfKillAction, WolfBeautyCharmAction

        messages = []

        def get_action_priority(action: "Action") -> int:
            priority_map = {
                "GuardProtectAction": 0,
                "WerewolfVoteAction": 1,
                "WerewolfKillAction": 1,
                "WitchSaveAction": 2,
                "WitchPoisonAction": 3,
                "SeerCheckAction": 4,
            }
            return priority_map.get(action.__class__.__name__, 100)

        sorted_actions = sorted(actions, key=get_action_priority)

        for action in sorted_actions:
            if action.validate():
                result_messages = action.execute()

                # Log detailed events for different action types
                if isinstance(action, GuardProtectAction):
                    self._log_event(
                        EventType.GUARD_PROTECTED,
                        self.locale.get("guard_protected", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )
                elif isinstance(action, WitchSaveAction):
                    self._log_event(
                        EventType.WITCH_SAVED,
                        self.locale.get("witch_saved", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )
                elif isinstance(action, WitchPoisonAction):
                    self._log_event(
                        EventType.WITCH_POISONED,
                        self.locale.get("witch_poisoned", target=action.target.name),
                        data={"target_id": action.target.player_id},
                    )
                    # Mark poisoned target for death
                    if action.target.is_alive() and self.game_state:
                        action.target.kill()
                        self.game_state.night_deaths.add(action.target.player_id)
                        self.game_state.death_causes[action.target.player_id] = "witch_poison"
                elif isinstance(action, SeerCheckAction):
                    from llm_werewolf.core.roles.werewolf import HiddenWolf

                    result = action.target.get_camp()
                    if isinstance(action.target.role, HiddenWolf):
                        result = "villager"
                    self._log_event(
                        EventType.SEER_CHECKED,
                        self.locale.get("seer_checked", target=action.target.name, result=result),
                        data={"target_id": action.target.player_id, "result": result},
                        visible_to=[action.actor.player_id],  # Only seer sees this
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
