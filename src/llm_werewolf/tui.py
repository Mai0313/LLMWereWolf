from pathlib import Path

import logfire

from llm_werewolf.ui import run_tui
from llm_werewolf.core import GameEngine
from llm_werewolf.core.agent import create_agent
from llm_werewolf.core.utils import load_config
from llm_werewolf.core.config import create_game_config_from_player_count
from llm_werewolf.core.role_registry import create_roles


def main(config: str) -> None:
    """Run Werewolf game with TUI interface.

    Args:
        config: Path to the YAML configuration file
    """
    config_path = Path(config)
    players_config = load_config(config_path=config_path)

    # Automatically generate game config based on player count
    num_players = len(players_config.players)
    game_config = create_game_config_from_player_count(num_players)

    players = [
        create_agent(player_cfg, language=players_config.language)
        for player_cfg in players_config.players
    ]
    roles = create_roles(role_names=game_config.role_names)

    engine = GameEngine(game_config, language=players_config.language)
    engine.setup_game(players=players, roles=roles)
    logfire.info("tui_started", config_path=str(config_path), num_players=num_players)

    try:
        run_tui(engine)
    except KeyboardInterrupt:
        logfire.info("tui_aborted_by_user", config_path=str(config_path), num_players=num_players)
    except Exception as exc:
        logfire.error(
            "tui_execution_error",
            error=str(exc),
            config_path=str(config_path),
            num_players=num_players,
        )
        raise


def entry() -> None:
    """Entry point for the werewolf TUI command."""
    import fire

    fire.Fire(main)


if __name__ == "__main__":
    entry()
