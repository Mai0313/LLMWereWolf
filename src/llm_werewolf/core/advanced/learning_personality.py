"""
Learning Personality System - 学习型人格系统

实现人格动态学习、记忆系统、行为模式优化等高级特性
"""

import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
import pickle

from ..personality.models import PersonalityProfile, PersonalityDimension, MotivationType
from ..decision.models import IntentType


@dataclass
class PersonalityMemory:
    """人格记忆系统"""

    short_term_memory: deque = field(default_factory=lambda: deque(maxlen=50))  # 最近50个决策
    long_term_memory: Dict[str, Any] = field(default_factory=dict)  # 长期模式

    # 成功经验库
    successful_strategies: Dict[IntentType, List[Dict[str, Any]]] = field(default_factory=lambda: defaultdict(list))

    # 失败教训库
    failure_patterns: List[Dict[str, Any]] = field(default_factory=list)

    # 社交关系记忆
    social_relationships: Dict[str, float] = field(default_factory=dict)  # 信任度: -1.0到1.0

    def add_decision_memory(self, decision_data: Dict[str, Any]):
        """添加决策记忆"""
        self.short_term_memory.append(decision_data)

        # 如果决策成功，添加到成功经验库
        if decision_data.get('was_successful', False):
            intent = decision_data.get('intent')
            if intent:
                self.successful_strategies[intent].append(decision_data.copy())

        # 如果决策失败，分析失败模式
        elif not decision_data.get('was_successful', True):
            failure_data = {
                'intent': decision_data.get('intent'),
                'context': decision_data.get('context'),
                'outcome': decision_data.get('outcome'),
                'reasoning': decision_data.get('reasoning')
            }
            self.failure_patterns.append(failure_data)

    def update_social_relationship(self, other_player: str, trust_change: float):
        """更新社交关系"""
        current_trust = self.social_relationships.get(other_player, 0.0)
        new_trust = max(-1.0, min(1.0, current_trust + trust_change))
        self.social_relationships[other_player] = new_trust

    def get_trust_level(self, other_player: str) -> float:
        """获取对其他玩家的信任度"""
        return self.social_relationships.get(other_player, 0.0)

    def get_successful_intent_patterns(self) -> Dict[IntentType, float]:
        """获取成功意图模式"""
        patterns = {}
        for intent, strategies in self.successful_strategies.items():
            if strategies:
                # 计算平均置信度作为模式强度
                avg_confidence = sum(s.get('confidence', 0) for s in strategies) / len(strategies)
                success_rate = sum(1 for s in strategies if s.get('was_successful', True)) / len(strategies)
                patterns[intent] = avg_confidence * success_rate
        return patterns


@dataclass
class PersonalityEvolution:
    """人格演变参数"""

    learning_rate: float = 0.1  # 学习速率
    adaptation_rate: float = 0.05  # 适应速率
    retention_rate: float = 0.9  # 记忆保留率

    # 维度敏感度（哪些维度更容易变化）
    dimension_sensitivity: Dict[PersonalityDimension, float] = field(default_factory=lambda: {
        PersonalityDimension.RISK_TOLERANCE: 0.8,        # 风险态度容易根据结果调整
        PersonalityDimension.SOCIAL_PRESSURE: 0.6,    # 社交敏感性中等
        PersonalityDimension.DOMINANCE: 0.3,          # 控制欲较难改变
        PersonalityDimension.LOGIC_CAPACITY: 0.4,      # 逻辑能力较稳定
        PersonalityDimension.DECEPTION_COMFORT: 0.7,    # 撒谎舒适度可调整
        PersonalityDimension.TRUST_BASELINE: 0.9,      # 信任基线容易调整
        PersonalityDimension.EGO: 0.5,                # 自敏中等
        PersonalityDimension.CONSISTENCY: 0.2,        # 一致性需求最难改变
    })

    # 动机敏感度
    motivation_sensitivity: Dict[MotivationType, float] = field(default_factory=lambda: {
        MotivationType.SURVIVAL: 0.8,
        MotivationType.CONTROL: 0.6,
        MotivationType.REVENGE: 0.7,
        MotivationType.VALIDATION: 0.5,
        MotivationType.TEAM: 0.9
    })


class LearningPersonalitySystem:
    """学习型人格系统"""

    def __init__(self, base_profile: PersonalityProfile):
        self.base_profile = base_profile
        self.memory = PersonalityMemory()
        self.evolution = PersonalityEvolution()

        # 演变历史追踪
        self.evolution_history: List[Dict[str, Any]] = []

        # 当前人格状态（会基于学习进行微调）
        self.current_dimensions = base_profile.base_personality.dimensions.copy()
        self.current_motivations = base_profile.current_mental_state.motivations.copy()

        # 学习统计
        self.learning_stats = {
            'decisions_count': 0,
            'successful_decisions': 0,
            'failed_decisions': 0,
            'dimension_changes': 0,
            'motivation_changes': 0
        }

    def process_decision_result(self, decision_data: Dict[str, Any]) -> None:
        """处理决策结果并学习"""
        self.learning_stats['decisions_count'] += 1

        # 添加到记忆系统
        self.memory.add_decision_memory(decision_data)

        # 根据结果调整人格
        if decision_data.get('was_successful', False):
            self.learning_stats['successful_decisions'] += 1
            self._reinforce_successful_patterns(decision_data)
        else:
            self.learning_stats['failed_decisions'] += 1
            self._learn_from_failure(decision_data)

        # 更新社交关系
        self._update_social_relationships(decision_data)

        # 记录演变历史
        self._record_evolution_step(decision_data)

    def _reinforce_successful_patterns(self, decision_data: Dict[str, Any]) -> None:
        """强化成功模式"""
        intent = decision_data.get('intent')
        if not intent:
            return

        # 根据成功意图调整相关人格维度
        intent_dimension_mapping = {
            IntentType.STRONG_ACCUSE: {
                PersonalityDimension.DOMINANCE: 0.1,
                PersonalityDimension.RISK_TOLERANCE: 0.1,
                PersonalityDimension.EGO: 0.05
            },
            IntentType.LOW_PROFILE_SPEECH: {
                PersonalityDimension.RISK_TOLERANCE: -0.1,
                PersonalityDimension.DOMINANCE: -0.05
            },
            IntentType.EMOTIONAL_APPEAL: {
                PersonalityDimension.SOCIAL_PRESSURE: 0.05,
                PersonalityDimension.TRUST_BASELINE: 0.05
            },
            IntentType.TEST_SUSPECT: {
                PersonalityDimension.LOGIC_CAPACITY: 0.1,
                PersonalityDimension.RISK_TOLERANCE: 0.05
            },
            IntentType.FOLLOW_OTHERS: {
                PersonalityDimension.SOCIAL_PRESSURE: 0.1,
                PersonalityDimension.DOMINANCE: -0.1
            }
        }

        if intent in intent_dimension_mapping:
            adjustments = intent_dimension_mapping[intent]
            for dimension, change in adjustments.items():
                self._adjust_dimension(dimension, change * self.evolution.learning_rate)

    def _learn_from_failure(self, decision_data: Dict[str, Any]) -> None:
        """从失败中学习"""
        intent = decision_data.get('intent')
        if not intent:
            return

        # 分析失败原因并调整人格
        failure_reason = decision_data.get('failure_reason', 'unknown')

        # 基于失败原因的调整策略
        if failure_reason == 'wrong_target':
            # 选错了目标，增加逻辑能力
            self._adjust_dimension(PersonalityDimension.LOGIC_CAPACITY, 0.1 * self.evolution.learning_rate)
            self._adjust_dimension(PersonalityDimension.RISK_TOLERANCE, -0.05 * self.evolution.learning_rate)

        elif failure_reason == 'trust_violated':
            # 信任被背叛，调整信任基线
            self._adjust_dimension(PersonalityDimension.TRUST_BASELINE, -0.15 * self.evolution.learning_rate)

        elif failure_reason == 'social_pressure':
            # 社交压力下失败，调整社交敏感度
            self._adjust_dimension(PersonalityDimension.SOCIAL_PRESSURE, -0.1 * self.evolution.learning_rate)

        elif failure_reason == 'too_aggressive':
            # 过于激进，调整控制欲
            self._adjust_dimension(PersonalityDimension.DOMINANCE, -0.1 * self.evolution.learning_rate)

    def _update_social_relationships(self, decision_data: Dict[str, Any]) -> None:
        """更新社交关系"""
        # 分析决策中的社交互动
        if decision_data.get('intent') in [IntentType.STRONG_ACCUSE, IntentType.TEST_SUSPECT]:
            target = decision_data.get('target')
            if target and decision_data.get('was_successful'):
                # 成功指控或质疑，降低对目标的信任
                self.memory.update_social_relationship(target, -0.1)
            else:
                # 失败的指控，可能降低自己的社交信誉
                pass  # 可以实现其他玩家的记录

        elif decision_data.get('intent') in [IntentType.FOLLOW_OTHERS, IntentType.DEFEND_OTHERS]:
            target = decision_data.get('target')
            if target:
                # 支持他人，增加信任
                self.memory.update_social_relationship(target, 0.05)

    def _adjust_dimension(self, dimension: PersonalityDimension, change: float) -> None:
        """调整人格维度"""
        current_value = self.current_dimensions.get(dimension, 0.5)
        new_value = max(0.0, min(1.0, current_value + change * self.evolution.dimension_sensitivity[dimension]))

        if abs(new_value - current_value) > 0.01:  # 只记录有意义的变化
            self.current_dimensions[dimension] = new_value
            self.learning_stats['dimension_changes'] += 1

    def _adjust_motivation(self, motivation: MotivationType, change: float) -> None:
        """调整动机"""
        current_value = self.current_motivations.get(motivation, 0.5)
        new_value = max(0.0, min(1.0, current_value + change * self.evolution.motivation_sensitivity[motivation]))

        if abs(new_value - current_value) > 0.01:
            self.current_motivations[motivation] = new_value
            self.learning_stats['motivation_changes'] += 1

    def _record_evolution_step(self, decision_data: Dict[str, Any]) -> None:
        """记录演变步骤"""
        evolution_step = {
            'timestamp': time.time(),
            'decision_id': decision_data.get('decision_id'),
            'intent': decision_data.get('intent'),
            'was_successful': decision_data.get('was_successful'),
            'confidence': decision_data.get('confidence'),
            'dimensions_before': self.base_profile.base_personality.dimensions.copy(),
            'dimensions_after': self.current_dimensions.copy(),
            'motivations_before': self.base_profile.current_mental_state.motivations.copy(),
            'motivations_after': self.current_motivations.copy(),
            'dimension_changes': self.learning_stats['dimension_changes'],
            'motivation_changes': self.learning_stats['motivation_changes']
        }

        self.evolution_history.append(evolution_step)

    def get_updated_profile(self) -> PersonalityProfile:
        """获取更新后的人格档案"""
        from ..personality.models import Personality, MentalState

        # 创建更新后的基础人格
        updated_personality = Personality(dimensions=self.current_dimensions)

        # 创建更新后的心理状态
        updated_mental_state = MentalState(
            motivations=self.current_motivations,
            stress_level=self.base_profile.current_mental_state.stress_level,
            confidence=self.base_profile.current_mental_state.confidence,
            last_updated_round=self.base_profile.current_mental_state.last_updated_round
        )

        # 创建新的人格档案
        updated_profile = PersonalityProfile(
            base_personality=updated_personality,
            current_mental_state=updated_mental_state,
            personality_name=f"Learned_{self.base_profile.personality_name}",
            description=f"Evolved from {self.base_profile.personality_name}"
        )

        return updated_profile

    def predict_success_probability(self, intent: IntentType, context: Dict[str, Any]) -> float:
        """预测成功概率"""
        # 基于历史成功模式预测
        successful_patterns = self.memory.get_successful_intent_patterns()
        base_probability = successful_patterns.get(intent, 0.5)

        # 根据当前人格调整概率
        intent_dimension_mapping = {
            IntentType.STRONG_ACCUME: PersonalityDimension.DOMINANCE,
            IntentType.RISK_TOLERANCE: PersonalityDimension.RISK_TOLERANCE,
            IntentType.SOCIAL_PRESSURE: PersonalityDimension.SOCIAL_PRESSURE,
            IntentType.LOGIC_CAPACITY: PersonalityDimension.LOGIC_CAPACITY
        }

        if intent in intent_dimension_mapping:
            dimension = intent_dimension_mapping[intent]
            dimension_value = self.current_dimensions.get(dimension, 0.5)

            # 维度值越高，该意图的成功概率越高
            dimension_factor = dimension_value * 0.3
        else:
            dimension_factor = 0.0

        # 根据动机调整
        current_motivation = max(self.current_motivations.values())
        motivation_factor = current_motivation * 0.2

        # 根据社交关系调整
        if 'target' in context:
            target = context['target']
            if target:
                trust_level = self.memory.get_trust_level(target)
                social_factor = (trust_level + 1.0) * 0.1  # [-0.1, 0.1]
            else:
                social_factor = 0.0
        else:
            social_factor = 0.0

        # 组合所有因素
        final_probability = max(0.0, min(1.0, base_probability + dimension_factor + motivation_factor + social_factor))

        return final_probability

    def get_learning_summary(self) -> Dict[str, Any]:
        """获取学习摘要"""
        evolution_depth = self._calculate_evolution_depth()
        learning_efficiency = self._calculate_learning_efficiency()

        return {
            'total_decisions': self.learning_stats['decisions_count'],
            'success_rate': (self.learning_stats['successful_decisions'] /
                          max(1, self.learning_stats['decisions_count'])),
            'dimension_changes': self.learning_stats['dimension_changes'],
            'motivation_changes': self.learning_stats['motivation_changes'],
            'evolution_depth': evolution_depth,
            'learning_efficiency': learning_efficiency,
            'memory_size': len(self.memory.short_term_memory),
            'successful_patterns_count': len(self.memory.successful_strategies),
            'relationship_count': len(self.memory.social_relationships)
        }

    def _calculate_evolution_depth(self) -> float:
        """计算演变深度"""
        depth = 0.0

        # 维度变化深度
        for dimension in PersonalityDimension:
            original_value = self.base_profile.base_personality.dimensions.get(dimension, 0.5)
            current_value = self.current_dimensions.get(dimension, 0.5)
            depth += abs(original_value - current_value)

        # 动机变化深度
        for motivation in MotivationType:
            original_value = self.base_profile.current_mental_state.motivations.get(motivation, 0.5)
            current_value = self.current_motivations.get(motivation, 0.5)
            depth += abs(original_value - current_value)

        return depth / (len(PersonalityDimension) + len(MotivationType))

    def _calculate_learning_efficiency(self) -> float:
        """计算学习效率"""
        if self.learning_stats['decisions_count'] == 0:
            return 0.0

        success_rate = self.learning_stats['successful_decisions'] / self.learning_stats['decisions_count']

        # 根据变化频率调整效率
        change_frequency = (self.learning_stats['dimension_changes'] +
                           self.learning_stats['motivation_changes'])

        # 适度的变化频率带来高效率
        optimal_change_frequency = 0.1 * self.learning_stats['decisions_count']
        if change_frequency > 0:
            frequency_efficiency = 1.0 - abs(change_frequency - optimal_change_frequency) / (optimal_change_frequency + 1)
        else:
            frequency_efficiency = 0.5

        # 综合成功率、变化频率和记忆质量
        memory_quality = len(self.memory.successful_strategies) / max(1, self.learning_stats['decisions_count'])

        efficiency = (success_rate * 0.5 + frequency_efficiency * 0.3 + memory_quality * 0.2)

        return efficiency

    def save_learning_state(self, filepath: str):
        """保存学习状态"""
        learning_state = {
            'base_profile_name': self.base_profile.personality_name,
            'current_dimensions': self.current_dimensions,
            'current_motivations': self.current_motivations,
            'memory': self.memory,
            'evolution_history': self.evolution_history,
            'learning_stats': self.learning_stats,
            'evolution_parameters': {
                'learning_rate': self.evolution.learning_rate,
                'adaptation_rate': self.evolution.adaptation_rate,
                'retention_rate': self.evolution.retention_rate
            }
        }

        with open(filepath, 'wb') as f:
            pickle.dump(learning_state, f)

        print(f"🧠 Learning state saved to: {filepath}")

    @classmethod
    def load_learning_state(cls, base_profile: PersonalityProfile, filepath: str):
        """加载学习状态"""
        try:
            with open(filepath, 'rb') as f:
                learning_state = pickle.load(f)

            # 创建学习型人格系统
            learning_system = cls(base_profile)
            learning_system.current_dimensions = learning_state['current_dimensions']
            learning_system.current_motivations = learning_state['current_motivations']
            learning_system.memory = learning_state['memory']
            learning_system.evolution_history = learning_state['evolution_history']
            learning_system.learning_stats = learning_state['learning_stats']

            # 恢复演变参数
            learning_system.evolution.learning_rate = learning_state['evolution_parameters']['learning_rate']
            learning_system.evolution.adaptation_rate = learning_state['evolution_parameters']['adaptation_rate']
            learning_system.evolution.retention_rate = learning_state['evolution_parameters']['retention_rate']

            print(f"🧠 Learning state loaded from: {filepath}")
            return learning_system

        except Exception as e:
            print(f"❌ Failed to load learning state: {e}")
            return cls(base_profile)  # 返回原始系统