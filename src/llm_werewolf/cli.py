import logging
import sys
from pathlib import Path
from typing import Final

import fire
from rich.console import Console

from llm_werewolf.config import (
    create_agent_from_player_config,
    get_preset_by_name,
    list_preset_names,
    load_players_config,
)
from llm_werewolf.core import GameEngine
from llm_werewolf.utils import log_error, log_game_event, setup_logger

console = Console()

DEFAULT_CONFIG_PATH: Final = Path(__file__).resolve().parents[2] / "configs" / "demo.yaml"
VALID_LOG_LEVELS: Final = {"DEBUG", "INFO", "WARNING", "ERROR"}


def main(
    config: str | None = None,
    preset: str | None = None,
    log_file: str | None = None,
    log_level: str = "INFO",
) -> None:
    """依據 YAML 設定載入遊戲、建立代理並啟動 Werewolf 遊戲。"""

    config_path = Path(config) if config else DEFAULT_CONFIG_PATH

    try:
        players_config = load_players_config(config_path)
    except (FileNotFoundError, ValueError) as exc:
        log_error(exc, "Failed to load player configuration")
        console.print(f"[red]配置讀取失敗：{exc}[/red]")
        sys.exit(1)

    preset_name = preset or players_config.preset or "9-players"
    available_presets = list_preset_names()
    if preset_name not in available_presets:
        console.print(
            f"[red]無效的 preset '{preset_name}'，可用選項：{available_presets}[/red]"
        )
        sys.exit(1)

    log_level_name = log_level.upper()
    if log_level_name not in VALID_LOG_LEVELS:
        console.print(
            f"[red]無效的 log level '{log_level}'。可選：{sorted(VALID_LOG_LEVELS)}[/red]"
        )
        sys.exit(1)

    setup_logger(level=getattr(logging, log_level_name), log_file=log_file)

    game_config = get_preset_by_name(preset_name)
    if len(players_config.players) != game_config.num_players:
        console.print(
            "[red]玩家數量與 preset 要求不符："
            f"設定檔 {len(players_config.players)} 位，preset '{preset_name}' 需要 {game_config.num_players} 位。[/red]"
        )
        sys.exit(1)

    try:
        players = [
            (
                f"player_{idx + 1}",
                player_cfg.name,
                create_agent_from_player_config(player_cfg),
            )
            for idx, player_cfg in enumerate(players_config.players)
        ]
    except Exception as exc:
        log_error(exc, "Failed to create agents from configuration")
        console.print(f"[red]建立玩家代理時發生錯誤：{exc}[/red]")
        sys.exit(1)

    engine = GameEngine(game_config)
    engine.setup_game(players, game_config.to_role_list())
    log_game_event(
        "game_created",
        (
            f"Game created from '{config_path}' with preset '{preset_name}' "
            f"and mode '{players_config.game_type}'"
        ),
    )

    console.print(f"[green]已載入設定檔：{config_path.resolve()}[/green]")
    console.print(f"[cyan]Preset：{preset_name}[/cyan]")
    console.print(f"[cyan]介面模式：{players_config.game_type}[/cyan]")

    try:
        if players_config.game_type == "tui":
            try:
                from llm_werewolf.ui import run_tui
            except ImportError as exc:
                console.print(f"[red]TUI 依賴尚未安裝：{exc}[/red]")
                console.print("請執行： [cyan]uv sync[/cyan]")
                sys.exit(1)

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
    except Exception as exc:  # noqa: BLE001
        log_error(exc, "Error during game execution")
        console.print(f"[red]執行遊戲時發生錯誤：{exc}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    fire.Fire(main)
