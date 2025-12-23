#!/usr/bin/env python3
"""
Arena CLI - 竞技场命令行接口

提供完整的Phase 1-3功能CLI入口
"""

import argparse
import json
import time
import sys
from pathlib import Path

from core.arena.tournament import Tournament, TournamentConfig, TournamentMode
from core.arena.statistics import ArenaStatistics
from core.arena.replay import ReplayController, ReplayViewer
from core.personality.personality import PredefinedPersonalities


def run_tournament(config_file: str, mode: str = "multi_game", games: int = 10):
    """运行锦标赛"""
    print(f"🏆 Starting Tournament Mode: {mode} with {games} games")

    # 加载配置
    config_path = Path(config_file)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return

    with open(config_path) as f:
        config = json.load(f)

    # 创建锦标赛配置
    tournament_config = TournamentConfig(
        name=f"Tournament_{int(time.time())}",
        mode=TournamentMode(mode),
        number_of_games=games,
        player_configs=config.get('players', []),
        enable_personality_system=config.get('enable_personality_system', True),
        language=config.get('language', 'zh-TW'),
        max_rounds_per_game=config.get('max_rounds_per_game', 20),
        timeout_per_decision=config.get('timeout_per_decision', 30.0),
        collect_detailed_stats=True,
        save_replays=True,
        enable_ranking=True,
        max_concurrent_games=1
    )

    # 创建锦标赛
    tournament = Tournament(tournament_config)

    def on_game_start(game_result):
        print(f"🎮 Starting Game {game_result.game_id}")

    def on_game_end(game_result):
        print(f"✅ Game {game_result.game_id} completed")
        print(f"   Winner: {game_result.winner}")
        print(f"   Duration: {game_result.duration:.1}s")
        print(f"   Rounds: {game_result.rounds}")

    def on_progress(completed, total, game_result):
        print(f"📊 Progress: {completed}/{total} games")
        if game_result.winner == "werewolf":
            print(f"   Werewolf victory! 🐺")
        else:
            print(f"   Villager victory! 👥")

    tournament_config.game_start_callback = on_game_start
    tournament_config.game_end_callback = on_game_end
    tournament_config.progress_callback = on_progress

    # 运行锦标赛
    results = tournament.run_full_tournament()

    # 显示结果
    tournament.print_summary()

    # 保存结果
    results_dir = Path("tournament_results")
    results_dir.mkdir(exist_ok=True)
    tournament.save_results(results_dir / f"tournament_{int(time.time())}.json")

    return results

def run_statistics(data_files: list, output_file: str = None):
    """运行统计分析"""
    print("📊 Running Statistical Analysis...")

    stats = ArenaStatistics()

    # 加载数据文件
    for data_file in data_files:
        data_path = Path(data_file)
        if data_path.exists():
            with open(data_path) as f:
                data = json.load(f)
            if 'games' in data:
                for game in data['games']:
                    stats.add_game_data(game)
            elif 'rankings' in data:
                stats.add_tournament_data(data)
        else:
            print(f"⚠️  Data file not found: {data_file}")

    # 生成报告
    print(stats.generate_report())

    if output_file:
        stats.export_json(output_file)
    else:
        stats.export_json("arena_statistics.json")

def run_replay(replay_file: str, player_name: str = None, view_mode: str = "judge"):
    """运行复盘"""
    print(f"📺 Starting Replay Analysis")

    # 加载回放数据
    replay_path = Path(replay_file)
    if not replay_path.exists():
        print(f"❌ Replay file not found: {replay_path}")
        return

    with open(replay_path) as f:
        replay_data = json.load(f)

    # 创建回放控制器
    controller = ReplayController(replay_data)

    # 创建查看器
    viewer = ReplayViewer(controller)

    # 设置视角
    from core.arena.replay import ReplayViewMode
    if player_name and view_mode == "player":
        controller.set_view_mode(ReplayViewMode.PLAYER, player_name)
    elif view_mode in ReplayViewMode.__members__:
        controller.set_view_mode(ReplayViewMode(view_mode))

    print(f"Replay Mode: {controller.state.view_mode.value}")
    print(f"Total Events: {len(controller.events)}")

    if player_name:
        print(f"Selected Player: {player_name}")

    # 生成总结报告
    summary = viewer.generate_summary_report()
    print("\n" + summary)

def list_personalities():
    """列出可用的人格"""
    print("🎭 Available Personalities:")
    print("=" * 50)

    personalities = PredefinedPersonalities.list_available_personalities()
    for i, personality in enumerate(personalities, 1):
        profile = PredefinedPersonalities.create_profile(personality)
        print(f"  {i}. {personality}")
        print(f"     Description: {profile.description}")

        # 显示关键特质
        dimensions = profile.base_personality.dimensions
        key_traits = []
        if dimensions.get('dominance', 0) > 0.7:
            key_traits.append("High Dominance")
        if dimensions.get('risk_tolerance', 0) > 0.7:
            key_traits.append("Risk-taking")
        if dimensions.get('logic_capacity', 0) > 0.7:
            key_traits.append("Logical")
        if dimensions.get('deception_comfort', 0) > 0.7:
            key_traits.append("Deceptive")

        if key_traits:
            print(f"     Traits: {', '.join(key_traits)}")
        print()

    print("=" * 50)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Arena CLI - LLM Werewolf Competition System")

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 锦标赛命令
    tournament_parser = subparsers.add_parser('tournament', help='Run tournaments')
    tournament_parser.add_argument('config', help='Configuration file')
    tournament_parser.add_argument('--mode', choices=['multi_game', 'round_robin', 'elimination'], default='multi_game')
    tournament_parser.add_argument('--games', type=int, default=10, help='Number of games to play')

    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='Run statistical analysis')
    stats_parser.add_argument('--data-files', nargs='+', help='Data files to analyze')
    stats_parser.add_argument('--output', help='Output file for statistics')

    # 复盘命令
    replay_parser = subparsers.add_parser('replay', help='Run replay analysis')
    replay_parser.add_argument('replay_file', help='Replay data file')
    replay_parser.add_argument('--player', help='Player name for player view')
    replay_parser.add_argument('--mode', choices=['judge', 'player', 'spectator'], default='judge', help='View mode')

    # 人格列表命令
    personality_parser = subparsers.add_parser('personalities', help='List available personalities')
    personalities_parser.set_defaults(func=list_personalities)

    # 简单演示命令
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    demo_parser.add_argument('--type', choices=['personality', 'tournament', 'statistics'], default='personality', help='Demo type')

    # 解析参数
    args = parser.parse_args()

    try:
        if args.command == 'tournament':
            run_tournament(args.config, args.mode, args.games)

        elif args.command == 'stats':
            run_statistics(args.data_files, args.output)

        elif args.command == 'replay':
            run_replay(args.replay_file, args.player, args.mode)

        elif args.command == 'personalities':
            list_personalities()

        elif args.command == 'demo':
            if args.type == 'personality':
                list_personalities()
            elif args.type == 'tournament':
                demo_config = f'''{
  "language": "zh-TW",
  "players": [
    {{
      "name": "DemoWolf",
      "model": "demo",
      "personality_profile": "aggressive_wolf",
      "enable_personality_system": true
    }},
    {{
      "name": "DemoSeer",
      "model": "demo",
      "personality_profile": "cautious_seer",
      "enable_personality_system": true
    }},
    {{
      "name": "DemoWitch",
      "model": "demo",
      "personality_profile": "emotional_witch",
      "enable_personality_system": true
    }},
    {{
      "name": "DemoHunter",
      "model": "demo",
      "personality_profile": "balanced_hunter",
      "enable_personality_system": true
    }},
    {{
      "name": "DemoVillager1",
      "model": "demo",
      "enable_personality_system": false
    }},
    {{
      "name": "DemoVillager2",
      "model": "demo",
      "enable_personality_system": false
    }},
    {{
      "name": "DemoVillager3",
      "model": "demo",
      "enable_personality_system": false
    }},
    {{
      "name": "DemoVillager4",
      "model": "demo",
      "enable_personality_system": false
    }},
    {{
      "name": "DemoVillager5",
      "model": "demo",
      "enable_personality_system": false
    }}
  ],
  "enable_personality_system": true
}}'''
                demo_config_file = f"demo_tournament_config_{int(time.time())}.json"
                with open(demo_config_file, 'w') as f:
                    json.dump(json.loads(demo_config), f, indent=2)

                print(f"🎮 Demo tournament config created: {demo_config_file}")
                run_tournament(demo_config_file, 'multi_game', 5)

    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Use --help for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()