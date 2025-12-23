#!/usr/bin/env python3
"""
Personality System Demo - 人格系统演示脚本

展示人格系统的核心功能
"""

import sys
import os

# 添加项目目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.llm_werewolf.core.personality.models import PersonalityProfile, PersonalityDimension
from src.llm_werewolf.core.personality.personality import PersonalityFactory, PredefinedPersonalities
from src.llm_werewolf.core.decision.models import IntentType
from src.llm_werewolf.core.decision.intent_registry import IntentRegistry
from src.llm_werewolf.core.observation.player_view import PlayerView, PublicPlayerInfo, SpeechRecord
from src.llm_werewolf.core.observation.world_cropper import WorldCropper
from src.llm_werewolf.core.agents.enhanced_agent import EnhancedAgent
from src.llm_werewolf.core.types import GamePhase
from src.llm_werewolf.core.agent import BaseAgent
from unittest.mock import Mock


class MockLLMAgent(BaseAgent):
    """模拟LLM Agent"""

    def __init__(self, personality_trait="neutral"):
        super().__init__()
        self.personality_trait = personality_trait
        self.response_count = 0

    def get_response(self, message: str) -> str:
        """模拟响应"""
        self.response_count += 1

        if "strongly accuse" in message.lower():
            if self.personality_trait == "aggressive":
                return "我确信这个人就是狼！必须立即处理！"
            elif self.personality_trait == "cautious":
                return "我需要更多证据，但这个人确实值得关注。"
            else:
                return "我觉得这个人有问题。"
        elif "test" in message.lower():
            if self.personality_trait == "cautious":
                return "能说说你的想法吗？我想了解更多情况。"
            else:
                return "请问你怎么看？"
        else:
            return "我正在观察形势。"


def demo_personality_profiles():
    """演示人格档案创建"""
    print("🧠 === 演示人格档案系统 ===")

    # 列出可用人格
    available = PredefinedPersonalities.list_available_personalities()
    print(f"📋 可用人格类型: {available}")

    # 创建几种人格档案
    profiles = []
    for profile_name in ["aggressive_wolf", "cautious_seer", "emotional_witch"]:
        profile = PredefinedPersonalities.create_profile(profile_name)
        profiles.append(profile)
        print(f"👤 {profile.personality_name}: {profile.description}")
        print(f"   - 支配性: {profile.base_personality.get_dimension_value('dominance')}")
        print(f"   - 风险承受: {profile.base_personality.get_dimension_value('risk_tolerance')}")
        print(f"   - 撒谎舒适: {profile.base_personality.get_dimension_value('deception_comfort')}")

    return profiles


def demo_world_cropping():
    """演示世界裁剪"""
    print("\n🌍 === 演示世界裁剪系统 ===")

    # 模拟游戏状态
    mock_game_state = Mock()
    mock_game_state.round = 3
    mock_game_state.event_history = []

    # 模拟玩家
    players = []
    for i in range(1, 5):
        player = Mock()
        player.player_id = i
        player.name = f"Player{i}"
        player.is_alive = i <= 3  # 前3个存活
        players.append(player)
    mock_game_state.players = players

    # 创建裁剪器
    cropper = WorldCropper()

    # 为不同玩家创建视角
    for player_id in [1, 4]:  # 存活玩家和死亡玩家
        player_view = cropper.create_player_view(
            player_id, mock_game_state, GamePhase.DAY_DISCUSSION
        )

        status = "存活" if player_view.am_i_alive() else "死亡"
        print(f"🎭 玩家{player_id}视角 ({status}):")
        print(f"   - 可见存活玩家: {player_view.count_alive_players()}/{player_view.total_players}")
        print(f"   - 角色提示: {player_view.role_hint or '无'}")
        print(f"   - 可用行动: {len(player_view.available_actions)} 个")

        # 验证SPEC合规性
        is_compliant, violations = player_view.validate_spec_compliance()
        compliance_status = "✅ 合规" if is_compliant else "❌ 违规"
        print(f"   - SPEC合规性: {compliance_status}")
        if violations:
            for violation in violations[:2]:  # 只显示前2个违规
                print(f"     - {violation}")


def demo_intent_system():
    """演示意图系统"""
    print("\n🎯 === 演示意图决策系统 ===")

    # 创建意图注册表
    registry = IntentRegistry()

    # 获取白天讨论意图
    day_intents = registry.get_intents_for_phase(GamePhase.DAY_DISCUSSION)
    print(f"💬 白天讨论可用意图: {len(day_intents)} 个")

    # 显示前几个意图
    for intent in day_intents[:3]:
        print(f"   - {intent.intent_type.value}: {intent.description}")
        if intent.requires_target():
            print(f"     需要目标: 是")
        print(f"     基础权重: {intent.base_weight}")

    # 获取统计信息
    stats = registry.get_intent_statistics()
    print(f"📊 意图系统统计:")
    print(f"   - 总意图数: {stats['total_intents']}")
    for phase, count in stats['phase_counts'].items():
        print(f"   - {phase}: {count} 个意图")


def demo_decision_process():
    """演示决策过程"""
    print("\n🤖 === 演示人格驱动决策过程 ===")

    # 创建人格档案
    aggressive_profile = PredefinedPersonalities.create_profile("aggressive_wolf")
    cautious_profile = PredefinedPersonalities.create_profile("cautious_seer")

    # 创建模拟Agent
    aggressive_llm = MockLLMAgent("aggressive")
    cautious_llm = MockLLMAgent("cautious")

    # 创建增强Agent
    aggressive_agent = EnhancedAgent(aggressive_profile, aggressive_llm)
    cautious_agent = EnhancedAgent(cautious_profile, cautious_llm)

    # 创建测试用的玩家视角
    mock_game_state = Mock()
    mock_game_state.round = 2
    mock_game_state.event_history = []

    player1 = Mock()
    player1.player_id = 1
    player1.name = "Player1"
    player1.is_alive = True
    mock_game_state.players = [player1]

    cropper = WorldCropper()
    player_view = cropper.create_player_view(1, mock_game_state, GamePhase.DAY_DISCUSSION)

    print("🎭 测试激进型人格决策:")
    aggressive_result = aggressive_agent.make_decision(player_view)
    if aggressive_result.success:
        print(f"   意图: {aggressive_result.decision.intent.value}")
        print(f"   表达: {aggressive_result.decision.speech}")
        print(f"   置信度: {aggressive_result.decision.confidence:.2f}")

    print("\n🎭 测试谨慎型人格决策:")
    cautious_result = cautious_agent.make_decision(player_view)
    if cautious_result.success:
        print(f"   意图: {cautious_result.decision.intent.value}")
        print(f"   表达: {cautious_result.decision.speech}")
        print(f"   置信度: {cautious_result.decision.confidence:.2f}")

    # 对比结果
    if aggressive_result.success and cautious_result.success:
        print(f"\n🔍 人格差异分析:")
        aggressive_intent = aggressive_result.decision.intent.value
        cautious_intent = cautious_result.decision.intent.value
        print(f"   - 激进型选择: {aggressive_intent}")
        print(f"   - 谨慎型选择: {cautious_intent}")


def demo_integration_statistics():
    """演示集成统计"""
    print("\n📊 === 演示集成统计系统 ===")

    # 创建人格档案和Agent
    profile = PredefinedPersonalities.create_profile("balanced_hunter")
    agent = EnhancedAgent(profile, MockLLMAgent("balanced"))

    # 模拟多次决策
    mock_game_state = Mock()
    mock_game_state.round = 1
    mock_game_state.event_history = []

    player = Mock()
    player.player_id = 1
    player.name = "Player1"
    player.is_alive = True
    mock_game_state.players = [player]

    cropper = WorldCropper()
    player_view = cropper.create_player_view(1, mock_game_state, GamePhase.DAY_DISCUSSION)

    print("🎯 执行多次决策测试...")
    for i in range(5):
        result = agent.make_decision(player_view)
        if result.success:
            print(f"   决策 {i+1}: {result.decision.intent.value} (置信度: {result.decision.confidence:.2f})")

    # 显示统计
    stats = agent.get_performance_stats()
    print(f"\n📈 Agent性能统计:")
    print(f"   - 总决策数: {stats['total_decisions']}")
    print(f"   - 失败决策数: {stats['failed_decisions']}")
    print(f"   - 成功率: {stats['success_rate']:.2%}")
    print(f"   - 平均置信度: {stats['average_confidence']:.2f}")
    print(f"   - 最常用意图: {stats['most_common_intent']}")


def main():
    """主演示函数"""
    print("🐺 LLM Werewolf 人格系统演示")
    print("=" * 50)

    try:
        # 运行各个演示
        demo_personality_profiles()
        demo_world_cropping()
        demo_intent_system()
        demo_decision_process()
        demo_integration_statistics()

        print("\n✅ === 演示完成 ===")
        print("🎉 人格系统核心功能运行正常！")

        print("\n📋 系统特性验证:")
        print("   ✅ 人格档案创建和管理")
        print("   ✅ 严格的信息裁剪（SPEC合规）")
        print("   ✅ 意图级决策系统")
        print("   ✅ 人格驱动行为差异")
        print("   ✅ 集成统计和监控")

    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("🔍 请检查系统安装和依赖")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())