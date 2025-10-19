"""CLI entry point for the LLM Werewolf game."""

import sys
from pathlib import Path
import argparse

from rich.console import Console

from llm_werewolf.ai import DemoAgent
from llm_werewolf.core import GameEngine
from llm_werewolf.utils import log_error, setup_logger, log_game_event
from llm_werewolf.config import (
    list_preset_names,
    get_preset_by_name,
    load_players_config,
    create_agent_from_player_config,
)

console = Console()


def create_demo_game(preset_name: str = "9-players") -> GameEngine:
    """Create a demo game with AI agents.

    Args:
        preset_name: Name of the preset configuration to use.

    Returns:
        GameEngine: Initialized game engine.
    """
    # Get preset configuration
    config = get_preset_by_name(preset_name)

    # Create game engine
    engine = GameEngine(config)

    # Create players with demo agents
    players = []
    for i in range(config.num_players):
        player_id = f"player_{i + 1}"
        player_name = f"Player{i + 1}"
        agent = DemoAgent()
        players.append((player_id, player_name, agent))

    # Get roles from config
    roles = config.to_role_list()

    # Setup game
    engine.setup_game(players, roles)

    log_game_event("game_created", f"Demo game created with preset '{preset_name}'")

    return engine


def create_game_from_yaml(yaml_path: str | Path, preset_override: str | None = None) -> GameEngine:
    """Create a game from YAML configuration file.

    Args:
        yaml_path: Path to the YAML configuration file.
        preset_override: Optional preset name to override config file.

    Returns:
        GameEngine: Initialized game engine.

    Raises:
        ValueError: If configuration is invalid.
    """
    # Load and validate configuration
    players_config = load_players_config(yaml_path)

    # Determine preset (CLI override > YAML config > default)
    preset_name = preset_override or players_config.preset or "9-players"

    # Get preset configuration
    game_config = get_preset_by_name(preset_name)

    # Validate player count matches preset
    num_players = len(players_config.players)
    if num_players != game_config.num_players:
        msg = (
            f"Player count mismatch: YAML has {num_players} players "
            f"but preset '{preset_name}' requires {game_config.num_players}"
        )
        raise ValueError(msg)

    # Create game engine
    engine = GameEngine(game_config)

    # Create players from config
    players = []
    for i, player_cfg in enumerate(players_config.players):
        player_id = f"player_{i + 1}"
        player_name = player_cfg.name
        agent = create_agent_from_player_config(player_cfg)
        players.append((player_id, player_name, agent))

    # Get roles from config
    roles = game_config.to_role_list()

    # Setup game
    engine.setup_game(players, roles)

    log_game_event(
        "game_created", f"Game created from YAML config '{yaml_path}' with preset '{preset_name}'"
    )

    return engine


def run_console_mode(engine: GameEngine) -> None:
    """Run the game in console mode (no TUI).

    Args:
        engine: The game engine to run.
    """
    console.print("\n" + "=" * 50)
    console.print("LLM WEREWOLF GAME - Console Mode")
    console.print("=" * 50 + "\n")

    try:
        result = engine.play_game()
        console.print(f"\n{result}")

        # Print final statistics
        if engine.game_state:
            console.print("\n=== Game Statistics ===")
            console.print(f"Total rounds: {engine.game_state.round_number}")
            console.print(f"Total events: {len(engine.get_events())}")

            alive = engine.game_state.get_alive_players()
            dead = engine.game_state.get_dead_players()

            console.print(f"\nSurvivors ({len(alive)}):")
            for player in alive:
                console.print(f"  - {player.name} ({player.get_role_name()})")

            console.print(f"\nCasualties ({len(dead)}):")
            for player in dead:
                console.print(f"  - {player.name} ({player.get_role_name()})")

    except KeyboardInterrupt:
        console.print("\n\nGame interrupted by user.")
    except Exception as e:
        log_error(e, "Error during game execution")
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


def run_tui_mode(engine: GameEngine, show_debug: bool = True) -> None:
    """Run the game with TUI interface.

    Args:
        engine: The game engine to run.
        show_debug: Whether to show debug panel.
    """
    try:
        from llm_werewolf.ui import run_tui

        console.print("\n[cyan]Starting TUI mode...[/cyan]")
        console.print("[dim]Press 'q' to quit, 'd' to toggle debug panel, 'n' for next step[/dim]")

        run_tui(engine, show_debug)

    except ImportError as e:
        console.print(f"[red]Error: TUI dependencies not available: {e}[/red]")
        console.print("Install with: [cyan]uv sync[/cyan]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n\nGame interrupted by user.")
    except Exception as e:
        log_error(e, "Error during TUI execution")
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="LLM Werewolf - AI-powered Werewolf game with TUI interface"
    )

    parser.add_argument(
        "--config", type=str, help="Path to YAML configuration file for custom player setup"
    )

    parser.add_argument(
        "--preset",
        type=str,
        default="9-players",
        choices=list_preset_names(),
        help="Game preset to use (role configuration)",
    )

    parser.add_argument("--no-tui", action="store_true", help="Run in console mode without TUI")

    parser.add_argument("--debug", action="store_true", help="Show debug panel in TUI mode")

    parser.add_argument("--log-file", type=str, help="Path to log file")

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    import logging

    log_level = getattr(logging, args.log_level)
    setup_logger(level=log_level, log_file=args.log_file)

    # Create game
    try:
        if args.config:
            # Create game from YAML configuration
            config_path = Path(args.config)
            if not config_path.exists():
                console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
                sys.exit(1)

            engine = create_game_from_yaml(config_path, preset_override=args.preset)
            console.print(f"[green]Game created from config: {config_path}[/green]")
        else:
            # Create demo game with DemoAgents
            engine = create_demo_game(args.preset)
            console.print(f"[yellow]Running demo mode with preset: {args.preset}[/yellow]")
    except Exception as e:
        log_error(e, "Error creating game")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    # Run game
    if args.no_tui:
        run_console_mode(engine)
    else:
        run_tui_mode(engine, show_debug=args.debug)


if __name__ == "__main__":
    main()
