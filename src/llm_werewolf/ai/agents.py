"""Unified agent system for LLM Werewolf game.

This module contains all agent implementations and player configuration logic.
Simplified design with minimal abstractions.
"""

import os
import random
from typing import Any
from pathlib import Path

import yaml
from pydantic import Field, BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

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
# Base Agent Interface
# ============================================================================


class BaseAgent:
    """Base class for all AI agents.

    Simplified interface - agents just need to respond to messages.
    """

    def __init__(self, model_name: str = "unknown") -> None:
        """Initialize the agent.

        Args:
            model_name: Name of the AI model (e.g., "gpt-4", "human", "demo").
        """
        self.model_name = model_name
        self.conversation_history: list[dict[str, str]] = []

    def get_response(self, message: str) -> str:
        """Get a response from the AI agent.

        Args:
            message: The input message/prompt for the AI.

        Returns:
            str: The AI's response.
        """
        raise NotImplementedError

    def initialize(self) -> None:
        """Initialize the agent (optional setup before game starts)."""
        pass

    def reset(self) -> None:
        """Reset the agent's state for a new game."""
        self.conversation_history.clear()

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to the conversation history.

        Args:
            role: The role of the message sender (e.g., "user", "assistant").
            content: The message content.
        """
        self.conversation_history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        """Get the conversation history.

        Returns:
            list[dict[str, str]]: A copy of the conversation history.
        """
        return self.conversation_history.copy()

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(model={self.model_name})"


# ============================================================================
# Agent Implementations
# ============================================================================


class DemoAgent(BaseAgent):
    """Simple demo agent that uses random responses.

    For testing and demonstration purposes only.
    """

    def __init__(self) -> None:
        """Initialize the demo agent."""
        super().__init__(model_name="demo-random")

    def get_response(self, message: str) -> str:
        """Get a random demo response.

        Args:
            message: The input message (ignored).

        Returns:
            str: A random response.
        """
        responses = [
            "I agree.",
            "I'm not sure about that.",
            "Let me think about it.",
            "That's interesting.",
            "I have my suspicions.",
        ]
        return random.choice(responses)  # noqa: S311


class HumanAgent(BaseAgent):
    """Agent for human players (console input)."""

    def __init__(self) -> None:
        """Initialize the human agent."""
        super().__init__(model_name="human")
        from rich.console import Console

        self.console = Console()

    def get_response(self, message: str) -> str:
        """Get response from human input.

        Args:
            message: The prompt message.

        Returns:
            str: Human's response.
        """
        self.console.print(f"\n{message}")
        return input("Your response: ")


class LLMAgent(BaseAgent):
    """Unified agent for all LLM providers using OpenAI ChatCompletion API.

    Supports OpenAI, Anthropic, xAI, local models, and any ChatCompletion-compatible API.
    """

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> None:
        """Initialize the LLM agent.

        Args:
            model_name: Name of the model to use (e.g., "gpt-4", "claude-3-5-sonnet").
            api_key: API key for the provider. Can be None for local models.
            base_url: Base URL for the API endpoint.
            temperature: Temperature for response generation (0.0-2.0).
            max_tokens: Maximum tokens in response.
        """
        super().__init__(model_name=model_name)
        self.api_key = api_key or "not-needed"
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client: Any = None

    def initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError as e:
            msg = "openai package not installed. Install with: uv sync --group llm-openai"
            raise ImportError(msg) from e

    def get_response(self, message: str) -> str:
        """Get response from the LLM using ChatCompletion API.

        Args:
            message: The input message/prompt.

        Returns:
            str: The AI's response.
        """
        if self.client is None:
            self.initialize()

        # Add message to history
        self.conversation_history.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            assistant_message = response.choices[0].message.content or ""
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            return f"LLM API error: {e}"


# ============================================================================
# Factory Functions
# ============================================================================


def create_agent(config: PlayerConfig) -> BaseAgent:
    """Create an agent instance from player configuration.

    Args:
        config: Player configuration.

    Returns:
        BaseAgent: Created agent instance.

    Raises:
        ValueError: If configuration is invalid or API key is missing.
    """
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
