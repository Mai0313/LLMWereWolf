"""
Decision Runner - 决策运行器

协调完整的决策执行流程
"""

from typing import List, Dict, Optional, Callable, Any
from .models import Decision, DecisionContext, DecisionResult
from .intent_engine import IntentEngine
from ..personality.models import PersonalityProfile
from ..observation.player_view import PlayerView


class DecisionRunner:
    """决策运行器

    负责协调整个决策流程：
    1. 接收玩家视角
    2. 执行意图引擎
    3. 处理LLM渲染
    4. 返回最终决策
    """

    def __init__(self, personality_profile: PersonalityProfile):
        self.personality_profile = personality_profile
        self.intent_engine = IntentEngine(personality_profile)
        self.decision_history: List[Decision] = []
        self.llm_renderer: Optional[Callable] = None

    def set_llm_renderer(self, renderer: Callable):
        """设置LLM渲染器"""
        self.llm_renderer = renderer

    def run_decision_cycle(self, player_view: PlayerView) -> DecisionResult:
        """执行完整决策周期"""

        try:
            # 1. 生成决策
            decision = self.intent_engine.generate_decision(
                player_view,
                self.llm_renderer
            )

            # 2. 记录决策
            self._record_decision(decision)

            # 3. 验证决策
            validation_result = self._validate_decision(decision, player_view)

            if not validation_result["is_valid"]:
                print(f"Warning: Decision validation failed: {validation_result['errors']}")
                # 可以选择返回默认决策或尝试重新生成
                decision = self._create_fallback_decision(player_view)

            # 4. 返回结果
            return DecisionResult(
                success=True,
                decision=decision,
                execution_details={
                    "personality": self.personality_profile.personality_name,
                    "confidence": decision.confidence,
                    "intent_type": decision.intent.value
                }
            )

        except Exception as e:
            # 异常处理
            error_decision = self._create_error_decision(player_view, str(e))
            return DecisionResult(
                success=False,
                decision=error_decision,
                error_message=str(e),
                execution_details={"error_type": type(e).__name__}
            )

    def _record_decision(self, decision: Decision):
        """记录决策历史"""
        self.decision_history.append(decision)

        # 保持决策历史在合理范围内
        if len(self.decision_history) > 50:
            self.decision_history = self.decision_history[-30:]

    def _validate_decision(self, decision: Decision, player_view: PlayerView) -> Dict[str, Any]:
        """验证决策"""

        errors = []

        # 基本格式检查
        if not decision.is_valid_format():
            errors.append("Decision format is invalid")

        # 逻辑一致性检查
        if decision.intent and decision.target:
            if not self._is_valid_target(decision.target, player_view):
                errors.append(f"Invalid target: {decision.target}")

        # 人格一致性检查
        personality_consistency = self._check_personality_consistency(decision)
        if not personality_consistency["is_consistent"]:
            errors.extend(personality_consistency["issues"])

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def _is_valid_target(self, target: int, player_view: PlayerView) -> bool:
        """检查目标是否有效"""
        # 确保目标存在且在相关范围内
        alive_ids = player_view.get_alive_player_ids()
        all_ids = [p.player_id for p in player_view.alive_players + player_view.dead_players]

        return target in all_ids and (target in alive_ids or target == player_view.player_id)

    def _check_personality_consistency(self, decision: Decision) -> Dict[str, Any]:
        """检查人格一致性"""

        issues = []
        personality = self.personality_profile.base_personality

        # 检查支配性是否匹配
        if decision.intent.value in ["strong_accuse", "test_suspect"]:
            dominance = personality.dimensions.get("dominance", 0.5)
            if dominance < 0.2 and decision.confidence > 0.8:
                issues.append("High dominance decision but personality is submissive")

        return {
            "is_consistent": len(issues) == 0,
            "issues": issues
        }

    def _create_fallback_decision(self, player_view: PlayerView) -> Decision:
        """创建回退决策（验证失败时使用）"""
        from .models import IntentType

        # 选择最安全的意图
        if player_view.current_phase.value == "day_voting":
            safe_intent = IntentType.ABSTAIN_VOTE
        else:
            safe_intent = IntentType.LOW_PROFILE_SPEECH

        return Decision(
            intent=safe_intent,
            target=None,
            speech="我需要再考虑一下。",
            confidence=0.3,
            reasoning_trace="Fallback decision due to validation failure",
            personality_name=self.personality_profile.personality_name
        )

    def _create_error_decision(self, player_view: PlayerView, error_message: str) -> Decision:
        """创建错误决策"""
        from .models import IntentType

        return Decision(
            intent=IntentType.LOW_PROFILE_SPEECH,
            target=None,
            speech="我需要时间思考这个问题。",
            confidence=0.1,
            reasoning_trace=f"Error encountered: {error_message}",
            personality_name=self.personality_profile.personality_name
        )

    def get_decision_statistics(self) -> Dict[str, Any]:
        """获取决策统计信息"""
        if not self.decision_history:
            return {
                "total_decisions": 0,
                "intent_distribution": {},
                "average_confidence": 0.0,
                "most_common_intent": None
            }

        # 统计意图分布
        intent_counts = {}
        total_confidence = 0.0

        for decision in self.decision_history:
            intent_key = decision.intent.value if decision.intent else "unknown"
            intent_counts[intent_key] = intent_counts.get(intent_key, 0) + 1
            total_confidence += decision.confidence

        most_common_intent = max(intent_counts.items(), key=lambda x: x[1]) if intent_counts else (None, 0)

        return {
            "total_decisions": len(self.decision_history),
            "intent_distribution": intent_counts,
            "average_confidence": total_confidence / len(self.decision_history),
            "most_common_intent": most_common_intent[0]
        }

    def get_recent_decisions(self, count: int = 5) -> List[Decision]:
        """获取最近的决策记录"""
        return self.decision_history[-count:] if self.decision_history else []

    def reset_history(self):
        """重置决策历史"""
        self.decision_history = []