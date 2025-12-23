"""
Personality Factory and Predefined Personalities - 人格工厂和预定义人格

提供人格创建、配置加载和预定义人格模板。
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import random

from .models import Personality, PersonalityDimension, MentalState, PersonalityProfile, MotivationType


class PersonalityFactory:
    """人格配置工厂

    负责从配置文件、静态定义或随机生成创建人格实例
    """

    @staticmethod
    def create_from_config(config_path: str | Path) -> Personality:
        """从YAML配置文件创建人格"""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Personality config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return PersonalityFactory._create_from_dict(data)

    @staticmethod
    def _create_from_dict(data: Dict[str, Any]) -> Personality:
        """从字典数据创建人格"""
        dimensions = {}

        # 处理维度数据
        if 'dimensions' in data:
            for dim_name, value in data['dimensions'].items():
                try:
                    dimension = PersonalityDimension(dim_name)
                    dimensions[dimension] = float(value)
                except ValueError:
                    raise ValueError(f"Invalid personality dimension: {dim_name}")

        # 确保所有维度都有值（缺失的使用默认值0.5）
        for dim in PersonalityDimension:
            if dim not in dimensions:
                dimensions[dim] = 0.5

        return Personality(dimensions=dimensions)

    @staticmethod
    def create_random() -> Personality:
        """创建随机人格（用于测试）"""
        dimensions = {}
        for dim in PersonalityDimension:
            # 生成0.2-0.8之间的随机值，避免极端值
            dimensions[dim] = round(random.uniform(0.2, 0.8), 2)

        return Personality(dimensions=dimensions)

    @staticmethod
    def create_default_for_role(role_name: str) -> Personality:
        """根据角色创建默认人格"""

        role_personalities = {
            "werewolf": {
                PersonalityDimension.RISK_TOLERANCE: 0.7,
                PersonalityDimension.SOCIAL_PRESSURE: 0.6,
                PersonalityDimension.DOMINANCE: 0.8,
                PersonalityDimension.LOGIC_CAPACITY: 0.6,
                PersonalityDimension.DECEPTION_COMFORT: 0.8,
                PersonalityDimension.TRUST_BASELINE: 0.3,
                PersonalityDimension.EGO: 0.7,
                PersonalityDimension.CONSISTENCY: 0.5,
            },
            "seer": {
                PersonalityDimension.RISK_TOLERANCE: 0.4,
                PersonalityDimension.SOCIAL_PRESSURE: 0.5,
                PersonalityDimension.DOMINANCE: 0.6,
                PersonalityDimension.LOGIC_CAPACITY: 0.9,
                PersonalityDimension.DECEPTION_COMFORT: 0.4,
                PersonalityDimension.TRUST_BASELINE: 0.6,
                PersonalityDimension.EGO: 0.5,
                PersonalityDimension.CONSISTENCY: 0.8,
            },
            "witch": {
                PersonalityDimension.RISK_TOLERANCE: 0.5,
                PersonalityDimension.SOCIAL_PRESSURE: 0.7,
                PersonalityDimension.DOMINANCE: 0.4,
                PersonalityDimension.LOGIC_CAPACITY: 0.8,
                PersonalityDimension.DECEPTION_COMFORT: 0.6,
                PersonalityDimension.TRUST_BASELINE: 0.4,
                PersonalityDimension.EGO: 0.6,
                PersonalityDimension.CONSISTENCY: 0.7,
            },
            "hunter": {
                PersonalityDimension.RISK_TOLERANCE: 0.6,
                PersonalityDimension.SOCIAL_PRESSURE: 0.4,
                PersonalityDimension.DOMINANCE: 0.7,
                PersonalityDimension.LOGIC_CAPACITY: 0.5,
                PersonalityDimension.DECEPTION_COMFORT: 0.5,
                PersonalityDimension.TRUST_BASELINE: 0.5,
                PersonalityDimension.EGO: 0.8,
                PersonalityDimension.CONSISTENCY: 0.6,
            },
            "villager": {
                PersonalityDimension.RISK_TOLERANCE: 0.4,
                PersonalityDimension.SOCIAL_PRESSURE: 0.8,
                PersonalityDimension.DOMINANCE: 0.3,
                PersonalityDimension.LOGIC_CAPACITY: 0.5,
                PersonalityDimension.DECEPTION_COMFORT: 0.3,
                PersonalityDimension.TRUST_BASELINE: 0.6,
                PersonalityDimension.EGO: 0.4,
                PersonalityDimension.CONSISTENCY: 0.6,
            },
        }

        dimensions = role_personalities.get(role_name.lower(), {})

        # 确保所有维度都有值
        for dim in PersonalityDimension:
            if dim not in dimensions:
                dimensions[dim] = 0.5

        return Personality(dimensions=dimensions)

    @staticmethod
    def create_full_profile(
        personality: Personality,
        profile_name: str,
        description: Optional[str] = None
    ) -> PersonalityProfile:
        """创建完整的人格档案"""

        # 初始化默认心理状态
        mental_state = MentalState(
            motivations={
                MotivationType.SURVIVAL: 0.5,
                MotivationType.CONTROL: 0.5,
                MotivationType.REVENGE: 0.3,
                MotivationType.VALIDATION: 0.5,
                MotivationType.TEAM: 0.6,
            },
            stress_level=0.2,  # 初始略紧张
            confidence=0.5,    # 初始中等自信
        )

        return PersonalityProfile(
            base_personality=personality,
            current_mental_state=mental_state,
            personality_name=profile_name,
            description=description or personality.get_description()
        )


class PredefinedPersonalities:
    """预定义人格库

    包含几种典型的人格模板，可直接使用或作为参考
    """

    # 人格模板配置
    PERSONALITY_TEMPLATES = {
        "aggressive_wolf": {
            "name": "激进型狼人",
            "description": "喜欢主动出击，控场欲强，善于欺骗",
            "dimensions": {
                "risk_tolerance": 0.8,
                "social_pressure": 0.3,
                "dominance": 0.9,
                "logic_capacity": 0.6,
                "deception_comfort": 0.9,
                "trust_baseline": 0.2,
                "ego": 0.8,
                "consistency": 0.4,
            }
        },
        "cautious_seer": {
            "name": "谨慎型预言家",
            "description": "逻辑分析强，行事谨慎，注重一致性",
            "dimensions": {
                "risk_tolerance": 0.3,
                "social_pressure": 0.5,
                "dominance": 0.6,
                "logic_capacity": 0.9,
                "deception_comfort": 0.4,
                "trust_baseline": 0.7,
                "ego": 0.5,
                "consistency": 0.8,
            }
        },
        "emotional_witch": {
            "name": "情绪化女巫",
            "description": "容易受情绪影响，社交敏感，追求认同",
            "dimensions": {
                "risk_tolerance": 0.5,
                "social_pressure": 0.9,
                "dominance": 0.4,
                "logic_capacity": 0.6,
                "deception_comfort": 0.6,
                "trust_baseline": 0.4,
                "ego": 0.6,
                "consistency": 0.3,
            }
        },
        "balanced_hunter": {
            "name": "平衡型猎人",
            "description": "性格均衡，有责任心，维护正义",
            "dimensions": {
                "risk_tolerance": 0.5,
                "social_pressure": 0.5,
                "dominance": 0.6,
                "logic_capacity": 0.6,
                "deception_comfort": 0.5,
                "trust_baseline": 0.5,
                "ego": 0.6,
                "consistency": 0.7,
            }
        },
        "passive_villager": {
            "name": "被动型平民",
            "description": "容易随大流，不喜冲突，寻求安全感",
            "dimensions": {
                "risk_tolerance": 0.2,
                "social_pressure": 0.9,
                "dominance": 0.2,
                "logic_capacity": 0.4,
                "deception_comfort": 0.2,
                "trust_baseline": 0.7,
                "ego": 0.3,
                "consistency": 0.5,
            }
        },
        "chaotic_player": {
            "name": "混乱型玩家",
            "description": "行为难以预测，喜欢冒险，不按常理出牌",
            "dimensions": {
                "risk_tolerance": 0.9,
                "social_pressure": 0.2,
                "dominance": 0.7,
                "logic_capacity": 0.4,
                "deception_comfort": 0.7,
                "trust_baseline": 0.3,
                "ego": 0.9,
                "consistency": 0.2,
            }
        },
    }

    @classmethod
    def get_template(cls, name: str) -> Dict[str, Any]:
        """获取指定的人格模板"""
        if name not in cls.PERSONALITY_TEMPLATES:
            available = list(cls.PERSONALITY_TEMPLATES.keys())
            raise ValueError(f"Personality template '{name}' not found. Available: {available}")

        return cls.PERSONALITY_TEMPLATES[name].copy()

    @classmethod
    def create_personality(cls, name: str) -> Personality:
        """从模板创建人格实例"""
        template = cls.get_template(name)
        personality_data = {
            "dimensions": template["dimensions"]
        }

        return PersonalityFactory._create_from_dict(personality_data)

    @classmethod
    def create_profile(cls, name: str) -> PersonalityProfile:
        """从模板创建完整人格档案"""
        template = cls.get_template(name)
        personality = cls.create_personality(name)

        return PersonalityFactory.create_full_profile(
            personality,
            template["name"],
            template["description"]
        )

    @classmethod
    def list_available_personalities(cls) -> list[str]:
        """列出所有可用的人格模板"""
        return list(cls.PERSONALITY_TEMPLATES.keys())

    @classmethod
    def get_personality_description(cls, name: str) -> str:
        """获取人格描述"""
        template = cls.get_template(name)
        return template.get("description", "无描述")