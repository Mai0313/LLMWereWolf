import dotenv
from pydantic import Field, BaseModel, field_validator
from openai.types.shared import ReasoningEffort
from pydantic_core.core_schema import ValidationInfo

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
