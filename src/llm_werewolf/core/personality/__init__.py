"""
Personality System - 人格与认知模型系统

此模块实现人格驱动的决策系统，严格遵循SPEC要求：
- 人格永远不感知完整规则
- AI行为来自"意图选择"而非直接策略
- 严格的信息隔离和人格驱动
"""

from .models import Personality, MentalState, PersonalityProfile
from .personality import PersonalityFactory, PredefinedPersonalities
from .cognitive_filter import CognitiveFilter

__all__ = [
    "Personality",
    "MentalState",
    "PersonalityProfile",
    "PersonalityFactory",
    "PredefinedPersonalities",
    "CognitiveFilter",
]