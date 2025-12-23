"""
Observation System - 观测与信息裁剪系统

严格遵循SPEC要求的信息隔离：
- AI永远不感知完整规则
- 信息以模糊、叙事化方式呈现
- 防止AI"开天眼"
"""

from .player_view import PlayerView, PublicPlayerInfo, SpeechRecord
from .world_cropper import WorldCropper
from .prompt_builder import PromptBuilder

__all__ = [
    "PlayerView",
    "PublicPlayerInfo",
    "SpeechRecord",
    "WorldCropper",
    "PromptBuilder",
]