"""Tests for ai/agents.py module."""

import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest
from pydantic import ValidationError

from llm_werewolf.ai.agents import LLMAgent, PlayerConfig, PlayersConfig, load_config, create_agent
from llm_werewolf.core.agent import DemoAgent, HumanAgent


class TestPlayerConfig:
    """Tests for PlayerConfig model."""

    def test_valid_demo_config(self) -> None:
        """Test creating a valid demo player config."""
        config = PlayerConfig(name="TestPlayer", model="demo")
        assert config.name == "TestPlayer"
        assert config.model == "demo"
        assert config.base_url is None

    def test_valid_human_config(self) -> None:
        """Test creating a valid human player config."""
        config = PlayerConfig(name="Human", model="human")
        assert config.name == "Human"
        assert config.model == "human"
        assert config.base_url is None

    def test_valid_llm_config(self) -> None:
        """Test creating a valid LLM player config."""
        config = PlayerConfig(
            name="GPT",
            model="gpt-4",
            base_url="https://api.openai.com/v1",
            api_key_env="OPENAI_API_KEY",
        )
        assert config.name == "GPT"
        assert config.model == "gpt-4"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.api_key_env == "OPENAI_API_KEY"

    def test_llm_without_base_url(self) -> None:
        """Test that LLM config without base_url raises error."""
        with pytest.raises(ValidationError, match="base_url is required"):
            PlayerConfig(name="GPT", model="gpt-4", api_key_env="OPENAI_API_KEY", base_url=None)

    def test_demo_without_base_url(self) -> None:
        """Test that demo config doesn't require base_url."""
        config = PlayerConfig(name="Demo", model="demo")
        assert config.base_url is None

    def test_human_without_base_url(self) -> None:
        """Test that human config doesn't require base_url."""
        config = PlayerConfig(name="Human", model="human")
        assert config.base_url is None


class TestPlayersConfig:
    """Tests for PlayersConfig model."""

    def test_valid_players_config(self) -> None:
        """Test creating a valid players configuration."""
        config = PlayersConfig(
            language="en-US",
            players=[PlayerConfig(name=f"Player{i}", model="demo") for i in range(6)],
        )
        assert config.language == "en-US"
        assert len(config.players) == 6

    def test_default_language(self) -> None:
        """Test default language is en-US."""
        config = PlayersConfig(
            players=[PlayerConfig(name=f"Player{i}", model="demo") for i in range(6)]
        )
        assert config.language == "en-US"

    def test_too_few_players(self) -> None:
        """Test that too few players raises error."""
        with pytest.raises(ValidationError):
            PlayersConfig(
                players=[PlayerConfig(name=f"Player{i}", model="demo") for i in range(3)]
            )

    def test_too_many_players(self) -> None:
        """Test that too many players raises error."""
        with pytest.raises(ValidationError):
            PlayersConfig(
                players=[PlayerConfig(name=f"Player{i}", model="demo") for i in range(25)]
            )

    def test_duplicate_player_names(self) -> None:
        """Test that duplicate player names raises error."""
        with pytest.raises(ValidationError, match="Duplicate player names"):
            PlayersConfig(
                players=[
                    PlayerConfig(name="Alice", model="demo"),
                    PlayerConfig(name="Bob", model="demo"),
                    PlayerConfig(name="Alice", model="demo"),
                    PlayerConfig(name="David", model="demo"),
                    PlayerConfig(name="Eve", model="demo"),
                    PlayerConfig(name="Frank", model="demo"),
                ]
            )

    def test_unique_player_names(self) -> None:
        """Test that unique player names passes validation."""
        config = PlayersConfig(
            players=[
                PlayerConfig(name="Alice", model="demo"),
                PlayerConfig(name="Bob", model="demo"),
                PlayerConfig(name="Charlie", model="demo"),
                PlayerConfig(name="David", model="demo"),
                PlayerConfig(name="Eve", model="demo"),
                PlayerConfig(name="Frank", model="demo"),
            ]
        )
        assert len(config.players) == 6


class TestLLMAgent:
    """Tests for LLMAgent class."""

    def test_llm_agent_creation(self) -> None:
        """Test creating an LLM agent."""
        agent = LLMAgent(
            name="TestAgent",
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            language="en-US",
        )
        assert agent.name == "TestAgent"
        assert agent.model == "gpt-4"
        assert agent.api_key == "test-key"
        assert agent.base_url == "https://api.openai.com/v1"
        assert agent.language == "en-US"
        assert agent.chat_history == []
        assert agent.decision_history == []

    @patch("llm_werewolf.ai.agents.OpenAI")
    def test_llm_agent_client_creation(self, mock_openai: Mock) -> None:
        """Test that LLM agent creates OpenAI client."""
        agent = LLMAgent(
            name="TestAgent",
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            language="en-US",
        )
        # Access client to trigger creation
        _ = agent.client
        mock_openai.assert_called_once_with(
            api_key="test-key", base_url="https://api.openai.com/v1"
        )

    @patch("llm_werewolf.ai.agents.OpenAI")
    def test_llm_agent_get_response(self, mock_openai: Mock) -> None:
        """Test getting response from LLM agent."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        agent = LLMAgent(
            name="TestAgent",
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            language="en-US",
        )

        response = agent.get_response("Test message")

        assert response == "Test response"
        assert len(agent.chat_history) == 2
        assert agent.chat_history[0]["role"] == "user"
        assert "Test message" in agent.chat_history[0]["content"]
        assert "en-US" in agent.chat_history[0]["content"]
        assert agent.chat_history[1]["role"] == "assistant"
        assert agent.chat_history[1]["content"] == "Test response"

    @patch("llm_werewolf.ai.agents.OpenAI")
    def test_llm_agent_get_response_with_reasoning(self, mock_openai: Mock) -> None:
        """Test getting response from LLM agent with reasoning effort."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Reasoned response"
        mock_client.chat.completions.create.return_value = mock_response

        agent = LLMAgent(
            name="TestAgent",
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            language="zh-TW",
            reasoning_effort="high",
        )

        response = agent.get_response("Test message")

        assert response == "Reasoned response"
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["reasoning_effort"] == "high"

    def test_llm_agent_add_decision(self) -> None:
        """Test adding decision to LLM agent history."""
        agent = LLMAgent(
            name="TestAgent",
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            language="en-US",
        )

        agent.add_decision("Round 1: Checked Bob")
        agent.add_decision("Round 2: Protected Alice")

        assert len(agent.decision_history) == 2
        assert agent.decision_history[0] == "Round 1: Checked Bob"
        assert agent.decision_history[1] == "Round 2: Protected Alice"

    def test_llm_agent_get_decision_context_empty(self) -> None:
        """Test getting decision context when empty."""
        agent = LLMAgent(
            name="TestAgent",
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            language="en-US",
        )

        context = agent.get_decision_context()
        assert context == ""

    def test_llm_agent_get_decision_context(self) -> None:
        """Test getting decision context with decisions."""
        agent = LLMAgent(
            name="TestAgent",
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            language="en-US",
        )

        agent.add_decision("Round 1: Checked Bob")
        agent.add_decision("Round 2: Protected Alice")

        context = agent.get_decision_context()
        assert "Your previous actions:" in context
        assert "- Round 1: Checked Bob" in context
        assert "- Round 2: Protected Alice" in context


class TestCreateAgent:
    """Tests for create_agent factory function."""

    def test_create_demo_agent(self) -> None:
        """Test creating a demo agent."""
        config = PlayerConfig(name="Demo", model="demo")
        agent = create_agent(config)

        assert isinstance(agent, DemoAgent)
        assert agent.name == "Demo"
        assert agent.model == "demo"

    def test_create_human_agent(self) -> None:
        """Test creating a human agent."""
        config = PlayerConfig(name="Human", model="human")
        agent = create_agent(config)

        assert isinstance(agent, HumanAgent)
        assert agent.name == "Human"
        assert agent.model == "human"

    def test_create_llm_agent_with_api_key(self) -> None:
        """Test creating an LLM agent with API key."""
        config = PlayerConfig(
            name="GPT",
            model="gpt-4",
            base_url="https://api.openai.com/v1",
            api_key_env="TEST_API_KEY",
        )

        with patch.dict(os.environ, {"TEST_API_KEY": "test-key"}):
            agent = create_agent(config, language="zh-TW")

        assert isinstance(agent, LLMAgent)
        assert agent.name == "GPT"
        assert agent.model == "gpt-4"
        assert agent.api_key == "test-key"
        assert agent.base_url == "https://api.openai.com/v1"
        assert agent.language == "zh-TW"

    def test_create_llm_agent_without_api_key(self) -> None:
        """Test creating an LLM agent without API key raises error."""
        config = PlayerConfig(
            name="GPT",
            model="gpt-4",
            base_url="https://api.openai.com/v1",
            api_key_env="MISSING_KEY",
        )

        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(ValueError, match="API key not found"),
        ):
            create_agent(config)

    def test_create_demo_agent_case_insensitive(self) -> None:
        """Test creating demo agent is case insensitive."""
        config = PlayerConfig(name="Demo", model="DEMO")
        agent = create_agent(config)

        assert isinstance(agent, DemoAgent)

    def test_create_human_agent_case_insensitive(self) -> None:
        """Test creating human agent is case insensitive."""
        config = PlayerConfig(name="Human", model="HUMAN")
        agent = create_agent(config)

        assert isinstance(agent, HumanAgent)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_from_path(self, tmp_path: Path) -> None:
        """Test loading config from YAML file."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
language: en-US
players:
  - name: Alice
    model: demo
  - name: Bob
    model: demo
  - name: Charlie
    model: demo
  - name: David
    model: demo
  - name: Eve
    model: demo
  - name: Frank
    model: demo
"""
        )

        config = load_config(config_file)

        assert config.language == "en-US"
        assert len(config.players) == 6
        assert config.players[0].name == "Alice"
        assert config.players[0].model == "demo"

    def test_load_config_from_string(self, tmp_path: Path) -> None:
        """Test loading config from string path."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
language: zh-TW
players:
  - name: Player1
    model: demo
  - name: Player2
    model: demo
  - name: Player3
    model: demo
  - name: Player4
    model: demo
  - name: Player5
    model: demo
  - name: Player6
    model: demo
"""
        )

        config = load_config(str(config_file))

        assert config.language == "zh-TW"
        assert len(config.players) == 6

    def test_load_config_with_llm_players(self, tmp_path: Path) -> None:
        """Test loading config with LLM players."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
language: en-US
players:
  - name: GPT4
    model: gpt-4
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
  - name: Claude
    model: claude-3
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
  - name: Demo1
    model: demo
  - name: Demo2
    model: demo
  - name: Demo3
    model: demo
  - name: Demo4
    model: demo
"""
        )

        config = load_config(config_file)

        assert len(config.players) == 6
        assert config.players[0].name == "GPT4"
        assert config.players[0].model == "gpt-4"
        assert config.players[0].base_url == "https://api.openai.com/v1"
        assert config.players[1].name == "Claude"
        assert config.players[1].model == "claude-3"
