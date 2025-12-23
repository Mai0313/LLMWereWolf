"""
Prompt Builder - Prompt构造器

严格遵循SPEC格式的Prompt构建，确保AI接收的信息合规
"""

from typing import Dict, Any, Optional
from ..personality.models import PersonalityProfile, MentalState, PersonalityDimension
from ..decision.models import IntentType
from .player_view import PlayerView


class PromptBuilder:
    """Prompt构造器

    按照SPEC要求的格式构建决策提示：
    1. 当前心理状态摘要
    2. 可感知世界描述（裁剪后）
    3. 可选意图列表
    4. 表达风格约束
    """

    def build_decision_prompt(
        self,
        personality: PersonalityProfile,
        intent: IntentType,
        world_view: PlayerView,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        构造决策提示的主方法
        """

        # 确保所有必要的部分都存在
        sections = []

        # 1. 心理状态摘要
        sections.append(self._build_mental_state_section(personality.current_mental_state))

        # 2. 世界描述（严格裁剪）
        sections.append(self._build_world_description_section(world_view))

        # 3. 意图指导
        sections.append(self._build_intent_guidance_section(intent))

        # 4. 风格约束
        sections.append(self._build_style_constraints_section(
            personality.base_personality,
            personality.current_mental_state
        ))

        # 组合成最终Prompt
        final_prompt = "\n\n".join(sections)

        # 5. 最终指示
        final_prompt += f"""

## 请你发言

请根据以上信息，自然地表达你的{self._get_intent_description(intent)}。

记住，你是{personality.personality_name}，要保持你一贯的性格特点。
不要表现出不符合你性格的行为，也不要直接说明你的具体身份或能力。

用你自己的话来表达，就像真实的你一样："""

        # 6. SPEC合规性检查
        if self._contains_forbidden_terms(final_prompt):
            print("⚠️ WARNING: Prompt contains potentially forbidden terms")

        return final_prompt

    def _build_mental_state_section(self, mental_state: MentalState) -> str:
        """构建心理状态摘要"""

        strongest_motivation, motivation_strength = mental_state.get_strongest_motivation()

        # 描述压力水平
        stress_desc = self._describe_stress_level(mental_state.stress_level)

        # 描述自信水平
        confidence_desc = self._describe_confidence_level(mental_state.confidence)

        # 描述动机影响
        motivation_desc = self._describe_motivation_impact(strongest_motivation, motivation_strength)

        return f"""## 当前心理状态

你现在感觉{stress_desc}，{confidence_desc}。

{motivation_desc}

这会影响你当前的决策倾向和行为方式。"""

    def _build_world_description_section(self, world_view: PlayerView) -> str:
        """构建世界描述（严格裁剪，符合SPEC）"""

        # 基本信息
        description_parts = [
            f"## 当前局势",
            f"",
            f"现在是{world_view.current_time}。"
        ]

        # 玩家状态
        if world_view.am_i_alive():
            alive_count = world_view.count_alive_players()
            description_parts.append(f"你还活着，场上还有{alive_count}名存活玩家。")

            # 列出存活玩家
            description_parts.append(f"存活的玩家有：")
            for player in world_view.alive_players:
                if player.player_id != world_view.player_id:  # 不列出自己
                    description_parts.append(f"- 玩家{player.player_id}（座位{player.seat_number}）：{player.name}")

        else:
            description_parts.append("你已经不在人世，无法直接参与游戏。")

        # 角色提示
        if world_view.role_hint:
            description_parts.append(f"")
            description_parts.append(f"**特殊提示**：{world_view.role_hint}")

        # 上下文信息
        if world_view.context:
            description_parts.append(f"")
            if 'alive_count' in world_view.context:
                description_parts.append(f"目前存活比例：{world_view.context['alive_count']}/{world_view.context['total_players']}")

            if 'discussion_activity' in world_view.context:
                activity = world_view.context['discussion_activity']
                activity_desc = {'high': '非常热烈', 'medium': '适中', 'low': '比较冷清'}
                description_parts.append(f"讨论氛围：{activity_desc.get(activity, '一般')}")

        # 历史发言（只显示最近的）
        recent_speeches = world_view.get_recent_speeches(limit=3)
        if recent_speeches:
            description_parts.append(f"")
            description_parts.append(f"## 最近的发言")
            for speech in recent_speeches:
                speaker_name = world_view.get_player_name(speech.speaker_id)
                description_parts.append(f"**{speaker_name}**（第{speech.round}轮）：{speech.content}")

        # 死亡信息
        if world_view.death_announcements:
            description_parts.append(f"")
            description_parts.append(f"## 已知死亡情况")
            for death in world_view.death_announcements[-3:]:  # 只显示最近3个
                death_type = "投票处决" if death.is_execution else "夜间死亡"
                description_parts.append(f"**{death.player_name}**（第{death.round}轮){death_type}")

        # 可用行动
        if world_view.available_actions:
            description_parts.append(f"")
            description_parts.append(f"## 你可以选择的行动")
            for i, action in enumerate(world_view.available_actions, 1):
                description_parts.append(f"{i}. {action}")

        return "\n".join(description_parts)

    def _build_intent_guidance_section(self, intent: IntentType) -> str:
        """构建意图指导（不包含具体规则）"""

        intent_descriptions = {
            IntentType.STRONG_ACCUSE: "你想要强烈地表达对某个玩家的质疑，应该使用坚定有力的语言",
            IntentType.TEST_SUSPECT: "你想要试探性质地质疑某人，应该使用委婉的疑问式表达",
            IntentType.FOLLOW_OTHERS: "你想要跟随他人的观点，应该表示赞同和支持",
            IntentType.LOW_PROFILE_SPEECH: "你想要低调发言，应该保持谨慎和模糊",
            IntentType.EMOTIONAL_APPEAL: "你想要情绪化地表达自己，应该带有强烈的个人情感",
            IntentType.VOTE_SUSPECT: "你想要投票给最可疑的玩家",
            IntentType.VOTE_SAFE_TARGET: "你想要投票给相对安全的对象",
            IntentType.ABSTAIN_VOTE: "你选择弃票不参与投票",
        }

        description = intent_descriptions.get(intent, "按照你的方式表达自己")

        return f"""## 行动意图

{description}

记住要围绕这个核心意图来组织你的表达。"""

    def _build_style_constraints_section(
        self,
        personality: 'Personality',
        mental_state: MentalState
    ) -> str:
        """构建风格约束（基于人格维度）"""

        constraints = []

        # 基于人格维度生成约束
        dominance = personality.dimensions.get(PersonalityDimension.DOMINANCE, 0.5)
        if dominance > 0.7:
            constraints.append("说话应该有控制欲和自信，使用明确的表述")
        elif dominance < 0.3:
            constraints.append("说话应该比较谦逊或犹豫，可以使用委婉的语气")

        risk_tolerance = personality.dimensions.get(PersonalityDimension.RISK_TOLERANCE, 0.5)
        if risk_tolerance > 0.7:
            constraints.append("更愿意表达大胆的观点")
        elif risk_tolerance < 0.3:
            constraints.append("倾向于保守和谨慎的表达")

        deception_comfort = personality.dimensions.get(PersonalityDimension.DECEPTION_COMFORT, 0.5)
        if deception_comfort < 0.4:
            constraints.append("尽量避免明显的欺骗或模糊表述")

        logic_capacity = personality.dimensions.get(PersonalityDimension.LOGIC_CAPACITY, 0.5)
        if logic_capacity > 0.7:
            constraints.append("倾向于逻辑分析和详细推理")
        elif logic_capacity < 0.4:
            constraints.append("更依赖直觉和感受进行表达")

        consistency = personality.dimensions.get(PersonalityDimension.CONSISTENCY, 0.5)
        if consistency > 0.6:
            constraints.append("保持前后一致的行为和表达风格")

        # 基于当前状态调整
        if mental_state.stress_level > 0.7:
            constraints.append("当前压力较大，表达可能会有些紧张或急促")
        elif mental_state.confidence > 0.7:
            constraints.append("当前比较自信，表达会更果断")

        if not constraints:
            constraints.append("自然表达自己的真实想法即可")

        return f"""## 表达风格

{chr(10).join(f"- {c}" for c in constraints)}"""

    def _describe_stress_level(self, stress_level: float) -> str:
        """描述压力水平"""
        if stress_level > 0.8:
            return "极度紧张"
        elif stress_level > 0.6:
            return "比较紧张"
        elif stress_level > 0.4:
            return "有些压力"
        elif stress_level > 0.2:
            return "略显紧张"
        else:
            return "比较平静"

    def _describe_confidence_level(self, confidence: float) -> str:
        """描述自信水平"""
        if confidence > 0.8:
            return "对自己判断极度自信"
        elif confidence > 0.6:
            return "对自己判断比较自信"
        elif confidence > 0.4:
            return "对自己的判断有中等信心"
        elif confidence > 0.2:
            return "对自己的判断不太确定"
        else:
            return "对自己的判断毫无把握"

    def _describe_motivation_impact(self, motivation: str, strength: float) -> str:
        """描述动机影响"""
        if strength > 0.7:
            strength_desc = "强烈地"
        elif strength > 0.5:
            strength_desc = "明显地"
        elif strength > 0.3:
            strength_desc = "一定程度地"
        else:
            strength_desc = "轻微地"

        motivation_descriptions = {
            "survival": f"{strength_desc}担心自己的安全",
            "control": f"{strength_desc}想要掌控局势",
            "revenge": f"{strength_desc}想要报复某人",
            "validation": f"{strength_desc}希望获得他人认可",
            "team": f"{strength_desc}为团队目标而努力",
        }

        return motivation_descriptions.get(motivation, f"{strength_desc}受到某种动机驱动")

    def _get_intent_description(self, intent: IntentType) -> str:
        """获取意图描述"""
        descriptions = {
            IntentType.STRONG_ACCUSE: "强烈质疑",
            IntentType.TEST_SUSPECT: "试探性质疑",
            IntentType.FOLLOW_OTHERS: "支持他人",
            IntentType.LOW_PROFILE_SPEECH: "低调表达",
            IntentType.EMOTIONAL_APPEAL: "情感表达",
            IntentType.VOTE_SUSPECT: "投票选择",
            IntentType.VOTE_SAFE_TARGET: "安全投票",
            IntentType.ABSTAIN_VOTE: "弃票决定",
        }
        return descriptions.get(intent, "想法")

    def _contains_forbidden_terms(self, prompt: str) -> bool:
        """检查是否包含禁用词汇"""
        forbidden_terms = [
            '预言家', '女巫', '守卫', '猎人', '狼人',  # 具体角色名
            '杀', '毒', '验', '守',  # 具体动作
            '最优策略', '必胜', '攻略',  # 策略指导
            '身份', '阵营', '好人', '坏人',  # 直接身份描述
        ]

        prompt_lower = prompt.lower()
        return any(term in prompt_lower for term in forbidden_terms)