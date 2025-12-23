"""
World Cropper - 世界裁剪器

从完整的游戏状态生成严格裁剪的玩家视角，
确保AI无法获得不应知道的信息
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import random

from .player_view import (
    PlayerView,
    PublicPlayerInfo,
    SpeechRecord,
    VotingRecord,
    DeathAnnouncement
)
from ..types import GamePhase
from ..game_state import GameState
from ..player import Player


class WorldCropper:
    """世界裁剪器

    唯一知道完整真相的模块，负责严格裁剪信息
    """

    def __init__(self, ensure_spec_compliance: bool = True):
        self.ensure_spec_compliance = ensure_spec_compliance

    def create_player_view(
        self,
        player_id: int,
        game_state: GameState,
        phase: GamePhase
    ) -> PlayerView:
        """
        为指定玩家生成严格裁剪后的视图

        这是信息隔离的核心方法
        """

        # 1. 提取公开玩家信息
        alive_players, dead_players = self._extract_public_player_info(game_state)

        # 2. 提取历史信息（严格过滤）
        speech_history = self._extract_public_speech_history(game_state)
        voting_history = self._extract_public_voting_history(game_state)
        death_announcements = self._extract_death_announcements(game_state)

        # 3. 生成模糊的角色提示
        role_hint = self._generate_role_hint(player_id, game_state, phase)

        # 4. 生成抽象行动选项
        available_actions = self._generate_available_actions(player_id, game_state, phase)

        # 5. 构建决策上下文（不包含敏感信息）
        context = self._build_safe_context(player_id, game_state, phase)

        # 6. 生成叙事化时间信息
        current_time = self._generate_time_description(game_state, phase)

        player_view = PlayerView(
            player_id=player_id,
            current_phase=phase,
            current_round=game_state.round,
            seat_number=self._get_player_seat_number(player_id, game_state),
            alive_players=alive_players,
            dead_players=dead_players,
            total_players=len(game_state.players),
            speech_history=speech_history,
            voting_history=voting_history,
            death_announcements=death_announcements,
            role_hint=role_hint,
            available_actions=available_actions,
            context=context,
            current_time=current_time
        )

        # 7. 验证SPEC合规性
        if self.ensure_spec_compliance:
            is_compliant, violations = player_view.validate_spec_compliance()
            if not is_compliant:
                print(f"⚠️ SPEC VIOLATION in PlayerView: {violations}")
                # 可以选择抛出异常或自动修正
                raise ValueError(f"Player view violates SPEC: {violations}")

        return player_view

    def _extract_public_player_info(self, game_state: GameState) -> tuple[List[PublicPlayerInfo], List[PublicPlayerInfo]]:
        """提取只有公开信息的玩家数据"""

        alive_players = []
        dead_players = []

        for player in game_state.players:
            public_info = PublicPlayerInfo(
                player_id=player.player_id,
                name=player.name,
                is_alive=player.is_alive,
                seat_number=getattr(player, 'seat_number', player.player_id)  # 默认用ID作为座位号
            )

            if player.is_alive:
                alive_players.append(public_info)
            else:
                dead_players.append(public_info)

        return alive_players, dead_players

    def _extract_public_speech_history(self, game_state: GameState) -> List[SpeechRecord]:
        """提取公开发言历史（严格过滤）"""

        speech_history = []

        # 从游戏状态的事件日志中提取发言事件
        for event in game_state.event_history:
            if hasattr(event, 'event_type') and event.event_type == 'SPEECH':
                # 只添加公开发言，过滤内部思考或策略讨论
                if hasattr(event, 'is_public') and event.is_public:
                    speech_record = SpeechRecord(
                        speaker_id=getattr(event, 'speaker_id', 0),
                        content=getattr(event, 'content', ''),
                        round=getattr(event, 'round', game_state.round),
                        phase=getattr(event, 'phase', GamePhase.DAY_DISCUSSION)
                    )
                    speech_history.append(speech_record)

        return speech_history

    def _extract_public_voting_history(self, game_state: GameState) -> List[VotingRecord]:
        """提取公开投票历史"""

        voting_history = []

        for event in game_state.event_history:
            if hasattr(event, 'event_type') and event.event_type == 'VOTE':
                voting_record = VotingRecord(
                    voter_id=getattr(event, 'voter_id', 0),
                    target_id=getattr(event, 'target_id', None),
                    round=getattr(event, 'round', game_state.round),
                    phase=getattr(event, 'phase', GamePhase.DAY_VOTING)
                )
                voting_history.append(voting_record)

        return voting_history

    def _extract_death_announcements(self, game_state: GameState) -> List[DeathAnnouncement]:
        """提取死亡公告（隐藏具体死因）"""

        announcements = []

        for event in game_state.event_history:
            if hasattr(event, 'event_type') and event.event_type == 'DEATH':
                announcement = DeathAnnouncement(
                    player_id=getattr(event, 'player_id', 0),
                    player_name=getattr(event, 'player_name', 'Unknown'),
                    round=getattr(event, 'round', game_state.round),
                    is_execution=getattr(event, 'is_execution', False)
                )
                announcements.append(announcement)

        return announcements

    def _generate_role_hint(self, player_id: int, game_state: GameState, phase: GamePhase) -> Optional[str]:
        """生成故意模糊的角色提示"""

        player = self._find_player(player_id, game_state)
        if not player:
            return None

        # 只在夜晚给予角色相关的模糊提示
        if phase == GamePhase.NIGHT and hasattr(player, 'role') and player.role:
            role_name = getattr(player.role, 'name', 'unknown')

            # 根据角色类型给出模糊提示
            role_hints = {
                "werewolf": "你今晚和同伴可以一起讨论并选择一个人的命运",
                "seer": "你今晚可以窥探一个人的真实身份",
                "witch": "你今晚可以选择是否使用手中的神秘药剂",
                "guard": "你今晚可以选择守护一个人免受夜间伤害",
                "hunter": "你的特殊能力会在特定时刻触发",
                "villager": "你是村庄的一员，积极参与白天的讨论和投票",
            }

            hint = role_hints.get(role_name.lower())

            # 对于有夜晚行动能力的角色
            if hint and hasattr(player.role, 'has_night_action') and player.role.has_night_action:
                return hint

        return None

    def _generate_available_actions(self, player_id: int, game_state: GameState, phase: GamePhase) -> List[str]:
        """生成抽象的行动选项（避免泄露具体能力）"""

        available_actions = []
        player = self._find_player(player_id, game_state)

        if not player or not player.is_alive:
            return ["你已无法行动"]

        # 根据游戏阶段生成抽象选项
        if phase == GamePhase.DAY_DISCUSSION:
            available_actions.extend([
                "发表你的观点和看法",
                "质疑某人的发言",
                "支持或同意他人的观点",
                "保持谨慎或模糊发言",
                "引导讨论方向"
            ])

        elif phase == GamePhase.DAY_VOTING:
            available_actions.extend([
                "投票放逐你怀疑的玩家",
                "选择弃权不投票"
            ])

        elif phase == GamePhase.NIGHT and hasattr(player, 'role'):
            role_name = getattr(player.role, 'name', 'unknown')

            # 夜晚行动选项（故意抽象化）
            if hasattr(player.role, 'has_night_action') and player.role.has_night_action:
                if role_name.lower() == "werewolf":
                    available_actions.extend([
                        "与同伴商议目标",
                        "选择击杀目标",
                        "选择空刀不杀"
                    ])
                elif role_name.lower() == "seer":
                    available_actions.extend([
                        "选择查验目标",
                        "不使用查验能力"
                    ])
                elif role_name.lower() == "witch":
                    available_actions.extend([
                        "使用救人生存药剂",
                        "使用毒药攻击某人",
                        "不使用任何药剂"
                    ])
                elif role_name.lower() == "guard":
                    available_actions.extend([
                        "选择守护目标",
                        "选择不守护"
                    ])

        return available_actions

    def _build_safe_context(self, player_id: int, game_state: GameState, phase: GamePhase) -> Dict[str, Any]:
        """构建安全的上下文（不包含敏感信息）"""

        context = {}

        # 统计信息
        alive_count = len([p for p in game_state.players if p.is_alive])
        context['alive_count'] = alive_count
        context['total_players'] = len(game_state.players)

        # 当前轮次
        context['current_round'] = game_state.round

        # 存活玩家数量变化
        previous_deaths = len([d for d in game_state.event_history if getattr(d, 'event_type') == 'DEATH'])
        if previous_deaths > 0:
            context['deaths_so_far'] = previous_deaths

        # 讨论活跃度（非敏感）
        recent_speeches = len([e for e in game_state.event_history[-10:] if getattr(e, 'event_type') == 'SPEECH'])
        context['discussion_activity'] = 'high' if recent_speeches > 5 else 'medium' if recent_speeches > 2 else 'low'

        return context

    def _generate_time_description(self, game_state: GameState, phase: GamePhase) -> str:
        """生成叙事化的时间描述"""

        time_descriptions = {
            GamePhase.NIGHT: f"第{game_state.round}个夜晚，村庄陷入沉寂",
            GamePhase.DAY_DISCUSSION: f"第{game_state.round}个白天，村民们在广场聚集讨论",
            GamePhase.DAY_VOTING: f"第{game_state.round}个白天投票时刻",
            GamePhase.SHERIFF_ELECTION: f"第{game_state.round}天警长选举"
        }

        return time_descriptions.get(phase, "游戏进行中")

    def _get_player_seat_number(self, player_id: int, game_state: GameState) -> int:
        """获取玩家座位号"""
        player = self._find_player(player_id, game_state)
        return getattr(player, 'seat_number', player_id) if player else player_id

    def _find_player(self, player_id: int, game_state: GameState) -> Optional[Player]:
        """查找指定玩家"""
        return next((p for p in game_state.players if p.player_id == player_id), None)