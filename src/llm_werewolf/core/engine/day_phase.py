"""Day phase logic for the game engine."""

from typing import TYPE_CHECKING

from llm_werewolf.core.types import EventType, GamePhase
from llm_werewolf.core.player import Player

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.core.locale import Locale
    from llm_werewolf.core.game_state import GameState


class DayPhaseMixin:
    """Mixin for handling day phase logic."""

    game_state: "GameState | None"
    locale: "Locale"
    _log_event: "Callable"

    def _build_discussion_context(self, player: Player) -> str:
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
            f"It is Day {self.game_state.round_number}, discussion phase.",
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
                    speech = "".join(player.agent.get_response(game_context))

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
                except Exception as e:
                    messages.append(f"{player.name}: [Unable to speak - {e}]")

        return messages
