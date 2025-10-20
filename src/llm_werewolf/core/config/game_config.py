"""Core game configuration."""

from pydantic import Field, BaseModel, field_validator


class GameConfig(BaseModel):
    """Game configuration including player count, roles, and timing settings."""

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
    def validate_roles(cls, v: list[str]) -> list[str]:
        """Validate role names using the role registry.

        Args:
            v: The role names list.

        Returns:
            list[str]: The validated role names.

        Raises:
            ValueError: If roles are invalid or no werewolves present.
        """
        from llm_werewolf.core.role_registry import validate_role_names

        validate_role_names(v)
        return v
