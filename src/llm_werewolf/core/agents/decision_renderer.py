"""
Decision Renderer - 决策渲染器

处理意图到自然语言的转换
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
import re

from ..personality.models import PersonalityProfile
from ..decision.models import IntentType
from ..observation.player_view import PlayerView


class BaseDecisionRenderer(ABC):
    """决策渲染器基类"""

    @abstractmethod
    def render(
        self,
        intent: IntentType,
        personality_profile: PersonalityProfile,
        player_view: PlayerView,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """将意图渲染为自然语言"""
        pass


class RuleBasedRenderer(BaseDecisionRenderer):
    """基于规则的渲染器"""

    def __init__(self):
        # 基础模板库
        self.intent_templates = self._load_intent_templates()

        # 人格修饰符
        self.personality_modifiers = self._load_personality_modifiers()

    def render(
        self,
        intent: IntentType,
        personality_profile: PersonalityProfile,
        player_view: PlayerView,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """基于规则渲染意图"""

        # 1. 获取基础模板
        base_templates = self.intent_templates.get(intent, ["我需要表达我的看法。"])

        # 2. 选择基础表达
        base_expression = self._select_template(base_templates, personality_profile)

        # 3. 应用人格修饰
        modified_expression = self._apply_personality_modifiers(
            base_expression, personality_profile
        )

        # 4. 添加上下文适配
        contextualized_expression = self._apply_context_adaptation(
            modified_expression, player_view, context
        )

        # 5. 最终清理
        final_expression = self._clean_expression(contextualized_expression)

        return final_expression

    def _load_intent_templates(self) -> Dict[IntentType, List[str]]:
        """加载意图模板"""
        return {
            IntentType.STRONG_ACCUSE: [
                "我认为这个人明显有问题。",
                "我强烈怀疑这个人。",
                "这个人的行为太可疑了。",
                "我确信这个人不是好人。",
                "这个人必须被重点关注。"
            ],
            IntentType.TEST_SUSPECT: [
                "能解释一下你的行为吗？",
                "我想听听你的想法。",
                "你对这件事怎么看？",
                "能说说你为什么这么做吗？",
                "我想了解更多情况。"
            ],
            IntentType.FOLLOW_OTHERS: [
                "我同意刚才的说法。",
                "说得对，我也是这么想的。",
                "这个分析很有道理。",
                "我支持这个观点。",
                "确实如此，我也同意。"
            ],
            IntentType.LOW_PROFILE_SPEECH: [
                "让我再观望一下。",
                "我需要更多时间思考。",
                "暂时没什么要说的。",
                "我再看看情况发展。",
                "我保持中立观察。"
            ],
            IntentType.EMOTIONAL_APPEAL: [
                "这让我真的很担心。",
                "我感到很不安。",
                "这样下去真的不行。",
                "我们需要小心行事。",
                "这让我感到害怕。"
            ],
            IntentType.ABSTAIN_VOTE: [
                "我选择弃票。",
                "这次不投票了。",
                "需要更多信息再决定。",
                "我保持观望态度。",
                "暂时不参与投票。"
            ],
            IntentType.VOTE_SUSPECT: [
                "我投票给这个人。",
                "我认为应该投这个人。",
                "这是我的选择。",
                "决定投这个人。",
                "我就是投这个。"
            ]
        }

    def _load_personality_modifiers(self) -> Dict[str, Dict[str, str]]:
        """加载人格修饰符"""
        return {
            "dominance": {
                "high": ["确信", "明显", "必须", "强烈"],
                "low": ["可能", "或许", "考虑", "觉得"]
            },
            "logic_capacity": {
                "high": ["分析", "推理", "证据", "逻辑"],
                "low": ["感觉", "直觉", "就是", "单纯"]
            },
            "deception_comfort": {
                "high": ["某种程度上", "从特定角度", "可以说", "或许"]
            }
        }

    def _select_template(self, templates: List[str], personality_profile: PersonalityProfile) -> str:
        """基于人格选择模板"""
        dominance = personality_profile.base_personality.dimensions.get("dominance", 0.5)

        # 高控制欲的更选择确定性的表达
        if dominance > 0.7:
            strong_templates = [t for t in templates if any(
                word in t for word in ["强烈", "确信", "必须", "明显"]
            )]
            if strong_templates:
                return max(strong_templates, key=len)

        return templates[0] if templates else "我需要表达我的看法。"

    def _apply_personality_modifiers(self, expression: str, personality_profile: PersonalityProfile) -> str:
        """应用人格修饰词"""

        modified_expression = expression

        # 支配性修饰
        dominance = personality_profile.base_personality.dimensions.get("dominance", 0.5)
        if dominance > 0.8:
            modified_expression = self._intensify_expression(modified_expression)
        elif dominance < 0.3:
            modified_expression = self._soften_expression(modified_expression)

        # 逻辑能力修饰
        logic_capacity = personality_profile.base_personality.dimensions.get("logic_capacity", 0.5)
        if logic_capacity > 0.7:
            modified_expression = self._add_logic_elements(modified_expression)
        elif logic_capacity < 0.4:
            modified_expression = self._add_emotional_elements(modified_expression)

        return modified_expression

    def _apply_context_adaptation(
        self,
        expression: str,
        player_view: PlayerView,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """应用上下文适配"""

        adapted_expression = expression

        # 根据游戏阶段调整
        if player_view.current_phase.value == "day_voting":
            adapted_expression = self._make_expression_decisive(adapted_expression)
        elif player_view.current_phase.value == "day_discussion":
            adapted_expression = self._make_expression_exploratory(adapted_expression)

        # 根据压力水平调整
        if player_view.context.get("pressure_level", 0) > 0.7:
            adapted_expression = self._add_urgency_elements(adapted_expression)

        return adapted_expression

    def _clean_expression(self, expression: str) -> str:
        """清理表达的最终效果"""
        # 移除重复词
        expression = re.sub(r'(.)\1{2,}', r'\1', expression)

        # 确保以标点结尾
        if expression and expression[-1] not in "。！？...":
            expression += "。"

        return expression.strip()

    def _intensify_expression(self, expression: str) -> str:
        """强化表达"""
        intensity_words = ["很", "非常", "确实", "真的"]
        if not any(word in expression for word in intensity_words):
            return expression.replace("我", "我很") if expression.startswith("我") else expression
        return expression

    def _soften_expression(self, expression: str) -> str:
        """软化表达"""
        soft_words = ["或许", "可能", "大概", "感觉"]
        if not any(word in expression for word in soft_words):
            return expression.replace("我认为", "我感觉").replace("确信", "觉得")
        return expression

    def _add_logic_elements(self, expression: str) -> str:
        """添加逻辑元素"""
        if "因为" not in expression and len(expression) < 20:
            return f"基于观察，{expression}"
        return expression

    def _add_emotional_elements(self, expression: str) -> str:
        """添加情感元素"""
        if "感觉" not in expression and len(expression) < 15:
            return f"我感觉{expression}"
        return expression

    def _make_expression_decisive(self, expression: str) -> str:
        """使表达更果断"""
        if "?" in expression:
            return expression.replace("?", "。")
        return expression

    def _make_expression_exploratory(self, expression: str) -> str:
        """使表达更探索性"""
        if "。" in expression and len(expression) < 20:
            return expression.replace("。", "，我想了解更多。")
        return expression

    def _add_urgency_elements(self, expression: str) -> str:
        """添加紧急元素"""
        if "紧急" not in expression and "必须" not in expression:
            return f"我觉得{expression[:10]}这个问题需要紧急关注。"
        return expression


class LLMBasedRenderer(BaseDecisionRenderer):
    """基于LLM的渲染器"""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.rule_based_renderer = RuleBasedRenderer()  # 备用渲染器

    def render(
        self,
        intent: IntentType,
        personality_profile: PersonalityProfile,
        player_view: PlayerView,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """使用LLM渲染，失败时回退到规则渲染"""

        try:
            # 构建LLM提示
            prompt = self._build_llm_prompt(intent, personality_profile, player_view)

            # 获取LLM响应
            response = self.llm_client.get_response(prompt)

            # 验证响应
            if self._validate_response(response):
                return self._clean_response(response)
            else:
                raise ValueError("LLM response validation failed")

        except Exception as e:
            print(f"Warning: LLM rendering failed ({e}), falling back to rule-based")
            return self.rule_based_renderer.render(intent, personality_profile, player_view, context)

    def _build_llm_prompt(
        self,
        intent: IntentType,
        personality_profile: PersonalityProfile,
        player_view: PlayerView
    ) -> str:
        """构建LLM提示"""
        prompt = f"""你是一个{personality_profile.personality_name}。

你的性格特点：{personality_profile.base_personality.get_description()}

当前游戏情况：{player_view.current_time}

你的意图是：{intent.value}

请你用最自然的方式表达这个意图。不要说你正在"推理"或"分析"，直接说结论。
保持你一贯的性格特点。

请你直接表达观点："""

        return prompt

    def _validate_response(self, response: str) -> bool:
        """验证LLM响应"""
        if not response or len(response.strip()) < 3:
            return False

        # 检查是否包含过多的元语言
        meta_indicators = ["我分析", "我认为", "我推论", "我考虑"]
        response_lower = response.lower()
        meta_count = sum(1 for indicator in meta_indicators if indicator in response_lower)

        # 如果超过50%是元语言，则认为无效
        if len(response.split()) > 0 and meta_count / len(response.split()) > 0.5:
            return False

        return True

    def _clean_response(self, response: str) -> str:
        """清理LLM响应"""
        lines = response.strip().split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith(("我分析", "我认为", "我推论")):
                cleaned_lines.append(line)

        result = '\n'.join(cleaned_lines).strip()

        # 确保有标点结尾
        if result and result[-1] not in "。！？...":
            result += "。"

        return result