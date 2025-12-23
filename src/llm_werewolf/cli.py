from pathlib import Path

import fire
import logfire
from rich.console import Console

from llm_werewolf.core import GameEngine
from llm_werewolf.core.agent import create_agent
from llm_werewolf.core.utils import load_config
from llm_werewolf.core.config import create_game_config_from_player_count
from llm_werewolf.core.locale import Locale
from llm_werewolf.core.role_registry import create_roles
from llm_werewolf.ui.console_presenter import ConsolePresenter

# 🆕 Personality System Integration
from llm_werewolf.core.personality_integration_manager import PersonalityManager

console = Console()


def main(config: str) -> None:
    """Run Werewolf game in console mode (auto-play).

    Args:
        config: Path to the YAML configuration file
    """
    config_path = Path(config)
    players_config = load_config(config_path=config_path)

    # Check if personality system is enabled
    enable_personality_system = getattr(players_config, 'enable_personality_system', False)

    # Automatically generate game config based on player count
    num_players = len(players_config.players)
    game_config = create_game_config_from_player_count(num_players)

    # 🆕 Create players with personality system support
    players = []
    for i, player_cfg in enumerate(players_config.players):
        # Create base agent
        base_agent = create_agent(player_cfg, language=players_config.language)

        # Check if personality system is enabled for this player
        if (enable_personality_system and
            getattr(player_cfg, 'enable_personality_system', False)):

            # Get personality adapter and create enhanced agent
            personality_adapter = PersonalityManager.get_personality_adapter()
            if personality_adapter:
                enhanced_agent = personality_adapter.create_enhanced_agent(
                    player_id=i + 1,
                    base_agent=base_agent,
                    personality_profile_name=getattr(player_cfg, 'personality_profile', None)
                )
                players.append(enhanced_agent)
            else:
                players.append(base_agent)
        else:
            players.append(base_agent)

    roles = create_roles(role_names=game_config.role_names)

    # Initialize locale and game engine with language support and personality system
    locale = Locale(players_config.language)
    engine = GameEngine(
        game_config,
        language=players_config.language,
        enable_personality_system=enable_personality_system
    )

    # Set up beautified console presenter
    presenter = ConsolePresenter(locale)
    engine.on_event = presenter.present_event

    engine.setup_game(players=players, roles=roles)
    logfire.info("game_created", config_path=str(config_path), num_players=num_players)

    # 🆕 Log personality system status
    if enable_personality_system:
        console.print(f"[green]Personality system enabled with {len([p for p in players_config.players if getattr(p, 'enable_personality_system', False)])} players[/green]")

    console.print(
        f"[green]{locale.get('config_loaded', config_path=config_path.resolve())}[/green]"
    )
    console.print(f"[cyan]{locale.get('player_count_info', num_players=num_players)}[/cyan]")
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
            num_players=num_players,
        )
        # Use locale for error message
        if players_config.language == "zh-TW":
            console.print(f"[red]執行遊戲時發生錯誤: {exc}[/red]")
        elif players_config.language == "zh-CN":
            console.print(f"[red]执行游戏时发生错误: {exc}[/red]")
        else:
            console.print(f"[red]Error executing game: {exc}[/red]")
        raise


def entry() -> None:
    """Entry point for the werewolf console command."""
    fire.Fire(main)


if __name__ == "__main__":
    entry()
