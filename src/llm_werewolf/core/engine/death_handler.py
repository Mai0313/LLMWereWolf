"""Death handling logic for the game engine."""

import random
from typing import TYPE_CHECKING

from llm_werewolf.core.types import Camp, EventType, PlayerProtocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from llm_werewolf.core.locale import Locale
    from llm_werewolf.core.game_state import GameState


class DeathHandlerMixin:
    """Mixin for handling death-related game logic."""

    game_state: "GameState | None"
    locale: "Locale"
    _log_event: "Callable"

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
            "All villager abilities disabled due to Elder execution",
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
        else:
            if hasattr(target.role, "lives") and target.role.lives > 1:
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

    def _handle_death_abilities(self) -> list[str]:
        """Handle abilities that trigger on death (Hunter, AlphaWolf).

        Returns:
            list[str]: Messages from death abilities.
        """
        if not self.game_state:
            return []

        from llm_werewolf.core.action_selector import ActionSelector

        messages = []
        all_deaths = self.game_state.night_deaths | self.game_state.day_deaths

        for player_id in all_deaths:
            if player_id in self.game_state.death_abilities_used:
                continue
            player = self.game_state.get_player(player_id)
            if not player:
                continue

            if player.role.name in ("Hunter", "AlphaWolf"):
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
                    if player.role.name == "Hunter":
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
                hasattr(player.role, "charmed_player")
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
