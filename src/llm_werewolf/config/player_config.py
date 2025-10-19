import os
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

if TYPE_CHECKING:
    from llm_werewolf.ai import BaseAgent


class PlayerConfig(BaseModel):
    """Configuration for a single player in the game.

    Agent type is determined by the model field:
    - model="human": Human player via console input
    - model="demo": Random response bot for testing
    - model=<model_name> + base_url: LLM agent with ChatCompletion API
    """

    name: str = Field(..., description="Display name for the player")
    model: str = Field(
        ...,
        description="Model name: 'human', 'demo', or LLM model name (e.g., 'gpt-4', 'claude-3-5-sonnet-20241022')",
    )
    base_url: str | None = Field(
        default=None,
        description="API base URL (required for LLM models, e.g., https://api.openai.com/v1)",
    )
    api_key_env: str | None = Field(
        default=None,
        description="Environment variable name containing the API key (e.g., OPENAI_API_KEY)",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=500, gt=0, description="Maximum response tokens")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Validate that base_url is provided for LLM models.

        Args:
            v: Base URL.
            info: Validation context.

        Returns:
            str | None: Validated base URL.

        Raises:
            ValueError: If base_url is required but not provided.
        """
        model = info.data.get("model", "")
        if model not in {"human", "demo"} and not v:
            msg = f"base_url is required for LLM model '{model}'"
            raise ValueError(msg)
        return v


class PlayersConfig(BaseModel):
    """Root configuration containing all players and optional game settings."""

    players: list[PlayerConfig] = Field(..., min_length=1, description="List of player configs")
    preset: str | None = Field(
        default=None, description="Optional preset name for roles (e.g., '9-players')"
    )

    @field_validator("players")
    @classmethod
    def validate_player_names_unique(cls, v: list[PlayerConfig]) -> list[PlayerConfig]:
        """Validate that all player names are unique.

        Args:
            v: List of player configs.

        Returns:
            list[PlayerConfig]: Validated player configs.

        Raises:
            ValueError: If duplicate player names are found.
        """
        names = [p.name for p in v]
        if len(names) != len(set(names)):
            duplicates = {name for name in names if names.count(name) > 1}
            msg = f"Duplicate player names found: {duplicates}"
            raise ValueError(msg)
        return v


def create_agent_from_player_config(config: PlayerConfig) -> "BaseAgent":
    """Create an agent instance from player configuration.

    Args:
        config: Player configuration.

    Returns:
        BaseAgent: Created agent instance.

    Raises:
        ValueError: If configuration is invalid or API key is missing.
    """
    from llm_werewolf.ai import DemoAgent, HumanAgent, LLMAgent

    model = config.model.lower()

    if model == "human":
        return HumanAgent()

    if model == "demo":
        return DemoAgent()

    # For LLM models
    api_key = None
    if config.api_key_env:
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            msg = (
                f"API key not found in environment variable '{config.api_key_env}' "
                f"for player '{config.name}'"
            )
            raise ValueError(msg)

    return LLMAgent(
        model_name=config.model,
        api_key=api_key,
        base_url=config.base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def load_players_config(yaml_path: str | Path) -> PlayersConfig:
    """Load and validate player configuration from YAML file.

    Args:
        yaml_path: Path to the YAML configuration file.

    Returns:
        PlayersConfig: Validated configuration.

    Raises:
        FileNotFoundError: If YAML file doesn't exist.
        ValueError: If YAML is invalid or validation fails.
    """
    yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        msg = f"Configuration file not found: {yaml_path}"
        raise FileNotFoundError(msg)

    try:
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        msg = f"Invalid YAML format: {e}"
        raise ValueError(msg) from e

    if not isinstance(data, dict):
        msg = "YAML file must contain a dictionary at root level"
        raise ValueError(msg)

    return PlayersConfig(**data)
