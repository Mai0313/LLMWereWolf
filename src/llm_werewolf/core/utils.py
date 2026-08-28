from pathlib import Path

import yaml

from llm_werewolf.core.config import PlayersConfig


def load_config(config_path: str | Path) -> PlayersConfig:
    config_path = Path(config_path) if isinstance(config_path, str) else config_path
    data = yaml.safe_load(config_path.read_text())
    return PlayersConfig(**data)
