"""
Game Runner - 游戏运行器

负责执行单个游戏并收集数据
"""

import time
from typing import Dict, Any, Optional, Callable

from ..game_engine import GameEngine
from ..agent import create_agent
from ..role_registry import create_roles
from ..config import create_game_config_from_player_count
from ..types import GamePhase
from .tournament import GameResult


class GameRunner:
    """游戏运行器"""

    def __init__(self, tournament_config):
        self.tournament_config = tournament_config
        self.event_collector = EventCollector()

    def run_game(self, game_result: GameResult) -> GameResult:
        """运行单局游戏"""
        start_time = time.time()

        # 设置事件收集器
        event_handlers = []

        # 创建游戏配置
        num_players = len(game_result.player_configs)
        game_config = create_game_config_from_player_count(num_players)

        # 创建玩家
        players = []
        for player_config in game_result.player_configs:
            # 使用人格系统适配器创建玩家
            if self.tournament_config.enable_personality_system and player_config.get('enable_personality_system'):
                from ..personality_integration_manager import PersonalityManager
                personality_adapter = PersonalityManager.get_personality_adapter()

                base_agent = create_agent(player_config, self.tournament_config.language)

                if personality_adapter:
                    player = personality_adapter.create_enhanced_agent(
                        player_id=len(players) + 1,
                        base_agent=base_agent,
                        personality_profile_name=player_config.get('personality_profile')
                    )
                else:
                    player = base_agent
            else:
                player = create_agent(player_config, self.tournament_config.language)

            players.append(player)

        # 创建角色
        roles = create_roles(role_names=game_config.role_names)

        # 创建游戏引擎
        engine = GameEngine(
            game_config,
            language=self.tournament_config.language,
            enable_personality_system=self.tournament_config.enable_personality_system
        )

        # 设置事件收集
        engine.on_event = self.event_collector.collect_event

        # 启动游戏
        engine.setup_game(players=players, roles=roles)

        # 运行游戏循环
        current_round = 1
        max_rounds = self.tournament_config.max_rounds_per_game

        try:
            while not engine.is_game_over() and current_round <= max_rounds:
                # 执行游戏回合
                phase = engine.get_current_phase()

                if phase == GamePhase.NIGHT:
                    self._run_night_phase(engine, game_result)
                elif phase == GamePhase.DAY_DISCUSSION:
                    self._run_discussion_phase(engine, game_result)
                elif phase == GamePhase.DAY_VOTING:
                    self._run_voting_phase(engine, game_result)
                elif phase == GamePhase.CHECK_WIN:
                    if not engine.check_victory():
                        engine.next_round()
                        current_round += 1
                else:
                    # 其他阶段的处理
                    if hasattr(engine, phase.value.lower() + '_phase'):
                        phase_handler = getattr(engine, phase.value.lower() + '_phase')
                        phase_handler()

                # 防止无限循环
                if hasattr(engine, 'next_phase'):
                    engine.next_phase()

                time.sleep(0.1)  # 短暂延迟避免CPU占用过高

        except Exception as e:
            print(f"Game execution error: {e}")
        finally:
            # 更新游戏结果
            end_time = time.time()
            game_result.duration = end_time - start_time
            game_result.end_time = end_time
            game_result.rounds = current_round
            game_result.events = self.event_collector.events
            game_result.winner = self._determine_winner(engine)
            game_result.player_results = self._extract_player_results(engine, players)

            # 清理状态
            engine.cleanup()

        return game_result

    def _run_night_phase(self, engine, game_result: GameResult):
        """运行夜晚阶段"""
        # 获取夜晚行动
        night_actions = []

        for player in engine.game_state.get_alive_players():
            if hasattr(player, 'role') and player.role:
                # 获取夜晚动作
                actions = player.role.get_night_actions(engine.game_state, player)
                for action in actions:
                    night_actions.append({
                        "player": player.name,
                        "action type": action.__class__.__name__,
                        "target": getattr(action, 'target', None),
                        "result": action.execute(engine.game_state)
                    })

        # 记录夜晚行动
        game_result.decisions.extend(night_actions)

    def _run_discussion_phase(self, engine, game_result: GameResult):
        """运行讨论阶段"""
        # 获取讨论发言
        discussion_data = []

        for player in engine.game_state.get_alive_players():
            # 获取玩家发言
            prompt = engine.create_discussion_prompt(player)

            try:
                response = engine.get_player_response(player, GamePhase.DAY_DISCUSSION, prompt)

                discussion_data.append({
                    "player": player.name,
                    "speech": response,
                    "phase": "discussion",
                    "round": engine.game_state.round
                })
            except Exception as e:
                print(f"Discussion error for {player.name}: {e}")

        # 记录讨论
        game_result.decisions.extend(discussion_data)

    def _run_voting_phase(self, engine, game_result: GameResult):
        """运行投票阶段"""
        # 获取投票数据
        voting_data = []

        for player in engine.game_state.get_alive_players():
            if player.can_vote():
                prompt = engine.create_voting_prompt(player)

                try:
                    response = engine.get_player_response(player, GamePhase.DAY_VOTING, prompt)

                    # 解析投票
                    target = self._parse_vote_target(response, engine.game_state)

                    voting_data.append({
                        "player": player.name,
                        "target": target,
                        "phase": "voting",
                        "round": engine.game_state.round
                    })
                except Exception as e:
                    print(f"Voting error for {player.name}: {e}")

        # 记录投票
        game_result.decisions.extend(voting_data)

    def _parse_vote_target(self, response: str, game_state) -> Optional[str]:
        """解析投票目标"""
        # 简化的投票解析
        import re

        # 查找数字
        numbers = re.findall(r'\d+', response)
        if numbers:
            target_id = int(numbers[0])
            for player in game_state.players:
                if player.player_id == target_id:
                    return player.name

        return None  # 弃票或解析失败

    def _determine_winner(self, engine) -> str:
        """确定游戏胜利者"""
        if hasattr(engine, 'check_victory') and engine.check_victory():
            # 检查狼人数量
            werewolves = 0
            villagers = 0

            for player in engine.game_state.players:
                if player.is_alive():
                    if hasattr(player, 'role'):
                        if 'werewolf' in str(type(player.role)).lower():
                            werewolves += 1
                        else:
                            villagers += 1

            if werewolves == 0:
                return "villager"
            elif werewolves >= villagers:
                return "werewolf"

        return "unknown"

    def _extract_player_results(self, engine, players) -> Dict[str, Dict[str, Any]]:
        """提取玩家表现数据"""
        results = {}

        for player in players:
            player_data = {
                "name": player.name,
                "is_alive": player.is_alive(),
                "role": str(type(player.role).__name__) if hasattr(player, 'role') else 'unknown',
                "survival_rounds": engine.game_state.round if player.is_alive() else 0,
                "personality_profile": getattr(player, 'personality_profile', None),
                "decisions_made": 0,
                "confidence_avg": 0.0,
                "alignment_score": 0.0
            }

            # 计算决策统计
            if self.tournament_config.collect_detailed_stats:
                player_data.update(self._calculate_decision_stats(player, engine))

            results[player.name] = player_data

        return results

    def _calculate_decision_stats(self, player, engine) -> Dict[str, Any]:
        """计算决策统计数据"""
        # 从事件历史中提取决策数据
        decisions = []
        confidence_scores = []

        for event in self.event_collector.events:
            if hasattr(event, 'player_id') and hasattr(player, 'player_id'):
                if event.player_id == player.player_id:
                    if hasattr(event, 'confidence'):
                        confidence_scores.append(event.confidence)
                    decisions.append(event)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

        # 计算对齐度得分（简化的版本）
        alignment_score = 0.5  # 默认值，可以根据实际实现调整

        return {
            "decisions_made": len(decisions),
            "confidence_avg": avg_confidence,
            "alignment_score": alignment_score
        }


class EventCollector:
    """事件收集器"""

    def __init__(self):
        self.events = []

    def collect_event(self, event):
        """收集游戏事件"""
        event_data = {
            "type": getattr(event, 'event_type', 'unknown'),
            "message": getattr(event, 'message', ''),
            "player_id": getattr(event, 'player_id', None),
            "target_id": getattr(event, 'target_id', None),
            "phase": getattr(event, 'phase', 'unknown'),
            "round": getattr(event, 'round', 0),
            "timestamp": time.time()
        }

        self.events.append(event_data)