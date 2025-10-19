<center>

# LLM Werewolf 🐺

[![PyPI version](https://img.shields.io/pypi/v/swebenchv2.svg)](https://pypi.org/project/swebenchv2/)
[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/LLMWereWolf/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/LLMWereWolf/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/LLMWereWolf/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/LLMWereWolf/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/LLMWereWolf/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/LLMWereWolf/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/LLMWereWolf.svg)](https://github.com/Mai0313/LLMWereWolf/graphs/contributors)

</center>

An AI-powered Werewolf (Mafia) game with support for multiple LLM models and a beautiful Terminal User Interface (TUI).

Other Languages: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## Features

- 🎮 **Complete Game Logic**: Full implementation of Werewolf game rules with 20+ roles
- 🤖 **LLM Integration**: Abstract interface for easy integration with any LLM (OpenAI, Anthropic, local models, etc.)
- 🖥️ **Beautiful TUI**: Real-time game visualization using Textual framework
- ⚙️ **Configurable**: Multiple preset configurations for different player counts
- 📊 **Event System**: Comprehensive event logging and game state tracking
- 🧪 **Well-Tested**: High code coverage with comprehensive test suite

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# Install base dependencies
uv sync

# Optional: Install LLM provider dependencies
uv sync --group llm-openai      # For OpenAI models
uv sync --group llm-anthropic   # For Claude models
uv sync --group llm-all         # For all supported LLM providers

# Run with TUI (default, uses demo agents)
uv run llm-werewolf

# Run in console mode
uv run llm-werewolf --no-tui
```

### Environment Setup

Create a `.env` file for your LLM API keys:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# xAI (Grok)
XAI_API_KEY=xai-...
XAI_MODEL=grok-beta

# Local models (Ollama, etc.)
LOCAL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL=llama2
```

### Basic Usage

```bash
# Run with custom player configuration (recommended for real games)
uv run llm-werewolf --config players.yaml

# Start a 9-player demo game with TUI (uses demo agents)
uv run llm-werewolf --preset 9-players

# Start a 6-player game without TUI
uv run llm-werewolf --preset 6-players --no-tui

# Enable debug panel
uv run llm-werewolf --debug

# View help
uv run llm-werewolf --help
```

### Player Configuration

Configure custom AI players and human players using a YAML file:

```bash
# Copy example configuration
cp configs/players.yaml.example my-game.yaml

# Edit the configuration
# configs/players.yaml.example contains detailed comments and examples
```

Example `players.yaml`:

```yaml
preset: 9-players
players:
  - name: GPT-4 Detective
    provider: openai
    model: gpt-4
    api_key_env: OPENAI_API_KEY

  - name: Claude Analyst
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    api_key_env: ANTHROPIC_API_KEY

  - name: Human Player
    provider: human

  - name: Local Llama
    provider: local
    model: llama3
    base_url: http://localhost:11434/v1
```

Supported providers: `openai`, `anthropic`, `local`, `custom`, `human`, `demo`

## Supported Roles

### Werewolf Camp 🐺

- **Werewolf**: Standard werewolf who kills at night
- **Alpha Wolf**: Wolf King who can shoot when eliminated
- **White Wolf**: Can kill another werewolf every other night
- **Wolf Beauty**: Charms a player who dies if Beauty dies
- **Guardian Wolf**: Can protect one werewolf each night
- **Hidden Wolf**: Appears as villager to Seer
- **Blood Moon Apostle**: Can transform into werewolf
- **Nightmare Wolf**: Can block a player's ability

### Villager Camp 👥

- **Villager**: Ordinary villager with no special abilities
- **Seer**: Can check one player's identity each night
- **Witch**: Has save and poison potions (one-time use each)
- **Hunter**: Can shoot someone when eliminated
- **Guard**: Can protect one player each night
- **Idiot**: Survives voting but loses voting rights
- **Elder**: Takes two attacks to kill
- **Knight**: Can duel a player once per game
- **Magician**: Can swap two players' roles once
- **Cupid**: Links two players as lovers on night 1
- **Raven**: Marks a player for extra vote
- **Graveyard Keeper**: Can check dead players' identities

## Configuration

### Using Presets

```bash
# Available presets
uv run llm-werewolf --preset 6-players   # Beginner (6 players)
uv run llm-werewolf --preset 9-players   # Standard (9 players)
uv run llm-werewolf --preset 12-players  # Advanced (12 players)
uv run llm-werewolf --preset 15-players  # Full game (15 players)
uv run llm-werewolf --preset expert      # Expert configuration
uv run llm-werewolf --preset chaos       # Chaotic role mix
```

### Custom Configuration

Create a custom configuration in Python:

```python
from llm_werewolf import GameConfig

config = GameConfig(
    num_players=9,
    role_names=[
        "Werewolf",
        "Werewolf",
        "Seer",
        "Witch",
        "Hunter",
        "Villager",
        "Villager",
        "Villager",
        "Villager",
    ],
    night_timeout=60,
    day_timeout=300,
)
```

## LLM Integration

### Using Built-in LLM Agents

The package provides ready-to-use agents for popular LLM providers:

```python
from llm_werewolf.ai import OpenAIAgent, AnthropicAgent, GenericLLMAgent, create_agent_from_config
from llm_werewolf import GameEngine
from llm_werewolf.config import get_preset

# Method 1: Create agents directly
openai_agent = OpenAIAgent(model_name="gpt-4")
claude_agent = AnthropicAgent(model_name="claude-3-5-sonnet-20241022")
ollama_agent = GenericLLMAgent(model_name="llama2", base_url="http://localhost:11434/v1")

# Method 2: Create from configuration (auto-loads from .env)
agent = create_agent_from_config(
    provider="openai",  # or "anthropic", "local", "xai", etc.
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=500,
)

# Setup game with LLM agents
config = get_preset("9-players")
engine = GameEngine(config)

players = [
    ("p1", "GPT-4 Player", OpenAIAgent("gpt-4")),
    ("p2", "Claude Player", AnthropicAgent("claude-3-5-sonnet-20241022")),
    ("p3", "Llama Player", GenericLLMAgent("llama2")),
    # ... more players
]

roles = config.to_role_list()
engine.setup_game(players, roles)
```

### Supported LLM Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo, etc.
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, etc.
- **xAI**: Grok models
- **Local**: Ollama, LM Studio, or any OpenAI-compatible endpoint
- **Azure OpenAI**: Azure-hosted OpenAI models
- **Custom**: Any OpenAI-compatible API

### Implementing Your Own Agent

For custom LLM integrations, implement the `BaseAgent` class:

```python
from llm_werewolf.ai import BaseAgent


class MyLLMAgent(BaseAgent):
    def __init__(self, model_name: str = "my-model"):
        super().__init__(model_name)
        # Initialize your LLM client here
        self.client = YourLLMClient()

    def get_response(self, message: str) -> str:
        """
        Get response from your LLM.

        Args:
            message: The game prompt (role info, game state, action request, etc.)

        Returns:
            str: The LLM's response
        """
        # Add to conversation history (optional)
        self.add_to_history("user", message)

        # Call your LLM API
        response = self.client.generate(message)

        # Add response to history (optional)
        self.add_to_history("assistant", response)

        return response
```

### Agent Interface Details

The `BaseAgent` provides:

- `get_response(message: str) -> str`: Main method to implement (required)
- `initialize()`: Setup method called before game starts (optional)
- `reset()`: Clear conversation history for new game (optional)
- `add_to_history(role: str, content: str)`: Track conversation (optional)
- `get_history() -> list[dict]`: Get conversation history (optional)

## TUI Interface

The TUI provides real-time visualization with a modern terminal interface:

### Interface Preview

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐺 Werewolf Game                                                    AI-Powered Werewolf  │
│ q Quit  d Toggle Debug  n Next Step                                         [00:02:34]   │
├──────────────────────┬─────────────────────────────────────────┬──────────────────────────┤
│                      │ ╭─────── Game Status ─────────╮        │                          │
│    Players           │ │ 🌙 Round 2 - Night          │        │    Debug Info            │
│ ──────────────────   │ │                             │        │ ──────────────────────   │
│ Name      Model      │ │ Total Players:    8/9       │        │ Session ID:              │
│           Status     │ │ Werewolves:       2         │        │   ww_20251019_163022     │
│ ──────────────────   │ │ Villagers:        6         │        │                          │
│ Alice     gpt-4      │ ╰─────────────────────────────╯        │ Config: players.yaml     │
│           ✓ 🛡️      │                                         │                          │
│ Bob       claude-3.5 │                                         │ Players: 9               │
│           ✓          │                                         │ AI: 6  Human: 1          │
│ Charlie   llama3     │                                         │                          │
│           ✓          │                                         │ Roles:                   │
│ David     gpt-3.5    │ ╭──── Chat / Events ────────╮          │  - Werewolf x2           │
│           ✓ ❤️       │ │ [00:02:28] 🎮 Game started│          │  - Seer x1               │
│ Eve       grok-beta  │ │ [00:02:29] ⏰ Phase: Night│          │  - Witch x1              │
│           ✓ ❤️       │ │ [00:02:30] 🐺 Werewolves  │          │  - Hunter x1             │
│ Frank     human      │ │           discuss targets │          │  - Guard x1              │
│           ✓          │ │ [00:02:31] ⏰ Phase: Day  │          │  - Villager x3           │
│ Grace     claude-3.5 │ │ [00:02:32] 💀 Iris died   │          │                          │
│           ✓          │ │ [00:02:33] 💬 Alice: "I   │          │ Night timeout: 60s       │
│ Henry     demo       │ │           think Bob's act-│          │ Day timeout: 300s        │
│           ✓          │ │           ing suspicious" │          │                          │
│ Iris      demo       │ │ [00:02:34] 💬 Bob: "I'm a │          │ Errors: 0                │
│           ✗          │ │           villager! Alice │          │                          │
│                      │ │           is deflecting!" │          │ Source: YAML config      │
│                      │ │ [00:02:35] 💬 Charlie:    │          │                          │
│                      │ │           "Last night's   │          │                          │
│                      │ │           death pattern..." │        │                          │
│                      │ ╰───────────────────────────╯          │                          │
│                      │                                         │                          │
└──────────────────────┴─────────────────────────────────────────┴──────────────────────────┘
```

### Panel Description

- **Player Panel** (Left): Shows all players with their AI models, status indicators, and roles

  - ✓/✗: Alive/Dead status
  - 🛡️: Protected by Guard
  - ❤️: Linked as Lovers
  - ☠️: Poisoned
  - 🔴: Marked by Raven

- **Game Panel** (Top Center): Displays current round, phase, and real-time statistics

  - Phase icons: 🌙 Night | ☀️ Day Discussion | 🗳️ Voting | 🏁 Game Over
  - Live player counts by faction
  - Vote counts during voting phase

- **Chat Panel** (Bottom Center): Scrollable event log with **full player discussions and game events**

  - 💬 **Player speeches**: Real-time AI-generated discussions, accusations, and defenses
  - Color-coded messages based on event importance
  - Event icons for quick visual scanning
  - Shows complete conversation flow during day discussion phase

- **Debug Panel** (Right, optional): Shows session info, configuration, and error tracking

  - Toggle visibility with 'd' key
  - Displays game configuration and runtime info

### TUI Controls

- `q`: Quit the application
- `d`: Toggle debug panel
- `n`: Advance to next step (for debugging)
- Mouse: Scroll through chat history

## Game Flow

1. **Setup**: Players are assigned random roles
2. **Night Phase**: Roles with night abilities act in priority order
3. **Day Discussion**: Players discuss and share information
4. **Day Voting**: Players vote to eliminate a suspect
5. **Check Victory**: Game checks if any camp has won
6. Repeat steps 2-5 until victory condition is met

## Victory Conditions

- **Villagers Win**: When all werewolves are eliminated
- **Werewolves Win**: When werewolves equal or outnumber villagers
- **Lovers Win**: When only the two lovers remain alive

## Development

### Running Tests

```bash
# Install test dependencies
uv sync --group test

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/core/test_roles.py -v
```

### Code Quality

```bash
# Install dev dependencies
uv sync --group dev

# Run linters
uv run ruff check src/

# Format code
uv run ruff format src/
```

## Architecture

The project follows a modular architecture:

- **Core**: Game logic (roles, players, state, engine, victory)
- **Config**: Game configurations and presets
- **AI**: Abstract agent interface for LLM integration
- **UI**: TUI components (Textual-based)
- **Utils**: Helper functions (logger, validator)

## Requirements

- Python 3.10+
- Dependencies: pydantic, textual, rich

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Credits

Built with:

- [Pydantic](https://pydantic.dev/) for data validation
- [Textual](https://textual.textualize.io/) for TUI
- [Rich](https://rich.readthedocs.io/) for terminal formatting
