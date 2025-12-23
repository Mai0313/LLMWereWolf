"""
Personality Data Models - 人格数据模型

定义人格系统的核心数据结构，严格遵循SPEC规范。
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, Any
from enum import Enum
import random


class PersonalityDimension(str, Enum):
    """人格维度 - SPEC定义的8个核心维度"""

    RISK_TOLERANCE = "risk_tolerance"          # 风险承受度：面对危险和不确定性时的倾向
    SOCIAL_PRESSURE = "social_pressure"        # 社交压力敏感：在群体压力下改变观点的程度
    DOMINANCE = "dominance"                    # 控制欲：想要主导局面和决策的强度
    LOGIC_CAPACITY = "logic_capacity"          # 推理能力：逻辑分析和推断的能力
    DECEPTION_COMFORT = "deception_comfort"    # 撒谎舒适度：进行欺骗行为时的心理舒适程度
    TRUST_BASELINE = "trust_baseline"          # 初始信任度对他人陈述的默认信任水平
    EGO = "ego"                               # 自尊敏感：对个人形象和面子的重要程度
    CONSISTENCY = "consistency"               # 一致性需求：保持言行一致的心理需求


class MotivationType(str, Enum):
    """动机类型 - SPEC定义的5个核心动机"""

    SURVIVAL = "survival"      # 生存焦虑：对被淘汰的恐惧
    CONTROL = "control"        # 控场欲：想要掌控游戏局面的欲望
    REVENGE = "revenge"        # 报复：想要惩罚伤害自己的人
    VALIDATION = "validation"  # 被认可：想要获得他人认同和支持
    TEAM = "team"             # 阵营目标：为所在阵营获胜的努力


class Personality(BaseModel):
    """人格配置模型

    包含8个维度的数值化人格特质，每个维度取值0.0-1.0
    """

    dimensions: Dict[PersonalityDimension, float] = Field(
        description="8个维度的人格特质，每个值0.0-1.0"
    )

    @validator('dimensions')
    def validate_dimensions(cls, v):
        """验证所有维度值在合理范围内"""
        for dim, value in v.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Personality dimension {dim} must be between 0.0 and 1.0, got {value}")

        # 确保所有8个维度都存在
        required_dims = set(PersonalityDimension)
        provided_dims = set(v.keys())
        missing_dims = required_dims - provided_dims

        if missing_dims:
            raise ValueError(f"Missing personality dimensions: {missing_dims}")

        return v

    def get_dimension_value(self, dimension: PersonalityDimension) -> float:
        """获取指定维度的值"""
        return self.dimensions.get(dimension, 0.5)

    def get_description(self) -> str:
        """生成人格描述"""
        traits = []

        if self.dimensions[PersonalityDimension.DOMINANCE] > 0.7:
            traits.append("有很强的控制欲")
        elif self.dimensions[PersonalityDimension.DOMINANCE] < 0.3:
            traits.append("比较顺从")

        if self.dimensions[PersonalityDimension.RISK_TOLERANCE] > 0.7:
            traits.append("喜欢冒险")
        elif self.dimensions[PersonalityDimension.RISK_TOLERANCE] < 0.3:
            traits.append("谨慎保守")

        if self.dimensions[PersonalityDimension.DECEPTION_COMFORT] > 0.7:
            traits.append("善于撒谎")
        elif self.dimensions[PersonalityDimension.DECEPTION_COMFORT] < 0.3:
            traits.append("诚实直率")

        if self.dimensions[PersonalityDimension.LOGIC_CAPACITY] > 0.7:
            traits.append("逻辑推理能力强")
        elif self.dimensions[PersonalityDimension.LOGIC_CAPACITY] < 0.3:
            traits.append("更凭直觉行事")

        if not traits:
            traits.append("性格均衡")

        return "、".join(traits)


class MentalState(BaseModel):
    """动态心理状态

    记录玩家在游戏过程中的心理变化
    """

    motivations: Dict[MotivationType, float] = Field(
        description="5个动机的当前强度，0.0-1.0"
    )

    stress_level: float = Field(
        ge=0.0,
        le=1.0,
        default=0.0,
        description="当前压力水平，0.0为平静，1.0极度紧张"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        default=0.5,
        description="当前自信心水平，0.0毫无信心，1.0极度自信"
    )

    last_updated_round: int = Field(
        default=0,
        description="上次更新的回合数"
    )

    @validator('motivations')
    def validate_motivations(cls, v):
        """验证所有动机值在合理范围内"""
        for motivation, value in v.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Motivation {motivation} must be between 0.0 and 1.0, got {value}")

        # 确保所有5个动机都存在
        required_motivations = set(MotivationType)
        provided_motivations = set(v.keys())
        missing_motivations = required_motivations - provided_motivations

        if missing_motivations:
            raise ValueError(f"Missing motivations: {missing_motivations}")

        return v

    def update_motivation(self, motivation: MotivationType, delta: float):
        """更新动机强度，带边界检查"""
        current_value = self.motivations.get(motivation, 0.5)
        new_value = max(0.0, min(1.0, current_value + delta))
        self.motivations[motivation] = new_value

    def decay_motivations(self, decay_rate: float = 0.1):
        """动机强度自然衰减"""
        for motivation in self.motivations:
            self.motivations[motivation] = max(
                0.1,  # 保持基础动机
                self.motivations[motivation] * (1.0 - decay_rate)
            )

    def get_strongest_motivation(self) -> tuple[MotivationType, float]:
        """获取最强的动机"""
        return max(self.motivations.items(), key=lambda x: x[1])


class PersonalityProfile(BaseModel):
    """完整人格档案

    结合静态人格特质和动态心理状态
    """

    base_personality: Personality = Field(description="基础人格特质")
    current_mental_state: MentalState = Field(description="当前心理状态")
    personality_name: str = Field(description="人格名称")
    description: Optional[str] = Field(default=None, description="人格描述")

    # 认知过滤器（延迟初始化）
    cognitive_filter: Optional[Any] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True  # 允许认知过滤器的任意类型

    def update_mental_state(self, round_number: int):
        """更新心理状态（每回合调用）"""
        if round_number > self.current_mental_state.last_updated_round:
            # 自然衰减
            self.current_mental_state.decay_motivations()
            self.current_mental_state.last_updated_round = round_number

    def is_stressed(self) -> bool:
        """判断是否处于高压力状态"""
        return self.current_mental_state.stress_level > 0.7

    def is_confident(self) -> bool:
        """判断是否处于高自信状态"""
        return self.current_mental_state.confidence > 0.7

    def get_risk_tolerance(self) -> float:
        """获取当前风险承受能力（结合人格和状态）"""
        base_risk = self.base_personality.get_dimension_value(PersonalityDimension.RISK_TOLERANCE)
        stress_modifier = 1.0 - self.current_mental_state.stress_level * 0.3  # 压力降低风险承受
        confidence_modifier = self.current_mental_state.confidence * 0.2  # 自信增加风险承受

        return max(0.0, min(1.0, base_risk * stress_modifier + confidence_modifier))

    def should_be_deceptive(self) -> bool:
        """判断是否应该采取欺骗策略"""
        base_deception = self.base_personality.get_dimension_value(PersonalityDimension.DECEPTION_COMFORT)
        logic_factor = self.base_personality.get_dimension_value(PersonalityDimension.LOGIC_CAPACITY)

        # 高逻辑能力的人在需要时更愿意欺骗
        effective_deception = base_deception * (0.7 + logic_factor * 0.3)

        return effective_deception > 0.5

    def get_speech_style_modifier(self) -> Dict[str, float]:
        """获取语言风格调节因子"""
        return {
            "dominance": self.base_personality.get_dimension_value(PersonalityDimension.DOMINANCE),
            "emotional": 1.0 - self.base_personality.get_dimension_value(PersonalityDimension.LOGIC_CAPACITY),
            "consistent": self.base_personality.get_dimension_value(PersonalityDimension.CONSISTENCY),
            "social_pressure_sensitivity": self.base_personality.get_dimension_value(
                PersonalityDimension.SOCIAL_PRESSURE
            ),
        }