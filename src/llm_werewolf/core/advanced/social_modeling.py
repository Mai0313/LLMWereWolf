"""
Social Modeling System - 社交建模系统

实现玩家间关系、信任网络、影响力传播、群体动力学等社交特性
"""

import time
import networkx as nx
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import math

from ..personality.models import PersonalityDimension


@dataclass
class SocialNode:
    """社交网络节点"""

    player_id: str
    personality_score: float = 0.5  # 人格影响力分数
    current_reputation: float = 0.0  # 当前声誉
    influence_radius: float = 1.0    # 影响力半径

    # 社交特质
    charisma: float = 0.5        # 魅力值：影响他人的能力
    persuasiveness: float = 0.5    # 说服力：改变他人观点的能力
    resistance: float = 0.5        # 抵抗力：抵抗他人影响的能力

    # 动态状态
    stress_impact: float = 0.0    # 当前压力对社交表现的影响
    confidence_effect: float = 0.0  # 当前自信对社交表现的影响


@dataclass
class SocialEdge:
    """社交网络边"""

    source_id: str
    target_id: str
    trust_level: float = 0.0       # 信任度 [-1.0, 1.0]
    influence_level: float = 0.0    # 影响程度 [0.0, 1.0]
    interaction_count: int = 0      # 互动次数
    last_interaction_time: float = 0.0

    # 关系类型
    relationship_type: str = "neutral"  # ally, enemy, neutral, mixed

    def update_from_interaction(self, interaction_data: Dict[str, Any]):
        """根据互动数据更新关系"""
        self.interaction_count += 1
        self.last_interaction_time = time.time()

        # 信任度更新
        trust_change = interaction_data.get('trust_change', 0.0)
        self.trust_level = max(-1.0, min(1.0, self.trust_level + trust_change * 0.1))

        # 影响度更新
        influence_change = interaction_data.get('influence_change', 0.0)
        self.influence_level = max(0.0, min(1.0, self.influence_level + influence_change * 0.1))

        # 更新关系类型
        if self.trust_level > 0.6:
            self.relationship_type = "ally"
        elif self.trust_level < -0.6:
            self.relationship_type = "enemy"
        else:
            self.relationship_type = "neutral"


class SocialNetwork:
    """社交网络"""

    def __init__(self):
        self.nodes: Dict[str, SocialNode] = {}
        self.edges: Dict[Tuple[str, str], SocialEdge] = {}
        self.network_graph = nx.DiGraph()

        # 群体动力学
        self.factions: Dict[str, List[str]] = defaultdict(list)  # 派系分组
        self.leadership_scores: Dict[str, float] = {}  # 领导力分数

    def add_player(self, player_id: str, personality_data: Dict[str, Any]):
        """添加玩家到社交网络"""
        # 计算社交特质
        dominance = personality_data.get('dominance', 0.5)
        social_pressure = personality_data.get('social_pressure', 0.5)
        persuasion = personality_data.get('persuasion', 0.5)

        node = SocialNode(
            player_id=player_id,
            charisma=(dominance + social_pressure) / 2 * 0.8 + np.random.normal(0, 0.1),
            persuasiveness=persuasion * 0.8 + np.random.normal(0, 0.1),
            resistance=1.0 - social_pressure * 0.6 + np.random.normal(0, 0.1),
            influence_radius=1.0 + dominance * 0.5
        )

        self.nodes[player_id] = node
        self.network_graph.add_node(player_id, **node.__dict__)

    def add_interaction(self, source_id: str, target_id: str, interaction_data: Dict[str, Any]):
        """添加社交互动"""
        edge_key = (source_id, target_id)

        if edge_key not in self.edges:
            self.edges[edge_key] = SocialEdge(source_id, target_id)
            self.network_graph.add_edge(source_id, target_id)

        self.edges[edge_key].update_from_interaction(interaction_data)

        # 更新反向边（双向关系）
        reverse_edge_key = (target_id, source_id)
        trust_change = -interaction_data.get('trust_change', 0.0) * 0.5  # 反向影响较小

        if reverse_edge_key not in self.edges:
            self.edges[reverse_edge_key] = SocialEdge(target_id, source_id)
            self.network_graph.add_edge(target_id, source_id)

        reverse_interaction = interaction_data.copy()
        reverse_interaction['trust_change'] = trust_change
        self.edges[reverse_edge_key].update_from_interaction(reverse_interaction)

    def calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """计算中心性指标"""
        try:
            # 网络中心性
            degree_centrality = nx.degree_centrality(self.network_graph.weighted_degree)
            betweenness_centrality = nx.betweenness_centrality(self.network_graph)
            closeness_centrality = nx.closeness_centrality(self.network_graph)
            eigenvector_centrality = nx.eigenvector_centrality(self.network_graph)

            # Pagerank
            pagerank = nx.pagerank(self.network_graph)

            centrality_metrics = {}
            for node_id in self.nodes:
                centrality_metrics[node_id] = {
                    'degree': degree_centrality.get(node_id, 0.0),
                    'betweenness': betweenness_centrality.get(node_id, 0.0),
                    'closeness': closeness_centrality.get(node_id, 0.0),
                    'eigenvector': eigenvector_centrality.get(node_id, 0.0),
                    'pagerank': pagerank.get(node_id, 0.0)
                }

            return centrality_metrics
        except:
            return {}

    def identify_factions(self) -> Dict[str, List[str]]:
        """识别派系（基于信任网络）"""
        # 使用社区检测算法
        try:
            communities = nx.community.louvain_communities(self.network_graph)
            factions = defaultdict(list)

            for i, community in enumerate(communities):
                faction_name = f"faction_{i+1}"
                for node in community:
                    factions[faction_name].append(node)

            # 为每个派系指定颜色标签
            faction_colors = ["red", "blue", "green", "yellow", "purple", "orange"]
            self.factions = {
                f"{faction}_color": faction_colors[i % len(faction_colors)]
                for i, faction in enumerate(factions.keys())
            }

            return dict(factions)
        except:
            return {"default_faction": list(self.nodes.keys())}

    def calculate_influence_spread(self, source_id: str, message_type: str) -> Dict[str, float]:
        """计算影响力传播"""
        if source_id not in self.nodes:
            return {}

        source_node = self.nodes[source_id]
        influence_scores = {}
        visited = set()

        # 使用深度优先搜索传播影响力
        def propagate_influence(node_id: str, current_influence: float, depth: int, path: List[str]):
            if node_id in visited or depth > 3 or current_influence < 0.01:
                return

            visited.add(node_id)
            influence_scores[node_id] = influence_scores.get(node_id, 0.0) + current_influence

            # 获取出边
            for neighbor in self.network_graph.neighbors(node_id):
                edge_key = (node_id, neighbor)
                if edge_key in self.edges:
                    edge = self.edges[edge_key]
                    node = self.nodes[neighbor]

                    # 计算传播衰减
                    base_attenuation = 0.6
                    alignment_bonus = 1.0

                    # 信任度调整
                    if edge.trust_level > 0:
                        alignment_bonus = 1.0 + edge.trust_level * 0.3
                    elif edge.trust_level < 0:
                        alignment_bonus = 0.5 + edge.trust_level * 0.2

                    # 阻抗力调整
                    resistance_multiplier = 1.0 - node.resistance * 0.5

                    new_influence = (current_influence * base_attenuation *
                                     alignment_bonus * resistance_multiplier)

                    propagate_influence(neighbor, new_influence, depth + 1, path + [node_id])

        # 开始传播
        initial_influence = source_node.charisma * source_node.persuasiveness
        propagate_influence(source_id, initial_influence, 0, [source_id])

        return influence_scores

    def predict_voting_outcome(self, voter_id: str, candidates: List[str]) -> Dict[str, float]:
        """预测投票结果"""
        voting_weights = {}
        voter_node = self.nodes[voter_id]

        for candidate in candidates:
            weight = 0.0

            # 基础权重
            base_weight = 1.0

            # 信任度权重
            edge_key = (voter_id, candidate)
            if edge_key in self.edges:
                edge = self.edges[edge_key]
                trust_weight = max(0.0, edge.trust_level)  # 信任度越低，越可能投反对票
                weight = base_weight * (1.0 + trust_weight)
            else:
                # 无历史关系，使用默认权重
                weight = base_weight

            # 社交影响力
            influence_data = self.calculate_influence_spread(candidate, "voting_request")
            candidate_influence = influence_data.get(voter_id, 0.0)
            weight += candidate_influence * 0.3

            voting_weights[candidate] = weight

        # 归一化权重
        total_weight = sum(voting_weights.values())
        if total_weight > 0:
            for candidate in voting_weights:
                voting_weights[candidate] /= total_weight
        else:
            # 弃权处理
            for candidate in voting_weights:
                voting_weights[candidate] = 1.0 / len(candidates)

        return voting_weights

    def detect_social_dynamics(self) -> Dict[str, Any]:
        """检测社交动态"""
        dynamics = {}

        # 派系分析
        factions = self.identify_factions()
        dynamics['faction_analysis'] = {
            'number_of_factions': len(factions),
            'faction_sizes': {name: len(members) for name, members in factions.items()},
            'dominant_faction': max(factions.items(), key=lambda x: len(x[1]))[0] if factions else None
        }

        # 中心性分析
        centrality_metrics = self.calculate_centrality_metrics()
        if centrality_metrics:
            # 找出最有影响力的玩家
            most_influential = max(centrality_metrics.items(),
                                  key=lambda x: x[1]['eigenvector'])
            dynamics['influence_analysis'] = {
                'most_influential_player': most_influential[0],
                'influence_metric': most_influential[1]['eigenvector']
            }

        # 信任密度
        trust_density = 0.0
        edge_count = 0
        total_trust = 0.0

        for edge in self.edges.values():
            edge_count += 1
            total_trust += abs(edge.trust_level)

        if edge_count > 0:
            trust_density = total_trust / edge_count

        dynamics['trust_analysis'] = {
            'trust_density': trust_density,
            'total_interactions': edge_count,
            'avg_trust_level': total_trust / edge_count if edge_count > 0 else 0.0
        }

        return dynamics


class SocialModelingSystem:
    """社交建模系统主类"""

    def __init__(self):
        self.network = SocialNetwork()
        self.interaction_history: List[Dict[str, Any]] = []
        self.dynamics_history: List[Dict[str, Any]] = []

    def process_social_event(self, event_data: Dict[str, Any]) -> None:
        """处理社交事件"""
        self.interaction_history.append(event_data)

        event_type = event_data.get('type', 'unknown')

        if event_type == 'speech_interaction':
            self._process_speech_interaction(event_data)
        elif event_type == 'voting_interaction':
            self._process_voting_interaction(event_data)
        elif event_type == 'player_death':
            self._process_death_event(event_data)
        elif event_type == 'alliance_formation':
            self._process_alliance_formation(event_data)

    def _process_speech_interaction(self, event_data: Dict[str, Any]) -> None:
        """处理言语互动"""
        speaker = event_data.get('speaker')
        target = event_data.get('target')
        sentiment = event_data.get('sentiment', 'neutral')

        if speaker and target and speaker != target:
            trust_change = 0.0
            influence_change = 0.0

            if sentiment == 'positive':
                trust_change = 0.1
                influence_change = 0.1
            elif sentiment == 'negative':
                trust_change = -0.15
                influence_change = -0.05

            interaction_data = {
                'trust_change': trust_change,
                'influence_change': influence_change,
                'event_type': 'speech'
            }

            self.network.add_interaction(speaker, target, interaction_data)

    def _process_voting_interaction(self, event_data: Dict[str, Any]) -> None:
        """处理投票互动"""
        voter = event_data.get('voter')
        target = event_data.get('target')

        if voter and target:
            # 投票反映信任关系
            trust_change = -0.05  # 投票通常表示某种程度上不信任
            influence_change = 0.02

            interaction_data = {
                'trust_change': trust_change,
                'influence_change': influence_change,
                'event_type': 'voting'
            }

            self.network.add_interaction(voter, target, interaction_data)

    def _process_death_event(self, event_data: Dict[str, Any]) -> None:
        """处理死亡事件"""
        deceased = event_data.get('player')
        death_event_type = event_data.get('death_type', 'unknown')

        if deceased:
            # 死亡事件影响所有关系
            for other_player in self.network.nodes:
                if other_player != deceased:
                    trust_decrease = 0.1 if death_event_type == 'vote_out' else 0.05
                    interaction_data = {
                        'trust_change': -trust_decrease,
                        'influence_change': 0.0,
                        'event_type': 'death'
                    }
                    self.network.add_interaction(other_player, deceased, interaction_data)

    def _process_alliance_formation(self, event_data: Dict[str, Any]) -> None:
        """处理联盟形成"""
        alliance_members = event_data.get('members', [])

        if len(alliance_members) >= 2:
            # 联盟成员之间的信任度增加
            for i, member1 in enumerate(alliance_members):
                for member2 in alliance_members[i+1:]:
                    trust_increase = 0.2
                    interaction_data = {
                        'trust_change': trust_increase,
                        'influence_change': 0.05,
                        'event_type': 'alliance'
                    }
                    self.network.add_interaction(member1, member2, interaction_data)

    def predict_group_dynamics(self) -> Dict[str, Any]:
        """预测群体动态"""
        dynamics = self.network.detect_social_dynamics()

        # 添加预测性分析
        prediction = {
            'current_dynamics': dynamics,
            'predicted_next_moves': [],
            'vulnerabilities': [],
            'opportunities': []
        }

        # 预测下一步可能的行动
        if 'faction_analysis' in dynamics:
            factions = dynamics['faction_analysis']

            if len(factions['number_of_factions']) > 1:
                # 多阵营情况，预测可能的冲突
                dominant_faction = dynamics['faction_analysis']['dominant_faction']
                other_factions = [name for name in factions if name != dominant_faction]

                prediction['predicted_next_moves'].append(
                    f"{dominant_faction} likely to consolidate power"
                )
                prediction['vulnerabilities'].append(
                    f"Smaller factions may be targeted by {dominant_faction}"
                )

        return prediction

    def generate_social_network_analysis(self) -> str:
        """生成社交网络分析报告"""
        dynamics = self.network.detect_social_dynamics()

        report = []
        report.append("📊 SOCIAL NETWORK ANALYSIS")
        report.append("=" * 50)

        # 网络概览
        report.append(f"Network: {len(self.network.nodes)} nodes, {len(self.network.edges)/2} edges")

        # 派系分析
        if 'faction_analysis' in dynamics:
            faction_analysis = dynamics['faction_analysis']
            report.append(f"\n🏃 Faction Structure:")
            report.append(f"Number of factions: {faction_analysis['number_of_factions']}")
            for faction_name, members in faction_analysis.get('faction_sizes', {}).items():
                report.append(f"  {faction_name}: {members} members")

        # 影响力分析
        if 'influence_analysis' in dynamics:
            influence = dynamics['influence_analysis']
            report.append(f"\n👑 Influence Analysis:")
            report.append(f"Most influential: {influence['most_influential_player']}")
            report.append(f"Influence score: {influence['influence_metric']:.3f}")

        # 信任分析
        if 'trust_analysis' in dynamics:
            trust = dynamics['trust_analysis']
            report.append(f"\n🤝 Trust Analysis:")
            report.append(f"Trust density: {trust['trust_density']:.3f}")
            report.append(f"Average trust: {trust['avg_trust_level']:.3f}")

        report.append("\n" + "=" * 50)

        return "\n".join(report)