"""Role registry for managing role types and creation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_werewolf.core.roles.base import Role


def get_role_map() -> dict[str, type["Role"]]:
    """Get the mapping of role names to role classes.

    Returns:
        dict[str, type[Role]]: Mapping of role name strings to Role classes.
    """
    from llm_werewolf.core.roles import (
        Seer,
        Cupid,
        Elder,
        Guard,
        Idiot,
        Lover,
        Raven,
        Thief,
        Witch,
        Hunter,
        Knight,
        Magician,
        Villager,
        Werewolf,
        AlphaWolf,
        WhiteWolf,
        HiddenWolf,
        WolfBeauty,
        GuardianWolf,
        NightmareWolf,
        GraveyardKeeper,
        BloodMoonApostle,
    )

    return {
        # Werewolf roles
        "Werewolf": Werewolf,
        "AlphaWolf": AlphaWolf,
        "WhiteWolf": WhiteWolf,
        "WolfBeauty": WolfBeauty,
        "GuardianWolf": GuardianWolf,
        "HiddenWolf": HiddenWolf,
        "BloodMoonApostle": BloodMoonApostle,
        "NightmareWolf": NightmareWolf,
        # Villager roles
        "Villager": Villager,
        "Seer": Seer,
        "Witch": Witch,
        "Hunter": Hunter,
        "Guard": Guard,
        "Idiot": Idiot,
        "Elder": Elder,
        "Knight": Knight,
        "Magician": Magician,
        "Cupid": Cupid,
        "Raven": Raven,
        "GraveyardKeeper": GraveyardKeeper,
        # Neutral roles
        "Thief": Thief,
        "Lover": Lover,
    }


def get_werewolf_roles() -> set[str]:
    """Get the set of role names that are werewolf roles.

    Returns:
        set[str]: Set of werewolf role names.
    """
    return {
        "Werewolf",
        "AlphaWolf",
        "WhiteWolf",
        "WolfBeauty",
        "GuardianWolf",
        "HiddenWolf",
        "NightmareWolf",
        "BloodMoonApostle",
    }


def validate_role_names(role_names: list[str]) -> None:
    """Validate that all role names are recognized and at least one werewolf exists.

    Args:
        role_names: List of role names to validate.

    Raises:
        ValueError: If a role name is not recognized or no werewolves are present.
    """
    role_map = get_role_map()
    werewolf_roles = get_werewolf_roles()

    # Check all roles are valid
    for role_name in role_names:
        if role_name not in role_map:
            msg = f"Unknown role: {role_name}"
            raise ValueError(msg)

    # Check for at least one werewolf
    werewolf_count = sum(1 for role in role_names if role in werewolf_roles)
    if werewolf_count == 0:
        msg = "At least one werewolf role is required"
        raise ValueError(msg)


def create_roles(role_names: list[str]) -> list[type["Role"]]:
    """Create Role classes list from role names.

    Args:
        role_names: List of role names.

    Returns:
        list[type[Role]]: List of Role classes (not instances).

    Raises:
        ValueError: If a role name is not recognized.
    """
    role_map = get_role_map()
    roles = []

    for role_name in role_names:
        if role_name not in role_map:
            msg = f"Unknown role: {role_name}"
            raise ValueError(msg)
        roles.append(role_map[role_name])

    return roles
