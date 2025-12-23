"""
Response Parser - 响应解析器

解析和验证AI响应，确保输出格式正确
"""

import re
import json
from typing import Dict, Any, Optional, List, Tuple
from pydantic import ValidationError

from ..decision.models import Decision, IntentType


class ResponseParser:
    """响应解析器

    负责解析AI响应并验证输出格式
    """

    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.decision_patterns = self._load_decision_patterns()

    def parse_to_decision(
        self,
        response: str,
        required_intent_type: Optional[IntentType] = None
    ) -> Tuple[Optional[Decision], List[str]]:
        """将响应解析为Decision对象"""

        # 初始化错误列表
        errors = []

        try:
            # 预处理响应
            cleaned_response = self._preprocess_response(response)

            # 尝试解析JSON格式
            if self._is_json_format(cleaned_response):
                return self._parse_json_decision(cleaned_response, required_intent_type, errors)

            # 尝试解析自然语言
            return self._parse_natural_language_decision(cleaned_response, required_intent_type, errors)

        except Exception as e:
            errors.append(f"Parsing error: {str(e)}")
            return None, errors

    def _preprocess_response(self, response: str) -> str:
        """预处理响应文本"""

        # 移除多余的空白行
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)

        # 统一标点符号
        response = response.replace('！', '!').replace('？', '?').replace('。', '.')

        return response.strip()

    def _is_json_format(self, response: str) -> bool:
        """检查是否为JSON格式"""
        return bool(re.search(r'^\s*\{.*\}\s*$', response, re.DOTALL))

    def _parse_json_decision(
        self,
        response: str,
        required_intent_type: Optional[IntentType],
        errors: List[str]
    ) -> Tuple[Optional[Decision], List[str]]:
        """解析JSON格式的决策"""

        try:
            data = json.loads(response)

            # 验证必需字段
            if 'intent' not in data:
                errors.append("Missing 'intent' field in JSON response")
                return None, errors

            intent_value = data['intent']
            try:
                intent_type = IntentType(intent_value)
            except ValueError as e:
                errors.append(f"Invalid intent type: {intent_value}")
                return None, errors

            # 检查意图类型要求
            if required_intent_type and intent_type != required_intent_type:
                errors.append(f"Expected intent {required_intent_type}, got {intent_type}")
                return None, errors

            # 解析其他字段
            speech = data.get('speech', '')
            target = data.get('target')
            confidence = float(data.get('confidence', 0.5))

            # 验证字段
            if not speech.strip():
                errors.append("Empty speech field")
                return None, errors

            # 创建决策对象
            decision = Decision(
                intent=intent_type,
                target=target,
                speech=speech,
                confidence=max(0.0, min(1.0, confidence)),
                reasoning_trace=data.get('reasoning_trace', 'JSON format response')
            )

            return decision, errors

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
            return None, errors
        except ValidationError as e:
            errors.append(f"Decision validation error: {str(e)}")
            return None, errors

    def _parse_natural_language_decision(
        self,
        response: str,
        required_intent_type: Optional[IntentType],
        errors: List[str]
    ) -> Tuple[Optional[Decision], List[str]]:
        """解析自然语言格式的决策"""

        # 检测意图类型
        detected_intent = self._detect_intent_from_text(response)

        if not detected_intent:
            errors.append("Could not detect intent from natural language response")
            return None, errors

        # 检查意图类型要求
        if required_intent_type and detected_intent != required_intent_type:
            errors.append(f"Expected intent {required_intent_type}, detected {detected_intent}")
            return None, errors

        # 提取目标（如果需要）
        target = self._extract_target_from_text(response, detected_intent)

        # 计算置信度
        confidence = self._calculate_confidence_from_text(response)

        # 创建决策对象
        decision = Decision(
            intent=detected_intent,
            target=target,
            speech=response,
            confidence=confidence,
            reasoning_trace="Natural language parsing"
        )

        return decision, errors

    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """加载意图识别模式"""
        return {
            IntentType.STRONG_ACCUSE: [
                r'我确信|我强烈怀疑|明显有问题|必须关注|毫无疑问',
                r'这个人.*异常|行为.*可疑|情况.*不正常'
            ],
            IntentType.TEST_SUSPECT: [
                r'能解释.*吗|想听听.*看法|怎么了|为什么.*',
                r'请说明.*情况|能不能.*分析'
            ],
            IntentType.FOLLOW_OTHERS: [
                r'我同意|我支持|说得对|正是如此',
                r'这个观点.*好|分析.*到位|我也这么想'
            ],
            IntentType.LOW_PROFILE_SPEECH: [
                r'观望一下|再想想|暂时.*说|保持.*观察|没意见',
                r'需要.*时间|让我.*看|等等.*情况'
            ],
            IntentType.EMOTIONAL_APPEAL: [
                r'觉得.*不安|让人.*担心|很.*紧张|感到.*害怕',
                r'心情.*复杂|真是.*难受|状况.*危急'
            ],
            IntentType.ABSTAIN_VOTE: [
                r'弃票|不投票|观望|保持.*中立|暂时.*决定',
                r'需要.*信息|再考虑.*一下'
            ],
            IntentType.VOTE_SUSPECT: [
                r'投票.*给|我投.*|选择.*|决定投|就是.*了',
                r'目标.*是|对象.*为'
            ]
        }

    def _load_decision_patterns(self) -> Dict[str, str]:
        """加载决策解析模式"""
        return {
            'target_extraction': r'(?:投票|选择|针对|目标|投)(?:.*?)(?:玩家|玩家号?|ID)?\s*(\d+)',
            'confidence_indicators': r'(肯定|确定|一定|绝对|或许|可能|大概|好像|感觉)'
        }

    def _detect_intent_from_text(self, text: str) -> Optional[IntentType]:
        """从文本中检测意图类型"""
        text_lower = text.lower()

        # 为每个意图类型计算匹配分数
        intent_scores = {}
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            intent_scores[intent_type] = score

        # 选择得分最高的意图
        if not intent_scores or max(intent_scores.values()) == 0:
            return None

        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def _extract_target_from_text(self, text: str, intent: IntentType) -> Optional[int]:
        """从文本中提取目标ID"""
        if not intent.requires_target():
            return None

        # 使用正则表达式提取数字
        target_pattern = self.decision_patterns['target_extraction']
        match = re.search(target_pattern, text)
        if match:
            try:
                target_id = int(match.group(1))
                return target_id
            except (ValueError, IndexError):
                pass

        # 备用方法：查找所有数字
        numbers = re.findall(r'\b(?:玩家|player|ID)?\s*(\d+)\b', text, re.IGNORECASE)
        for num in numbers:
            try:
                target_id = int(num)
                if 1 <= target_id <= 20:  # 合理的玩家ID范围
                    return target_id
            except ValueError:
                continue

        return None

    def _calculate_confidence_from_text(self, text: str) -> float:
        """从文本计算置信度"""
        confidence = 0.5  # 基础置信度

        # 确定性词汇加分
        high_confidence_words = ['肯定', '确定', '一定', '绝对', '坚信', '确信', '毫无', '明确']
        for word in high_confidence_words:
            if word in text:
                confidence += 0.1

        # 不确定性词汇减分
        low_confidence_words = ['或许', '可能', '大概', '好像', '感觉', '似乎', '或许', '也许']
        for word in low_confidence_words:
            if word in text:
                confidence -= 0.1

        # 矛盾表达减分
        if re.search(r'虽然.*但是|虽然.*可是|尽管.*然而', text):
            confidence -= 0.15

        return max(0.0, min(1.0, confidence))

    def validate_decision_format(self, decision: Decision) -> List[str]:
        """验证决策格式"""
        errors = []

        # 检查必需字段
        if not decision.intent:
            errors.append("Missing intent")
        if not decision.speech or not decision.speech.strip():
            errors.append("Empty speech")

        # 检查置信度范围
        if not 0.0 <= decision.confidence <= 1.0:
            errors.append(f"Invalid confidence level: {decision.confidence}")

        # 检查目标合理性（如果需要）
        if decision.target and not (1 <= decision.target <= 20):
            errors.append(f"Invalid target ID: {decision.target}")

        # 检查文本长度
        if len(decision.speech) > 500:
            errors.append("Speech too long (>500 characters)")

        # 检查语言一致性
        if self._has_mixed_languages(decision.speech):
            errors.append("Mixed language content detected")

        return errors

    def _has_mixed_languages(self, text: str) -> bool:
        """检查是否包含混合语言"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))

        # 如果中英文字符比例过于失衡，可能是混合语言
        if chinese_chars > 0 and english_chars > 0:
            ratio = min(chinese_chars, english_chars) / max(chinese_chars, english_chars)
            return ratio < 0.2  # 如果较小语言占比不到20%，认为混合

        return False