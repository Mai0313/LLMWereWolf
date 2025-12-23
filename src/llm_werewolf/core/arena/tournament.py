"""
Tournament - 锦标赛系统

实现自动多局比赛和排名系统
"""

import time
import uuid
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from ..game_engine import GameEngine
from ..types import GamePhase
from ..config.player_config import PlayersConfig


class TournamentMode(str, Enum):
    """锦标赛模式"""
    ROUND_ROBIN = "round_robin"  # 循环赛
    ELIMINATION = "elimination"   # 淘汰赛
    SWISS = "swiss"              # 瑞士制
    MULTI_GAME = "multi_game"     # 多场比赛


class TournamentStatus(str, Enum):
    """锦标赛状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TournamentConfig:
    """锦标赛配置"""

    # 基础配置
    name: str
    mode: TournamentMode
    number_of_games: int

    # 玩家配置
    player_configs: List[Dict[str, Any]]
    enable_personality_system: bool = True

    # 游戏设置
    language: str = "zh-TW"
    max_rounds_per_game: int = 20
    timeout_per_decision: float = 30.0

    # 统计设置
    collect_detailed_stats: bool = True
    save_replays: bool = True
    enable_ranking: bool = True

    # 并发设置
    max_concurrent_games: int = 1

    # 回调设置
    game_start_callback: Optional[Callable] = None
    game_end_callback: Optional[Callable] = None
    progress_callback: Optional[Callable] = None


@dataclass
class GameResult:
    """单局游戏结果"""

    game_id: str
    tournament_id: str
    player_configs: List[Dict[str, Any]]

    # 游戏结果
    winner: str  # "werewolf" or "villager"
    rounds: int
    duration: float

    # 玩家表现
    player_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 详细数据
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

    # 时间戳
    start_time: float = field(default_factory=time.time)
    end_time: float = field(default_factory=time.time)


class Tournament:
    """锦标赛管理器"""

    def __init__(self, config: TournamentConfig):
        self.config = config
        self.tournament_id = str(uuid.uuid4())
        self.status = TournamentStatus.PENDING

        # 游戏记录
        self.games: List[GameResult] = []
        self.current_game: Optional[GameResult] = None

        # 排名和统计
        self.rankings: Dict[str, Dict[str, Any]] = {}
        self.overall_statistics: Dict[str, Any] = {}

        # 时间信息
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

        # 游戏生成器
        self._game_generator = self._create_game_generator()

    def _create_game_generator(self):
        """创建游戏生成器"""
        if self.config.mode == TournamentMode.MULTI_GAME:
            return self._multi_game_generator()
        elif self.config.mode == TournamentMode.ROUND_ROBIN:
            return self._round_robin_generator()
        elif self.config.mode == TournamentMode.ELIMINATION:
            return self._elimination_generator()
        else:
            return self._multi_game_generator()

    def _multi_game_generator(self):
        """多场比赛模式生成器"""
        for i in range(self.config.number_of_games):
            yield {
                "game_id": f"{self.tournament_id}_game_{i+1}",
                "player_configs": self.config.player_configs.copy(),
                "game_number": i + 1
            }

    def _round_robin_generator(self):
        """循环赛模式生成器"""
        # 简化实现：生成所有可能的玩家组合
        from itertools import combinations

        players = self.config.player_configs
        game_players = players[:9]  # 最多9人游戏

        for i in range(self.config.number_of_games):
            # 简单循环：每局打一样的配置
            yield {
                "game_id": f"{self.tournament_id}_robin_{i+1}",
                "player_configs": game_players.copy(),
                "game_number": i + 1
            }

    def _elimination_generator(self):
        """淘汰赛模式生成器"""
        # 简化实现
        remaining_players = self.config.player_configs.copy()
        round_num = 1

        while len(self.games) < self.config.number_of_games:
            if len(remaining_players) < 2:
                break

            game_players = remaining_players[:9]
            yield {
                "game_id": f"{self.tournament_id}_elim_{round_num}",
                "player_configs": game_players.copy(),
                "game_number": round_num
            }

            round_num += 1

    def start(self):
        """开始锦标赛"""
        if self.status != TournamentStatus.PENDING:
            raise ValueError(f"Tournament cannot start from status: {self.status}")

        self.status = TournamentStatus.RUNNING
        self.started_at = time.time()

        # 初始化玩家统计
        for player_config in self.config.player_configs:
            self.rankings[player_config["name"]] = {
                "name": player_config["name"],
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "avg_rounds": 0.0,
                "total_score": 0,
                "personality_profile": player_config.get("personality_profile"),
                "games_played": 0
            }

        print(f"🏆 Tournament '{self.config.name}' started")
        print(f"📊 Mode: {self.config.mode.value}")
        print(f"🎮 Games: {self.config.number_of_games}")
        print(f"👥 Players: {len(self.config.player_configs)}")

    def run_single_game(self) -> Optional[GameResult]:
        """运行单局游戏"""
        try:
            # 获取下一局配置
            try:
                game_config = next(self._game_generator)
            except StopIteration:
                return None  # 没有更多游戏

            # 创建游戏结果记录
            game_result = GameResult(
                game_id=game_config["game_id"],
                tournament_id=self.tournament_id,
                player_configs=game_config["player_configs"]
            )

            self.current_game = game_result

            # 调用回调
            if self.config.game_start_callback:
                self.config.game_start_callback(game_result)

            # 运行游戏
            from .game_runner import GameRunner
            runner = GameRunner(self.config)
            actual_result = runner.run_game(game_result)

            # 更新统计
            self._update_statistics(actual_result)
            self.games.append(actual_result)

            # 调用回调
            if self.config.game_end_callback:
                self.config.game_end_callback(actual_result)

            if self.config.progress_callback:
                self.config.progress_callback(
                    len(self.games),
                    self.config.number_of_games,
                    actual_result
                )

            return actual_result

        except Exception as e:
            print(f"❌ Game failed: {e}")
            return None

    def run_full_tournament(self):
        """运行完整的锦标赛"""
        self.start()

        try:
            while self.status == TournamentStatus.RUNNING:
                result = self.run_single_game()

                if result is None:
                    # 没有更多游戏
                    break

                # 检查是否应该继续
                if len(self.games) >= self.config.number_of_games:
                    break

        except KeyboardInterrupt:
            print("\n⏸️  Tournament paused")
            self.status = TournamentStatus.PAUSED
        except Exception as e:
            print(f"❌ Tournament error: {e}")
            self.status = TournamentStatus.CANCELLED
        finally:
            if self.status == TournamentStatus.RUNNING:
                self.complete()

        return self.games

    def complete(self):
        """完成锦标赛"""
        self.status = TournamentStatus.COMPLETED
        self.completed_at = time.time()

        # 计算最终统计
        self._calculate_final_rankings()
        self._calculate_overall_statistics()

        print(f"\n🏆 Tournament completed!")
        print(f"📊 Total games: {len(self.games)}")
        print(f"⏱️  Duration: {self.completed_at - self.started_at:.2f}s")

    def _update_statistics(self, result: GameResult):
        """更新游戏统计"""
        for player_name, player_data in result.player_results.items():
            if player_name in self.rankings:
                stats = self.rankings[player_name]

                # 基础统计
                stats["games_played"] += 1

                # 胜负统计
                if player_data.get("winner") == result.winner:
                    stats["wins"] += 1
                    stats["total_score"] += 100  # 胜利+100分
                else:
                    stats["losses"] += 1
                    stats["total_score"] += 0  # 失败0分

                # 计算胜率
                stats["win_rate"] = stats["wins"] / max(1, stats["games_played"])

                # 计算平均回合数
                stats["avg_rounds"] = (
                    stats.get("avg_rounds", 0) * (stats["games_played"] - 1) + result.rounds
                ) / stats["games_played"]

                # 根据表现调整分数
                performance_score = self._calculate_performance_score(player_data)
                stats["total_score"] += performance_score

    def _calculate_performance_score(self, player_data: Dict[str, Any]) -> int:
        """计算表现分数"""
        score = 0

        # 存活时间奖励
        survival_rounds = player_data.get("survival_rounds", 0)
        score += survival_rounds * 5

        # 决策质量
        decisions = player_data.get("decisions", [])
        for decision in decisions:
            if decision.get("confidence", 0) > 0.8:
                score += 2
            if decision.get("alignment_score", 0) > 0.7:
                score += 3

        return score

    def _calculate_final_rankings(self):
        """计算最终排名"""
        sorted_players = sorted(
            self.rankings.items(),
            key=lambda x: (-x[1]["total_score"], -x[1]["win_rate"])
        )

        for rank, (player_name, stats) in enumerate(sorted_players, 1):
            stats["final_rank"] = rank
            stats["rank_change"] = stats.get("rank_change", 0)  # 可以在这里实现排名变化

        self.rankings = dict(sorted_players)

    def _calculate_overall_statistics(self):
        """计算总体统计"""
        total_games = len(self.games)

        # 基础统计
        werewolf_wins = sum(1 for g in self.games if g.winner == "werewolf")
        villager_wins = sum(1 for g in self.games if g.winner == "villager")

        # 平均时长
        total_duration = sum(g.duration for g in self.games)
        avg_duration = total_duration / max(1, total_games)

        # 平均回合
        total_rounds = sum(g.rounds for g in self.games)
        avg_rounds = total_rounds / max(1, total_games)

        # 人格类型统计
        personality_stats = {}
        for player_name, stats in self.rankings.items():
            personality = stats.get("personality_profile", "unknown")
            if personality not in personality_stats:
                personality_stats[personality] = {
                    "players": [],
                    "total_wins": 0,
                    "total_games": 0,
                    "avg_score": 0
                }

            personality_stats[personality]["players"].append(player_name)
            personality_stats[personality]["total_wins"] += stats["wins"]
            personality_stats[personality]["total_games"] += stats["games_played"]

        # 计算人格类型平均分
        for personality, stats in personality_stats.items():
            if stats["total_games"] > 0:
                players = [p for p in self.rankings if p in stats["players"]]
                stats["avg_score"] = sum(self.rankings[p]["total_score"] for p in players) / len(players)

        self.overall_statistics = {
            "tournament_id": self.tournament_id,
            "total_games": total_games,
            "werewolf_win_rate": werewolf_wins / max(1, total_games),
            "villager_win_rate": villager_wins / max(1, total_games),
            "avg_duration": avg_duration,
            "avg_rounds": avg_rounds,
            "personality_statistics": personality_stats,
            "best_player": next(iter(self.rankings.values())) if self.rankings else None,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }

    def get_rankings(self) -> Dict[str, Dict[str, Any]]:
        """获取排名"""
        return self.rankings.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.overall_statistics.copy()

    def save_results(self, filepath: str):
        """保存锦标赛结果"""
        results = {
            "config": {
                "name": self.config.name,
                "mode": self.config.mode.value,
                "number_of_games": self.config.number_of_games,
                "player_configs": self.config.player_configs
            },
            "tournament_id": self.tournament_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "games": [
                {
                    "game_id": g.game_id,
                    "winner": g.winner,
                    "rounds": g.rounds,
                    "duration": g.duration,
                    "player_results": g.player_results,
                    "start_time": g.start_time,
                    "end_time": g.end_time
                }
                for g in self.games
            ],
            "rankings": self.rankings,
            "overall_statistics": self.overall_statistics
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"📊 Tournament results saved to: {filepath}")

    def print_summary(self):
        """打印锦标赛摘要"""
        if not self.games:
            print("❌ No games completed")
            return

        print("\n" + "="*60)
        print(f"🏆 {self.config.name} - Tournament Results")
        print("="*60)

        print(f"📊 Overall Statistics:")
        print(f"  Total Games: {len(self.games)}")
        print(f"  Werewolf Win Rate: {self.overall_statistics.get('werewolf_win_rate', 0):.1%}")
        print(f"  Villager Win Rate: {self.overall_statistics.get('villager_win_rate', 0):.1%}")
        print(f"  Average Duration: {self.overall_statistics.get('avg_duration', 0):.1}s")
        print(f"  Average Rounds: {self.overall_statistics.get('avg_rounds', 0):.1}")

        print(f"\n🏅 Final Rankings:")
        for rank, (player_name, stats) in enumerate(self.rankings.items(), 1):
            print(f"  {rank:2d}. {player_name}")
            print(f"      Wins: {stats['wins']}/{stats['games_played']} ({stats['win_rate']:.1%})")
            print(f"      Score: {stats['total_score']}")
            print(f"      Personality: {stats.get('personality_profile', 'unknown')}")

        if self.overall_statistics.get('personality_statistics'):
            print(f"\n🎭 Personality Performance:")
            for personality, stats in self.overall_statistics['personality_statistics'].items():
                print(f"  {personality}: avg score {stats['avg_score']:.1f}, "
                      f"{stats['total_wins']}/{stats['total_games']} games")

        print("="*60)