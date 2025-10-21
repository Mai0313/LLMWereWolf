import random
from typing import TYPE_CHECKING, Any
from pathlib import Path

from rich.console import Console

from llm_werewolf.core.agent import BaseAgent
from llm_werewolf.core.types import Camp, Event, EventType, GamePhase
from llm_werewolf.core.config import GameConfig
from llm_werewolf.core.events import EventLogger
from llm_werewolf.core.locale import Locale
from llm_werewolf.core.player import Player
from llm_werewolf.core.actions import Action, VoteAction
from llm_werewolf.core.victory import VictoryChecker
from llm_werewolf.core.game_state import GameState
from llm_werewolf.core.roles.base import Role
from llm_werewolf.core.roles.villager import Elder, Idiot, Hunter
from llm_werewolf.core.roles.werewolf import AlphaWolf, WolfBeauty
from llm_werewolf.core.action_selector import ActionSelector

if TYPE_CHECKING:
    from collections.abc import Callable

console = Console()


class GameEngine:
    """Core game engine that controls the flow of the Werewolf game."""

    def __init__(self, config: GameConfig | None = None, language: str = "en-US") -> None:
        """Initialize the game engine.

        Args:
            config: Game configuration.
            language: Language code for localization (en-US, zh-TW, zh-CN).
        """
        self.config = config
        self.game_state: GameState | None = None
        self.event_logger = EventLogger()
        self.victory_checker: VictoryChecker | None = None
        self.locale = Locale(language)
        self._last_phase: str = ""  # Track phase changes for separators

        self.on_event: Callable[[Event], None] = self._default_print_event

    def _default_print_event(self, event: Event) -> None:
        """Default event handler that prints to console.

        This can be overridden by TUI or other interfaces.

        Args:
            event: The game event to display.
        """
        # Print phase separator when phase changes
        if event.phase != self._last_phase and event.event_type == EventType.PHASE_CHANGED:
            if "night" in event.phase.lower():
                console.print(f"\n{self.locale.get('night_separator')}")
            elif "day" in event.phase.lower():
                console.print(f"\n{self.locale.get('day_separator')}")
            self._last_phase = event.phase

        console.print(event.message)

    def setup_game(self, players: list[BaseAgent], roles: list[Role]) -> None:
        """Initialize the game with players and roles.

        Args:
            players: List of agent instances with name and model attributes.
            roles: List of role instances to assign.
        """
        if len(players) != len(roles):
            msg = f"Number of players ({len(players)}) must match number of roles ({len(roles)})"
            raise ValueError(msg)

        shuffled_roles = roles.copy()
        random.shuffle(shuffled_roles)

        player_objects = []
        for idx, (agent, role_class) in enumerate(
            zip(players, shuffled_roles, strict=False), start=1
        ):
            player_id = f"player_{idx}"
            name = agent.name
            ai_model = agent.model
            player = Player(
                player_id=player_id, name=name, role=role_class, agent=agent, ai_model=ai_model
            )
            player_objects.append(player)

        self.game_state = GameState(player_objects)
        self.victory_checker = VictoryChecker(self.game_state)

        self._log_event(
            EventType.GAME_STARTED,
            self.locale.get("game_started", player_count=len(player_objects)),
            data={"player_count": len(player_objects)},
        )

    def assign_roles(self) -> dict[str, str]:
        """Assign roles to players (already done in setup_game).

        Returns:
            dict[str, str]: Mapping of player_id to role_name.
        """
        if not self.game_state:
            msg = "Game not initialized"
            raise RuntimeError(msg)

        return {p.player_id: p.get_role_name() for p in self.game_state.players}

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
                except Exception as e:
                    messages.append(f"{player.name}: [Unable to speak - {e}]")

        return messages

    def _build_voting_context(self, player: Player) -> str:
        """Build context for voting phase.

        Args:
            player: The player who will vote.

        Returns:
            str: Context message for the player's agent.
        """
        if not self.game_state:
            return ""

        context_parts = [
            f"You are {player.name}, a {player.get_role_name()}.",
            f"It is Day {self.game_state.round_number}, voting phase.",
            "",
        ]

        if self.game_state.night_deaths:
            deaths = [
                self.game_state.get_player(pid).name
                for pid in self.game_state.night_deaths
                if self.game_state.get_player(pid)
            ]
            context_parts.append(f"Last night: {', '.join(deaths)} died.")
        else:
            context_parts.append("No one died last night.")

        alive_players = [p.name for p in self.game_state.get_alive_players()]
        context_parts.append(f"\nAlive players: {', '.join(alive_players)}")
        context_parts.append("")

        context_parts.append(
            "Based on the discussion and your role knowledge, "
            "vote for the player you believe should be eliminated."
        )

        return "\n".join(context_parts)

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

    def _collect_votes(self) -> list[Action]:
        """Collect votes from all players.

        Returns:
            list[Action]: List of vote actions.
        """
        if not self.game_state:
            return []

        vote_actions: list[Action] = []
        for player in self.game_state.get_alive_players():
            if not player.can_vote():
                continue

            possible_targets = self.game_state.get_alive_players(except_ids=[player.player_id])
            if not possible_targets:
                continue

            if player.agent:
                context = self._build_voting_context(player)
                target_player = ActionSelector.get_target_from_agent(
                    agent=player.agent,
                    role_name=player.get_role_name(),
                    action_description="Vote for a player to eliminate",
                    possible_targets=possible_targets,
                    allow_skip=False,
                    additional_context=context,
                )

                if target_player:
                    vote_actions.append(VoteAction(player, target_player, self.game_state))

        return vote_actions

    def _process_votes(self, vote_actions: list[Action]) -> None:
        """Process and log vote actions.

        Args:
            vote_actions: List of vote actions to process.
        """
        for action in vote_actions:
            if action.validate():
                action.execute()
                self._log_event(
                    EventType.VOTE_CAST,
                    self.locale.get(
                        "vote_cast", voter=action.actor.name, target=action.target.name
                    ),
                    data={
                        "voter_id": action.actor.player_id,
                        "voter_name": action.actor.name,
                        "target_id": action.target.player_id,
                        "target_name": action.target.name,
                    },
                )

    def _display_vote_results(self, vote_counts: dict[str, int]) -> None:
        """Display vote results summary.

        Args:
            vote_counts: Dictionary mapping player_id to vote count.
        """
        if not self.game_state:
            return

        self._log_event(
            EventType.VOTE_RESULT,
            self.locale.get("vote_summary"),
            data={"vote_counts": vote_counts},
        )

        for target_id, count in sorted(vote_counts.items(), key=lambda x: x[1], reverse=True):
            target = self.game_state.get_player(target_id)
            if target:
                voters = [
                    self.game_state.get_player(voter_id).name
                    for voter_id, voted_for in self.game_state.votes.items()
                    if voted_for == target_id and self.game_state.get_player(voter_id)
                ]
                voters_str = ", ".join(voters)
                self._log_event(
                    EventType.VOTE_RESULT,
                    self.locale.get(
                        "vote_count", target=target.name, count=count, voters=voters_str
                    ),
                    data={"target_id": target_id, "count": count, "voters": voters},
                )

    def _handle_lover_death(self, dead_player: Player) -> None:
        """Handle lover partner death when a player dies.

        Args:
            dead_player: The player who died.
        """
        if not self.game_state or not dead_player.is_lover() or not dead_player.lover_partner_id:
            return

        partner = self.game_state.get_player(dead_player.lover_partner_id)
        if partner and partner.is_alive():
            partner.kill()
            self.game_state.day_deaths.add(partner.player_id)
            self._log_event(
                EventType.LOVER_DIED,
                self.locale.get("died_of_heartbreak", player=partner.name),
                data={"player_id": partner.player_id},
            )

    def _handle_wolf_beauty_charm_death(self, wolf_beauty: Player) -> None:
        """Handle charmed player death when Wolf Beauty dies.

        Args:
            wolf_beauty: The Wolf Beauty player who died.
        """
        if not self.game_state or not isinstance(wolf_beauty.role, WolfBeauty):
            return

        if wolf_beauty.role.charmed_player:
            charmed = self.game_state.get_player(wolf_beauty.role.charmed_player)
            if charmed and charmed.is_alive():
                charmed.kill()
                self.game_state.day_deaths.add(charmed.player_id)
                self._log_event(
                    EventType.PLAYER_DIED,
                    self.locale.get(
                        "died_from_charm",
                        player=charmed.name,
                        wolf_beauty=wolf_beauty.name,
                    ),
                    data={
                        "player_id": charmed.player_id,
                        "reason": "wolf_beauty_charm",
                    },
                )

    def _eliminate_voted_player(self, eliminated: Player) -> None:
        """Eliminate a player who received the most votes.

        Args:
            eliminated: The player to eliminate.
        """
        if not self.game_state:
            return

        eliminated_id = eliminated.player_id

        # Special case: Idiot reveals instead of dying
        if isinstance(eliminated.role, Idiot) and not eliminated.role.revealed:
            eliminated.role.revealed = True
            eliminated.disable_voting()
            self._log_event(
                EventType.ROLE_REVEALED,
                self.locale.get("idiot_revealed", player=eliminated.name),
                data={"player_id": eliminated_id, "role": "Idiot"},
            )
            return

        # Normal elimination
        eliminated.kill()
        self.game_state.day_deaths.add(eliminated_id)
        self.game_state.death_causes[eliminated_id] = "vote"

        self._log_event(
            EventType.PLAYER_ELIMINATED,
            self.locale.get(
                "player_eliminated",
                player=eliminated.name,
                role=eliminated.get_role_name(),
            ),
            data={"player_id": eliminated_id, "role": eliminated.get_role_name()},
        )

        # Handle Elder penalty
        if isinstance(eliminated.role, Elder):
            self._handle_elder_penalty()
            self._log_event(
                EventType.ROLE_REVEALED,
                self.locale.get("elder_executed"),
                data={"player_id": eliminated_id},
            )

        # Handle cascading deaths
        self._handle_lover_death(eliminated)
        self._handle_wolf_beauty_charm_death(eliminated)

    def run_voting_phase(self) -> list[str]:
        """Execute the voting phase.

        Returns:
            list[str]: Messages from the voting phase.
        """
        if not self.game_state:
            msg = "Game not initialized"
            raise RuntimeError(msg)

        messages = []
        self.game_state.set_phase(GamePhase.DAY_VOTING)
        messages.append("\n=== Voting Phase ===")

        # Collect and process votes
        vote_actions = self._collect_votes()
        self._process_votes(vote_actions)

        vote_counts = self.game_state.get_vote_counts()

        if vote_counts:
            self._display_vote_results(vote_counts)

            # Determine elimination
            max_votes = max(vote_counts.values())
            candidates = [pid for pid, count in vote_counts.items() if count == max_votes]

            if len(candidates) == 1:
                eliminated = self.game_state.get_player(candidates[0])
                if eliminated:
                    self._eliminate_voted_player(eliminated)
            else:
                self._log_event(EventType.VOTE_RESULT, self.locale.get("vote_tied"), data={})
        else:
            self._log_event(EventType.VOTE_RESULT, self.locale.get("no_votes"), data={})

        death_ability_messages = self._handle_death_abilities()
        messages.extend(death_ability_messages)

        return messages

    def _handle_werewolf_kill(self, target: Player) -> list[str]:
        """Handle werewolf kill and its consequences.

        Args:
            target: The target player.

        Returns:
            list[str]: Messages describing the kill.
        """
        if not self.game_state:
            return []

        messages: list[str] = []

        if self.game_state.witch_saved_target == target.player_id:
            self._log_event(
                EventType.WITCH_SAVED,
                self.locale.get("saved_by_witch", player=target.name),
                data={"player_id": target.player_id},
            )
        elif self.game_state.guard_protected == target.player_id:
            self._log_event(
                EventType.GUARD_PROTECTED,
                self.locale.get("protected_by_guard", player=target.name),
                data={"player_id": target.player_id},
            )
        else:
            if isinstance(target.role, Elder) and target.role.lives > 1:
                target.role.lives -= 1
                self._log_event(
                    EventType.PLAYER_DIED,
                    self.locale.get("elder_attacked", player=target.name),
                    data={"player_id": target.player_id},
                )
            else:
                target.kill()
                self.game_state.night_deaths.add(target.player_id)

                self._log_event(
                    EventType.PLAYER_DIED,
                    self.locale.get("killed_by_werewolves", player=target.name),
                    data={"player_id": target.player_id},
                )

                if target.is_lover() and target.lover_partner_id:
                    partner = self.game_state.get_player(target.lover_partner_id)
                    if partner and partner.is_alive():
                        partner.kill()
                        self.game_state.night_deaths.add(partner.player_id)
                        self._log_event(
                            EventType.LOVER_DIED,
                            self.locale.get("died_of_heartbreak", player=partner.name),
                            data={"player_id": partner.player_id},
                        )

        return messages

    def _handle_elder_penalty(self) -> None:
        """Disable all villager abilities when Elder is voted out."""
        if not self.game_state:
            return

        for player in self.game_state.players:
            if player.get_camp() == Camp.VILLAGER.value and player.is_alive():
                player.role.disabled = True

        self._log_event(
            EventType.ROLE_REVEALED,
            "All villager abilities disabled due to Elder execution",
            data={"reason": "elder_penalty"},
        )

    def _handle_death_abilities(self) -> list[str]:
        """Handle abilities that trigger on death (Hunter, AlphaWolf).

        Returns:
            list[str]: Messages from death abilities.
        """
        if not self.game_state:
            return []

        messages = []
        all_deaths = self.game_state.night_deaths | self.game_state.day_deaths

        for player_id in all_deaths:
            if player_id in self.game_state.death_abilities_used:
                continue
            player = self.game_state.get_player(player_id)
            if not player:
                continue

            if isinstance(player.role, (Hunter, AlphaWolf)):
                death_cause = self.game_state.death_causes.get(player_id)
                if death_cause == "witch_poison":
                    self._log_event(
                        EventType.MESSAGE,
                        self.locale.get("poisoned_no_ability", player=player.name),
                        data={"player_id": player_id},
                    )
                    self.game_state.death_abilities_used.add(player_id)
                    continue

                self.game_state.death_abilities_used.add(player_id)

                possible_targets = self.game_state.get_alive_players()
                if not possible_targets:
                    continue

                role_name = player.get_role_name()
                self._log_event(
                    EventType.MESSAGE,
                    self.locale.get("death_ability_active", player=player.name, role=role_name),
                    data={"player_id": player_id, "role": role_name},
                )

                if player.agent:
                    target = ActionSelector.get_target_from_agent(
                        agent=player.agent,
                        role_name=role_name,
                        action_description="Choose a player to shoot before you die",
                        possible_targets=possible_targets,
                        allow_skip=False,
                        additional_context=f"You ({player.name}) have been killed. You can take one player down with you.",
                    )
                else:
                    target = random.choice(possible_targets)  # noqa: S311

                if target and target.is_alive():
                    target.kill()
                    if self.game_state.phase.value == "night":
                        self.game_state.night_deaths.add(target.player_id)
                    else:
                        self.game_state.day_deaths.add(target.player_id)

                    # Use appropriate event based on role
                    if isinstance(player.role, Hunter):
                        event_msg = self.locale.get(
                            "hunter_shoots", hunter=player.name, target=target.name
                        )
                    else:  # AlphaWolf
                        event_msg = self.locale.get(
                            "alpha_wolf_shoots", alpha=player.name, target=target.name
                        )

                    self._log_event(
                        EventType.HUNTER_REVENGE,
                        event_msg,
                        data={
                            "shooter_id": player.player_id,
                            "target_id": target.player_id,
                            "role": role_name,
                        },
                    )

                    if target.is_lover() and target.lover_partner_id:
                        partner = self.game_state.get_player(target.lover_partner_id)
                        if partner and partner.is_alive():
                            partner.kill()
                            if self.game_state.phase.value == "night":
                                self.game_state.night_deaths.add(partner.player_id)
                            else:
                                self.game_state.day_deaths.add(partner.player_id)
                            messages.append(f"{partner.name} died of heartbreak (lover)!")

        return messages

    def resolve_deaths(self) -> list[str]:
        """Resolve all deaths based on night actions.

        Returns:
            list[str]: Messages describing deaths.
        """
        if not self.game_state:
            return []

        messages = []

        if self.game_state.werewolf_target:
            target = self.game_state.get_player(self.game_state.werewolf_target)
            if target:
                messages.extend(self._handle_werewolf_kill(target))
                if not target.is_alive() and target.player_id not in self.game_state.death_causes:
                    self.game_state.death_causes[target.player_id] = "werewolf"

        if self.game_state.witch_poison_target:
            target = self.game_state.get_player(self.game_state.witch_poison_target)
            if target and target.is_alive():
                target.kill()
                self.game_state.night_deaths.add(target.player_id)
                self.game_state.death_causes[target.player_id] = "witch_poison"

                self._log_event(
                    EventType.WITCH_POISONED,
                    f"{target.name} was poisoned by witch",
                    data={"player_id": target.player_id},
                )

                if target.is_lover() and target.lover_partner_id:
                    partner = self.game_state.get_player(target.lover_partner_id)
                    if partner and partner.is_alive():
                        partner.kill()
                        self.game_state.night_deaths.add(partner.player_id)
                        messages.append(f"{partner.name} died of heartbreak (lover)!")
                        self._log_event(
                            EventType.LOVER_DIED,
                            f"{partner.name} died of heartbreak",
                            data={"player_id": partner.player_id},
                        )

        for player in self.game_state.players:
            if (
                isinstance(player.role, WolfBeauty)
                and not player.is_alive()
                and player.role.charmed_player
            ):
                charmed = self.game_state.get_player(player.role.charmed_player)
                if charmed and charmed.is_alive():
                    charmed.kill()
                    self.game_state.night_deaths.add(charmed.player_id)
                    messages.append(
                        f"{charmed.name} died from Wolf Beauty's charm "
                        f"(Wolf Beauty {player.name} died)!"
                    )
                    self._log_event(
                        EventType.PLAYER_DIED,
                        f"{charmed.name} died from Wolf Beauty's charm",
                        data={"player_id": charmed.player_id, "reason": "wolf_beauty_charm"},
                    )

        death_ability_messages = self._handle_death_abilities()
        messages.extend(death_ability_messages)

        return messages

    def check_victory(self) -> bool:
        """Check if any victory condition is met.

        Returns:
            bool: True if the game has ended.
        """
        if not self.victory_checker:
            return False

        result = self.victory_checker.check_victory()

        if result.has_winner:
            if self.game_state:
                self.game_state.set_phase(GamePhase.ENDED)
                self.game_state.winner = result.winner_camp

            self._log_event(
                EventType.GAME_ENDED,
                f"Game ended. {result.winner_camp} wins! {result.reason}",
                data={
                    "winner_camp": result.winner_camp,
                    "winner_ids": result.winner_ids,
                    "reason": result.reason,
                },
            )

            return True

        return False

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

        def get_action_priority(action: Action) -> int:
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

    def play_game(self) -> str:
        """Run the main game loop.

        Returns:
            str: The final game result.
        """
        if not self.game_state:
            return "Game not initialized"

        while not self.check_victory():
            self.game_state.reset_deaths()

            self.run_night_phase()

            if self.check_victory():
                break

            self.run_day_phase()

            self.run_voting_phase()

            if self.check_victory():
                break

            self.game_state.next_phase()

        if self.game_state.winner:
            return self.locale.get("game_over", winner=self.game_state.winner)

        return self.locale.get("game_ended", winner="unknown", reason="")

    def _log_event(
        self,
        event_type: EventType,
        message: str,
        data: dict | None = None,
        visible_to: list[str] | None = None,
    ) -> None:
        """Log an event and notify listeners.

        Args:
            event_type: Type of the event.
            message: Event message.
            data: Additional event data.
            visible_to: List of player IDs who can see this event.
        """
        if not self.game_state:
            return

        event = self.event_logger.create_event(
            event_type=event_type,
            round_number=self.game_state.round_number,
            phase=self.game_state.phase.value,
            message=message,
            data=data,
            visible_to=visible_to,
        )

        self.on_event(event)

    def get_game_state(self) -> GameState | None:
        """Get the current game state.

        Returns:
            GameState | None: The game state.
        """
        return self.game_state

    def get_events(self) -> list[Event]:
        """Get all game events.

        Returns:
            list[Event]: List of events.
        """
        return self.event_logger.events

    def step(self) -> list[str]:
        """Execute one step of the game (one phase)."""
        if not self.game_state:
            return ["Game not initialized"]

        if self.check_victory():
            return [f"Game Over! {self.game_state.winner} camp wins!"]

        phase_messages = []
        current_phase = self.game_state.get_phase()

        if current_phase == GamePhase.SETUP:
            self.game_state.next_phase()
            phase_messages = [
                "Game initialized! Press 'n' to start the first night phase.",
                f"Round {self.game_state.round_number} begins.",
            ]
        elif current_phase == GamePhase.NIGHT:
            phase_messages = self.run_night_phase()
            if not self.check_victory():
                self.game_state.next_phase()
        elif current_phase == GamePhase.DAY_DISCUSSION:
            phase_messages = self.run_day_phase()
            self.game_state.next_phase()
        elif current_phase == GamePhase.DAY_VOTING:
            phase_messages = self.run_voting_phase()
            if not self.check_victory():
                self.game_state.next_phase()

        return phase_messages

    def save_game(self, file_path: str | Path) -> None:
        """Save the current game state to a file.

        Args:
            file_path: Path to save the game state.

        Raises:
            RuntimeError: If game is not initialized.
        """
        if not self.game_state:
            msg = "Game not initialized"
            raise RuntimeError(msg)

        from llm_werewolf.core.serialization import save_game_state

        save_game_state(self.game_state, file_path)

    def load_game(
        self, file_path: str | Path, agent_factory: dict[str, Any] | None = None
    ) -> None:
        """Load a game state from a file.

        Args:
            file_path: Path to load the game state from.
            agent_factory: Optional dictionary mapping player_id to agent instances.
                          If not provided, players will have no agents.

        Note:
            Agents cannot be serialized, so they must be recreated manually.
            Pass a dictionary mapping player_id to agent instances to restore agents.
        """
        from llm_werewolf.core.serialization import load_game_state

        self.game_state = load_game_state(file_path, agent_factory)
        self.victory_checker = VictoryChecker(self.game_state)
