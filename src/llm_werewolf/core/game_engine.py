import random
from typing import TYPE_CHECKING

from rich.console import Console

from llm_werewolf.core.events import Event, EventType, EventLogger
from llm_werewolf.core.player import Player
from llm_werewolf.core.actions import Action, VoteAction
from llm_werewolf.core.victory import VictoryChecker
from llm_werewolf.core.game_state import GamePhase, GameState
from llm_werewolf.config.game_config import GameConfig

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.ai import AgentType
    from llm_werewolf.core.roles.base import Role


console = Console()


class GameEngine:
    """Core game engine that controls the flow of the Werewolf game."""

    def __init__(self, config: GameConfig | None = None) -> None:
        """Initialize the game engine.

        Args:
            config: Game configuration.
        """
        self.config = config
        self.game_state: GameState | None = None
        self.event_logger = EventLogger()
        self.victory_checker: VictoryChecker | None = None

        # Callback for UI updates
        self.on_event: Callable[[Event], None] = self.print_event

    def print_event(self, event: Event) -> None:
        prefix = f"[回合 {event.round_number}][{event.phase.upper()}]"
        console.print(f"{prefix} {event.message}")

    def setup_game(self, players: list[tuple[str, str, "AgentType"]], roles: list["Role"]) -> None:
        """Initialize the game with players and roles.

        Args:
            players: List of tuples (player_id, name, agent).
            roles: List of role instances to assign.
        """
        if len(players) != len(roles):
            msg = f"Number of players ({len(players)}) must match number of roles ({len(roles)})"
            raise ValueError(msg)

        # Shuffle roles for random assignment
        shuffled_roles = roles.copy()
        random.shuffle(shuffled_roles)

        # Create player objects
        player_objects = []
        for (player_id, name, agent), role_class in zip(players, shuffled_roles, strict=False):
            ai_model = getattr(agent, "model_name", "unknown") if agent else "human"
            player = Player(
                player_id=player_id, name=name, role=role_class, agent=agent, ai_model=ai_model
            )
            player_objects.append(player)

        # Initialize game state
        self.game_state = GameState(player_objects)
        self.victory_checker = VictoryChecker(self.game_state)

        # Log game start event
        self._log_event(
            EventType.GAME_STARTED,
            f"Game started with {len(player_objects)} players",
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
            f"Night {self.game_state.round_number} begins",
            data={"phase": "night", "round": self.game_state.round_number},
        )

        messages.append(f"\n=== Night {self.game_state.round_number} ===")

        # Get all players with night actions
        players_with_night_actions = self.game_state.get_players_with_night_actions()

        # Get night actions from each player
        night_actions: list[Action] = []
        for player in players_with_night_actions:
            # Here you would get the action from the player's agent
            # For now, we'll use a placeholder
            action = player.role.get_night_actions(self.game_state)
            if action:
                night_actions.extend(action)

        # Process actions
        action_messages = self.process_actions(night_actions)
        messages.extend(action_messages)

        # Resolve night deaths
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
            f"Day {self.game_state.round_number} begins",
            data={"phase": "day", "round": self.game_state.round_number},
        )

        messages.append(f"\n=== Day {self.game_state.round_number} ===")

        # Announce who died last night
        if self.game_state.night_deaths:
            for player_id in self.game_state.night_deaths:
                player = self.game_state.get_player(player_id)
                if player:
                    messages.append(f"{player.name} was killed last night.")
        else:
            messages.append("No one died last night.")

        # Day discussion - players share thoughts and suspicions
        messages.append("\n--- Discussion Phase ---")
        alive_players = self.game_state.get_alive_players()

        for player in alive_players:
            if player.agent:
                # Build context for the player
                game_context = self._build_discussion_context(player)

                # Get player's speech from their agent
                try:
                    speech = player.agent.get_response(game_context)

                    # Log the player's speech
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

    def _build_discussion_context(self, player: "Player") -> str:
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

        # Add information about who died
        if self.game_state.night_deaths:
            deaths = [
                self.game_state.get_player(pid).name
                for pid in self.game_state.night_deaths
                if self.game_state.get_player(pid)
            ]
            context_parts.append(f"Last night, {', '.join(deaths)} died.")
        else:
            context_parts.append("No one died last night.")

        # Add alive players
        alive_players = [p.name for p in self.game_state.get_alive_players()]
        context_parts.append(f"\nAlive players: {', '.join(alive_players)}")
        context_parts.append("")

        # Add role-specific instructions
        context_parts.append(
            "Share your thoughts, suspicions, or information. "
            "Your goal is to help your team win while staying in character."
        )
        context_parts.append(
            "\nProvide a brief statement (1-3 sentences) for this discussion round."
        )

        return "\n".join(context_parts)

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

        # Get votes from players
        vote_actions: list[Action] = []
        for player in self.game_state.get_alive_players():
            if not player.can_vote():
                continue

            # Get vote from agent
            # This is a simplified version, in a real implementation, the agent
            # would be prompted with the current game state and asked for a vote
            if player.agent:
                possible_targets = self.game_state.get_alive_players(except_ids=[player.player_id])
                if possible_targets:
                    target_player = random.choice(possible_targets)  # noqa: S311
                    vote_actions.append(VoteAction(player, target_player, self.game_state))

        # Process votes
        vote_messages = self.process_actions(vote_actions)
        messages.extend(vote_messages)

        # Get vote counts
        vote_counts = self.game_state.get_vote_counts()

        if vote_counts:
            # Find player with most votes
            max_votes = max(vote_counts.values())
            candidates = [pid for pid, count in vote_counts.items() if count == max_votes]

            if len(candidates) == 1:
                eliminated_id = candidates[0]
                eliminated = self.game_state.get_player(eliminated_id)
                if eliminated:
                    # Check if Idiot
                    from llm_werewolf.core.roles.villager import Idiot

                    if isinstance(eliminated.role, Idiot) and not eliminated.role.revealed:
                        eliminated.role.revealed = True
                        eliminated.disable_voting()
                        messages.append(
                            f"{eliminated.name} reveals they are the Idiot and survives!"
                        )
                    else:
                        eliminated.kill()
                        self.game_state.day_deaths.add(eliminated_id)
                        messages.append(
                            f"{eliminated.name} was eliminated by vote. "
                            f"They were a {eliminated.get_role_name()}."
                        )

                        self._log_event(
                            EventType.PLAYER_ELIMINATED,
                            f"{eliminated.name} was voted out",
                            data={"player_id": eliminated_id, "role": eliminated.get_role_name()},
                        )
            else:
                messages.append("Vote tied. No one is eliminated.")
        else:
            messages.append("No votes cast.")

        return messages

    def _handle_werewolf_kill(self, target: "Player") -> list[str]:
        """Handle werewolf kill and its consequences.

        Args:
            target: The target player.

        Returns:
            list[str]: Messages describing the kill.
        """
        if not self.game_state:
            return []

        messages = []

        # Check if saved by witch
        if self.game_state.witch_saved_target == target.player_id:
            messages.append(f"{target.name} was saved by the witch!")
        # Check if protected by guard
        elif self.game_state.guard_protected == target.player_id:
            messages.append(f"{target.name} was protected by the guard!")
        else:
            # Check if Elder with 2 lives
            from llm_werewolf.core.roles.villager import Elder

            if isinstance(target.role, Elder) and target.role.lives > 1:
                target.role.lives -= 1
                messages.append(f"{target.name} was attacked but survived (Elder)!")
            else:
                target.kill()
                self.game_state.night_deaths.add(target.player_id)

                self._log_event(
                    EventType.WEREWOLF_KILLED,
                    f"{target.name} was killed by werewolves",
                    data={"player_id": target.player_id},
                )

                # Check if lover dies
                if target.is_lover() and target.lover_partner_id:
                    partner = self.game_state.get_player(target.lover_partner_id)
                    if partner and partner.is_alive():
                        partner.kill()
                        self.game_state.night_deaths.add(partner.player_id)
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

        # Werewolf kill
        if self.game_state.werewolf_target:
            target = self.game_state.get_player(self.game_state.werewolf_target)
            if target:
                messages.extend(self._handle_werewolf_kill(target))

        # Witch poison
        if self.game_state.witch_poison_target:
            target = self.game_state.get_player(self.game_state.witch_poison_target)
            if target and target.is_alive():
                target.kill()
                self.game_state.night_deaths.add(target.player_id)

                self._log_event(
                    EventType.WITCH_POISONED,
                    f"{target.name} was poisoned by witch",
                    data={"player_id": target.player_id},
                )

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

    def process_actions(self, actions: list) -> list[str]:
        """Process a list of actions.

        Args:
            actions: List of Action objects to process.

        Returns:
            list[str]: Messages from processing actions.
        """
        messages = []

        # Sort actions by priority (if they have priority)
        # For now, we can assume a predefined order or add priority to actions
        # This is a simplified sorting, a more robust solution would be needed
        def get_action_priority(action: Action) -> int:
            priority_map = {
                "GuardProtectAction": 0,
                "WerewolfKillAction": 1,
                "WitchSaveAction": 2,
                "WitchPoisonAction": 3,
                "SeerCheckAction": 4,
            }
            return priority_map.get(action.__class__.__name__, 100)

        sorted_actions = sorted(actions, key=get_action_priority)

        # Execute each action
        for action in sorted_actions:
            if action.validate():
                result_messages = action.execute()
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
            # Reset deaths for the new round
            self.game_state.reset_deaths()

            # Night phase
            self.run_night_phase()

            # Check victory after night
            if self.check_victory():
                break

            # Day phase
            self.run_day_phase()

            # Voting phase
            self.run_voting_phase()

            # Check victory after voting
            if self.check_victory():
                break

            # Move to next round
            self.game_state.next_phase()

        # Game ended
        if self.game_state.winner:
            return f"Game Over! {self.game_state.winner} camp wins!"

        return "Game ended"

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

        # Notify UI or other listeners
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
            # Transition from setup to first night phase
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
