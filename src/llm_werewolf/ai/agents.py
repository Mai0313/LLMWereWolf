import os
from pathlib import Path

import yaml
import dotenv

from llm_werewolf.core.agent import LLMAgent, DemoAgent, HumanAgent
from llm_werewolf.core.config import PlayerConfig, PlayersConfig

dotenv.load_dotenv()


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
