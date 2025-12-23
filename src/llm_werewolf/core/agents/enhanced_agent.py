"""
Enhanced Agent - 增强版Agent基类

实现人格驱动的Agent接口，支持意图级决策
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import time

from ..personality.models import PersonalityProfile
from ..decision.models import Decision, DecisionContext, DecisionResult
from ..decision.decision_runner import DecisionRunner
from ..observation.player_view import PlayerView
from ..observation.prompt_builder import PromptBuilder
from ..agent import BaseAgent


class EnhancedAgent(ABC):
    """增强版Agent基类

    集成人格系统，支持意图级决策
    """

    def __init__(
        self,
        personality_profile: PersonalityProfile,
        base_agent: Optional[BaseAgent] = None,
        decision_timeout: float = 30.0
    ):
        self.personality_profile = personality_profile
        self.base_agent = base_agent
        self.decision_timeout = decision_timeout

        # 初始化决策系统
        self.decision_runner = DecisionRunner(personality_profile)
        self.prompt_builder = PromptBuilder()

        # 决策历史
        self.decision_history: List[Decision] = []

        # 设置LLM渲染器（如果有base_agent）
        if base_agent:
            self.decision_runner.set_llm_renderer(self._llm_render_decision)

        # 性能统计
        self.total_decisions = 0
        self.failed_decisions = 0

    def make_decision(self, player_view: PlayerView) -> DecisionResult:
        """
        核心决策接口 - 替代原有的get_response
        """

        start_time = time.time()
        self.total_decisions += 1

        try:
            # 1. 更新人格状态
            self._update_personality_state(player_view)

            # 2. 运行决策周期
            result = self.decision_runner.run_decision_cycle(player_view)

            # 3. 记录决策
            if result.success:
                self.decision_history.append(result.decision)

            # 4. 检查超时
            elapsed = time.time() - start_time
            if elapsed > self.decision_timeout:
                print(f"Warning: Decision took {elapsed:.2f}s, exceeding timeout {self.decision_timeout}s")

            return result

        except Exception as e:
            self.failed_decisions += 1
            return self._create_error_result(player_view, str(e))

    def _update_personality_state(self, player_view: PlayerView):
        """根据当前视图更新人格状态"""

        # 更新心理状态
        self.personality_profile.update_mental_state(player_view.current_round)

        # 根据游戏情况调整动机
        self._adjust_motivations(player_view)

    def _adjust_motivations(self, player_view: PlayerView):
        """根据当前情况调整动机强度"""

        # 存活压力
        alive_count = player_view.count_alive_players()
        total_players = player_view.total_players
        survival_pressure = 1.0 - (alive_count / total_players)
        self.personality_profile.current_mental_state.update_motivation("survival", survival_pressure * 0.3)

        # 控制欲（存活人数少时增加）
        if alive_count <= 5:
            self.personality_profile.current_mental_state.update_motivation("control", 0.3)

        # 压力水平
        if alive_count <= 4:
            self.personality_profile.current_mental_state.stress_level = min(1.0, 0.4 + (4 - alive_count) * 0.2)

        # 自信水平（基于决策历史）
        if len(self.decision_history) > 0:
            recent_success = sum(1 for d in self.decision_history[-3:] if d.confidence > 0.6)
            self.personality_profile.current_mental_state.confidence = 0.5 + recent_success * 0.15

    def _llm_render_decision(
        self,
        personality: PersonalityProfile,
        intent_type: 'IntentType',
        player_view: PlayerView
    ) -> str:
        """
        使用LLM渲染自然语言表达
        """

        if not self.base_agent:
            return self._fallback_expression(intent_type, player_view)

        try:
            # 构建Prompt
            prompt = self.prompt_builder.build_decision_prompt(
                personality=personality,
                intent=intent_type,
                world_view=player_view
            )

            # 获取LLM响应
            response = self.base_agent.get_response(prompt)

            # 清理和验证响应
            cleaned_response = self._clean_llm_response(response)

            return cleaned_response or self._fallback_expression(intent_type, player_view)

        except Exception as e:
            print(f"LLM rendering failed: {e}")
            return self._fallback_expression(intent_type, player_view)

    def _clean_llm_response(self, response: str) -> Optional[str]:
        """清理LLM响应"""

        if not response:
            return None

        # 移除可能的思考过程描述
        lines = response.strip().split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line and not self._is_meta_content(line):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines) if cleaned_lines else None

    def _is_meta_content(self, line: str) -> bool:
        """检查是否为元内容（思考过程）"""
        meta_indicators = [
            "我分析", "我认为", "让我思考", "出于",
            "基于", "考虑到", "因为", "所以",
            "首先", "其次", "然后", "最后"
        ]
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in meta_indicators)

    def _fallback_expression(self, intent_type: 'IntentType', player_view: PlayerView) -> str:
        """提供基础表达（LLM失败时使用）"""
        from ..decision.models import IntentType

        basic_expressions = {
            IntentType.STRONG_ACCUSE: "我对此有强烈怀疑。",
            IntentType.TEST_SUSPECT: "能解释一下你的行为吗？",
            IntentType.LOW_PROFILE_SPEECH: "让我再想想。",
            IntentType.ABSTAIN_VOTE: "我选择弃票。",
            IntentType.EMOTIONAL_APPEAL: "这让我很担忧。",
        }

        return basic_expressions.get(intent_type, "我需要表达我的看法。")

    def _create_error_result(self, player_view: PlayerView, error_message: str) -> DecisionResult:
        """创建错误结果"""
        from ..decision.models import IntentType, Decision

        fallback_decision = Decision(
            intent=IntentType.LOW_PROFILE_SPEECH,
            target=None,
            speech="我需要时间思考这个情况。",
            confidence=0.1,
            reasoning_trace=f"Error: {error_message}",
            personality_name=self.personality_profile.personality_name
        )

        return DecisionResult(
            success=False,
            decision=fallback_decision,
            error_message=error_message
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        success_rate = 1.0 - (self.failed_decisions / max(1, self.total_decisions))
        decision_stats = self.decision_runner.get_decision_statistics()

        return {
            "total_decisions": self.total_decisions,
            "failed_decisions": self.failed_decisions,
            "success_rate": success_rate,
            "average_confidence": decision_stats["average_confidence"],
            "most_common_intent": decision_stats["most_common_intent"],
            "personality_name": self.personality_profile.personality_name,
            "current_stress": self.personality_profile.current_mental_state.stress_level,
            "current_confidence": self.personality_profile.current_mental_state.confidence
        }

    def reset_statistics(self):
        """重置统计数据"""
        self.total_decisions = 0
        self.failed_decisions = 0
        self.decision_runner.reset_history()


class EnhancedLLMAgent(EnhancedAgent):
    """增强版LLM Agent

    集成LLM的增强Agent实现
    """

    def __init__(
        self,
        personality_profile: PersonalityProfile,
        llm_client: BaseAgent,
        model_name: str = "gpt-4"
    ):
        super().__init__(personality_profile, llm_client)
        self.model_name = model_name

    def _llm_render_decision(
        self,
        personality: PersonalityProfile,
        intent_type: 'IntentType',
        player_view: PlayerView
    ) -> str:
        """LLM专用渲染器"""

        prompt = self.prompt_builder.build_decision_prompt(
            personality=personality,
            intent=intent_type,
            world_view=player_view
        )

        # 添加模型特定的指令
        if self.model_name.startswith("gpt"):
            prompt += "\n\n请用你自然的语言风格直接回答，不要使用任何元语言（如'首先我认为'等）。"
        elif self.model_name.startswith("claude"):
            prompt += "\n\n请直接表达你的观点，避免使用分析性的语言结构。"

        return super()._llm_render_decision(personality, intent_type, player_view)


class HybridAgent(EnhancedAgent):
    """混合Agent

    可以在人格模式和传统模式间切换的Agent
    """

    def __init__(
        self,
        personality_profile: PersonalityProfile,
        base_agent: BaseAgent,
        use_personality_mode: bool = True
    ):
        super().__init__(personality_profile, base_agent)
        self.use_personality_mode = use_personality_mode

    def set_mode(self, use_personality_mode: bool):
        """设置运行模式"""
        self.use_personality_mode = use_personality_mode
        print(f"Agent mode set to: {'Personality-driven' if use_personality_mode else 'Traditional'}")

    def get_response(self, message: str) -> str:
        """兼容传统接口的响应方法"""

        if self.use_personality_mode:
            # 这里需要将message转换为PlayerView
            # 暂时返回基础响应
            return f"[Personality Mode] 我需要基于人格做出回应：{message[:50]}..."
        else:
            # 使用传统LLM响应
            return self.base_agent.get_response(message)

    def make_decision(self, player_view: PlayerView) -> DecisionResult:
        """决策接口，根据模式选择不同处理"""

        if self.use_personality_mode:
            return super().make_decision(player_view)
        else:
            # 传统模式处理
            # 这里需要实现传统响应到Decision的转换
            return self._traditional_mode_decision(player_view)

    def _traditional_mode_decision(self, player_view: PlayerView) -> DecisionResult:
        """传统模式决策处理"""
        # 简化实现，实际中需要更复杂的转换逻辑
        from ..decision.models import IntentType, Decision

        traditional_prompt = f"Game state: {player_view.current_phase}, Round: {player_view.current_round}"
        response = self.base_agent.get_response(traditional_prompt)

        fallback_decision = Decision(
            intent=IntentType.LOW_PROFILE_SPEECH,
            target=None,
            speech=response or "我正在思考...",
            confidence=0.5,
            reasoning_trace="Traditional mode response"
        )

        return DecisionResult(
            success=True,
            decision=fallback_decision,
            execution_details={"mode": "traditional"}
        )