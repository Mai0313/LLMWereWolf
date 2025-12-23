"""
Arena Statistics - 统计分析系统

提供详细的统计分析和可视化功能
"""

import json
import time
from typing import Dict, Any, List, Optional
from collections import defaultdict
import statistics
import math


class ArenaStatistics:
    """统计分析器"""

    def __init__(self):
        self.raw_data: List[Dict[str, Any]] = []
        self.aggregated_stats: Dict[str, Any] = {}
        self.comparative_analysis: Dict[str, Any] = {}

    def add_game_data(self, game_result: Dict[str, Any]):
        """添加游戏数据"""
        self.raw_data.append(game_result)
        self._invalidate_aggregated_stats()

    def add_tournament_data(self, tournament_results: Dict[str, Any]):
        """添加锦标赛数据"""
        if 'games' in tournament_results:
            for game in tournament_results['games']:
                self.add_game_data(game)

        if 'rankings' in tournament_results:
            self.aggregated_stats['tournament_rankings'] = tournament_results['rankings']

        if 'overall_statistics' in tournament_results:
            self.aggregated_stats.update(tournament_results['overall_statistics'])

    def _invalidate_aggregated_stats(self):
        """失效缓存统计"""
        self.aggregated_stats.clear()
        self.comparative_analysis.clear()

    def calculate_basic_stats(self) -> Dict[str, Any]:
        """计算基础统计"""
        if not self.raw_data:
            return {}

        if 'basic_stats' in self.aggregated_stats:
            return self.aggregated_stats['basic_stats']

        total_games = len(self.raw_data)

        # 胜负统计
        werewolf_wins = sum(1 for g in self.raw_data if g.get('winner') == 'werewolf')
        villager_wins = sum(1 for g in self.raw_data if g.get('winner') == 'villager')

        # 时长和回合数统计
        durations = [g.get('duration', 0) for g in self.raw_data if g.get('duration')]
        rounds = [g.get('rounds', 0) for g in self.raw_data if g.get('rounds')]

        basic_stats = {
            'total_games': total_games,
            'werewolf_wins': werewolf_wins,
            'villager_wins': villager_wins,
            'werewolf_win_rate': werewolf_wins / max(1, total_games),
            'villager_win_rate': villager_wins / max(1, total_games),

            # 时长统计
            'avg_duration': statistics.mean(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'duration_std': statistics.stdev(durations) if len(durations) > 1 else 0,

            # 回合数统计
            'avg_rounds': statistics.mean(rounds) if rounds else 0,
            'min_rounds': min(rounds) if rounds else 0,
            'max_rounds': max(rounds) if rounds else 0,
            'rounds_std': statistics.stdev(rounds) if len(rounds) > 1 else 0,
        }

        self.aggregated_stats['basic_stats'] = basic_stats
        return basic_stats

    def calculate_player_stats(self) -> Dict[str, Any]:
        """计算玩家统计"""
        if not self.raw_data:
            return {}

        if 'player_stats' in self.aggregated_stats:
            return self.aggregated_stats['player_stats']

        player_stats = defaultdict(lambda: {
            'name': '',
            'games_played': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'avg_survival_rounds': 0.0,
            'personality_profile': None,
            'total_duration': 0.0,
            'role_distribution': defaultdict(int),
            'decision_frequency': 0.0,
            'performance_score': 0.0
        })

        # 处理每局游戏数据
        for game in self.raw_data:
            winner = game.get('winner', 'unknown')
            player_results = game.get('player_results', {})

            for player_name, player_data in player_results.items():
                stats = player_stats[player_name]
                stats['name'] = player_name
                stats['games_played'] += 1

                # 胜负统计
                if player_data.get('winner') == winner:
                    stats['wins'] += 1
                else:
                    stats['losses'] += 1

                # 统计信息
                stats['avg_survival_rounds'] = (
                    stats['avg_survival_rounds'] * (stats['games_played'] - 1) +
                    player_data.get('survival_rounds', 0)
                ) / stats['games_played']

                stats['total_duration'] += game.get('duration', 0)
                stats['personality_profile'] = player_data.get('personality_profile')

                # 角色分布
                role = player_data.get('role', 'unknown')
                stats['role_distribution'][role] += 1

                # 决策频率
                decisions = player_data.get('decisions_made', 0)
                stats['decision_frequency'] = (
                    stats['decision_frequency'] * (stats['games_played'] - 1) + decisions
                ) / stats['games_played']

            # 计算胜率
        for stats in player_stats.values():
            if stats['games_played'] > 0:
                stats['win_rate'] = stats['wins'] / stats['games_played']
                stats['avg_duration'] = stats['total_duration'] / stats['games_played']
                stats['performance_score'] = self._calculate_performance_score(stats)

        # 转换为普通字典
        player_stats_dict = {name: dict(stats) for name, stats in player_stats.items()}
        self.aggregated_stats['player_stats'] = player_stats_dict
        return player_stats_dict

    def _calculate_performance_score(self, stats: Dict[str, Any]) -> float:
        """计算综合表现分数"""
        score = 0.0

        # 胜率得分 (40%)
        score += stats.get('win_rate', 0) * 40

        # 生存时间得分 (20%)
        survival_score = min(1.0, stats.get('avg_survival_rounds', 0) / 20)
        score += survival_score * 20

        # 决策频率得分 (20%)
        decision_score = min(1.0, stats.get('decision_frequency', 0) / 10)
        score += decision_score * 20

        # 角色多样性得分 (20%)
        role_diversity = len(stats.get('role_distribution', {}))
        diversity_score = min(1.0, role_diversity / 5)
        score += diversity_score * 20

        return score

    def calculate_personality_stats(self) -> Dict[str, Any]:
        """计算人格类型统计"""
        player_stats = self.calculate_player_stats()

        personality_stats = defaultdict(lambda: {
            'count': 0,
            'players': [],
            'total_wins': 0,
            'total_games': 0,
            'avg_win_rate': 0.0,
            'avg_score': 0.0,
            'avg_survival_rounds': 0.0,
            'performance_distribution': {
                'excellent': 0,  # 80-100分
                'good': 0,        # 60-80分
                'average': 0,      # 40-60分
                'poor': 0          # 0-40分
            }
        })

        # 按人格类型分组
        for player_name, stats in player_stats.items():
            personality = stats.get('personality_profile') or 'unknown'
            personality_stats[personality]['count'] += 1
            personality_stats[personality]['players'].append(player_name)
            personality_stats[personality]['total_wins'] += stats['wins']
            personality_stats[personality]['total_games'] += stats['games_played']

            # 表现分布
            score = stats.get('performance_score', 0)
            if score >= 80:
                personality_stats[personality]['performance_distribution']['excellent'] += 1
            elif score >= 60:
                personality_stats[personality]['performance_distribution']['good'] += 1
            elif score >= 40:
                personality_stats[personality]['performance_distribution']['average'] += 1
            else:
                personality_stats[personality]['performance_distribution']['poor'] += 1

        # 计算平均值
        for personality, stats in personality_stats.items():
            if stats['total_games'] > 0:
                stats['avg_win_rate'] = stats['total_wins'] / stats['total_games']

                # 获取该类型所有玩家的平均数据
                players = [p for p in player_stats.values()
                          if p.get('personality_profile') == personality]
                if players:
                    stats['avg_score'] = statistics.mean([p.get('performance_score', 0) for p in players])
                    stats['avg_survival_rounds'] = statistics.mean([p.get('avg_survival_rounds', 0) for p in players])

        return dict(personality_stats)

    def calculate_correlations(self) -> Dict[str, Any]:
        """计算相关性分析"""
        player_stats = self.calculate_player_stats()

        # 准备数据
        data_matrix = []
        features = ['win_rate', 'avg_survival_rounds', 'decision_frequency', 'performance_score']

        for stats in player_stats.values():
            row = [stats.get(feature, 0) for feature in features]
            data_matrix.append(row)

        if len(data_matrix) < 2:
            return {}

        # 计算相关系数矩阵
        correlation_matrix = {}
        for i, feature1 in enumerate(features):
            correlation_matrix[feature1] = {}
            col1 = [row[i] for row in data_matrix]

            for j, feature2 in enumerate(features):
                col2 = [row[j] for row in data_matrix]
                if len(col1) > 1 and len(col2) > 1:
                    try:
                        correlation = self._calculate_correlation(col1, col2)
                        correlation_matrix[feature1][feature2] = correlation
                    except:
                        correlation_matrix[feature1][feature2] = 0.0

        return correlation_matrix

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """计算相关系数"""
        n = len(x)
        if n < 2:
            return 0.0

        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)

        std_x = statistics.stdev(x) if n > 1 else 0.0
        std_y = statistics.stdev(y) if n > 1 else 0.0

        if std_x == 0 or std_y == 0:
            return 0.0

        covariance = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / n
        correlation = covariance / (std_x * std_y)

        return correlation

    def generate_report(self) -> str:
        """生成统计报告"""
        report = []
        report.append("=" * 80)
        report.append("📊 ARENA STATISTICS REPORT")
        report.append("=" * 80)

        # 基础统计
        basic_stats = self.calculate_basic_stats()
        report.append("\n📈 BASIC STATISTICS")
        report.append(f"Total Games: {basic_stats.get('total_games', 0)}")
        report.append(f"Werewolf Win Rate: {basic_stats.get('werewolf_win_rate', 0):.1%}")
        report.append(f"Villager Win Rate: {basic_stats.get('villager_win_rate', 0):.1%}")
        report.append(f"Average Duration: {basic_stats.get('avg_duration', 0):.1}s")
        report.append(f"Average Rounds: {basic_stats.get('avg_rounds', 0):.1}")

        # 玩家统计
        player_stats = self.calculate_player_stats()
        if player_stats:
            report.append("\n🏅 TOP PLAYERS")
            sorted_players = sorted(player_stats.items(), key=lambda x: x[1].get('performance_score', 0), reverse=True)
            for i, (name, stats) in enumerate(sorted_players[:5], 1):
                report.append(f"{i}. {name}")
                report.append(f"   Score: {stats.get('performance_score', 0):.1f}")
                report.append(f"   Win Rate: {stats.get('win_rate', 0):.1%}")
                report.append(f"   Survival: {stats.get('avg_survival_rounds', 0):.1f} rounds")

        # 人格统计
        personality_stats = self.calculate_personality_stats()
        if personality_stats:
            report.append("\n🎭 PERSONALITY PERFORMANCE")
            for personality, stats in sorted(personality_stats.items(),
                                            key=lambda x: x[1].get('avg_score', 0), reverse=True):
                report.append(f"{personality}:")
                report.append(f"   Count: {stats['count']}")
                report.append(f"   Avg Score: {stats.get('avg_score', 0):.1f}")
                report.append(f"   Win Rate: {stats.get('avg_win_rate', 0):.1%}")

        # 相关性分析
        correlations = self.calculate_correlations()
        if correlations:
            report.append("\n🔗 CORRELATIONS")
            for feature1, correlations_row in correlations.items():
                strong_correlations = {k: v for k, v in correlations_row.items()
                                       if abs(v) > 0.5 and k != feature1}
                if strong_correlations:
                    report.append(f"{feature1}:")
                    for feature2, corr in strong_correlations.items():
                        direction = "positive" if corr > 0 else "negative"
                        report.append(f"   {feature2}: {corr:.2f} ({direction})")

        report.append("=" * 80)
        return "\n".join(report)

    def export_json(self, filepath: str):
        """导出统计数据为JSON"""
        export_data = {
            "generated_at": time.time(),
            "basic_stats": self.calculate_basic_stats(),
            "player_stats": self.calculate_player_stats(),
            "personality_stats": self.calculate_personality_stats(),
            "correlations": self.calculate_correlations(),
            "raw_data_count": len(self.raw_data)
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"📊 Statistics exported to: {filepath}")

    def get_leaderboard(self, metric: str = 'performance_score') -> List[Dict[str, Any]]:
        """获取排行榜"""
        player_stats = self.calculate_player_stats()

        if metric not in ['performance_score', 'win_rate', 'avg_survival_rounds', 'decision_frequency']:
            metric = 'performance_score'

        sorted_players = sorted(
            player_stats.items(),
            key=lambda x: x[1].get(metric, 0),
            reverse=True
        )

        leaderboard = []
        for rank, (name, stats) in enumerate(sorted_players, 1):
            leaderboard.append({
                "rank": rank,
                "name": name,
                "score": stats.get(metric, 0),
                "stats": stats,
                "metric": metric
            })

        return leaderboard