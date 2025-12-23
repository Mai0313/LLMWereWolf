"""
Personality Integration - 人格系统集成

将人格系统集成到现有GameEngine中，确保向后兼容
"""

from typing import Dict, Optional, Any, List
from pathlib import Path

from ..personality.models import PersonalityProfile
from ..personality.personality import PersonalityFactory, PredefinedPersonalities
from ..observation.world_cropper import WorldCropper
from ..observation.player_view import PlayerView
from ..agents.personality_adapter import PersonalityAdapter
from ..agents.enhanced_agent import EnhancedAgent
from ..agent import BaseAgent
from ..types import GamePhase


class PersonalityIntegrationError(Exception):
    """人格集成异常"""
    pass


class PersonalityEngineIntegration:
    """人格引擎集成类

    负责将人格系统与现有GameEngine无缝集成
    """

    def __init__(self, enable_personality_system: bool = False):
        self.enable_personality_system = enable_personality_system
        self.personality_adapter = PersonalityAdapter()
        self.world_cropper = WorldCropper()
        self.enhanced_agents: Dict[int, EnhancedAgent] = {}

        # 配置和统计
        self.integration_stats = {
            "total_adaptations": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "fallback_to_traditional": 0
        }

    def adapt_player_agent(
        self,
        player_id: int,
        original_agent: BaseAgent,
        personality_profile_name: Optional[str] = None,
        player_config: Optional[Dict[str, Any]] = None
    ) -> BaseAgent:
        """适配玩家Agent为增强版Agent"""

        self.integration_stats["total_adaptations"] += 1

        try:
            if not self.enable_personality_system:
                # 人格系统未启用，返回原始Agent
                return original_agent

            # 配置人格参数
            config_profile = player_config.get("personality_profile") if player_config else personality_profile_name
            force_mode = player_config.get("force_personality_mode", False) if player_config else False

            # 创建增强版Agent
            enhanced_agent = self.personality_adapter.create_enhanced_agent(
                player_id=player_id,
                base_agent=original_agent,
                personality_profile_name=config_profile,
                force_personality_mode=force_mode
            )

            self.enhanced_agents[player_id] = enhanced_agent

            # 记录成功适配
            print(f"Successfully adapted agent for player {player_id} with personality: {config_profile or 'default'}")
            return enhanced_agent

        except Exception as e:
            print(f"Warning: Failed to adapt agent for player {player_id}: {e}")
            self.integration_stats["failed_decisions"] += 1
            return original_agent

    def get_player_response(
        self,
        player_id: int,
        original_agent: BaseAgent,
        original_prompt: str,
        game_state: 'GameState',
        phase: GamePhase
    ) -> str:
        """获取玩家响应（支持人格系统）"""

        # 检查是否是增强Agent
        enhanced_agent = self.enhanced_agents.get(player_id)

        if not enhanced_agent or not self.enable_personality_system:
            # 使用原始方法
            try:
                return original_agent.get_response(original_prompt)
            except Exception as e:
                print(f"Original agent response failed: {e}")
                return "我需要时间思考..."

        # 使用人格系统
        try:
            # 1. 创建玩家视角
            player_view = self.world_cropper.create_player_view(player_id, game_state, phase)

            # 2. 生成决策
            decision_result = enhanced_agent.make_decision(player_view)

            # 3. 更新统计
            if decision_result.success:
                self.integration_stats["successful_decisions"] += 1
                return decision_result.decision.speech
            else:
                self.integration_stats["failed_decisions"] += 1
                print(f"Personality decision failed: {decision_result.error_message}")

                # 回退到传统方式
                return self._fallback_response(original_agent, original_prompt)

        except Exception as e:
            self.integration_stats["failed_decisions"] += 1
            print(f"Personality system error: {e}")
            return self._fallback_response(original_agent, original_prompt)

    def _fallback_response(self, original_agent: BaseAgent, original_prompt: str) -> str:
        """回退响应（人格系统失败时）"""
        try:
            self.integration_stats["fallback_to_traditional"] += 1
            return original_agent.get_response(original_prompt)
        except Exception as e:
            print(f"Fallback response also failed: {e}")
            return "我需要时间思考这个问题..."

    def get_integration_statistics(self) -> Dict[str, Any]:
        """获取集成统计信息"""
        stats = self.integration_stats.copy()

        # 计算成功率
        total_attempts = stats["successful_decisions"] + stats["failed_decisions"]
        if total_attempts > 0:
            stats["success_rate"] = stats["successful_decisions"] / total_attempts
        else:
            stats["success_rate"] = 0.0

        # 获取人格系统统计
        if self.enhanced_agents:
            personality_stats = self.personality_adapter.get_system_statistics()
            stats.update(personality_stats)

        return stats

    def validate_integration(self) -> Dict[str, Any]:
        """验证集成状态"""
        validation_result = {
            "is_healthy": True,
            "issues": [],
            "warnings": [],
            "components": {}
        }

        # 检查人格系统是否启用
        if not self.enable_personality_system:
            validation_result["components"]["personality_system"] = "disabled"
            return validation_result

        # 验证各个组件
        validation_result["components"]["world_cropper"] = "active"
        validation_result["components"]["personality_adapter"] = "active"
        validation_result["components"]["enhanced_agents"] = f"{len(self.enhanced_agents)} active"

        # 检查成功率
        stats = self.get_integration_statistics()
        if stats.get("success_rate", 0) < 0.8:
            validation_result["warnings"].append(f"Low success rate: {stats.get('success_rate', 0):.2%}")

        if stats.get("fallback_to_traditional", 0) > stats.get("successful_decisions", 0):
            validation_result["warnings"].append("High fallback rate to traditional system")

        # 检查每个Agent的状态
        for player_id, agent in self.enhanced_agents.items():
            try:
                agent_status = self.personality_adapter.get_agent_status(player_id)
                if agent_status and agent_status.get("success_rate", 1.0) < 0.7:
                    validation_result["issues"].append(f"Agent {player_id} has low success rate")
            except Exception as e:
                validation_result["issues"].append(f"Failed to get status for agent {player_id}: {e}")

        validation_result["is_healthy"] = len(validation_result["issues"]) == 0
        return validation_result

    def reset_integration_statistics(self):
        """重置集成统计"""
        self.integration_stats = {
            "total_adaptations": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "fallback_to_traditional": 0
        }

        # 重置所有Agent统计
        for agent in self.enhanced_agents.values():
            agent.reset_statistics()

    def create_test_profiles(self) -> List[PersonalityProfile]:
        """创建测试用人格档案"""
        test_profiles = []

        # 创建几种典型人格用于测试
        test_configs = [
            ("aggressive_test", 0.8, 0.3, 0.9),  # 激进型
            ("cautious_test", 0.3, 0.8, 0.4),   # 谨慎型
            ("balanced_test", 0.5, 0.5, 0.5),   # 平衡型
        ]

        for profile_name, dominance, social_pressure, risk_tolerance in test_configs:
            from ..personality.models import Personality, PersonalityDimension

            personality = Personality(dimensions={
                PersonalityDimension.DOMINANCE: dominance,
                PersonalityDimension.SOCIAL_PRESSURE: social_pressure,
                PersonalityDimension.RISK_TOLERANCE: risk_tolerance,
                PersonalityDimension.LOGIC_CAPACITY: 0.6,
                PersonalityDimension.DECEPTION_COMFORT: 0.5,
                PersonalityDimension.TRUST_BASELINE: 0.5,
                PersonalityDimension.EGO: 0.5,
                PersonalityDimension.CONSISTENCY: 0.6,
            })

            profile = PersonalityFactory.create_full_profile(
                personality,
                f"test_{profile_name}",
                f"Test profile: {profile_name}"
            )

            test_profiles.append(profile)
            self.personality_adapter.register_custom_profile(profile_name, profile)

        return test_profiles

    def export_integration_report(self) -> Dict[str, Any]:
        """导出集成报告"""
        stats = self.get_integration_statistics()
        validation = self.validate_integration()

        report = {
            "timestamp": str(Path(__file__).absolute()),
            "personality_system_enabled": self.enable_personality_system,
            "integration_statistics": stats,
            "validation_status": validation,
            "enhanced_agents_info": {}
        }

        # 添加每个Agent的详细信息
        for player_id, agent in self.enhanced_agents.items():
            agent_status = self.personality_adapter.get_agent_status(player_id)
            if agent_status:
                report["enhanced_agents_info"][player_id] = {
                    "personality_name": agent_status.get("personality_name"),
                    "total_decisions": agent_status.get("total_decisions"),
                    "success_rate": agent_status.get("success_rate"),
                    "average_confidence": agent_status.get("average_confidence")
                }

        return report

    def set_personality_mode(self, enabled: bool):
        """强制设置人格系统模式"""
        self.enable_personality_system = enabled

        if enabled:
            print("Personality system ENABLED")
        else:
            print("Personality system DISABLED")

    def get_agent_decision_history(self, player_id: int) -> List[Dict[str, Any]]:
        """获取Agent决策历史"""
        agent = self.enhanced_agents.get(player_id)
        if not agent:
            return []

        history = agent.decision_runner.get_recent_decisions()
        return [
            {
                "intent": decision.intent.value,
                "speech": decision.speech,
                "confidence": decision.confidence,
                "timestamp": decision.timestamp,
                "reasoning_trace": decision.reasoning_trace
            }
            for decision in history
        ]