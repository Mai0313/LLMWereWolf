"""Sheriff election phase logic for the game engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llm_werewolf.core.types import EventType, PlayerProtocol
from llm_werewolf.core.action_selector import ActionSelector

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.core.locale import Locale
    from llm_werewolf.core.game_state import GameState


class SheriffElectionMixin:
    """Mixin for handling sheriff election phase logic."""

    game_state: GameState | None
    locale: Locale
    _log_event: Callable

    def execute_sheriff_election(self) -> None:
        """Execute the sheriff election phase.

        This includes:
        1. Campaign phase: Players volunteer to run for sheriff
        2. Speech phase: Candidates give campaign speeches
        3. Voting phase: All players vote for sheriff
        4. Result announcement: Winner becomes sheriff
        """
        if not self.game_state:
            return

        self._log_event(
            EventType.SHERIFF_CAMPAIGN_STARTED, self.locale.get("sheriff_campaign_started")
        )

        # Phase 1: Collect candidates
        candidates = self._collect_sheriff_candidates()

        if not candidates:
            self._log_event(EventType.MESSAGE, self.locale.get("no_candidates"))
            self.game_state.sheriff_election_done = True
            return

        if len(candidates) == 1:
            # Only one candidate, auto-elect
            self._elect_sheriff(candidates[0])
            self.game_state.sheriff_election_done = True
            return

        # Phase 2: Campaign speeches
        self._conduct_campaign_speeches(candidates)

        # Phase 3: Voting
        vote_counts = self._conduct_sheriff_voting(candidates)

        # Phase 4: Determine winner
        self._determine_sheriff_winner(vote_counts, candidates)

        self.game_state.sheriff_election_done = True

    def _collect_sheriff_candidates(self) -> list[PlayerProtocol]:
        """Ask all alive players if they want to run for sheriff.

        Returns:
            list[PlayerProtocol]: List of players who want to run for sheriff.
        """
        if not self.game_state:
            return []

        candidates: list[PlayerProtocol] = []
        alive_players = self.game_state.get_alive_players()

        for player in alive_players:
            if not player.agent:
                continue

            context = self._build_campaign_context(player)
            decision = ActionSelector.ask_yes_no(
                player.agent, context, "Do you want to campaign for sheriff? (yes/no)"
            )

            if decision:
                candidates.append(player)
                self._log_event(
                    EventType.MESSAGE, self.locale.get("player_volunteers", player=player.name)
                )

        return candidates

    def _build_campaign_context(self, player: PlayerProtocol) -> str:
        """Build context for sheriff campaign decision.

        Args:
            player: The player deciding whether to campaign.

        Returns:
            str: Context message for the player's agent.
        """
        if not self.game_state:
            return ""

        context_parts = [
            f"You are {player.name}, a {player.get_role_name()}.",
            f"Current: Round {self.game_state.round_number} - Sheriff Election",
            "",
            "SHERIFF ELECTION:",
            "The sheriff election is now open. As sheriff, you will have:",
            "- 1.5x voting power during day voting phases",
            "- The ability to transfer the sheriff badge to another player when you die",
            "- Additional speaking authority and influence",
            "",
            "However, becoming sheriff also:",
            "- May draw attention to you (good or bad depending on your role)",
            "- May make you a target for werewolves if you're a villager",
            "- May help you mislead the village if you're a werewolf",
            "",
            "Consider your role and strategy before deciding.",
        ]

        return "\n".join(context_parts)

    def _conduct_campaign_speeches(self, candidates: list[PlayerProtocol]) -> None:
        """Have each candidate give a campaign speech.

        Args:
            candidates: List of sheriff candidates.
        """
        if not self.game_state:
            return

        self._log_event(
            EventType.MESSAGE, self.locale.get("campaign_speeches_start", count=len(candidates))
        )

        for candidate in candidates:
            if not candidate.agent:
                continue

            context = self._build_speech_context(candidate, candidates)
            speech = ActionSelector.get_free_response(
                candidate.agent,
                context,
                "Give your campaign speech (explain why you should be sheriff):",
            )

            self._log_event(
                EventType.SHERIFF_CANDIDATE_SPEECH,
                self.locale.get("candidate_speech", candidate=candidate.name, speech=speech),
                data={"player_id": candidate.player_id, "speech": speech},
            )

    def _build_speech_context(
        self, player: PlayerProtocol, candidates: list[PlayerProtocol]
    ) -> str:
        """Build context for campaign speech.

        Args:
            player: The candidate giving the speech.
            candidates: All candidates in the election.

        Returns:
            str: Context message for the candidate's agent.
        """
        if not self.game_state:
            return ""

        other_candidates = [c.name for c in candidates if c.player_id != player.player_id]

        context_parts = [
            f"You are {player.name}, a {player.get_role_name()}.",
            f"Current: Round {self.game_state.round_number} - Sheriff Election (Speech Phase)",
            "",
            "CAMPAIGN SPEECH:",
            f"You are one of {len(candidates)} candidates for sheriff.",
            f"Other candidates: {', '.join(other_candidates) if other_candidates else 'None'}",
            "",
            "Give a speech to convince other players to vote for you.",
            "You may:",
            "- Claim your role (true or false)",
            "- Explain why you'd be a good sheriff",
            "- Point out suspicions or share information",
            "- Make promises about how you'll use your sheriff powers",
            "",
            "Keep your speech concise (2-3 sentences).",
        ]

        return "\n".join(context_parts)

    def _conduct_sheriff_voting(self, candidates: list[PlayerProtocol]) -> dict[str, int]:
        """Have non-candidate players vote for sheriff.

        Args:
            candidates: List of sheriff candidates.

        Returns:
            dict[str, int]: Vote counts for each candidate.
        """
        if not self.game_state:
            return {}

        # Get all alive players who are NOT candidates
        candidate_ids = {c.player_id for c in candidates}
        alive_players = self.game_state.get_alive_players()
        voters = [p for p in alive_players if p.player_id not in candidate_ids]

        if not voters:
            self._log_event(EventType.MESSAGE, self.locale.get("no_voters"))
            return {c.player_id: 0 for c in candidates}

        self._log_event(
            EventType.MESSAGE, self.locale.get("sheriff_voting_start", count=len(voters))
        )

        vote_counts: dict[str, int] = {c.player_id: 0 for c in candidates}

        for voter in voters:
            if not voter.agent:
                continue

            context = self._build_sheriff_voting_context(voter, candidates)
            vote_target = ActionSelector.select_target(
                voter.agent, context, candidates, "Vote for sheriff", allow_skip=True
            )

            if vote_target:
                vote_counts[vote_target.player_id] += 1
                self._log_event(
                    EventType.SHERIFF_VOTE_CAST,
                    self.locale.get(
                        "sheriff_vote_cast", voter=voter.name, candidate=vote_target.name
                    ),
                    data={"voter_id": voter.player_id, "target_id": vote_target.player_id},
                )
            else:
                self._log_event(
                    EventType.MESSAGE, self.locale.get("sheriff_vote_abstained", voter=voter.name)
                )

        return vote_counts

    def _build_sheriff_voting_context(
        self, player: PlayerProtocol, candidates: list[PlayerProtocol]
    ) -> str:
        """Build context for sheriff voting.

        Args:
            player: The player who will vote.
            candidates: List of sheriff candidates.

        Returns:
            str: Context message for the player's agent.
        """
        if not self.game_state:
            return ""

        candidate_names = [c.name for c in candidates]

        context_parts = [
            f"You are {player.name}, a {player.get_role_name()}.",
            f"Current: Round {self.game_state.round_number} - Sheriff Election (Voting Phase)",
            "",
            "SHERIFF VOTING:",
            f"Candidates: {', '.join(candidate_names)}",
            "",
            "Vote for who you think should be sheriff.",
            "Consider:",
            "- Their campaign speech",
            "- Whether you trust them",
            "- Your role and win conditions",
            "",
            "You may also abstain from voting.",
        ]

        return "\n".join(context_parts)

    def _determine_sheriff_winner(
        self, vote_counts: dict[str, int], candidates: list[PlayerProtocol]
    ) -> None:
        """Determine the sheriff election winner.

        Args:
            vote_counts: Vote counts for each candidate.
            candidates: List of all candidates.
        """
        if not self.game_state or not vote_counts:
            return

        # Find max votes
        max_votes = max(vote_counts.values())
        winners = [pid for pid, count in vote_counts.items() if count == max_votes]

        # Announce vote results
        for candidate in candidates:
            votes = vote_counts.get(candidate.player_id, 0)
            self._log_event(
                EventType.MESSAGE,
                self.locale.get("sheriff_vote_result", candidate=candidate.name, votes=votes),
            )

        if len(winners) > 1:
            # Tie - handle based on rules (for now, no sheriff)
            winner_names = [
                self.game_state.get_player(pid).name
                for pid in winners
                if self.game_state.get_player(pid)
            ]
            self._log_event(
                EventType.SHERIFF_TIE,
                self.locale.get("sheriff_tie", candidates=", ".join(winner_names)),
            )
            # Could implement runoff voting here in the future
        else:
            # Single winner
            winner_id = winners[0]
            winner = self.game_state.get_player(winner_id)
            if winner:
                self._elect_sheriff(winner)

    def _elect_sheriff(self, player: PlayerProtocol) -> None:
        """Elect a player as sheriff.

        Args:
            player: The player to elect as sheriff.
        """
        if not self.game_state:
            return

        self.game_state.set_sheriff(player.player_id)
        self._log_event(
            EventType.SHERIFF_ELECTED,
            self.locale.get("sheriff_elected", player=player.name),
            data={"player_id": player.player_id},
        )
