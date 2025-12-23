"""
Decision Models - 决策数据模型

定义意图、决策等核心数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class IntentType(str, Enum):
    """意图类型 - 抽象级意图定义

    关键：这些是意图，不是具体规则动作
    """

    # === 白天发言意图 ===
    STRONG_ACCUSE = "strong_accuse"
    TEST_SUSPECT = "test_suspect"
    FOLLOW_OTHERS = "follow_others"
    LOW_PROFILE_SPEECH = "low_profile_speech"
    EMOTIONAL_APPEAL = "emotional_appeal"
    LOGICAL_ANALYSIS = "logical_analysis"
    QUESTION_OTHERS = "question_others"
    REVEAL_INFORMATION = "reveal_information"  # 故意模糊，不是具体技能

    # === 投票意图 ===
    VOTE_SUSPECT = "vote_suspect"
    VOTE_SAFE_TARGET = "vote_safe_target"
    ABSTAIN_VOTE = "abstain_vote"
    STRATEGIC_VOTE = "strategic_vote"  # 策略性投票

    # === 夜晚动作意图（高度抽象）===
    PROTECT_TARGET = "protect_target"      # 守卫类意图
    INVESTIGATE_TARGET = "investigate_target"  # 调查类意图
    KILL_TARGET = "kill_target"            # 击杀类意图
    USE_SPECIAL_ABILITY = "use_special_ability"  # 特殊能力使用
    SKIP_NIGHT_ACTION = "skip_night_action"  # 放弃夜晚行动

    # === 互动意图 ===
    REQUEST_INFORMATION = "request_information"
    SHARE_SUSPICIONS = "share_suspicions"
    DEFEND_OTHERS = "defend_others"
    FORM_ALLIANCE = "form_alliance"


class Intent(BaseModel):
    """意图定义

    描述一个抽象的行为意图，不涉及具体规则
    """

    intent_type: IntentType = Field(description="意图类型")
    description: str = Field(description="意图描述，避免具体规则术语")
    required_parameters: List[str] = Field(
        default_factory=list,
        description="此意图需要的参数（如'target'）"
    )
    compatible_phases: List[str] = Field(
        default_factory=list,
        description="适用的游戏阶段列表"
    )
    compatible_roles: List[str] = Field(
        default_factory=list,
        description="适用角色类型（'all'表示通用）"
    )
    base_weight: float = Field(
        default=1.0,
        ge=0.0,
        description="基础权重（人格调整前）"
    )

    def is_compatible_with_phase(self, phase: str) -> bool:
        """检查是否与指定阶段兼容"""
        return phase in self.compatible_phases or "all" in self.compatible_phases

    def is_compatible_with_role(self, role: str) -> bool:
        """检查是否与指定角色兼容"""
        return role in self.compatible_roles or "all" in self.compatible_roles or not self.compatible_roles

    def requires_target(self) -> bool:
        """检查是否需要目标参数"""
        return "target" in self.required_parameters


class IntentWithWeight(Intent):
    """带权重的意图"""

    weight: float = Field(ge=0.0, description="经过人格和动机调整后的权重")
    target: Optional[int] = Field(default=None, description="目标玩家ID（如果需要）")
    reasoning: Optional[str] = Field(default=None, description="选择此意图的推理过程")
    motivation_influence: Optional[Dict[str, float]] = Field(
        default=None,
        description="动机影响分析"
    )

    def __str__(self) -> str:
        """字符串表示"""
        if self.target:
            return f"{self.intent_type.value}(target={self.target}, weight={self.weight:.2f})"
        else:
            return f"{self.intent_type.value}(weight={self.weight:.2f})"


class Decision(BaseModel):
    """最终决策

    AI系统的最终输出，包含意图和自然语言表达
    """

    intent: IntentType = Field(description="选择的意图类型")
    target: Optional[int] = Field(default=None, description="目标玩家ID（如果适用）")
    speech: str = Field(description="自然语言表达")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="决策置信度"
    )
    reasoning_trace: Optional[str] = Field(
        default=None,
        description="决策推理轨迹（用于调试和分析）"
    )
    timestamp: Optional[str] = Field(default=None, description="决策时间戳")

    # 人格信息（用于分析）
    personality_name: Optional[str] = Field(default=None, description="人格名称")
    motivation_state: Optional[Dict[str, float]] = Field(
        default=None,
        description="决策时的动机状态"
    )

    def __post_init__(self):
        """后处理"""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def is_valid_format(self) -> bool:
        """验证决策格式是否有效"""
        return (
            self.intent is not None and
            self.speech and len(self.speech.strip()) > 0 and
            0.0 <= self.confidence <= 1.0
        )

    def get_decision_summary(self) -> str:
        """获取决策摘要"""
        summary = f"意图: {self.intent.value}"
        if self.target:
            summary += f", 目标: {self.target}"
        summary += f", 置信度: {self.confidence:.2f}"
        return summary


class DecisionContext(BaseModel):
    """决策上下文

    包含决策所需的所有非敏感上下文信息
    """

    player_id: int = Field(description="决策玩家ID")
    phase: str = Field(description="当前游戏阶段")
    round: int = Field(description="当前回合")
    can_act: bool = Field(description="是否可以行动")
    is_alive: bool = Field(description="是否存活")

    # 对环境信息的抽象描述
    recent_activity: str = Field(description="近期活动描述")
    pressure_level: float = Field(ge=0.0, le=1.0, description="当前感知的压力水平")
    social_dynamics: str = Field(description="社交环境描述")

    # 约束条件
    constraints: List[str] = Field(default_factory=list, description="决策约束")

    def get_activity_summary(self) -> str:
        """获取活动概要"""
        if self.pressure_level > 0.7:
            return f"当前局势{self.recent_activity}，你感到较大压力"
        elif self.pressure_level > 0.4:
            return f"当前局势{self.recent_activity}，有些紧张"
        else:
            return f"当前局势{self.recent_activity}，相对平静"


class DecisionResult(BaseModel):
    """决策结果

    包含决策执行的结果或尝试记录
    """

    success: bool = Field(description="决策是否成功执行")
    decision: Decision = Field(description="原始决策")
    execution_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="执行详情"
    )
    error_message: Optional[str] = Field(default=None, description="错误信息（如果有）")
    alternative_action: Optional[str] = Field(
        default=None,
        description="实际执行的替代操作"
    )