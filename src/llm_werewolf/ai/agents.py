import os
from pathlib import Path
from functools import cached_property

import yaml
import dotenv
from openai import OpenAI
from pydantic import Field, BaseModel, ConfigDict, computed_field, field_validator
from openai.types.shared import ReasoningEffort
from pydantic_core.core_schema import ValidationInfo

from llm_werewolf.core.agent import BaseAgent, DemoAgent, HumanAgent

dotenv.load_dotenv()


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
        title="Model Name",
        description="The model name of your player",
        examples=["gpt-5", "human", "demo"],
    )
    base_url: str | None = Field(
        default=None,
        title="API Base URL",
        description="API base URL (required for LLM models).",
        examples=["https://api.openai.com/v1", "https://api.anthropic.com/v1"],
    )
    api_key_env: str | None = Field(
        default=None,
        title="API Key Environment Variable",
        description="Environment variable name containing the API key (e.g., OPENAI_API_KEY)",
        examples=["OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
    )
    reasoning_effort: ReasoningEffort | None = Field(
        default=None, title="Reasoning Effort", description="Reasoning effort level for LLM"
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Validate that base_url is provided for LLM models."""
        model = info.data.get("model", "")
        if model not in {"human", "demo"} and not v:
            msg = f"base_url is required for LLM model '{model}'"
            raise ValueError(msg)
        return v


class LLMAgent(BaseAgent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: str
    base_url: str
    reasoning_effort: ReasoningEffort | None = Field(default=None)
    language: str = Field(...)
    chat_history: list[dict[str, str]] = Field(default=[])
    decision_history: list[str] = Field(default=[])

    @computed_field
    @cached_property
    def client(self) -> OpenAI:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return client

    def get_response(self, message: str) -> str:
        """Get a response from the LLM.

        Args:
            message: The prompt message.

        Returns:
            str: The complete response from the LLM.
        """
        message += f"\nPlease respond in {self.language}."
        self.chat_history.append({"role": "user", "content": message})

        if self.reasoning_effort:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                reasoning_effort=self.reasoning_effort,
                stream=False,
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model, messages=self.chat_history, stream=False
            )

        full_response = response.choices[0].message.content or ""
        self.chat_history.append({"role": "assistant", "content": full_response})
        return full_response

    def add_decision(self, decision: str) -> None:
        """Add a decision to the decision history.

        This records WHAT the agent decided without sensitive context.

        Args:
            decision: A safe summary of the decision (e.g., "Round 1: Checked Bob, result: villager")
        """
        self.decision_history.append(decision)

    def get_decision_context(self) -> str:
        """Get a formatted string of decision history for context.

        Returns:
            str: Formatted decision history without sensitive information.
        """
        if not self.decision_history:
            return ""
        return "\n\nYour previous actions:\n" + "\n".join(f"- {d}" for d in self.decision_history)


class PlayersConfig(BaseModel):
    """Root configuration containing all players and optional game settings."""

    language: str = Field(
        default="en-US",
        title="Language",
        description="Language code for the game.",
        examples=["en-US", "zh-TW"],
    )
    players: list[PlayerConfig] = Field(
        ...,
        title="Player List",
        description="List of player configs, you should define it under ./configs/<name>.yaml",
        min_length=6,
        max_length=20,
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


def create_agent(
    config: PlayerConfig, language: str = "en-US"
) -> DemoAgent | HumanAgent | LLMAgent:
    """Create an agent instance from player configuration.

    Args:
        config: Player configuration.
        language: Language code for the agent (e.g., "en-US", "zh-TW").

    Returns:
        DemoAgent | HumanAgent | LLMAgent: Created agent instance.

    Raises:
        ValueError: If configuration is invalid or API key is missing.
    """
    model = config.model.lower()

    if model == "human":
        return HumanAgent(name=config.name, model="human")

    if model == "demo":
        return DemoAgent(name=config.name, model="demo")

    api_key = None
    if config.api_key_env:
        api_key = os.getenv(config.api_key_env)
    if not api_key:
        raise ValueError(
            f"API key not found in environment variable '{config.api_key_env}' for player '{config.name}'"
        )

    return LLMAgent(
        name=config.name,
        model=config.model,
        api_key=api_key,
        base_url=config.base_url,
        language=language,
    )


def load_config(config_path: str | Path) -> PlayersConfig:
    config_path = Path(config_path) if isinstance(config_path, str) else config_path
    data = yaml.safe_load(config_path.read_text())
    return PlayersConfig(**data)
