import sys
import logging
from pathlib import Path

import fire
import logfire
from rich.console import Console

from llm_werewolf.ui import run_tui
from llm_werewolf.core import GameEngine
from llm_werewolf.utils import log_error, setup_logger, log_game_event
from llm_werewolf.config import load_config, get_preset_by_name, create_agent_from_player_config

console = Console()


def main(config: str) -> None:
    config_path = Path(config)
    players_config = load_config(config_path=config_path)

    setup_logger(
        level=getattr(logging, players_config.log_level), log_file=players_config.log_file
    )

    game_config = get_preset_by_name(players_config.preset)
    if len(players_config.players) != game_config.num_players:
        logfire.error(
            "player_count_mismatch",
            f"Configured {len(players_config.players)} players, but preset '{players_config.preset}' requires {game_config.num_players}.",
        )
        raise ValueError

    players = [
        (f"player_{idx + 1}", player_cfg.name, create_agent_from_player_config(player_cfg))
        for idx, player_cfg in enumerate(players_config.players)
    ]

    engine = GameEngine(game_config)
    engine.setup_game(players, game_config.to_role_list())
    log_game_event(
        "game_created",
        (
            f"Game created from '{config_path}' with preset '{players_config.preset}' "
            f"and mode '{players_config.game_type}'"
        ),
    )

    console.print(f"[green]已載入設定檔：{config_path.resolve()}[/green]")
    console.print(f"[cyan]Preset：{players_config.preset}[/cyan]")
    console.print(f"[cyan]介面模式：{players_config.game_type}[/cyan]")
    console.print(f"[cyan]Log level：{players_config.log_level}[/cyan]")
    if players_config.log_file:
        console.print(f"[cyan]Log file：{players_config.log_file}[/cyan]")

    try:
        if players_config.game_type == "tui":
            run_tui(engine, players_config.show_debug)
            return

        def _print_event(event) -> None:
            prefix = f"[回合 {event.round_number}][{event.phase.upper()}]"
            console.print(f"{prefix} {event.message}")

        engine.on_event = _print_event
        result = engine.play_game()
        console.print(f"\n{result}")

        if engine.game_state:
            alive = engine.game_state.get_alive_players()
            dead = engine.game_state.get_dead_players()

            console.print("\n存活玩家：")
            for player in alive:
                console.print(f"- {player.name} ({player.get_role_name()})")

            console.print("\n淘汰玩家：")
            for player in dead:
                console.print(f"- {player.name} ({player.get_role_name()})")

    except KeyboardInterrupt:
        console.print("\n遊戲已由使用者中止。")
    except Exception as exc:
        log_error(exc, "Error during game execution")
        console.print(f"[red]執行遊戲時發生錯誤：{exc}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    fire.Fire(main)
