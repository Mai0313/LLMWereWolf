from typing import TYPE_CHECKING

from pydantic import Field, BaseModel, field_validator

if TYPE_CHECKING:
    from llm_werewolf.core.roles.base import Role


class GameConfig(BaseModel):
    num_players: int = Field(
        ..., ge=6, le=20, description="Number of players in the game", examples=[6, 9, 12]
    )
    role_names: list[str] = Field(
        ...,
        description="List of role names to use in the game",
        examples=[["Werewolf", "Seer", "Witch", "Hunter", "Guard", "Villager"]],
    )

    night_timeout: int = Field(
        default=60,
        ge=10,
        description="Timeout for night actions in seconds",
        examples=[30, 60, 90],
    )
    day_timeout: int = Field(
        default=300,
        ge=30,
        description="Timeout for day discussion in seconds",
        examples=[120, 300, 600],
    )
    vote_timeout: int = Field(
        default=60, ge=10, description="Timeout for voting in seconds", examples=[30, 60, 90]
    )

    allow_revote: bool = Field(
        default=False, description="Allow players to change their vote", examples=[True, False]
    )
    show_role_on_death: bool = Field(
        default=True, description="Reveal player's role when they die", examples=[True, False]
    )
    enable_sheriff: bool = Field(
        default=False,
        description="Enable sheriff election (future feature)",
        examples=[True, False],
    )

    @field_validator("role_names")
    @classmethod
    def validate_role_count(cls, v: list[str], info: object) -> list[str]:
        """Validate that the number of roles matches the number of players.

        Args:
            v: The role names list.
            info: Validation info containing other fields.

        Returns:
            list[str]: The validated role names.

        Raises:
            ValueError: If role count doesn't match player count.
        """
        num_players = info.data.get("num_players")
        if num_players and len(v) != num_players:
            msg = f"Number of roles ({len(v)}) must match number of players ({num_players})"
            raise ValueError(msg)
        return v

    @field_validator("role_names")
    @classmethod
    def validate_minimum_werewolves(cls, v: list[str]) -> list[str]:
        """Validate that there is at least one werewolf.

        Args:
            v: The role names list.

        Returns:
            list[str]: The validated role names.

        Raises:
            ValueError: If no werewolves are present.
        """
        werewolf_roles = {
            "Werewolf",
            "AlphaWolf",
            "WhiteWolf",
            "WolfBeauty",
            "GuardianWolf",
            "HiddenWolf",
            "NightmareWolf",
            "BloodMoonApostle",
        }

        werewolf_count = sum(1 for role in v if role in werewolf_roles)

        if werewolf_count == 0:
            msg = "At least one werewolf role is required"
            raise ValueError(msg)

        return v

    def to_role_list(self) -> list["Role"]:
        """Convert role names to Role instances.

        Returns:
            list[Role]: List of role instances.

        Raises:
            ValueError: If a role name is not recognized.
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

        role_map: dict[str, type[Role]] = {
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

        roles = []
        for role_name in self.role_names:
            if role_name not in role_map:
                msg = f"Unknown role: {role_name}"
                raise ValueError(msg)
            roles.append(role_map[role_name])

        return roles
