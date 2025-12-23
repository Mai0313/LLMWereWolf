"""
Enhanced Game Engine - 增强版游戏引擎

在现有GameEngine基础上集成人格系统
"""

from typing import Optional, Dict, Any, List
import logging

from .personality_integration import PersonalityEngineIntegration
from .base import GameEngineBase
from ..types import GamePhase
from ...base_agent import BaseAgent


class EnhancedGameEngineDecorator:
    """游戏引擎增强装饰器

    不修改原有GameEngine，通过装饰器模式添加人格功能
    """

    def __init__(self, original_engine, enable_personality_system: bool = False):
        self.original_engine = original_engine
        self.personality_integration = PersonalityEngineIntegration(enable_personality_system)
        self.logger = logging.getLogger(__name__)

    def request_player_action(self, player, phase: GamePhase, prompt: str) -> Any:
        """请求玩家行动（支持人格系统）"""
        return self._get_personality_enhanced_response(
            player.player_id,
            player.agent,
            prompt,
            phase
        )

    def _get_personality_enhanced_response(
        self,
        player_id: int,
        agent: BaseAgent,
        original_prompt: str,
        phase: GamePhase
    ) -> str:
        """获取人格增强的响应"""
        try:
            response = self.personality_integration.get_player_response(
                player_id=player_id,
                original_agent=agent,
                original_prompt=original_prompt,
                game_state=self.original_engine.game_state,
                phase=phase
            )
            return response
        except Exception as e:
            self.logger.error(f"Personality integration error: {e}")
            return agent.get_response(original_prompt)

    def adapt_players_with_personalities(self, player_configs: Optional[List[Dict[str, Any]]] = None):
        """为玩家适配人格系统"""
        if not player_configs:
            return

        for config in player_configs:
            player_id = config.get("player_id")
            if player_id is None:
                continue

            # 找到对应的玩家
            for player in self.original_engine.game_state.players:
                if player.player_id == player_id:
                    # 适配Agent
                    enhanced = self.personality_integration.adapt_player_agent(
                        player_id=player_id,
                        original_agent=player.agent,
                        player_config=config
                    )

                    # 替换原始Agent
                    player.agent = enhanced
                    break

    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成状态报告"""
        return self.personality_integration.export_integration_report()

    def enable_personality_mode(self):
        """启用人格模式"""
        self.personality_integration.set_personality_mode(True)

    def disable_personality_mode(self):
        """禁用人格模式"""
        self.personality_integration.set_personality_mode(False)

    def is_personality_enabled(self) -> bool:
        """检查人格系统是否启用"""
        return self.personality_integration.enable_personality_system

    def get_player_decision_history(self, player_id: int) -> List[Dict[str, Any]]:
        """获取玩家决策历史"""
        return self.personality_integration.get_agent_decision_history(player_id)

    # 委托所有其他方法给原始引擎
    def __getattr__(self, name):
        return getattr(self.original_engine, name)


def create_enhanced_engine(
    original_engine,
    enable_personality: bool = False,
    player_configs: Optional[List[Dict[str, Any]]] = None
) -> EnhancedGameEngineDecorator:
    """创建增强版游戏引擎的工厂函数"""

    enhanced_engine = EnhancedGameEngineDecorator(
        original_engine,
        enable_personality_system=enable_personality
    )

    # 如果提供了玩家配置，自动适配人格
    if player_configs and enable_personality:
        enhanced_engine.adapt_players_with_personalities(player_configs)

    return enhanced_engine


# 为了向后兼容，提供简单的切换功能
def switch_to_personality_mode(game_engine, player_configs: Optional[List[Dict[str, Any]]] = None):
    """将现有游戏引擎切换到人格模式"""
    enhanced = create_enhanced_engine(game_engine, enable_personality=True, player_configs=player_configs)
    enhanced.enable_personality_mode()
    return enhanced


def switch_to_traditional_mode(game_engine):
    """切换回传统模式（禁用人格功能）"""
    if isinstance(game_engine, EnhancedGameEngineDecorator):
        game_engine.disable_personality_mode()
    return game_engine