"""
Player View - 玩家视角模型

定义严格裁剪后的玩家可见信息，确保SPEC合规
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from ..types import GamePhase


class PublicPlayerInfo(BaseModel):
    """公开的玩家信息 - 严格限制可公开的信息"""

    player_id: int = Field(description="玩家ID")
    name: str = Field(description="玩家名称")
    is_alive: bool = Field(description="是否存活")
    seat_number: int = Field(description="座位编号")

    # 注意：严格禁止包含真实身份信息
    # 不包含：role, camp, abilities, status_effects 等

    class Config:
        # 确保不会被意外扩展包含敏感信息
        extra = "forbid"


class SpeechRecord(BaseModel):
    """发言记录 - 仅保存公开发言"""

    speaker_id: int = Field(description="发言者ID")
    content: str = Field(description="发言内容")
    round: int = Field(description="回合数")
    phase: GamePhase = Field(description="游戏阶段")
    timestamp: Optional[str] = Field(default=None, description="时间戳")

    # 注意：不包含隐藏的意图分析或心理状态


class VotingRecord(BaseModel):
    """投票记录 - 仅显示公开的投票结果"""

    voter_id: int = Field(description="投票者ID")
    target_id: Optional[int] = Field(description="目标玩家ID（弃票则为None）")
    round: int = Field(description="投票回合")
    phase: GamePhase = Field(description="投票阶段")

    # 注意：不包含投票原因或内部推理


class DeathAnnouncement(BaseModel):
    """死亡公告 - 仅显示公开信息"""

    player_id: int = Field(description="死亡玩家ID")
    player_name: str = Field(description="死亡玩家姓名")
    round: int = Field(description="死亡回合")
    is_execution: bool = Field(description="是否为投票处决")

    # 重要：不显示具体死因（狼刀/毒药/特殊技能）


class PlayerView(BaseModel):
    """玩家视角 - 严格裁剪后的世界信息

    这是AI能够接触的全部世界信息，必须严格遵守SPEC限制
    """

    # === 基本信息 ===
    player_id: int = Field(description="当前玩家ID")
    current_phase: GamePhase = Field(description="当前游戏阶段")
    current_round: int = Field(description="当前回合数")
    seat_number: int = Field(description="当前玩家座位号")

    # === 公开信息 ===
    alive_players: List[PublicPlayerInfo] = Field(description="存活玩家列表")
    dead_players: List[PublicPlayerInfo] = Field(description="死亡玩家列表")
    total_players: int = Field(description="总玩家数")

    # === 历史信息（仅公开） ===
    speech_history: List[SpeechRecord] = Field(description="公开发言历史")
    voting_history: List[VotingRecord] = Field(description="投票历史")
    death_announcements: List[DeathAnnouncement] = Field(description="死亡公告列表")

    # === 角色提示（故意模糊） ===
    role_hint: Optional[str] = Field(
        description="模糊的角色提示，如'你拥有特殊能力'",
        default=None
    )

    # === 可用行动（抽象化） ===
    available_actions: List[str] = Field(
        description="抽象的行动选项，避免泄露具体能力",
        default_factory=list
    )

    # === 上下文数据（决策相关，但非敏感） ===
    context: Dict[str, Any] = Field(
        description="决策相关的非敏感上下文",
        default_factory=dict
    )

    # === 时间信息 ===
    current_time: Optional[str] = Field(
        default=None,
        description="游戏内时间提示（叙事化）"
    )

    class Config:
        # 严格禁止扩展，确保不会意外包含敏感信息
        extra = "forbid"

    def get_alive_player_ids(self) -> List[int]:
        """获取存活玩家ID列表"""
        return [p.player_id for p in self.alive_players if p.is_alive]

    def get_player_name(self, player_id: int) -> Optional[str]:
        """根据ID获取玩家名称"""
        for player in self.alive_players + self.dead_players:
            if player.player_id == player_id:
                return player.name
        return None

    def count_alive_players(self) -> int:
        """统计存活玩家数量"""
        return len([p for p in self.alive_players if p.is_alive])

    def get_recent_speeches(self, limit: int = 3) -> List[SpeechRecord]:
        """获取最近的发言记录"""
        return self.speech_history[-limit:] if self.speech_history else []

    def am_i_alive(self) -> bool:
        """检查自己是否存活"""
        my_info = next((p for p in self.alive_players if p.player_id == self.player_id), None)
        return my_info is not None and my_info.is_alive

    def get_self_info(self) -> Optional[PublicPlayerInfo]:
        """获取自己的公开信息"""
        return next((p for p in self.alive_players if p.player_id == self.player_id), None)

    def validate_spec_compliance(self) -> tuple[bool, List[str]]:
        """验证是否符合SPEC合规性要求"""
        violations = []

        # 检查是否包含敏感字段名
        sensitive_fields = ['role', 'camp', 'ability', 'status_effect', 'werewolf', 'seer', 'witch']
        all_fields = []

        # 收集所有字段名
        for field_name in self.model_fields_set:
            all_fields.append(field_name)

        # 检查上下文中的敏感信息
        if self.context:
            for key in self.context:
                all_fields.append(f"context.{key}")

        # 检查敏感字段
        for field in all_fields:
            for sensitive in sensitive_fields:
                if sensitive in field.lower():
                    violations.append(f"Found potentially sensitive field: {field}")

        # 检查发言内容是否包含过多游戏机制信息
        for speech in self.speech_history:
            content_lower = speech.content.lower()
            forbidden_terms = ['预言家', '女巫', '守卫', '技能', '能力验证']
            for term in forbidden_terms:
                if term in content_lower:
                    violations.append(f"Speech contains forbidden term: {term}")

        # 检查死亡公告是否泄露死因
        for death in self.death_announcements:
            content_lower = str(death).lower()
            causes = ['狼刀', '毒药', '守护', '技能']
            for cause in causes:
                if cause in content_lower:
                    violations.append(f"Death announcement reveals cause: {cause}")

        return len(violations) == 0, violations