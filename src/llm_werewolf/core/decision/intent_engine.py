"""
Intent Engine - 意图引擎

协调意图生成、过滤和选择的核心逻辑
"""

from typing import List, Dict, Optional, Any
import random

from .models import Intent, IntentType, IntentWithWeight, Decision, DecisionContext
from .intent_registry import IntentRegistry
from ..personality.models import PersonalityProfile
from ..observation.player_view import PlayerView
from ..types import GamePhase


class IntentEngine:
    """意图引擎

    负责整个意图决策流程：
    1. 获取可用意图
    2. 认知过滤
    3. 意图选择
    4. 决策生成
    """

    def __init__(self, personality_profile: PersonalityProfile):
        # 延迟导入以避免循环依赖，并修正导入路径
        from ..personality.cognitive_filter import CognitiveFilter
        
        self.personality_profile = personality_profile
        self.intent_registry = IntentRegistry()
        self.cognitive_filter = CognitiveFilter(personality_profile)

    def generate_decision(
        self,
        player_view: PlayerView,
        llm_renderer: Optional[callable] = None
    ) -> Decision:
        """生成完整决策"""

        # 1. 构建决策上下文
        context = self._build_decision_context(player_view)

        # 2. 获取可用意图
        available_intents = self._get_available_intents(player_view, context)

        # 3. 认知过滤和加权
        weighted_intents = self.cognitive_filter.filter_intents(
            available_intents,
            context.dict()
        )

        # 4. 选择意图
        selected_intent = self._select_intent_by_weight(weighted_intents)

        # 5. 生成决策（包含自然语言表达）
        decision = self._create_decision(selected_intent, player_view, context, llm_renderer)

        return decision

    def _build_decision_context(self, player_view: PlayerView) -> DecisionContext:
        """构建决策上下文"""

        # 分析当前社交动态
        social_dynamics = self._analyze_social_dynamics(player_view)

        # 评估压力水平
        pressure_level = self._estimate_pressure_level(player_view)

        # 分析近期活动
        recent_activity = self._describe_recent_activity(player_view)

        # 识别决策约束
        constraints = self._identify_constraints(player_view)

        return DecisionContext(
            player_id=player_view.player_id,
            phase=player_view.current_phase.value,
            round=player_view.current_round,
            can_act=player_view.am_i_alive(),
            is_alive=player_view.am_i_alive(),
            recent_activity=recent_activity,
            pressure_level=pressure_level,
            social_dynamics=social_dynamics,
            constraints=constraints
        )

    def _get_available_intents(self, player_view: PlayerView, context: DecisionContext) -> List[Intent]:
        """获取可用意图"""

        # 从角色提示中推断角色类型（故意模糊）
        role_hint = self._extract_role_hint(player_view.role_hint)

        # 获取阶段意图
        available_intents = self.intent_registry.get_intents_for_phase(
            player_view.current_phase,
            role_hint,
            context.can_act
        )

        # 过滤不符合上下文的意图
        filtered_intents = []
        for intent in available_intents:
            if self._is_intent_contextually_valid(intent, context):
                filtered_intents.append(intent)

        return filtered_intents

    def _select_intent_by_weight(self, weighted_intents: List[IntentWithWeight]) -> IntentWithWeight:
        """基于权重选择意图"""

        if not weighted_intents:
            # 异常情况：提供默认意图
            return self._create_default_intent()

        # 使用权重进行随机选择
        weights = [intent.weight for intent in weighted_intents]
        selected_index = random.choices(range(len(weighted_intents)), weights=weights)[0]
        selected_intent = weighted_intents[selected_index]

        # 如果需要目标但未指定，自动选择
        if selected_intent.intent.requires_target() and not selected_intent.target:
            selected_intent.target = self._auto_select_target(selected_intent.intent.intent_type)

        return selected_intent

    def _create_decision(
        self,
        selected_intent: IntentWithWeight,
        player_view: PlayerView,
        context: DecisionContext,
        llm_renderer: Optional[callable]
    ) -> Decision:
        """创建最终决策"""

        # 基于人格生成基础表达
        base_expression = self._generate_base_expression(selected_intent, player_view)

        # 如果有LLM渲染器，使用LLM优化表达
        final_speech = base_expression
        if llm_renderer:
            try:
                final_speech = llm_renderer(
                    self.personality_profile,
                    selected_intent.intent.intent_type,
                    player_view
                )
            except Exception as e:
                print(f"Warning: LLM rendering failed: {e}, using base expression")
                final_speech = base_expression

        # 计算置信度
        confidence = self._calculate_confidence(selected_intent, context)

        return Decision(
            intent=selected_intent.intent.intent_type,
            target=selected_intent.target,
            speech=final_speech,
            confidence=confidence,
            reasoning_trace=selected_intent.reasoning,
            personality_name=self.personality_profile.personality_name,
            motivation_state=self.personality_profile.current_mental_state.motivations.copy()
        )

    def _analyze_social_dynamics(self, player_view: PlayerView) -> str:
        """分析社交动态"""

        # 分析投票模式
        if player_view.context.get('discussion_activity') == 'high':
            return "讨论激烈，观点对立明显"
        elif player_view.context.get('discussion_activity') == 'low':
            return "讨论冷清，多人保持沉默"
        else:
            return "讨论氛围适中，观点多样"

    def _estimate_pressure_level(self, player_view: PlayerView) -> float:
        """评估当前压力水平"""

        pressure = 0.3  # 基础压力

        # 存活玩家数量影响
        alive_ratio = player_view.count_alive_players() / player_view.total_players
        if alive_ratio < 0.5:
            pressure += 0.4  # 生存压力大
        elif alive_ratio < 0.7:
            pressure += 0.2

        # 死亡数量影响
        if len(player_view.death_announcements) > 0:
            if player_view.death_announcements[-1].round >= player_view.current_round - 1:
                pressure += 0.2  # 最近有死亡

        # 个人状态影响
        if player_view.context.get('pressure_level'):
            pressure += player_view.context['pressure_level'] * 0.3

        return min(1.0, pressure)

    def _describe_recent_activity(self, player_view: PlayerView) -> str:
        """描述近期活动"""

        if player_view.current_phase == GamePhase.NIGHT:
            return "进入夜晚时刻，大家都在等待"
        elif player_view.current_phase == GamePhase.DAY_DISCUSSION:
            return "白天讨论阶段，大家在分析和推理"
        elif player_view.current_phase == GamePhase.DAY_VOTING:
            return "投票时刻，需要做出关键决定"
        else:
            return "游戏进行中"

    def _identify_constraints(self, player_view: PlayerView) -> List[str]:
        """识别决策约束"""

        constraints = []

        if not player_view.am_i_alive():
            constraints.append("你已死亡，无法参与行动")

        if player_view.count_alive_players() <= 3:
            constraints.append("人数很少，每个决定都很关键")

        if player_view.context.get('alive_count', 0) <= 5:
            constraints.append("局势已经相当严峻")

        return constraints

    def _extract_role_hint(self, role_hint: Optional[str]) -> Optional[str]:
        """从角色提示中提取角色类型（故意保持模糊）"""

        if not role_hint:
            return None

        role_hint = role_hint.lower()
        if "同伴" in role_hint and "命运" in role_hint:
            return "werewolf"
        elif "身份" in role_hint and "窥探" in role_hint:
            return "seer"
        elif "药剂" in role_hint or "神秘" in role_hint:
            return "witch"
        elif "守护" in role_hint or "保护" in role_hint:
            return "guard"
        elif "特殊能力" in role_hint and "时刻" in role_hint:
            return "hunter"
        else:
            return "villager"  # 默认

    def _is_intent_contextually_valid(self, intent: Intent, context: DecisionContext) -> bool:
        """验证意图是否符合上下文"""

        # 存活检查
        if not context.is_alive and not self._is_passive_intent(intent):
            return False

        # 存活玩家数量检查（需要目标的意图）
        if intent.requires_target() and context.can_act:
            if context.phase == "day_voting" and context.phase != context.phase:
                pass  # 投票阶段需要特殊处理

        return True

    def _is_passive_intent(self, intent: Intent) -> bool:
        """判断是否为被动意图"""
        passive_types = [IntentType.SKIP_NIGHT_ACTION, IntentType.LOW_PROFILE_SPEECH]
        return intent.intent_type in passive_types

    def _create_default_intent(self) -> IntentWithWeight:
        """创建默认意图（异常情况）"""
        default_intent = Intent(
            intent_type=IntentType.LOW_PROFILE_SPEECH,
            description="保持低调发言",
            compatible_phases=["all"],
            compatible_roles=["all"]
        )
        return IntentWithWeight(intent=default_intent, weight=1.0)

    def _auto_select_target(self, intent_type: IntentType) -> Optional[int]:
        """自动选择目标（当AI未指定时）"""

        # 这里应该从player_view中获取可用目标，暂时返回随机
        # 在实际使用中，这个方法应该接收player_view参数
        return None  # 需要外部处理目标选择

    def _generate_base_expression(
        self,
        selected_intent: IntentWithWeight,
        player_view: PlayerView
    ) -> str:
        """基于人格生成基础自然语言表达"""

        intent_type = selected_intent.intent.intent_type
        personality = self.personality_profile.base_personality

        # 基于意图类型和人格生成简单表达
        expressions = {
            IntentType.STRONG_ACCUSE: [
                "我认为这个玩家行为很可疑",
                "我强烈质疑这个玩家",
                "这个人明显有问题"
            ],
            IntentType.TEST_SUSPECT: [
                "我想听听这个玩家的解释",
                "能说说你为什么要这样做吗",
                "请解释一下你的行为"
            ],
            IntentType.LOW_PROFILE_SPEECH: [
                "我再观察一下",
                "暂时没什么好说的",
                "让我想想"
            ],
            IntentType.ABSTAIN_VOTE: [
                "我选择弃票",
                "暂时不投票",
                "需要更多信息"
            ]
        }

        possible_expressions = expressions.get(intent_type, ["我需要表达我的看法"])
        base_expression = random.choice(possible_expressions)

        # 根据人格调整表达风格
        dominance = personality.dimensions.get("dominance", 0.5)
        if dominance > 0.7:
            base_expression = base_expression.replace("我想", "我认为")
            base_expression = base_expression.replace("可以", "必须")

        return base_expression

    def _calculate_confidence(self, selected_intent: IntentWithWeight, context: DecisionContext) -> float:
        """计算决策置信度"""

        # 基础置信度来自权重
        confidence = selected_intent.weight

        # 调整因子
        if context.pressure_level > 0.8:
            confidence *= 0.8  # 高压力降低自信
        elif context.pressure_level < 0.3:
            confidence *= 1.2  # 低压力增加自信

        if len(context.constraints) > 2:
            confidence *= 0.9  # 约束多降低自信

        return min(1.0, max(0.1, confidence))