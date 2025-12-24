"""
Personality Adapter - 人格系统适配器

在现有GameEngine和新增人格系统间桥接
确保向后兼容性和平滑切换
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from ..personality.models import PersonalityProfile, Personality
from ..personality.personality import PersonalityFactory, PredefinedPersonalities
from .enhanced_agent import EnhancedAgent, EnhancedLLMAgent, HybridAgent
from ..agent import BaseAgent


class PersonalityAdapter:
    """人格系统适配器

    负责创建和管理人格增强的Agent实例
    """

    def __init__(self):
        self.personality_profiles: Dict[str, PersonalityProfile] = {}
        self.enhanced_agents: Dict[int, EnhancedAgent] = {}
        self.default_config_paths = [
            Path(__file__).parent.parent.parent.parent.parent / "configs" / "personalities"
        ]

    def create_enhanced_agent(
        self,
        player_id: int,
        base_agent: BaseAgent,
        personality_profile_name: Optional[str] = None,
        force_personality_mode: bool = False,
        model_name: str = "gpt-4"
    ) -> EnhancedAgent:
        """创建增强版Agent"""

        # 创建或获取人格档案
        if personality_profile_name:
            personality_profile = self._get_or_create_profile(personality_profile_name)
        else:
            personality_profile = self._create_default_profile()

        # 根据是否强制度选择Agent类型
        if force_personality_mode or personality_profile_name:
            if hasattr(base_agent, 'model'):  # LLM Agent
                enhanced_agent = EnhancedLLMAgent(
                    personality_profile=personality_profile,
                    llm_client=base_agent,
                    model_name=model_name
                )
            else:
                enhanced_agent = EnhancedAgent(
                    personality_profile=personality_profile,
                    base_agent=base_agent
                )
        else:
            # 混合模式，可切换
            enhanced_agent = HybridAgent(
                personality_profile=personality_profile,
                base_agent=base_agent,
                use_personality_mode=False  # 默认传统模式
            )

        self.enhanced_agents[player_id] = enhanced_agent
        return enhanced_agent

    def _get_or_create_profile(self, profile_name: str) -> PersonalityProfile:
        """获取或创建人格档案"""

        if profile_name in self.personality_profiles:
            return self.personality_profiles[profile_name]

        # 尝试从预定义人格创建
        if profile_name in PredefinedPersonalities.list_available_personalities():
            profile = PredefinedPersonalities.create_profile(profile_name)
            self.personality_profiles[profile_name] = profile
            return profile

        # 尝试从配置文件创建
        for config_path in self.default_config_paths:
            config_file = config_path / f"{profile_name}.yaml"
            if config_file.exists():
                personality = PersonalityFactory.create_from_config(config_file)
                profile = PersonalityFactory.create_full_profile(
                    personality, profile_name
                )
                self.personality_profiles[profile_name] = profile
                return profile

        # 创建随机人格（最后备选）
        print(f"Warning: Could not find profile '{profile_name}', creating random profile")
        random_personality = PersonalityFactory.create_random()
        profile = PersonalityFactory.create_full_profile(
            random_personality,
            profile_name
        )
        self.personality_profiles[profile_name] = profile
        return profile

    def _create_default_profile(self) -> PersonalityProfile:
        """创建默认人格档案"""
        from ..personality.personality import PersonalityFactory

        default_personality = PersonalityFactory.create_default_for_role("villager")
        return PersonalityFactory.create_full_profile(
            default_personality,
            "default"
        )

    def get_enhanced_agent(self, player_id: int) -> Optional[EnhancedAgent]:
        """获取增强版Agent"""
        return self.enhanced_agents.get(player_id)

    def list_available_profiles(self) -> List[str]:
        """列出所有可用的人格档案"""
        profiles = set(self.personality_profiles.keys())
        profiles.update(PredefinedPersonalities.list_available_personalities())

        # 添加配置文件的人格
        for config_path in self.default_config_paths:
            if config_path.exists():
                for config_file in config_path.glob("*.yaml"):
                    profiles.add(config_file.stem)

        return sorted(list(profiles))

    def register_custom_profile(self, profile_name: str, profile: PersonalityProfile):
        """注册自定义人格档案"""
        self.personality_profiles[profile_name] = profile

    def get_agent_status(self, player_id: int) -> Optional[Dict[str, Any]]:
        """获取Agent状态"""
        agent = self.enhanced_agents.get(player_id)
        if not agent:
            return None

        stats = agent.get_performance_stats()

        # 确定Agent类型
        agent_type = "EnhancedLLMAgent" if isinstance(agent, EnhancedLLMAgent) else \
                    "MixedAgent" if isinstance(agent, HybridAgent) else "EnhancedAgent"

        return {
            "player_id": player_id,
            "agent_type": agent_type,
            "personality_name": agent.personality_profile.personality_name,
            "is_personality_mode": getattr(agent, 'use_personality_mode', True),
            "total_decisions": stats["total_decisions"],
            "success_rate": stats["success_rate"],
            "average_confidence": stats["average_confidence"],
            "current_stress": stats["current_stress"],
            "current_confidence": stats["current_confidence"]
        }

    def switch_agent_mode(self, player_id: int, use_personality_mode: bool) -> bool:
        """切换Agent模式"""
        agent = self.enhanced_agents.get(player_id)
        if isinstance(agent, HybridAgent):
            agent.set_mode(use_personality_mode)
            return True
        return False

    def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统整体统计"""
        if not self.enhanced_agents:
            return {
                "total_agents": 0,
                "personality_mode_agents": 0,
                "system_health": "inactive"
            }

        total_agents = len(self.enhanced_agents)
        personality_mode_agents = sum(
            1 for agent in self.enhanced_agents.values()
            if getattr(agent, 'use_personality_mode', True)
        )

        total_decisions = sum(
            agent.total_decisions for agent in self.enhanced_agents.values()
        )
        total_failures = sum(
            agent.failed_decisions for agent in self.enhanced_agents.values()
        )

        avg_confidence = sum(
            agent.decision_runner.get_decision_statistics()["average_confidence"]
            for agent in self.enhanced_agents.values()
        ) / total_agents

        return {
            "total_agents": total_agents,
            "personality_mode_agents": personality_mode_agents,
            "available_profiles": len(self.list_available_profiles()),
            "total_system_decisions": total_decisions,
            "total_system_failures": total_failures,
            "system_success_rate": 1.0 - (total_failures / max(1, total_decisions)),
            "average_confidence": avg_confidence,
            "system_health": "healthy" if total_failures / max(1, total_decisions) < 0.1 else "needs_attention"
        }

    def reset_all_statistics(self):
        """重置所有Agent统计"""
        for agent in self.enhanced_agents.values():
            agent.reset_statistics()

    def validate_agent_config(self, player_id: int) -> Optional[Dict[str, Any]]:
        """验证Agent配置"""
        agent = self.enhanced_agents.get(player_id)
        if not agent:
            return None

        validation_result = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }

        # 检查人格配置
        if not agent.personality_profile:
            validation_result["issues"].append("Missing personality profile")
        else:
            # 检查人格维度是否合理
            for dim, value in agent.personality_profile.base_personality.dimensions.items():
                if not 0.0 <= value <= 1.0:
                    validation_result["issues"].append(f"Invalid dimension value for {dim}: {value}")

        # 检查决策历史
        stats = agent.get_performance_stats()
        if stats["success_rate"] < 0.7:
            validation_result["warnings"].append(f"Low success rate: {stats['success_rate']:.2%}")

        if stats["total_decisions"] > 0 and stats["average_confidence"] < 0.3:
            validation_result["warnings"].append(f"Low average confidence: {stats['average_confidence']:.2f}")

        validation_result["is_valid"] = len(validation_result["issues"]) == 0
        return validation_result