"""Day phase logic for the game engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llm_werewolf.core.types import EventType, GamePhase, PlayerProtocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.core.locale import Locale
    from llm_werewolf.core.game_state import GameState


class DayPhaseMixin:
    """Mixin for handling day phase logic."""

    game_state: GameState | None
    locale: Locale
    _log_event: Callable
    public_discussion_history: list[str]
    _get_public_discussion_context: Callable[[], str]

    def _build_discussion_context(self, player: PlayerProtocol) -> str:
        """Build context for day discussion.

        Args:
            player: The player who will speak.

        Returns:
            str: Context message for the player's agent.
        """
        if not self.game_state:
            return ""

        context_parts = [
            f"You are {player.name}, a {player.get_role_name()}.",
            f"Current: Round {self.game_state.round_number} - Day Discussion Phase",
            "",
        ]

        if self.game_state.night_deaths:
            deaths = [
                self.game_state.get_player(pid).name
                for pid in self.game_state.night_deaths
                if self.game_state.get_player(pid)
            ]
            context_parts.append(f"Last night, {', '.join(deaths)} died.")
        else:
            context_parts.append("No one died last night.")

        alive_players = [p.name for p in self.game_state.get_alive_players()]
        context_parts.append(f"\nAlive players: {', '.join(alive_players)}")

        # Include player's decision history (safe, no sensitive info)
        if player.agent:
            decision_context = player.agent.get_decision_context()
            if decision_context:
                context_parts.append(decision_context)

        # Include previous discussion history
        discussion_history = self._get_public_discussion_context()
        if discussion_history:
            context_parts.append(discussion_history)

        context_parts.append("")
        context_parts.append(
            "Share your thoughts, suspicions, or information. "
            "Your goal is to help your team win while staying in character."
        )
        context_parts.append(
            "\nProvide a brief statement (1-3 sentences) for this discussion round."
        )

        return "\n".join(context_parts)

    def run_day_phase(self) -> list[str]:
        """Execute the day discussion phase.

        Returns:
            list[str]: Messages from the day phase.
        """
        if not self.game_state:
            msg = "Game not initialized"
            raise RuntimeError(msg)

        messages = []
        self.game_state.set_phase(GamePhase.DAY_DISCUSSION)

        # Narrator: Daybreak
        self._log_event(
            EventType.MESSAGE, self.locale.get("narrator_daybreak"), data={"action": "daybreak"}
        )

        self._log_event(
            EventType.PHASE_CHANGED,
            self.locale.get("day_begins", round_number=self.game_state.round_number),
            data={"phase": "day", "round": self.game_state.round_number},
        )

        messages.append("")

        if self.game_state.night_deaths:
            for player_id in self.game_state.night_deaths:
                player = self.game_state.get_player(player_id)
                if player:
                    messages.append(f"{player.name} was killed last night.")
        else:
            messages.append("No one died last night.")

        messages.append("\n--- Discussion Phase ---")
        alive_players = self.game_state.get_alive_players()

        for player in alive_players:
            if player.agent:
                game_context = self._build_discussion_context(player)

                try:
                    speech = player.agent.get_response(game_context)

                    self._log_event(
                        EventType.PLAYER_SPEECH,
                        f"{player.name}: {speech}",
                        data={
                            "player_id": player.player_id,
                            "player_name": player.name,
                            "speech": speech,
                        },
                    )

                    messages.append(f"{player.name}: {speech}")

                    # Add to global public discussion history
                    self.public_discussion_history.append(f"{player.name}: {speech}")

                    # Record player's own speech in decision history
                    player.agent.add_decision(
                        f"Round {self.game_state.round_number} (Day discussion): You said: {speech}"
                    )
                except Exception as e:
                    self._log_event(
                        EventType.ERROR,
                        f"{player.name}: [發言失敗 - {e}]",
                        data={"player_id": player.player_id, "error": str(e)},
                    )
                    messages.append(f"{player.name}: [Unable to speak - {e}]")

        return messages
