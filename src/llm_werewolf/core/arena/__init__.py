"""
Arena System - AI竞技场系统

支持自动多局对战、统计、复盘等功能
"""

from .tournament import Tournament, TournamentConfig
from .game_runner import GameRunner
from .statistics import ArenaStatistics
from .replay import ReplaySystem

__all__ = [
    "Tournament",
    "TournamentConfig",
    "GameRunner",
    "ArenaStatistics",
    "ReplaySystem"
]