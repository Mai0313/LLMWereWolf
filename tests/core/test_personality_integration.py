"""
Personality Integration Tests - 人格系统集成测试

测试人格系统与现有游戏引擎的集成
"""

import pytest
from unittest.mock import Mock, MagicMock

from src.llm_werewolf.core.personality.models import PersonalityProfile, Personality, PersonalityDimension
from src.llm_werewolf.core.personality.personality import PersonalityFactory, PredefinedPersonalities
from src.llm_werewolf.core.observation.player_view import PlayerView
from src.llm_werewolf.core.observation.world_cropper import WorldCropper
from src.llm_werewolf.core.decision.models import IntentType
from src.llm_werewolf.core.agents.enhanced_agent import EnhancedAgent
from src.llm_werewolf.core.engine.personality_integration import PersonalityEngineIntegration
from src.llm_werewolf.core.types import GamePhase
from src.llm_werewolf.core.agent import BaseAgent


class TestPersonalityModels:
    """测试人格模型"""

    def test_personality_creation(self):
        """测试人格创建"""
        dimensions = {
            PersonalityDimension.DOMINANCE: 0.8,
            PersonalityDimension.RISK_TOLERANCE: 0.3,
            PersonalityDimension.SOCIAL_PRESSURE: 0.5
        }

        # 为所有缺失维度赋默认值
        for dim in PersonalityDimension:
            if dim not in dimensions:
                dimensions[dim] = 0.5

        personality = Personality(dimensions=dimensions)

        assert personality.dimensions[PersonalityDimension.DOMINANCE] == 0.8
        assert personality.get_dimension_value(PersonalityDimension.DOMINANCE) == 0.8
        assert personality.get_description() is not None

    def test_personality_profile(self):
        """测试完整人格档案"""
        from src.llm_werewolf.core.personality.models import MentalState, MotivationType

        personality = PersonalityFactory.create_from_dict({
            "dimensions": {
                "dominance": 0.7,
                "risk_tolerance": 0.6,
                "social_pressure": 0.4,
                "logic_capacity": 0.8,
                "deception_comfort": 0.5,
                "trust_baseline": 0.5,
                "ego": 0.6,
                "consistency": 0.7
            }
        })

        mental_state = MentalState(
            motivations={mt: 0.5 for mt in MotivationType}
        )

        profile = PersonalityProfile(
            base_personality=personality,
            current_mental_state=mental_state,
            personality_name="test_profile"
        )

        assert profile.personality_name == "test_profile"
        assert profile.get_risk_tolerance() > 0
        assert profile.should_be_deceptive() is False  # 中等撒谎舒适度

    def test_predefined_personalities(self):
        """测试预定义人格"""
        available = PredefinedPersonalities.list_available_personalities()
        assert "aggressive_wolf" in available
        assert "cautious_seer" in available

        # 创建激进狼人
        aggressive_profile = PredefinedPersonalities.create_profile("aggressive_wolf")
        assert aggressive_profile.personality_name == "激进型狼人"

        # 检查特征
        dominance = aggressive_profile.base_personality.get_dimension_value("dominance")
        assert dominance > 0.8  # 激进型应该有高控制欲


class TestWorldCropper:
    """测试世界裁剪器"""

    def test_player_view_creation(self):
        """测试玩家视角创建"""
        # 模拟游戏状态
        mock_game_state = Mock()
        mock_game_state.round = 2
        mock_game_state.event_history = []

        # 模拟玩家
        mock_player1 = Mock()
        mock_player1.player_id = 1
        mock_player1.name = "Player1"
        mock_player1.is_alive = True

        mock_player2 = Mock()
        mock_player2.player_id = 2
        mock_player2.name = "Player2"
        mock_player2.is_alive = False

        mock_game_state.players = [mock_player1, mock_player2]

        # 创建玩家视角
        cropper = WorldCropper()
        player_view = cropper.create_player_view(1, mock_game_state, GamePhase.DAY_DISCUSSION)

        # 验证基本信息
        assert player_view.player_id == 1
        assert player_view.current_round == 2
        assert player_view.am_i_alive() is True
        assert player_view.count_alive_players() == 1

        # 验证信息隔离 - 不包含敏感信息
        public_fields = ['player_id', 'name', 'is_alive', 'seat_number']
        for player in player_view.alive_players:
            for attr in player.__dict__:
                if attr not in public_fields:
                    pytest.fail(f"Player view contains sensitive field: {attr}")

    def test_spec_compliance_validation(self):
        """测试SPEC合规性验证"""
        mock_game_state = Mock()
        mock_game_state.round = 1
        mock_game_state.event_history = []

        mock_player = Mock()
        mock_player.player_id = 1
        mock_player.name = "TestPlayer"
        mock_player.is_alive = True
        mock_game_state.players = [mock_player]

        cropper = WorldCropper()
        player_view = cropper.create_player_view(1, mock_game_state, GamePhase.DAY_DISCUSSION)

        # 应该通过合规性检查
        is_compliant, violations = player_view.validate_spec_compliance()
        assert is_compliant, f"Compliance violations: {violations}"


class TestPersonalityIntegration:
    """测试人格系统集成"""

    @pytest.fixture
    def integration(self):
        """创建集成实例"""
        return PersonalityEngineIntegration(enable_personality_system=True)

    def test_agent_adaptation(self, integration):
        """测试Agent适配"""
        mock_agent = Mock(spec=BaseAgent)
        mock_agent.get_response.return_value = "Test response"

        # 适配Agent
        enhanced_agent = integration.adapt_player_agent(
            player_id=1,
            original_agent=mock_agent,
            personality_profile_name="aggressive_wolf"
        )

        # 验证结果
        assert enhanced_agent is not None
        assert hasattr(enhanced_agent, 'personality_profile')
        assert enhanced_agent.personality_profile.personality_name == "激进型狼人"

        # 验证统计更新
        stats = integration.get_integration_statistics()
        assert stats["total_adaptations"] == 1

    def test_decision_flow(self, integration):
        """测试决策流程"""
        mock_agent = Mock(spec=BaseAgent)
        mock_agent.get_response.return_value = "I think this player is suspicious."

        # 适配Agent
        enhanced_agent = integration.adapt_player_agent(
            player_id=1,
            original_agent=mock_agent,
            personality_profile_name="aggressive_wolf"
        )

        # 模拟游戏状态
        mock_game_state = Mock()
        mock_game_state.round = 1
        mock_game_state.event_history = []

        # 模拟玩家视角
        cropper = WorldCropper()
        player_view = cropper.create_player_view(1, mock_game_state, GamePhase.DAY_DISCUSSION)

        # 生成决策
        result = enhanced_agent.decision_runner.run_decision_cycle(player_view)

        # 验证结果
        assert result.success is True
        assert result.decision.speech is not None
        assert result.decision.intent in [IntentType.STRONG_ACCUSE, IntentType.TEST_SUSPECT, IntentType.LOW_PROFILE_SPEECH]

    def test_fallback_mechanism(self, integration):
        """测试回退机制"""
        mock_agent = Mock(spec=BaseAgent)
        mock_agent.get_response.return_value = "Fallback response"

        # 先禁用人格系统
        integration.enable_personality_system = False

        response = integration.get_player_response(
            player_id=1,
            original_agent=mock_agent,
            original_prompt="What do you think?",
            game_state=Mock(),
            phase=GamePhase.DAY_DISCUSSION
        )

        # 应该回退到原始方式
        assert response == "Fallback response"
        mock_agent.get_response.assert_called_once()

    def test_integration_statistics(self, integration):
        """测试集成统计"""
        mock_agent = Mock(spec=BaseAgent)
        integration.adapt_player_agent(1, mock_agent, "aggressive_wolf")
        integration.adapt_player_agent(2, mock_agent, "cautious_seer")

        stats = integration.get_integration_statistics()

        assert stats["total_agents"] == 2
        assert "personality_mode_agents" in stats
        assert "system_health" in stats

    def test_validation(self, integration):
        """测试集成验证"""
        validation_result = integration.validate_integration()

        assert "is_healthy" in validation_result
        assert "issues" in validation_result
        assert "warnings" in validation_result
        assert "components" in validation_result


class TestEndToEndFlow:
    """端到端流程测试"""

    def test_full_personality_flow(self):
        """测试完整人格流程"""
        # 创建人格档案
        profile = PredefinedPersonalities.create_profile("aggressive_wolf")

        # 创建模拟LLM Agent
        mock_llm = Mock(spec=BaseAgent)
        mock_llm.get_response.return_value = "I strongly suspect this player!"

        # 创建增强Agent
        enhanced_agent = EnhancedAgent(
            personality_profile=profile,
            base_agent=mock_llm
        )

        # 创建玩家视角
        mock_game_state = Mock()
        mock_game_state.round = 2
        mock_game_state.event_history = []

        cropper = WorldCropper()
        player_view = cropper.create_player_view(1, mock_game_state, GamePhase.DAY_DISCUSSION)

        # 执行决策
        decision_result = enhanced_agent.make_decision(player_view)

        # 验证决策
        assert decision_result.success is True
        assert decision_result.decision.speech is not None
        assert 0.0 <= decision_result.decision.confidence <= 1.0

        # 验证人格一致性
        stats = enhanced_agent.get_performance_stats()
        assert stats["personality_name"] == "激进型狼人"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])