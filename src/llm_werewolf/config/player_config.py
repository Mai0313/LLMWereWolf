"""Player configuration for YAML-based game setup."""

import os
from typing import TYPE_CHECKING
from pathlib import Path

import yaml
from pydantic import Field, BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

if TYPE_CHECKING:
    from llm_werewolf.ai import BaseAgent


class PlayerConfig(BaseModel):
    """Configuration for a single player in the game.

    This model defines how each player should be configured, including
    which AI model/provider to use, or if it's a human player.
    """

    name: str = Field(..., description="Display name for the player")
    provider: str = Field(
        ..., description="Provider type: openai, anthropic, local, human, demo, or custom"
    )
    model: str | None = Field(default=None, description="Model name (e.g., gpt-4, claude-3)")
    base_url: str | None = Field(default=None, description="API base URL")
    api_key_env: str | None = Field(
        default=None,
        description="Environment variable name containing the API key (e.g., OPENAI_API_KEY)",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=500, gt=0, description="Maximum response tokens")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate that provider is supported.

        Args:
            v: Provider name.

        Returns:
            str: Validated provider name in lowercase.

        Raises:
            ValueError: If provider is not supported.
        """
        allowed = {"openai", "anthropic", "local", "human", "demo", "custom"}
        v_lower = v.lower()
        if v_lower not in allowed:
            msg = f"Provider must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return v_lower

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Validate that model is provided for LLM providers.

        Args:
            v: Model name.
            info: Validation context.

        Returns:
            str | None: Validated model name.

        Raises:
            ValueError: If model is required but not provided.
        """
        provider = info.data.get("provider", "").lower()
        if provider in {"openai", "anthropic", "local", "custom"} and not v:
            msg = f"Model name is required for provider '{provider}'"
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
    # Import here to avoid circular imports
    from llm_werewolf.ai import DemoAgent, HumanAgent, OpenAIAgent, AnthropicAgent, GenericLLMAgent

    provider = config.provider.lower()

    # Handle special providers
    if provider == "demo":
        return DemoAgent()

    if provider == "human":
        return HumanAgent()

    # For LLM providers, get API key from environment if specified
    api_key = None
    if config.api_key_env:
        api_key = os.getenv(config.api_key_env)
        if not api_key and provider != "local":
            msg = (
                f"API key not found in environment variable '{config.api_key_env}' "
                f"for player '{config.name}'"
            )
            raise ValueError(msg)

    # Create appropriate agent type
    if provider == "openai":
        return OpenAIAgent(
            model_name=config.model or "gpt-4",
            api_key=api_key,
            base_url=config.base_url,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    if provider == "anthropic":
        return AnthropicAgent(
            model_name=config.model or "claude-3-5-sonnet-20241022",
            api_key=api_key,
            base_url=config.base_url,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    # For local and custom providers, use GenericLLMAgent
    if provider in {"local", "custom"}:
        return GenericLLMAgent(
            model_name=config.model or "unknown",
            api_key=api_key,
            base_url=config.base_url or "http://localhost:11434/v1",
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    msg = f"Unsupported provider: {provider}"
    raise ValueError(msg)


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
