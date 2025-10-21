from pathlib import Path

import logfire
from rich.console import Console

from llm_werewolf.core import GameEngine
from llm_werewolf.ai.agents import load_config, create_agent
from llm_werewolf.core.config import get_preset_by_name
from llm_werewolf.core.locale import Locale
from llm_werewolf.core.role_registry import create_roles

console = Console()


def main(config: str) -> None:
    """Run Werewolf game in console mode (auto-play).

    Args:
        config: Path to the YAML configuration file
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

    # Initialize locale and game engine with language support
    locale = Locale(players_config.language)
    engine = GameEngine(game_config, language=players_config.language)
    engine.setup_game(players=players, roles=roles)
    logfire.info("game_created", config_path=str(config_path), preset=players_config.preset)

    console.print(
        f"[green]{locale.get('config_loaded', config_path=config_path.resolve())}[/green]"
    )
    console.print(f"[cyan]{locale.get('preset_info', preset=players_config.preset)}[/cyan]")
    console.print(f"[cyan]{locale.get('interface_mode')}[/cyan]")

    try:
        result = engine.play_game()
        console.print(f"\n{result}")

        if engine.game_state:
            alive = engine.game_state.get_alive_players()
            dead = engine.game_state.get_dead_players()

            console.print(locale.get("alive_players"))
            for player in alive:
                console.print(
                    locale.get("player_role_info", name=player.name, role=player.get_role_name())
                )

            console.print(locale.get("dead_players"))
            for player in dead:
                console.print(
                    locale.get("player_role_info", name=player.name, role=player.get_role_name())
                )

    except KeyboardInterrupt:
        # Use locale for interruption message
        if players_config.language == "zh-TW":
            console.print("\n遊戲已由使用者中止。")
        elif players_config.language == "zh-CN":
            console.print("\n游戏已由用户中止。")
        else:
            console.print("\nGame interrupted by user.")
    except Exception as exc:
        logfire.error(
            "game_execution_error",
            error=str(exc),
            config_path=str(config_path),
            preset=players_config.preset,
        )
        # Use locale for error message
        if players_config.language == "zh-TW":
            console.print(f"[red]執行遊戲時發生錯誤: {exc}[/red]")
        elif players_config.language == "zh-CN":
            console.print(f"[red]执行游戏时发生错误: {exc}[/red]")
        else:
            console.print(f"[red]Error executing game: {exc}[/red]")
        raise


if __name__ == "__main__":
    import fire

    fire.Fire(main)
