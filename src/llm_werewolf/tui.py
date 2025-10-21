from pathlib import Path

import logfire

from llm_werewolf.ui import run_tui
from llm_werewolf.core import GameEngine
from llm_werewolf.ai.agents import load_config, create_agent
from llm_werewolf.core.config import get_preset_by_name
from llm_werewolf.core.role_registry import create_roles


def main(config: str, debug: bool = False) -> None:
    """Run Werewolf game with TUI interface.

    Args:
        config: Path to the YAML configuration file
        debug: Show debug panel (default: False)
    """
    config_path = Path(config)
    players_config = load_config(config_path=config_path)

    game_config = get_preset_by_name(players_config.preset)
    if len(players_config.players) != game_config.num_players:
        logfire.error(
            "player_count_mismatch",
            configured_players=len(players_config.players),
            required_players=game_config.num_players,
            preset=players_config.preset,
        )
        raise ValueError

    players = [
        create_agent(player_cfg, language=players_config.language)
        for player_cfg in players_config.players
    ]
    roles = create_roles(role_names=game_config.role_names)

    engine = GameEngine(game_config)
    engine.setup_game(players=players, roles=roles)
    logfire.info(
        "tui_started", config_path=str(config_path), preset=players_config.preset, show_debug=debug
    )

    try:
        show_debug = debug or players_config.show_debug
        run_tui(engine, show_debug)
    except KeyboardInterrupt:
        logfire.info(
            "tui_aborted_by_user", config_path=str(config_path), preset=players_config.preset
        )
    except Exception as exc:
        logfire.error(
            "tui_execution_error",
            error=str(exc),
            config_path=str(config_path),
            preset=players_config.preset,
        )
        raise


if __name__ == "__main__":
    import fire

    fire.Fire(main)
