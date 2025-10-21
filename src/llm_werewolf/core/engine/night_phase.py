"""Night phase logic for the game engine."""

import random
from typing import TYPE_CHECKING

from llm_werewolf.core.types import EventType, GamePhase

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.core.locale import Locale
    from llm_werewolf.core.actions import Action
    from llm_werewolf.core.game_state import GameState


class NightPhaseMixin:
    """Mixin for handling night phase logic."""

    game_state: "GameState | None"
    locale: "Locale"
    _log_event: "Callable"
    process_actions: "Callable"
    resolve_deaths: "Callable"

    def _resolve_werewolf_votes(self) -> list[str]:
        """Resolve werewolf voting to determine kill target.

        Returns:
            list[str]: Messages describing the voting result.
        """
        if not self.game_state:
            return []

        messages: list[str] = []

        if not self.game_state.werewolf_votes:
            return messages

        vote_counts: dict[str, int] = {}
        for target_id in self.game_state.werewolf_votes.values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1

        max_votes = max(vote_counts.values())
        candidates = [pid for pid, count in vote_counts.items() if count == max_votes]

        if candidates:
            selected_target_id = random.choice(candidates)  # noqa: S311
            self.game_state.werewolf_target = selected_target_id

            target = self.game_state.get_player(selected_target_id)
            if target:
                self._log_event(
                    EventType.WEREWOLF_KILLED,
                    self.locale.get("werewolf_target", target=target.name),
                    data={"target_id": selected_target_id, "target_name": target.name},
                )

        return messages

    def run_night_phase(self) -> list[str]:
        """Execute the night phase where roles perform actions.

        Returns:
            list[str]: Messages describing night actions.
        """
        if not self.game_state:
            msg = "Game not initialized"
            raise RuntimeError(msg)

        messages = []
        self.game_state.set_phase(GamePhase.NIGHT)

        self._log_event(
            EventType.PHASE_CHANGED,
            self.locale.get("night_begins", round_number=self.game_state.round_number),
            data={"phase": "night", "round": self.game_state.round_number},
        )

        messages.append("")

        players_with_night_actions = self.game_state.get_players_with_night_actions()

        night_actions: list[Action] = []
        for player in players_with_night_actions:
            # Log that this role is acting
            role_name = player.get_role_name()
            self._log_event(
                EventType.ROLE_ACTING,
                self.locale.get("role_acting", role=role_name, player=player.name),
                data={"player_id": player.player_id, "role": role_name},
            )

            action = player.role.get_night_actions(self.game_state)
            if action:
                night_actions.extend(action)

        action_messages = self.process_actions(night_actions)
        messages.extend(action_messages)

        werewolf_vote_messages = self._resolve_werewolf_votes()
        messages.extend(werewolf_vote_messages)

        death_messages = self.resolve_deaths()
        messages.extend(death_messages)

        return messages
