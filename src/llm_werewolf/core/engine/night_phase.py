"""Night phase logic for the game engine."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from llm_werewolf.core.types import Camp, EventType, GamePhase

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.core.locale import Locale
    from llm_werewolf.core.game_state import GameState
    from llm_werewolf.core.actions.base import Action


class NightPhaseMixin:
    """Mixin for handling night phase logic."""

    game_state: GameState | None
    locale: Locale
    _log_event: Callable
    process_actions: Callable
    resolve_deaths: Callable
    werewolf_discussion_history: list[str]
    _get_werewolf_discussion_context: Callable[[], str]

    def _run_werewolf_discussion(self) -> list[str]:
        """Run werewolf discussion phase where werewolves discuss their target.

        Returns:
            list[str]: Messages from the discussion.
        """
        if not self.game_state:
            return []

        messages: list[str] = []
        werewolves = [
            p for p in self.game_state.get_players_by_camp(Camp.WEREWOLF) if p.is_alive()
        ]

        if len(werewolves) <= 1:
            # If only one werewolf, skip discussion
            return messages

        # Narrator: Werewolves wake up
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("narrator_werewolves_wake"),
            data={"action": "werewolves_wake"},
        )

        # Get possible targets
        possible_targets = [
            p for p in self.game_state.get_alive_players() if p.get_camp() != Camp.WEREWOLF
        ]

        if not possible_targets:
            return messages

        target_names = [p.name for p in possible_targets]
        werewolf_names = [w.name for w in werewolves]

        # Each werewolf discusses
        for werewolf in werewolves:
            if werewolf.agent:
                # Log preparing
                self._log_event(
                    EventType.MESSAGE,
                    f"💬 {werewolf.name}（狼人）正在思考...",
                    data={
                        "player_id": werewolf.player_id,
                        "player_name": werewolf.name,
                        "action": "preparing_speech",
                    },
                )

                # Build discussion context with werewolf history
                context_parts = [
                    f"You are {werewolf.name}, a Werewolf.",
                    f"Current: Round {self.game_state.round_number} - Night Phase",
                    f"You are working with these werewolves: {', '.join(werewolf_names)}.",
                    f"Available targets: {', '.join(target_names)}.",
                ]

                # Include werewolf discussion history
                werewolf_history = self._get_werewolf_discussion_context()
                if werewolf_history:
                    context_parts.append(werewolf_history)

                context_parts.extend([
                    "",
                    "Discuss with your fellow werewolves who should be eliminated tonight.",
                    "Share your thoughts and suggestions (1-2 sentences).",
                ])

                context = "\n".join(context_parts)

                try:
                    speech = werewolf.agent.get_response(context)

                    self._log_event(
                        EventType.PLAYER_DISCUSSION,
                        self.locale.get(
                            "werewolf_discussion", player=werewolf.name, speech=speech
                        ),
                        data={
                            "player_id": werewolf.player_id,
                            "player_name": werewolf.name,
                            "speech": speech,
                            "role": "Werewolf",
                        },
                    )

                    messages.append(f"🐺 {werewolf.name}: {speech}")

                    # Add to global werewolf discussion history
                    self.werewolf_discussion_history.append(f"{werewolf.name}: {speech}")

                    # Record werewolf's own speech in decision history
                    # This is safe: only records what they said, not sensitive context
                    werewolf.agent.add_decision(
                        f"Round {self.game_state.round_number} (Werewolf discussion): You said: {speech}"
                    )
                except Exception as e:
                    self._log_event(
                        EventType.ERROR,
                        f"{werewolf.name}: [討論失敗 - {e}]",
                        data={"player_id": werewolf.player_id, "error": str(e)},
                    )

        # Narrator: Time to vote
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("narrator_werewolves_vote"),
            data={"action": "werewolves_vote"},
        )

        return messages

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

        # Narrator: Night falls
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("narrator_night_falls"),
            data={"action": "night_falls"},
        )

        self._log_event(
            EventType.PHASE_CHANGED,
            self.locale.get("night_begins", round_number=self.game_state.round_number),
            data={"phase": "night", "round": self.game_state.round_number},
        )

        messages.append("")

        # Run werewolf discussion phase (if multiple werewolves exist)
        discussion_messages = self._run_werewolf_discussion()
        messages.extend(discussion_messages)

        # Get players with night actions (non-werewolf roles)
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

        # Narrator: Werewolves sleep (end of night)
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("narrator_werewolves_sleep"),
            data={"action": "werewolves_sleep"},
        )

        return messages
