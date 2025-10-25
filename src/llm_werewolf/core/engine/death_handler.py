"""Death handling logic for the game engine."""

import random
from collections.abc import Callable

from llm_werewolf.core.types import Camp, EventType, PlayerProtocol
from llm_werewolf.core.locale import Locale
from llm_werewolf.core.game_state import GameState
from llm_werewolf.core.action_selector import ActionSelector


class DeathHandlerMixin:
    """Mixin for handling death-related game logic."""

    game_state: GameState | None
    locale: Locale
    _log_event: Callable

    def _handle_lover_death(self, dead_player: PlayerProtocol) -> None:
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

    def _handle_wolf_beauty_charm_death(self, wolf_beauty: PlayerProtocol) -> None:
        """Handle charmed player death when Wolf Beauty dies.

        Args:
            wolf_beauty: The Wolf Beauty player who died.
        """
        if not self.game_state or not hasattr(wolf_beauty.role, "charmed_player"):
            return

        if wolf_beauty.role.charmed_player:
            charmed = self.game_state.get_player(wolf_beauty.role.charmed_player)
            if charmed and charmed.is_alive():
                charmed.kill()
                self.game_state.day_deaths.add(charmed.player_id)
                self._log_event(
                    EventType.PLAYER_DIED,
                    self.locale.get(
                        "died_from_charm", player=charmed.name, wolf_beauty=wolf_beauty.name
                    ),
                    data={"player_id": charmed.player_id, "reason": "wolf_beauty_charm"},
                )

    def _handle_elder_penalty(self) -> None:
        """Disable all villager abilities when Elder is voted out."""
        if not self.game_state:
            return

        for player in self.game_state.players:
            if player.get_camp() == Camp.VILLAGER.value and player.is_alive():
                player.role.disabled = True

        self._log_event(
            EventType.ROLE_REVEALED,
            self.locale.get("elder_penalty"),
            data={"reason": "elder_penalty"},
        )

    def _handle_werewolf_kill(self, target: PlayerProtocol) -> list[str]:
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
        elif hasattr(target.role, "lives") and target.role.lives > 1:
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

    def _handle_sheriff_badge_transfer(self) -> list[str]:
        """Handle sheriff badge transfer when sheriff dies.

        Returns:
            list[str]: Messages from badge transfer.
        """
        if not self.game_state:
            return []

        messages: list[str] = []
        all_deaths = self.game_state.night_deaths | self.game_state.day_deaths

        # Check if sheriff died
        if self.game_state.sheriff_id and self.game_state.sheriff_id in all_deaths:
            sheriff = self.game_state.get_player(self.game_state.sheriff_id)
            if not sheriff or sheriff.player_id in self.game_state.death_abilities_used:
                return messages

            self.game_state.death_abilities_used.add(sheriff.player_id)

            self._log_event(
                EventType.MESSAGE,
                self.locale.get("sheriff_died_transfer", sheriff=sheriff.name),
                data={"player_id": sheriff.player_id},
            )

            # Ask sheriff whether to transfer badge
            possible_targets = self.game_state.get_alive_players()
            if not possible_targets or not sheriff.agent:
                # No one to transfer to, or no agent - tear the badge
                self.game_state.remove_sheriff()
                self._log_event(
                    EventType.SHERIFF_BADGE_TORN,
                    self.locale.get("sheriff_badge_torn", sheriff=sheriff.name),
                    data={"player_id": sheriff.player_id},
                )
                return messages

            context = (
                f"You are {sheriff.name}, the sheriff, and you have died.\n"
                f"You can choose to:\n"
                f"1. Transfer the sheriff badge to another living player\n"
                f"2. Tear the badge (choose 'skip' or 'none')\n\n"
                f"Living players: {', '.join([p.name for p in possible_targets])}\n"
            )

            target = ActionSelector.get_target_from_agent(
                agent=sheriff.agent,
                role_name="Sheriff",
                action_description="Choose a player to transfer the sheriff badge to (or skip to tear it)",
                possible_targets=possible_targets,
                allow_skip=True,
                additional_context=context,
            )

            if target:
                # Transfer badge to target
                self.game_state.set_sheriff(target.player_id)
                self._log_event(
                    EventType.SHERIFF_BADGE_TRANSFERRED,
                    self.locale.get(
                        "sheriff_badge_transferred", sheriff=sheriff.name, target=target.name
                    ),
                    data={"from_player_id": sheriff.player_id, "to_player_id": target.player_id},
                )
            else:
                # Tear the badge
                self.game_state.remove_sheriff()
                self._log_event(
                    EventType.SHERIFF_BADGE_TORN,
                    self.locale.get("sheriff_badge_torn", sheriff=sheriff.name),
                    data={"player_id": sheriff.player_id},
                )

        return messages

    def _process_hunter_or_alpha_death(self, player: PlayerProtocol) -> list[str]:
        """Process Hunter or AlphaWolf death ability.

        Args:
            player: The player with death ability.

        Returns:
            list[str]: Messages from ability execution.
        """
        if not self.game_state:
            return []

        messages: list[str] = []
        possible_targets = self.game_state.get_alive_players()
        if not possible_targets:
            return messages

        role_name = player.get_role_name()
        self._log_event(
            EventType.MESSAGE,
            self.locale.get("death_ability_active", player=player.name, role=role_name),
            data={"player_id": player.player_id, "role": role_name},
        )

        # Get target from agent or random
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
            self._execute_death_shot(player, target, role_name, messages)

        return messages

    def _execute_death_shot(
        self, shooter: PlayerProtocol, target: PlayerProtocol, role_name: str, messages: list[str]
    ) -> None:
        """Execute the death shot and handle consequences.

        Args:
            shooter: The player shooting.
            target: The target player.
            role_name: Name of the shooter's role.
            messages: List to append messages to.
        """
        if not self.game_state:
            return

        target.kill()
        if self.game_state.phase.value == "night":
            self.game_state.night_deaths.add(target.player_id)
        else:
            self.game_state.day_deaths.add(target.player_id)

        # Log appropriate event based on role
        event_msg = (
            self.locale.get("hunter_shoots", hunter=shooter.name, target=target.name)
            if shooter.role.name == "Hunter"
            else self.locale.get("alpha_wolf_shoots", alpha=shooter.name, target=target.name)
        )

        self._log_event(
            EventType.HUNTER_REVENGE,
            event_msg,
            data={
                "shooter_id": shooter.player_id,
                "target_id": target.player_id,
                "role": role_name,
            },
        )

        # Handle lover death
        if target.is_lover() and target.lover_partner_id:
            partner = self.game_state.get_player(target.lover_partner_id)
            if partner and partner.is_alive():
                partner.kill()
                if self.game_state.phase.value == "night":
                    self.game_state.night_deaths.add(partner.player_id)
                else:
                    self.game_state.day_deaths.add(partner.player_id)
                messages.append(f"{partner.name} died of heartbreak (lover)!")

    def _handle_death_abilities(self) -> list[str]:
        """Handle abilities that trigger on death (Hunter, AlphaWolf).

        Returns:
            list[str]: Messages from death abilities.
        """
        if not self.game_state:
            return []

        # Handle sheriff badge transfer first
        sheriff_messages = self._handle_sheriff_badge_transfer()

        messages = []
        all_deaths = self.game_state.night_deaths | self.game_state.day_deaths

        for player_id in all_deaths:
            if player_id in self.game_state.death_abilities_used:
                continue
            player = self.game_state.get_player(player_id)
            if not player:
                continue

            if player.role.name in ("Hunter", "AlphaWolf"):
                # Check if poisoned
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
                ability_messages = self._process_hunter_or_alpha_death(player)
                messages.extend(ability_messages)

        messages.extend(sheriff_messages)
        return messages

    def _resolve_witch_poison_death(self) -> None:
        """Resolve witch poison death and lover consequence."""
        if not self.game_state or not self.game_state.witch_poison_target:
            return

        target = self.game_state.get_player(self.game_state.witch_poison_target)
        if not target or not target.is_alive():
            return

        target.kill()
        self.game_state.night_deaths.add(target.player_id)
        self.game_state.death_causes[target.player_id] = "witch_poison"

        self._log_event(
            EventType.WITCH_POISONED,
            self.locale.get("witch_poisoned_target", target=target.name),
            data={"player_id": target.player_id},
        )

        # Handle lover death
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

    def _resolve_wolf_beauty_charm_deaths(self) -> None:
        """Resolve charmed player deaths when Wolf Beauty dies."""
        if not self.game_state:
            return

        for player in self.game_state.players:
            if (
                hasattr(player.role, "charmed_player")
                and not player.is_alive()
                and player.role.charmed_player
            ):
                charmed = self.game_state.get_player(player.role.charmed_player)
                if charmed and charmed.is_alive():
                    charmed.kill()
                    self.game_state.night_deaths.add(charmed.player_id)
                    self._log_event(
                        EventType.PLAYER_DIED,
                        self.locale.get(
                            "died_from_charm", player=charmed.name, wolf_beauty=player.name
                        ),
                        data={"player_id": charmed.player_id, "reason": "wolf_beauty_charm"},
                    )

    def resolve_deaths(self) -> list[str]:
        """Resolve all deaths based on night actions.

        Returns:
            list[str]: Messages describing deaths.
        """
        if not self.game_state:
            return []

        messages = []

        # Handle werewolf kill
        if self.game_state.werewolf_target:
            target = self.game_state.get_player(self.game_state.werewolf_target)
            if target:
                messages.extend(self._handle_werewolf_kill(target))
                if not target.is_alive() and target.player_id not in self.game_state.death_causes:
                    self.game_state.death_causes[target.player_id] = "werewolf"

        # Handle witch poison
        self._resolve_witch_poison_death()

        # Handle wolf beauty charm deaths
        self._resolve_wolf_beauty_charm_deaths()

        # Handle death abilities
        death_ability_messages = self._handle_death_abilities()
        messages.extend(death_ability_messages)

        return messages
