"""
Replay System - 复盘系统

支持游戏回放、视角切换、决策分析等功能
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass

from ..types import GamePhase, PlayerStatus


class ReplayViewMode(str, Enum):
    """复盘视角模式"""
    JUDGE = "judge"         # 裁判视角：看到所有信息
    PLAYER = "player"       # 玩家视角：只能看到该玩家知道的信息
    SPECTATOR = "spectator"  # 观众视角：只看公开信息


@dataclass
class ReplayState:
    """复盘状态"""
    current_index: int = 0
    view_mode: ReplayViewMode = ReplayViewMode.JUDGE
    selected_player: Optional[str] = None
    playback_speed: float = 1.0
    is_paused: bool = True

    def copy(self):
        """复制状态"""
        return ReplayState(
            current_index=self.current_index,
            view_mode=self.view_mode,
            selected_player=self.selected_player,
            playback_speed=self.playback_speed,
            is_paused=self.is_paused
        )


class ReplayController:
    """复盘控制器"""

    def __init__(self, game_data: Dict[str, Any]):
        self.game_data = game_data
        self.events = sorted(game_data.get('events', []), key=lambda x: x.get('timestamp', 0))
        self.player_results = game_data.get('player_results', {})
        self.decisions = game_data.get('decisions', [])

        self.state = ReplayState()
        self.callbacks = {}

        # 构建回放索引
        self._build_replay_indices()

    def _build_replay_indices(self):
        """构建回放索引"""
        self.phase_events = {}
        self.round_events = {}
        self.player_events = defaultdict(list)

        for i, event in enumerate(self.events):
            # 阶段索引
            phase = event.get('phase', 'unknown')
            if phase not in self.phase_events:
                self.phase_events[phase] = []
            self.phase_events[phase].append((i, event))

            # 回合索引
            round_num = event.get('round', 0)
            if round_num not in self.round_events:
                self.round_events[round_num] = []
            self.round_events[round_num].append((i, event))

            # 玩家索引
            player_id = event.get('player_id')
            player_name = self._get_player_name_by_id(player_id)
            if player_name:
                self.player_events[player_name].append((i, event))

    def _get_player_name_by_id(self, player_id: Any) -> Optional[str]:
        """根据ID获取玩家名称"""
        player_id = str(player_id)  # 确保是字符串

        for player_name, player_data in self.player_results.items():
            # 这里可以在game_data中添加player_id映射
            # 暂时使用名称匹配
            if player_id in player_name:
                return player_name
        return None

    def set_callback(self, event_type: str, callback: Callable):
        """设置回调函数"""
        self.callbacks[event_type] = callback

    def trigger_callback(self, event_type: str, data: Any = None):
        """触发回调"""
        if event_type in self.callbacks:
            self.callbacks[event_type](data)

    def get_current_event(self) -> Optional[Dict[str, Any]]:
        """获取当前事件"""
        if 0 <= self.state.current_index < len(self.events):
            return self.events[self.state.current_index]
        return None

    def next_event(self) -> bool:
        """下一个事件"""
        if self.state.current_index < len(self.events) - 1:
            self.state.current_index += 1
            self.trigger_callback('event_changed', self.get_current_event())
            return True
        return False

    def previous_event(self) -> bool:
        """上一个事件"""
        if self.state.current_index > 0:
            self.state.current_index -= 1
            self.trigger_callback('event_changed', self.get_current_event())
            return True
        return False

    def jump_to_index(self, index: int) -> bool:
        """跳转到指定索引"""
        if 0 <= index < len(self.events):
            self.state.current_index = index
            self.trigger_callback('event_changed', self.get_current_event())
            return True
        return False

    def jump_to_phase(self, phase: str) -> bool:
        """跳转到指定阶段"""
        if phase in self.phase_events and self.phase_events[phase]:
            first_index = self.phase_events[phase][0][0]
            return self.jump_to_index(first_index)
        return False

    def jump_to_round(self, round_num: int) -> bool:
        """跳转到指定回合"""
        if round_num in self.round_events and self.round_events[round_num]:
            first_index = self.round_events[round_num][0][0]
            return self.jump_to_index(first_index)
        return False

    def jump_to_player_event(self, player_name: str, event_index: int = 0) -> bool:
        """跳转到指定玩家的事件"""
        if (player_name in self.player_events and
            len(self.player_events[player_name]) > event_index):
            target_index = self.player_events[player_name][event_index][0]
            return self.jump_to_index(target_index)
        return False

    def set_view_mode(self, mode: ReplayViewMode, player_name: Optional[str] = None):
        """设置视角模式"""
        self.state.view_mode = mode
        if mode == ReplayViewMode.PLAYER and player_name:
            self.state.selected_player = player_name
        elif mode != ReplayViewMode.PLAYER:
            self.state.selected_player = None

        self.trigger_callback('view_changed', self.state)

    def get_filtered_events(self) -> List[Dict[str, Any]]:
        """根据当前视角获取过滤后的事件"""
        if self.state.view_mode == ReplayViewMode.JUDGE:
            return [self.events[self.state.current_index]] if 0 <= self.state.current_index < len(self.events) else []

        elif self.state.view_mode == ReplayViewMode.PLAYER and self.state.selected_player:
            # 只显示该玩家相关的和公开事件
            filtered_events = []
            current_event = self.get_current_event()

            if current_event:
                # 检查是否是公开事件或该玩家相关
                is_public = self._is_public_event(current_event)
                is_player_related = self._is_player_event(current_event, self.state.selected_player)

                if is_public or is_player_related:
                    # 如果是玩家相关事件，可能需要过滤信息
                    filtered_event = self._filter_event_for_player(current_event, self.state.selected_player)
                    filtered_events.append(filtered_event)

            return filtered_events

        else:  # SPECTATOR
            # 只显示公开事件
            current_event = self.get_current_event()
            return [current_event] if current_event and self._is_public_event(current_event) else []

    def _is_public_event(self, event: Dict[str, Any]) -> bool:
        """判断是否为公开事件"""
        public_types = [
            'GAME_STARTED', 'PHASE_CHANGED', 'DEATH_ANNOUNCEMENT',
            'VOTE_STARTED', 'VOTE_COMPLETED', 'GAME_ENDED'
        ]
        return any(public_type in event.get('type', '').upper() for public_type in public_types)

    def _is_player_event(self, event: Dict[str, Any], player_name: str) -> bool:
        """判断是否是玩家相关事件"""
        return (event.get('player_name') == player_name or
                event.get('target_name') == player_name or
                (self._get_player_name_by_id(event.get('player_id')) == player_name))

    def _filter_event_for_player(self, event: Dict[str, Any], player_name: str) -> Dict[str, Any]:
        """为玩家过滤事件信息"""
        filtered_event = event.copy()

        # 过滤敏感信息
        sensitive_keys = ['actual_target_role', 'werewolf_discussion', 'private_info']
        for key in sensitive_keys:
            if key in filtered_event:
                del filtered_event[key]

        # 如果是目标信息，且玩家不是目标，可能需要隐藏详细信息
        if 'target' in filtered_event and filtered_event.get('player_name') != player_name:
            if 'target_details' in filtered_event:
                del filtered_event['target_details']

        return filtered_event

    def get_analysis_at_point(self) -> Dict[str, Any]:
        """获取当前时间点的分析数据"""
        current_event = self.get_current_event()
        current_index = self.state.current_index

        # 统计到当前点的事件
        past_events = self.events[:current_index + 1] if current_event else []

        analysis = {
            "current_time": current_event.get('timestamp', 0) if current_event else 0,
            "event_count": len(past_events),
            "current_phase": current_event.get('phase', 'unknown') if current_event else 'unknown',
            "current_round": current_event.get('round', 0) if current_event else 0,
            "player_status": self._get_player_status_at_point(),
            "decision_summary": self._get_decision_summary_at_point(past_events),
            "survival_stats": self._get_survival_stats_at_point(current_index)
        }

        return analysis

    def _get_player_status_at_point(self) -> Dict[str, str]:
        """获取当前时间点的玩家状态"""
        status = {}

        # 先设为全部存活
        for player_name in self.player_results.keys():
            status[player_name] = PlayerStatus.ALIVE.value

        # 根据死亡公告更新状态
        current_index = self.state.current_index
        for i in range(min(current_index + 1, len(self.events))):
            event = self.events[i]
            if event.get('type') == 'PLAYER_DEATH':
                player_name = event.get('player_name')
                if player_name:
                    status[player_name] = PlayerStatus.DEAD.value

        return status

    def _get_decision_summary_at_point(self, past_events: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取当前时间点的决策统计"""
        decision_count = defaultdict(int)

        for event in past_events:
            if event.get('type') in ['SPEECH', 'VOTE', 'NIGHT_ACTION']:
                player_name = event.get('player_name')
                if player_name:
                    decision_count[player_name] += 1

        return dict(decision_count)

    def _get_survival_stats_at_point(self, current_index: int) -> Dict[str, Any]:
        """获取生存统计"""
        state = self._get_player_status_at_point()

        alive_players = sum(1 for status in state.values() if status == PlayerStatus.ALIVE.value)
        total_players = len(state)

        return {
            "alive_count": alive_players,
            "dead_count": total_players - alive_players,
            "survival_rate": alive_players / max(1, total_players)
        }

    def export_replay_data(self, filepath: str):
        """导出回放数据"""
        replay_data = {
            "game_id": self.game_data.get('game_id', 'unknown'),
            "events": self.events,
            "player_results": self.player_results,
            "decisions": self.decisions,
            "analysis_points": self._create_analysis_points()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(replay_data, f, indent=2, ensure_ascii=False)

        print(f"📼 Replay data exported to: {filepath}")

    def _create_analysis_points(self) -> List[Dict[str, Any]]:
        """创建关键分析点"""
        analysis_points = []

        # 添加阶段变化点
        phase_changes = set()
        for i, event in enumerate(self.events):
            if event.get('type') == 'PHASE_CHANGED':
                phase_changes.add(i)

        # 添加死亡事件点
        death_events = []
        for i, event in enumerate(self.events):
            if event.get('type') == 'PLAYER_DEATH':
                death_events.append(i)

        # 添加投票事件点
        vote_events = []
        for i, event in enumerate(self.events):
            if event.get('type') in ['VOTE_STARTED', 'VOTE_COMPLETED']:
                vote_events.append(i)

        # 合并并排序
        all_points = sorted(set(phase_changes) | set(death_events) | set(vote_events))

        for point in all_points:
            self.state.current_index = point
            analysis = self.get_analysis_at_point()
            analysis["event_index"] = point
            analysis_points.append(analysis)

        return analysis_points


class ReplayViewer:
    """复盘查看器"""

    def __init__(self, controller: ReplayController):
        self.controller = controller

    def display_current_state(self) -> str:
        """显示当前状态"""
        current_event = self.controller.get_current_event()
        if not current_event:
            return "⏹️  No events available"

        # 基础信息
        phase = current_event.get('phase', 'unknown')
        round_num = current_event.get('round', 0)
        timestamp = current_event.get('timestamp', 0)

        # 获取分析数据
        analysis = self.controller.get_analysis_at_point()

        output = []
        output.append(f"⚡ Event {self.controller.state.current_index + 1}/{len(self.controller.events)}")
        output.append(f"📍 Phase: {phase}, Round {round_num}")
        output.append(f"🕒 Time: {timestamp:.2f}s")
        output.append(f"💀 Alive: {analysis['survival_stats']['alive_count']}/{len(analysis['player_status'])}")

        # 显示过滤后的事件
        filtered_events = self.controller.get_filtered_events()
        for event in filtered_events:
            output.append(f"📢 {event.get('message', 'No message')}")

        return "\n".join(output)

    def get_timeline(self) -> List[Dict[str, Any]]:
        """获取时间线"""
        timeline = []

        for i, event in enumerate(self.controller.events):
            timeline.append({
                "index": i,
                "type": event.get('type', 'unknown'),
                "message": event.get('message', 'No message'),
                "phase": event.get('phase', 'unknown'),
                "round": event.get('round', 0),
                "timestamp": event.get('timestamp', 0)
            })

        return timeline

    def get_player_timeline(self, player_name: str) -> List[Dict[str, Any]]:
        """获取特定玩家的时间线"""
        player_timeline = []

        for i, event in enumerate(self.controller.events):
            if self.controller._is_player_event(event, player_name):
                player_timeline.append({
                    "index": i,
                    "type": event.get('type', 'unknown'),
                    "message": event.get('message', 'No message'),
                    "phase": event.get('phase', 'unknown'),
                    "round": event.get('round', 0),
                    "timestamp": event.get('timestamp', 0)
                })

        return player_timeline

    def generate_summary_report(self) -> str:
        """生成摘要报告"""
        analysis = self.controller._create_analysis_points()
        if not analysis:
            return "No analysis data available"

        report = ["📊 GAME REPLAY SUMMARY"]
        report.append("=" * 50)

        for point in analysis:
            phase = point.get('current_phase', 'unknown')
            round_num = point.get('current_round', 0)
            alive = point['survival_stats']['alive_count']
            total = len(point['player_status'])

            report.append(f"\n📍 Round {round_num} - {phase}")
            report.append(f"   Survivors: {alive}/{total} ({point['survival_stats']['survival_rate']:.1%})")

            if point['decision_summary']:
                most_active = max(point['decision_summary'].items(), key=lambda x: x[1])
                report.append(f"   Most Active: {most_active[0]} ({most_active[1]} decisions)")

        report.append("\n" + "=" * 50)

        return "\n".join(report)


from collections import defaultdict