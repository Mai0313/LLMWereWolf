"""
Intent Registry - 意图注册表

管理所有可用意图，提供意图查询和过滤功能
"""

from typing import List, Dict, Optional
from .models import Intent, IntentType
from ..types import GamePhase


class IntentRegistry:
    """意图注册表

    系统的核心意图库，定义所有可用的抽象意图
    """

    def __init__(self):
        self._intents: Dict[str, List[Intent]] = {}
        self._role_intents: Dict[str, List[Intent]] = {}
        self._intents_by_type: Dict[IntentType, Intent] = {}

        self._register_all_intents()

    def get_intents_for_phase(
        self,
        phase: GamePhase,
        role_hint: Optional[str] = None,
        can_act: bool = True
    ) -> List[Intent]:
        """获取指定阶段的可用意图"""

        # 获取基础意图（通用意图）
        base_intents = self._intents.get(phase.value, [])

        # 如果玩家不能行动，只保留被动意图
        if not can_act:
            base_intents = [intent for intent in base_intents if self._is_passive_intent(intent)]

        # 添加角色特定意图
        if role_hint and role_hint in self._role_intents:
            role_specific = self._role_intents[role_hint]
            base_intents.extend(role_specific)

        return base_intents

    def get_intent_by_type(self, intent_type: IntentType) -> Optional[Intent]:
        """根据类型获取意图"""
        return self._intents_by_type.get(intent_type)

    def list_all_intents(self) -> Dict[str, List[Intent]]:
        """列出所有意图（按阶段组织）"""
        return self._intents.copy()

    def validate_intent_intent(self, intent: Intent) -> bool:
        """验证意图格式是否符合SPEC"""

        # 检查描述中是否包含禁用术语
        forbidden_terms = [
            '预言家', '女巫', '守卫', '猎人', '狼人',
            '技能', '能力', '身份', '阵营',
            '杀', '毒', '验', '守'
        ]

        description_lower = intent.description.lower()
        for term in forbidden_terms:
            if term in description_lower:
                return False

        return True

    def _register_all_intents(self):
        """注册所有意图"""

        # === 白天讨论阶段意图 ===
        day_discussion_intents = [
            Intent(
                intent_type=IntentType.STRONG_ACCUSE,
                description="强烈地质疑某个玩家，认为其行为可疑",
                required_parameters=["target"],
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=1.2
            ),
            Intent(
                intent_type=IntentType.TEST_SUSPECT,
                description="试探性地询问和观察某个可疑对象",
                required_parameters=["target"],
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.8
            ),
            Intent(
                intent_type=IntentType.FOLLOW_OTHERS,
                description="赞同和支持他人的观点或提议",
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.6
            ),
            Intent(
                intent_type=IntentType.LOW_PROFILE_SPEECH,
                description="低调发言，避免引起过多注意",
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.7
            ),
            Intent(
                intent_type=IntentType.EMOTIONAL_APPEAL,
                description="用情感色彩强烈的语言表达自己",
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=1.0
            ),
            Intent(
                intent_type=IntentType.LOGICAL_ANALYSIS,
                description="基于观察和推理进行逻辑分析",
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.9
            ),
            Intent(
                intent_type=IntentType.QUESTION_OTHERS,
                description="向其他玩家提出问题，收集信息",
                required_parameters=["target"],
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.8
            ),
            Intent(
                intent_type=IntentType.SHARE_SUSPICIONS,
                description="分享自己的怀疑和观察，但不过于直接",
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.7
            ),
            Intent(
                intent_type=IntentType.DEFEND_OTHERS,
                description="为被质疑的玩家进行辩护",
                required_parameters=["target"],
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.6
            ),
            Intent(
                intent_type=IntentType.REQUEST_INFORMATION,
                description="向他人请求特定的信息或解释",
                compatible_phases=["day_discussion"],
                compatible_roles=["all"],
                base_weight=0.7
            ),
        ]

        # === 投票阶段意图 ===
        voting_intents = [
            Intent(
                intent_type=IntentType.VOTE_SUSPECT,
                description="投票给你最怀疑的玩家",
                required_parameters=["target"],
                compatible_phases=["day_voting"],
                compatible_roles=["all"],
                base_weight=1.0
            ),
            Intent(
                intent_type=IntentType.VOTE_SAFE_TARGET,
                description="投票给相对安全的目标，避免关键错误",
                required_parameters=["target"],
                compatible_phases=["day_voting"],
                compatible_roles=["all"],
                base_weight=0.7
            ),
            Intent(
                intent_type=IntentType.ABSTAIN_VOTE,
                description="选择不参与投票",
                compatible_phases=["day_voting"],
                compatible_roles=["all"],
                base_weight=0.5
            ),
            Intent(
                intent_type=IntentType.STRATEGIC_VOTE,
                description="基于策略考虑而非单纯怀疑进行投票",
                required_parameters=["target"],
                compatible_phases=["day_voting"],
                compatible_roles=["all"],
                base_weight=0.8
            ),
        ]

        # === 夜晚角色特定意图（高度抽象）===

        night_role_intents = {
            # 狼人相关
            "werewolf": [
                Intent(
                    intent_type=IntentType.KILL_TARGET,
                    description="和同伴讨论选择今晚的目标",
                    required_parameters=["target"],
                    compatible_phases=["night"],
                    compatible_roles=["werewolf"],
                    base_weight=1.0
                ),
                Intent(
                    intent_type=IntentType.SKIP_NIGHT_ACTION,
                    description="选择今晚不采取行动",
                    compatible_phases=["night"],
                    compatible_roles=["werewolf"],
                    base_weight=0.3
                ),
            ],

            # 预言家相关
            "seer": [
                Intent(
                    intent_type=IntentType.INVESTIGATE_TARGET,
                    description="选择一人进行身份探查",
                    required_parameters=["target"],
                    compatible_phases=["night"],
                    compatible_roles=["seer"],
                    base_weight=1.0
                ),
                Intent(
                    intent_type=IntentType.SKIP_NIGHT_ACTION,
                    description="选择今晚不使用能力",
                    compatible_phases=["night"],
                    compatible_roles=["seer"],
                    base_weight=0.2
                ),
            ],

            # 女巫相关
            "witch": [
                Intent(
                    intent_type=IntentType.USE_SPECIAL_ABILITY,
                    description="考虑使用手中的神秘药剂",
                    required_parameters=["target"],  # 目标可能是救人或毒杀
                    compatible_phases=["night"],
                    compatible_roles=["witch"],
                    base_weight=0.8
                ),
                Intent(
                    intent_type=IntentType.SKIP_NIGHT_ACTION,
                    description="决定不使用任何药剂",
                    compatible_phases=["night"],
                    compatible_roles=["witch"],
                    base_weight=0.5
                ),
            ],

            # 守卫相关
            "guard": [
                Intent(
                    intent_type=IntentType.PROTECT_TARGET,
                    description="选择一人进行保护",
                    required_parameters=["target"],
                    compatible_phases=["night"],
                    compatible_roles=["guard"],
                    base_weight=1.0
                ),
                Intent(
                    intent_type=IntentType.SKIP_NIGHT_ACTION,
                    description="选择不进行保护",
                    compatible_phases=["night"],
                    compatible_roles=["guard"],
                    base_weight=0.3
                ),
            ],

            # 村民和其他（无夜晚能力）
            "villager": [
                Intent(
                    intent_type=IntentType.SKIP_NIGHT_ACTION,
                    description="安静度过夜晚",
                    compatible_phases=["night"],
                    compatible_roles=["villager"],
                    base_weight=1.0
                ),
            ],

            # 猎人相关
            "hunter": [
                Intent(
                    intent_type=IntentType.SKIP_NIGHT_ACTION,
                    description="保持警惕，安静度过夜晚",
                    compatible_phases=["night"],
                    compatible_roles=["hunter"],
                    base_weight=1.0
                ),
            ],
        }

        # 存储意图
        self._intents["day_discussion"] = day_discussion_intents
        self._intents["day_voting"] = voting_intents
        self._intents["night"] = []  # 夜晚意图都是角色特定的

        self._role_intents = night_role_intents

        # 建立类型到意图的映射
        all_intents = []
        for intents in self._intents.values():
            all_intents.extend(intents)
        for intents in self._role_intents.values():
            all_intents.extend(intents)

        for intent in all_intents:
            if intent.intent_type not in self._intents_by_type:
                self._intents_by_type[intent.intent_type] = intent

    def _is_passive_intent(self, intent: Intent) -> bool:
        """判断是否为被动意图（不需要主动行动）"""
        passive_intents = [
            IntentType.SKIP_NIGHT_ACTION,
            IntentType.LOW_PROFILE_SPEECH,
            IntentType.ABSTAIN_VOTE,
        ]
        return intent.intent_type in passive_intents

    def get_intent_statistics(self) -> Dict[str, int]:
        """获取意图统计信息"""
        stats = {
            "total_intents": 0,
            "phase_counts": {},
            "role_specific_counts": {},
        }

        # 统计各阶段意图数
        for phase, intents in self._intents.items():
            stats["phase_counts"][phase] = len(intents)
            stats["total_intents"] += len(intents)

        # 统计角色特定意图数
        for role, intents in self._role_intents.items():
            stats["role_specific_counts"][role] = len(intents)
            stats["total_intents"] += len(intents)

        return stats