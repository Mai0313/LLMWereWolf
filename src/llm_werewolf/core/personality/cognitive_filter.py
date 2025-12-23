"""
Cognitive Filter - 认知过滤器

实现人格驱动的意图过滤和加权系统，严格遵循SPEC要求：
- 意图经过人格过滤
- 动机系统加权选择
- 模拟人类有限理性
"""

from typing import List, Dict, Any, Optional
import math
import random

from .models import Personality, MentalState, PersonalityProfile
from ..decision.models import Intent, IntentWithWeight
from ..types import GamePhase


class CognitiveFilter:
    """认知过滤器

    基于人格特质和心理状态过滤、加权意图选择
    """

    def __init__(self, personality_profile: PersonalityProfile):
        self.personality = personality_profile.base_personality
        self.mental_state = personality_profile.current_mental_state

    def filter_intents(
        self,
        available_intents: List[Intent],
        context: Dict[str, Any]
    ) -> List[IntentWithWeight]:
        """
        核心过滤逻辑：
        1. 根据人格过滤掉不合适的意图
        2. 根据动机和人格加权剩余意图
        3. 归一化权重
        """

        # Step 1: 人格过滤
        filtered_intents = self._personality_filter(available_intents, context)

        if not filtered_intents:
            # 如果所有意图都被过滤，提供默认意图
            filtered_intents = self._get_default_intents(available_intents)

        # Step 2: 动机和人格加权
        weighted_intents = self._apply_personality_weights(filtered_intents, context)

        # Step 3: 归一化权重
        return self._normalize_weights(weighted_intents)

    def _personality_filter(
        self,
        intents: List[Intent],
        context: Dict[str, Any]
    ) -> List[Intent]:
        """基于人格特质过滤意图"""

        filtered = []
        phase = context.get("phase", GamePhase.DAY_DISCUSSION)
        stress_level = self.mental_state.stress_level
        confidence = self.mental_state.confidence

        for intent in intents:
            if self._is_intent_compatible(intent, phase, stress_level, confidence):
                filtered.append(intent)

        return filtered

    def _is_intent_compatible(
        self,
        intent: Intent,
        phase: GamePhase,
        stress_level: float,
        confidence: float
    ) -> bool:
        """判断意图是否与当前人格状态兼容"""

        # 基于人格特质的过滤规则
        dominance = self.personality.get_dimension_value("dominance")
        risk_tolerance = self.personality.get_dimension_value("risk_tolerance")
        deception_comfort = self.personality.get_dimension_value("deception_comfort")
        social_pressure = self.personality.get_dimension_value("social_pressure")

        intent_type = intent.intent_type.value
        compatible = True

        # 控制欲低的玩家不太会选择强烈的控制意图
        if "strong" in intent_type.lower() or "accuse" in intent_type.lower():
            if dominance < 0.3 and random.random() > dominance * 2:
                compatible = False

        # 风险承受低的会避免冒险行为
        if "risky" in intent.description.lower() and risk_tolerance < 0.4:
            compatible = False

        # 撒谎舒适度低的不选择欺骗类意图
        if "deceptive" in intent.description.lower() and deception_comfort < 0.3:
            compatible = False

        # 高压力下，社交压力敏感的人更可能跟随他人
        if stress_level > 0.7 and social_pressure > 0.7 and "follow" not in intent_type.lower():
            # 在高压力下更可能选择跟随类意图
            if random.random() < 0.3:  # 30%概率过滤非跟随意图
                compatible = False

        # 低自信时避免极端行为
        if confidence < 0.3 and ("strong" in intent_type.lower() or "accuse" in intent_type.lower()):
            if random.random() < 0.4:  # 40%概率过滤强烈意图
                compatible = False

        return compatible

    def _apply_personality_weights(
        self,
        intents: List[Intent],
        context: Dict[str, Any]
    ) -> List[IntentWithWeight]:
        """基于人格和动机系统加权意图"""

        weighted_intents = []
        phase = context.get("phase", GamePhase.DAY_DISCUSSION)

        # 获取最强烈的动机
        strongest_motivation, motivation_strength = self.mental_state.get_strongest_motivation()

        for intent in intents:
            weight = self._calculate_base_weight(intent, phase)
            weight = self._apply_motivation_weights(weight, intent, strongest_motivation, motivation_strength)
            weight = self._apply_contextual_weights(weight, intent, context)

            weighted_intents.append(IntentWithWeight(
                intent=intent,
                weight=weight,
                reasoning=self._generate_reasoning(intent, weight, context)
            ))

        return weighted_intents

    def _calculate_base_weight(self, intent: Intent, phase: GamePhase) -> float:
        """计算基于人格的基准权重"""

        intent_type = intent.intent_type.value.lower()

        # 基础权重（所有意图平等开始）
        base_weight = 1.0

        # 控制欲权重
        if any(keyword in intent_type for keyword in ["strong", "accuse", "lead"]):
            dominance = self.personality.get_dimension_value("dominance")
            base_weight *= (0.5 + dominance * 1.5)  # 0.5-2.0倍

        # 社交压力权重
        if "follow" in intent_type or "support" in intent_type:
            social_pressure = self.personality.get_dimension_value("social_pressure")
            base_weight *= (0.5 + social_pressure * 1.5)

        # 风险承受权重
        if any(keyword in intent.description.lower() for keyword in ["risky", "aggressive", "dangerous"]):
            risk_tolerance = self.personality.get_dimension_value("risk_tolerance")
            base_weight *= (0.3 + risk_tolerance * 1.7)  # 0.3-2.0倍

        # 逻辑能力权重
        if "investigate" in intent_type or "analyze" in intent_type:
            logic_capacity = self.personality.get_dimension_value("logic_capacity")
            base_weight *= (0.7 + logic_capacity * 0.6)

        # 撒谎舒适度权重
        if "deceptive" in intent.description.lower() or "lie" in intent.description.lower():
            deception_comfort = self.personality.get_dimension_value("deception_comfort")
            base_weight *= (0.2 + deception_comfort * 1.8)

        # 一致性权重（减少随机性）
        consistency = self.personality.get_dimension_value("consistency")
        if intent_type in self._get_recent_intent_preferences():
            base_weight *= (0.8 + consistency * 0.4)  # 偏好已有行为

        return base_weight

    def _apply_motivation_weights(
        self,
        weight: float,
        intent: Intent,
        strongest_motivation: str,
        motivation_strength: float
    ) -> float:
        """应用动机权重"""

        intent_type = intent.intent_type.value.lower()
        motivation_multiplier = 1.5  # 强动机的影响力

        if strongest_motivation == "survival":
            # 生存焦虑：更保守，更跟随他人
            if "follow" in intent_type or "conservative" in intent_type.lower():
                weight *= (1.0 + motivation_strength * (motivation_multiplier - 1.0))
            elif "risky" in intent_type.lower() or "aggressive" in intent_type.lower():
                weight *= (1.0 - motivation_strength * 0.5)  # 降低冒险行为权重

        elif strongest_motivation == "control":
            # 控场欲：更强势，更主动
            if "strong" in intent_type or "lead" in intent_type:
                weight *= (1.0 + motivation_strength * (motivation_multiplier - 1.0))
            elif "passive" in intent_type or "follow" in intent_type:
                weight *= (1.0 - motivation_strength * 0.4)

        elif strongest_motivation == "revenge":
            # 报复：更攻击性
            if "accuse" in intent_type or "attack" in intent_type:
                weight *= (1.0 + motivation_strength * (motivation_multiplier - 1.0))

        elif strongest_motivation == "validation":
            # 被认可：更关注他人反应
            if "emotional" in intent_type or "appeal" in intent_type:
                weight *= (1.0 + motivation_strength * (motivation_multiplier - 1.0))

        elif strongest_motivation == "team":
            # 阵营目标：更理性分析
            if "investigate" in intent_type or "analyze" in intent_type:
                weight *= (1.0 + motivation_strength * 0.8)

        return weight

    def _apply_contextual_weights(
        self,
        weight: float,
        intent: Intent,
        context: Dict[str, Any]
    ) -> float:
        """应用上下文权重"""

        stress_level = self.mental_state.stress_level
        confidence = self.mental_state.confidence

        # 压力影响：高压力降低复杂行为权重
        if stress_level > 0.7:
            if "complex" in intent.description.lower():
                weight *= 0.7
            elif "simple" in intent.description.lower() or "follow" in intent.intent_type.value.lower():
                weight *= 1.2

        # 自信影响：高自信增加主动行为权重
        if confidence > 0.7:
            if "strong" in intent.intent_type.value.lower() or "lead" in intent.intent_type.value.lower():
                weight *= 1.1
        elif confidence < 0.3:
            # 低自信降低极端行为
            if "strong" in intent.intent_type.value.lower() or "accuse" in intent.intent_type.value.lower():
                weight *= 0.8

        return weight

    def _normalize_weights(self, weighted_intents: List[IntentWithWeight]) -> List[IntentWithWeight]:
        """归一化权重，确保总和为1.0"""

        total_weight = sum(intent.weight for intent in weighted_intents)

        if total_weight == 0:
            # 防止除零错误，平均分配权重
            uniform_weight = 1.0 / len(weighted_intents) if weighted_intents else 1.0
            for intent in weighted_intents:
                intent.weight = uniform_weight
        else:
            # 归一化
            for intent in weighted_intents:
                intent.weight = intent.weight / total_weight

        return weighted_intents

    def _get_default_intents(self, available_intents: List[Intent]) -> List[Intent]:
        """获取默认意图（当所有意图都被过滤时）"""

        # 优先选择最安全、最简单的意图
        default_types = ["follow_others", "low_profile_speech", "abstain_vote"]

        for intent in available_intents:
            if any(default_type in intent.intent_type.value for default_type in default_types):
                return [intent]

        # 如果没有找到，返回第一个可用意图
        return available_intents[:1] if available_intents else []

    def _get_recent_intent_preferences(self) -> set[str]:
        """获取最近倾向的意图类型（模拟一致性偏好）"""

        # 这里应该从决策历史中获取，暂时返回空集
        # TODO: 实现基于决策历史的一致性偏好
        return set()

    def _generate_reasoning(
        self,
        intent: Intent,
        weight: float,
        context: Dict[str, Any]
    ) -> str:
        """生成选择推理过程（用于调试和日志）"""

        strongest_motivation, _ = self.mental_state.get_strongest_motivation()

        reasoning_parts = []

        # 基础推理
        reasoning_parts.append(f"选择{intent.intent_type.value}")

        # 动机影响
        reasoning_parts.append(f"受{strongest_motivation}动机驱动")

        # 人格影响
        if weight > 1.5:
            reasoning_parts.append("高度符合人格特质")
        elif weight < 0.5:
            reasoning_parts.append("不太符合人格倾向")

        # 状态影响
        if self.mental_state.stress_level > 0.7:
            reasoning_parts.append("高压力影响决策")

        # 风险考虑
        risk_tolerance = self.personality.get_dimension_value("risk_tolerance")
        if risk_tolerance < 0.4 and "risky" in intent.description.lower():
            reasoning_parts.append("但风险承受度较低，权重下调")

        return "；".join(reasoning_parts)