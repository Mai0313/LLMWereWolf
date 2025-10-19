import os
import random
from pathlib import Path
from functools import cached_property

import yaml
from openai import OpenAI
from pydantic import Field, BaseModel, ConfigDict, computed_field, field_validator
from rich.console import Console
from pydantic_core.core_schema import ValidationInfo

console = Console()

# ============================================================================
# Player Configuration Models
# ============================================================================


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
        """Validate that base_url is provided for LLM models."""
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
    show_debug: bool = Field(default=False, description="Show the debug panel in TUI mode")

    @field_validator("players")
    @classmethod
    def validate_player_names_unique(cls, v: list[PlayerConfig]) -> list[PlayerConfig]:
        """Validate that all player names are unique."""
        names = [p.name for p in v]
        if len(names) != len(set(names)):
            duplicates = {name for name in names if names.count(name) > 1}
            msg = f"Duplicate player names found: {duplicates}"
            raise ValueError(msg)
        return v


# ============================================================================
# Agent Implementations
# ============================================================================


class DemoAgent(BaseModel):
    model_name: str = Field(default="demo")

    def get_response(self, message: str) -> str:
        """Return a canned response."""
        responses = [
            "I agree.",
            "I'm not sure about that.",
            "Let me think about it.",
            "That's interesting.",
            "I have my suspicions.",
        ]
        return random.choice(responses)  # noqa: S311

    def __repr__(self) -> str:
        """Return a string representation of the LLMAgent instance.

        Returns:
            str: A string in the format "DemoAgent(model={self.model_name})".
        """
        return f"DemoAgent(model={self.model_name})"


class HumanAgent(BaseModel):
    model_name: str = Field(default="human")

    def get_response(self, message: str) -> str:
        """Get response from human input.

        Args:
            message: The prompt message.

        Returns:
            str: Human's response.
        """
        console.print(f"\n{message}")
        return input("Your response: ")

    def __repr__(self) -> str:
        """Return a string representation of the LLMAgent instance.

        Returns:
            str: A string in the format "HumanAgent(model={self.model_name})".
        """
        return f"HumanAgent(model={self.model_name})"


class LLMAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_name: str
    api_key: str = Field(default="not-needed")
    base_url: str | None = Field(default=None)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=500)
    chat_history: list[dict[str, str]] = Field(default=[])

    @computed_field
    @cached_property
    def client(self) -> OpenAI:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return client

    def get_response(self, message: str) -> str:
        self.chat_history.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.chat_history,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        self.chat_history.append({
            "role": "assistant",
            "content": response.choices[0].message.content,
        })

        return response.choices[0].message.content

    def reset(self) -> None:
        self.chat_history.clear()
        self.client = None

    def add_to_history(self, role: str, content: str) -> None:
        self.chat_history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        return self.chat_history.copy()

    def __repr__(self) -> str:
        """Return a string representation of the LLMAgent instance.

        Returns:
            str: A string in the format "LLMAgent(model=<model_name>)".
        """
        return f"LLMAgent(model={self.model_name})"


# ============================================================================
# Factory Functions
# ============================================================================


def create_agent(config: PlayerConfig) -> LLMAgent | DemoAgent | HumanAgent:
    """Create an agent instance from player configuration.

    Args:
        config: Player configuration.

    Returns:
        LLMAgent | DemoAgent | HumanAgent: Created agent instance.

    Raises:
        ValueError: If configuration is invalid or API key is missing.
    """
    model = config.model.lower()

    if model == "human":
        return HumanAgent(model_name="human")

    if model == "demo":
        return DemoAgent(model_name="demo")

    # For LLM models
    api_key = None
    if config.api_key_env:
        api_key = os.getenv(config.api_key_env)
    if not api_key:
        raise ValueError(
            f"API key not found in environment variable '{config.api_key_env}' for player '{config.name}'"
        )

    return LLMAgent(
        model_name=config.model,
        api_key=api_key,
        base_url=config.base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def load_config(config_path: str | Path) -> PlayersConfig:
    config_path = Path(config_path) if isinstance(config_path, str) else config_path
    data = yaml.safe_load(config_path.read_text())
    return PlayersConfig(**data)
