from pathlib import Path

import logfire
from rich.console import Console

from llm_werewolf.ui import run_tui
from llm_werewolf.core import GameEngine
from llm_werewolf.config import load_config, get_preset_by_name, create_agent_from_player_config

console = Console()


def main(config: str, debug: bool = False) -> None:
    """Run Werewolf game with TUI interface.

    Args:
        config: Path to the YAML configuration file
        debug: Show debug panel (default: False)
    """
    logfire.configure()
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
        (f"player_{idx + 1}", player_cfg.name, create_agent_from_player_config(player_cfg))
        for idx, player_cfg in enumerate(players_config.players)
    ]

    engine = GameEngine(game_config)
    engine.setup_game(players, game_config.to_role_list())
    logfire.info(
        "tui_started", config_path=str(config_path), preset=players_config.preset, show_debug=debug
    )

    console.print(f"[green]已載入設定檔: {config_path.resolve()}[/green]")
    console.print(f"[cyan]Preset: {players_config.preset}[/cyan]")
    console.print("[cyan]介面模式: TUI[/cyan]")
    console.print(
        "\n[yellow]提示: 按 'n' 鍵進行下一步，按 'd' 切換除錯面板，按 'q' 退出[/yellow]\n"
    )

    try:
        # Use show_debug from command line flag, or fall back to config
        show_debug = debug or players_config.show_debug
        run_tui(engine, show_debug)
    except KeyboardInterrupt:
        console.print("\n遊戲已由使用者中止。")
    except Exception as exc:
        logfire.error(
            "tui_execution_error",
            error=str(exc),
            config_path=str(config_path),
            preset=players_config.preset,
        )
        console.print(f"[red]執行遊戲時發生錯誤: {exc}[/red]")
        raise


if __name__ == "__main__":
    import fire

    fire.Fire(main)
