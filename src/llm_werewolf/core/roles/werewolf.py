"""Werewolf camp roles."""

from llm_werewolf.core.roles.base import Camp, Role, RoleConfig, ActionPriority


class Werewolf(Role):
    """Standard Werewolf role.

    Werewolves wake up at night and collectively choose a victim to kill.
    They win when werewolves equal or outnumber villagers.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Werewolf role."""
        return RoleConfig(
            name="Werewolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are a Werewolf. Each night, you wake up with other werewolves "
                "and collectively choose a villager to eliminate. Your goal is to "
                "outnumber the villagers."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )


class AlphaWolf(Role):
    """Alpha Wolf (Wolf King) role.

    Similar to a standard werewolf, but when eliminated (by vote or hunter),
    can take another player down with them.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Alpha Wolf role."""
        return RoleConfig(
            name="Alpha Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Alpha Wolf. You wake up with other werewolves each night "
                "to kill a villager. When you are eliminated (by voting or hunter), "
                "you can immediately shoot and eliminate another player before you die."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=True,  # Can shoot when dying
        )


class WhiteWolf(Role):
    """White Wolf role.

    A werewolf who can kill another werewolf once every two nights.
    This makes the white wolf a lone wolf trying to be the last werewolf standing.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the White Wolf role."""
        return RoleConfig(
            name="White Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the White Wolf. You wake up with other werewolves to kill villagers. "
                "Additionally, every other night, you wake up alone and can choose to kill "
                "another werewolf. Your ultimate goal may be to be the last werewolf standing."
            ),
            priority=ActionPriority.WHITE_WOLF,
            can_act_night=True,
            can_act_day=False,
        )


class WolfBeauty(Role):
    """Wolf Beauty role.

    A werewolf who charms a player each night. If the Wolf Beauty dies,
    the charmed player dies too.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Wolf Beauty role."""
        return RoleConfig(
            name="Wolf Beauty",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Wolf Beauty. You wake up with other werewolves to kill villagers. "
                "Each night, you can also charm a player. If you die, the charmed player "
                "dies with you immediately."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )


class GuardianWolf(Role):
    """Guardian Wolf role.

    A werewolf who can protect one werewolf from elimination each night.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Guardian Wolf role."""
        return RoleConfig(
            name="Guardian Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Guardian Wolf. You wake up with other werewolves to kill villagers. "
                "Additionally, you can choose to protect one werewolf each night. "
                "The protected werewolf cannot be eliminated that night."
            ),
            priority=ActionPriority.GUARD,
            can_act_night=True,
            can_act_day=False,
        )


class HiddenWolf(Role):
    """Hidden Wolf role.

    A werewolf who appears as a villager when checked by the Seer.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Hidden Wolf role."""
        return RoleConfig(
            name="Hidden Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Hidden Wolf. You wake up with other werewolves to kill villagers. "
                "Your special ability is that you appear as a villager when checked by the Seer. "
                "This makes you much harder to detect."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )


class BloodMoonApostle(Role):
    """Blood Moon Apostle role.

    A werewolf supporter who doesn't wake up with other wolves but wins with them.
    Once per game, can turn into a real werewolf.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Blood Moon Apostle role."""
        return RoleConfig(
            name="Blood Moon Apostle",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Blood Moon Apostle. You support the werewolves but don't wake up "
                "with them initially. Once per game, if all werewolves are dead, you transform "
                "into a werewolf and can start killing. You appear as a villager to the Seer "
                "until transformed."
            ),
            priority=None,  # No night action until transformed
            can_act_night=False,
            can_act_day=False,
            max_uses=1,  # Can only transform once
        )


class NightmareWolf(Role):
    """Nightmare Wolf role.

    A werewolf who can block a player from using their ability for one night.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the Nightmare Wolf role."""
        return RoleConfig(
            name="Nightmare Wolf",
            camp=Camp.WEREWOLF,
            description=(
                "You are the Nightmare Wolf. You wake up with other werewolves to kill villagers. "
                "Additionally, you can choose one player each night to block their ability. "
                "That player cannot use their role ability that night."
            ),
            priority=ActionPriority.WEREWOLF,
            can_act_night=True,
            can_act_day=False,
        )
