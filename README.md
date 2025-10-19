<div align="center" markdown="1">

# LLM Werewolf 🐺

[![PyPI version](https://img.shields.io/pypi/v/llm_werewolf.svg)](https://pypi.org/project/llm_werewolf/)
[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/LLMWereWolf/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/LLMWereWolf/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/LLMWereWolf/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/LLMWereWolf/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/LLMWereWolf/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/LLMWereWolf/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/LLMWereWolf.svg)](https://github.com/Mai0313/LLMWereWolf/graphs/contributors)

</div>

An AI Werewolf (Mafia) game that supports multiple LLM models and features a polished Terminal User Interface (TUI).

Other languages: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## Features

- 🎮 **Complete Game Logic**: Implements the full Werewolf rule set with more than 20 roles
- 🤖 **LLM Integration**: Unified agent interface that makes it easy to plug in any LLM (OpenAI, Anthropic, DeepSeek, local models, etc.)
- 🖥️ **Polished TUI**: Real-time visualization built on Textual with an interactive terminal UI
- 👤 **Human Players**: Mix human players with AI agents in the same game
- ⚙️ **Configurable**: Use YAML configuration files to fine-tune players and game parameters
- 📊 **Event System**: Detailed event logging and game state tracking
- 🧪 **Well Tested**: High code coverage with a comprehensive test suite

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# Install base dependencies
uv sync

# Optional: install dependencies for specific LLM providers
uv sync --group llm-openai      # For OpenAI models
uv sync --group llm-anthropic   # For Claude models
uv sync --group llm-all         # For every supported provider
```

### Running the Game

The CLI entry points (`llm-werewolf` and `werewolf`) load a YAML configuration file that defines players and the interface mode.

```bash
# Launch the built-in demo configuration in the TUI (uses demo agents)
uv run llm-werewolf configs/demo.yaml

# Launch the LLM player configuration (set your API keys first)
uv run llm-werewolf configs/players.yaml

# If the package is installed globally
llm-werewolf configs/demo.yaml

# Run a custom configuration
uv run llm-werewolf my-game.yaml

# Use the werewolf alias
uv run werewolf configs/demo.yaml
```

Adjust interface options directly in the YAML:

- `game_type: tui` enables the interactive terminal interface (default)
- `game_type: console` switches to a plain text logging mode
- `show_debug: true` displays the TUI debug panel (only works in `tui` mode)
- `preset: <preset-name>` selects a preset role distribution (e.g., `6-players`, `9-players`, `12-players`, `15-players`, `expert`, `chaos`)

### Environment Setup

Create a `.env` file to store your LLM API keys:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# xAI (Grok)
XAI_API_KEY=xai-...

# Local models (Ollama, etc.) do not need API keys
# Set base_url directly in the YAML configuration
```

## Supported Roles

### Werewolf Camp 🐺

- **Werewolf**: The standard werewolf that joins the pack to kill at night
- **AlphaWolf**: Can shoot one player when eliminated
- **WhiteWolf**: May kill another werewolf every other night to become a lone wolf
- **WolfBeauty**: Charms a player; if the Wolf Beauty dies, the charmed player dies as well
- **GuardianWolf**: Protects a werewolf each night
- **HiddenWolf**: Appears as a villager when checked by the Seer
- **BloodMoonApostle**: Can convert into a werewolf
- **NightmareWolf**: Silences another player's ability

### Villager Camp 👥

- **Villager**: A classic villager with no special ability
- **Seer**: Checks one player's alignment each night (werewolf or villager)
- **Witch**: Has one heal and one poison potion
- **Hunter**: Can shoot one player when eliminated
- **Guard**: Protects a player from werewolf attacks each night
- **Idiot**: Survives a daytime execution but loses voting rights
- **Elder**: Needs to be attacked twice to die
- **Knight**: Can challenge another player to a duel once per game
- **Magician**: Swaps the roles of two players once per game
- **Cupid**: Links two players as lovers on the first night
- **Raven**: Marks a player to grant them an extra vote against them
- **GraveyardKeeper**: Learns the role of a dead player

### Neutral Roles 👻

- **Thief**: Chooses one of two extra role cards on the first night
- **Lover**: Linked by Cupid; when one lover dies, the other follows

## Configuration

### Using Presets

Set the `preset` field in the configuration file to apply a built-in role distribution:

- `6-players`: Beginner game (6 players) — 2 Werewolves + Seer, Witch, 2 Villagers
- `9-players`: Standard game (9 players) — 2 Werewolves + Seer, Witch, Hunter, Guard, 3 Villagers
- `12-players`: Advanced game (12 players) — 3 Werewolves (including AlphaWolf) + Seer, Witch, Hunter, Guard, Cupid, Idiot, 3 Villagers
- `15-players`: Full game (15 players) — 4 Werewolves (including AlphaWolf and WhiteWolf) + Seer, Witch, Hunter, Guard, Cupid, Idiot, Elder, Raven, 3 Villagers
- `expert`: Expert setup (12 players) with a complex selection including several special werewolves
- `chaos`: Chaotic setup (10 players) with uncommon role combinations for experienced players

### Custom Configuration

#### Player Configuration File

```bash
# Start from the demo configuration (all demo agents)
cp configs/demo.yaml my-game.yaml

# Or start from the LLM-enabled sample
cp configs/players.yaml my-game.yaml

# Edit the configuration
# configs/players.yaml includes field descriptions and examples
```

Example `my-game.yaml`:

```yaml
preset: 6-players        # Choose a preset
game_type: tui           # Interface mode: tui or console
show_debug: false        # Show the debug panel

players:
  - name: GPT-4 Detective
    model: gpt-4o
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: Claude Analyst
    model: claude-3-5-sonnet-20241022
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: DeepSeek Strategist
    model: deepseek-reasoner
    base_url: https://api.deepseek.com/v1
    api_key_env: DEEPSEEK_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: Human Player
    model: human          # Human-controlled player

  - name: Local Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # Local models do not require api_key_env

  - name: Test Bot
    model: demo           # Simple agent for testing
```

**Configuration Fields:**

- `preset`: Required. Defines the role distribution and player count
- `game_type`: Optional, defaults to `tui`
- `show_debug`: Optional, defaults to `false`
- `players`: Required. Player list whose length must match the preset `num_players`

**Player Configuration Fields:**

- `name`: Display name for the player
- `model`: Model type
  - `human`: Human player (responds via the terminal)
  - `demo`: Simple agent for testing (random responses)
  - LLM model names: e.g., `gpt-4o`, `claude-3-5-sonnet-20241022`, `llama3`
- `base_url`: API endpoint (required for LLM models)
- `api_key_env`: Name of the environment variable that holds the API key (required when the endpoint requires auth)
- `temperature`: Optional, default 0.7
- `max_tokens`: Optional, default 500

**Supported Model Types:**

- **OpenAI-compatible APIs**: Any provider that supports the OpenAI Chat Completions format
- **Human players**: `model: human`
- **Demo agents**: `model: demo`

**Local Model Example:**

You can skip `api_key_env` when using a local model such as Ollama:

```yaml
  - name: Ollama Llama3
    model: llama3
    base_url: http://localhost:11434/v1
    temperature: 0.7
    max_tokens: 500
```

## Agent System

### Built-in Agent Types

The project ships with three built-in agent types:

1. **LLMAgent**: Works with any LLM that exposes an OpenAI-compatible API
2. **HumanAgent**: Prompts a human player through the terminal
3. **DemoAgent**: Simple agent that returns randomized responses for testing

### Using Agents via YAML

The recommended way to configure agents is through the YAML configuration file (see the [Configuration](#configuration) section).

### Programmatic Agent Usage

Create agents directly in Python if you need more control:

```python
from llm_werewolf.ai import LLMAgent, HumanAgent, DemoAgent, create_agent, PlayerConfig
from llm_werewolf.core import GameEngine
from llm_werewolf.config import get_preset_by_name

# Method 1: instantiate agents directly
llm_agent = LLMAgent(
    model_name="gpt-4o",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    temperature=0.7,
    max_tokens=500,
)

human_agent = HumanAgent(model_name="human")
demo_agent = DemoAgent(model_name="demo")

# Method 2: build from a configuration object (loads API keys from env vars)
player_config = PlayerConfig(
    name="GPT-4 Player",
    model="gpt-4o",
    base_url="https://api.openai.com/v1",
    api_key_env="OPENAI_API_KEY",
    temperature=0.7,
    max_tokens=500,
)
agent = create_agent(player_config)

# Set up the game
game_config = get_preset_by_name("9-players")
engine = GameEngine(game_config)

players = [
    ("player_1", "GPT-4 Player", llm_agent),
    ("player_2", "Human Player", human_agent),
    ("player_3", "Test Bot", demo_agent),
    # ... more players
]

roles = game_config.to_role_list()
engine.setup_game(players, roles)
result = engine.play_game()
```

### Supported LLM Providers

Because the implementation targets OpenAI-compatible APIs, you can use:

- **OpenAI**: GPT-4, GPT-4o, GPT-3.5-turbo, etc.
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, etc.
- **DeepSeek**: DeepSeek-Reasoner, DeepSeek-Chat, etc.
- **xAI**: Grok series models
- **Local models**: Ollama, LM Studio, vLLM, and more
- **Other compatible APIs**: Any service that supports the OpenAI Chat Completions protocol

### Implementing a Custom Agent

Integrate a custom provider by implementing a lightweight agent interface:

```python
class MyCustomAgent:
    """Example implementation of a custom agent."""

    def __init__(self, client: YourLLMClient) -> None:
        self.client = client
        self.model_name = "my-custom-model"
        self._history: list[dict[str, str]] = []

    def get_response(self, message: str) -> str:
        """Fetch a response from the LLM.

        Args:
            message: User message or game prompt

        Returns:
            str: Response generated by the LLM
        """
        self._history.append({"role": "user", "content": message})
        reply = self.client.generate(message, history=self._history)
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        """Optional: clear the conversation history before a new game."""
        self._history.clear()
```

**Required interface:**

- `model_name` (attribute): Name of the model
- `get_response(message: str) -> str`: Receives game prompts and returns the reply

**Optional helpers:**

- `reset()`: Clear any internal state (conversation history, etc.)
- `add_to_history(role: str, content: str)`: Manually append to the history
- `get_history() -> list[dict[str, str]]`: Inspect the stored history

You can pass any custom agent directly to `GameEngine.setup_game()`.

## TUI Interface

The Terminal User Interface provides a modern, real-time visualization of the game using the [Textual](https://textual.textualize.io/) framework.

### Interface Preview

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐺 Werewolf Game                                                       AI-Powered Werewolf     │
│ q Quit  d Toggle Debug  n Next Step                                         [00:02:34]        │
├──────────────────────┬─────────────────────────────────────────┬───────────────────────────────┤
│                      │ ╭───── Game Status ─────╮               │                               │
│    Players           │ │ 🌙 Round 2 - Night    │               │    Debug Info                 │
│ ──────────────────   │ │                       │               │ ───────────────────────────   │
│ Name       Model     │ │ Players Alive: 8/9    │               │ Session ID:                  │
│            Status    │ │ Werewolves:    2      │               │   ww_20251019_163022          │
│ ──────────────────   │ │ Villagers:    6       │               │                               │
│ Alice     gpt-4o     │ ╰───────────────────────╯               │ Config: players.yaml          │
│           ✓ 🛡️       │                                          │                               │
│ Bob       claude     │                                          │ Players: 9                   │
│           ✓          │                                          │ AI: 7  Human: 1  Demo: 1     │
│ Charlie   llama3     │                                          │                               │
│           ✓          │                                          │ Roles:                       │
│ David     deepseek   │ ╭──── Events / Chat ────╮               │  - Werewolf x2               │
│           ✓ ❤️       │ │ [00:02:28] 🎮 Game start│               │  - Seer x1                   │
│ Eve       grok       │ │ [00:02:29] ⏰ Phase: Night│            │  - Witch x1                  │
│           ✓ ❤️       │ │ [00:02:30] 🐺 Wolves discuss│         │  - Hunter x1                 │
│ Frank     human      │ │             targets    │               │  - Guard x1                  │
│           ✓          │ │ [00:02:31] ⏰ Phase: Day │              │  - Villager x3               │
│ Grace     claude     │ │ [00:02:32] 💀 Iris died  │             │                               │
│           ✓          │ │ [00:02:33] 💬 Alice:     │             │ Night timeout: 60s           │
│ Henry     demo       │ │            "I think Bob │             │ Day timeout: 300s            │
│           ✓          │ │            is acting    │             │ Vote timeout: 60s            │
│ Iris      demo       │ │            suspicious"  │             │                               │
│           ✗          │ │ [00:02:34] 💬 Bob:      │             │ Errors: 0                    │
│                      │ │            "I'm a       │             │                               │
│                      │ │            villager!    │             │ Source: YAML config          │
│                      │ │            Alice is deflecting!"│     │                               │
│                      │ │ [00:02:35] 💬 Charlie:  │             │                               │
│                      │ │            "Last night's│             │                               │
│                      │ │            pattern felt │             │                               │
│                      │ │            strange..."  │             │                               │
│                      │ ╰─────────────────────────╯             │                               │
│                      │                                          │                               │
└──────────────────────┴──────────────────────────────────────────┴───────────────────────────────┘
```

### Panel Breakdown

#### Player Panel (left)

Shows all players:

- **Name**: Display name
- **Model**: AI model or `human`/`demo`
- **Status indicators**:
  - ✓: Alive
  - ✗: Dead
  - 🛡️: Protected by the Guard
  - ❤️: Linked as lovers
  - ☠️: Poisoned by the Witch
  - 🔴: Marked by the Raven

#### Game Panel (top center)

Displays the current game status:

- **Round and phase**:
  - 🌙 Night
  - ☀️ Day Discussion
  - 🗳️ Voting
  - 🏁 Game Over
- **Player counts**: Live players by faction
- **Voting tally**: Shown during the voting phase

#### Chat Panel (bottom center)

Scrollable event log that records every game event and conversation:

- 💬 **Player speeches**: AI-generated discussions, accusations, and defenses
- 🎮 **Game events**: Game start, phase transitions, etc.
- ⏰ **Phase changes**: Night, day, voting, etc.
- 💀 **Deaths**: Notifications about eliminated players
- 🐺 **Werewolf actions**: Night discussions among werewolves
- 🔮 **Ability usage**: Records of role abilities being triggered

Events are color-coded by importance so you can spot key information quickly.

#### Debug Panel (right, optional)

Toggle with the `d` key. Includes:

- Session ID
- Source configuration file
- Player counts and model breakdown
- Role distribution
- Timeouts for each phase
- Error tracking

### TUI Controls

- `q`: Quit the game
- `d`: Toggle the debug panel
- `n`: Advance to the next step manually (for debugging)
- Mouse scroll: Navigate through the chat history
- Arrow keys: Move between focusable widgets

### Console Mode

Set `game_type: console` in the configuration file if you prefer a plain-text log instead of the TUI.

## Game Flow

1. **Setup**: Players are assigned roles at random
2. **Night Phase**: Night roles act in priority order
3. **Day Discussion**: Players share information and debate
4. **Day Voting**: Players vote to eliminate a suspect
5. **Victory Check**: The engine checks for win conditions
6. Repeat steps 2–5 until a team wins

## Victory Conditions

The game checks for victory after every phase:

- **Villagers win**: All werewolves are eliminated
- **Werewolves win**: Werewolves equal or outnumber the villagers
- **Lovers win**: Only the two lovers remain alive (takes priority over faction wins)

## Development

### Development Environment

```bash
# Clone the project
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# Install every dependency (including dev and test extras)
uv sync --all-groups

# Or install selectively
uv sync                     # Base dependencies only
uv sync --group dev         # Development tooling
uv sync --group test        # Test dependencies
uv sync --group llm-all     # All LLM provider extras
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage (show missing lines)
uv run pytest --cov=src --cov-report=term-missing

# Run a specific test file
uv run pytest tests/core/test_roles.py -v

# Run a specific test function
uv run pytest tests/core/test_roles.py::test_werewolf_role -v

# Run tests in parallel for extra speed
uv run pytest -n auto
```

### Code Quality

```bash
# Run Ruff linter checks
uv run ruff check src/

# Automatically fix fixable issues
uv run ruff check --fix src/

# Format the codebase
uv run ruff format src/

# Type checking (if mypy is configured)
uv run mypy src/
```

### Pre-commit Hooks

A pre-commit configuration is included to enforce code quality before commits:

```bash
# Install the pre-commit hooks
uv run pre-commit install

# Run every hook manually
uv run pre-commit run --all-files
```

### Makefile Shortcuts

A Makefile is provided to streamline common tasks:

```bash
# List available commands
make help

# Remove generated artifacts
make clean

# Format code (runs pre-commit)
make format

# Run the full test suite
make test

# Build documentation
make gen-docs
```

## Project Structure

The codebase follows a modular structure with clear separation of concerns:

```
src/llm_werewolf/
├── cli.py                 # CLI entry point
├── ai/                    # Agent system
│   ├── agents.py         # LLM/Human/Demo agent implementations
│   └── message.py        # Message handling
├── config/               # Configuration system
│   ├── game_config.py    # Game configuration models
│   └── role_presets.py   # Role preset definitions
├── core/                 # Core game logic
│   ├── game_engine.py    # Game engine
│   ├── game_state.py     # Game state management
│   ├── player.py         # Player model
│   ├── actions.py        # Action system
│   ├── events.py         # Event tracking
│   ├── victory.py        # Victory condition checks
│   └── roles/            # Role implementations
│       ├── base.py       # Role base class
│       ├── werewolf.py   # Werewolf roles
│       ├── villager.py   # Villager roles
│       └── neutral.py    # Neutral roles
├── ui/                   # User interface
│   ├── tui_app.py        # TUI application
│   ├── styles.py         # TUI styling
│   └── components/       # TUI widgets
│       ├── player_panel.py
│       ├── game_panel.py
│       ├── chat_panel.py
│       └── debug_panel.py
└── utils/                # Utility helpers
    └── validator.py      # Validation utilities
```

### Module Overview

- **cli.py**: Loads configuration and launches the game
- **ai/**: Agent implementations for AI and human players
- **config/**: Game configuration models and presets
- **core/**: Core game logic, including roles, players, state, actions, and events
- **ui/**: Textual-based terminal interface components
- **utils/**: Shared utility functions

## System Requirements

- **Python**: 3.10 or higher
- **Operating Systems**: Linux, macOS, Windows
- **Terminal**: Modern terminal with ANSI color and Unicode support (required for TUI)

### Key Dependencies

- **pydantic** (≥2.12.3): Data validation and settings management
- **textual** (≥6.3.0): TUI framework
- **rich** (≥14.2.0): Terminal rendering
- **openai** (≥2.5.0): OpenAI API client (for LLM integration)
- **python-dotenv** (≥1.1.1): Environment variable loading
- **pyyaml** (≥6.0.3): YAML parsing
- **fire** (≥0.7.1): Command-line interface
- **logfire** (≥4.13.2): Structured logging

## FAQ

### How do I add more players?

Edit your YAML configuration, choose a `preset` that matches the desired player count, and add entries to the `players` list. Make sure the player count matches the preset `num_players`.

### Can I mix different LLM models?

Yes. You can mix providers and models within the same game, such as GPT-4, Claude, and local Llama variants.

### How do I include human players?

Set a player's `model` to `human` in the YAML configuration. During the game, that player responds directly through the terminal.

### How do I configure local models like Ollama?

Ensure Ollama is running, then configure the player in YAML:

```yaml
  - name: Ollama Player
    model: llama3
    base_url: http://localhost:11434/v1
```

`api_key_env` is not required.

### What if the game runs too quickly or too slowly?

Customize `GameConfig` to adjust the timeouts for each phase:

```python
from llm_werewolf.config import GameConfig

config = GameConfig(
    num_players=9,
    role_names=[...],
    night_timeout=90,  # 90-second night phase
    day_timeout=600,  # 10-minute day discussion
    vote_timeout=90,  # 90-second voting phase
)
```

### How do I define a custom role set?

Create a custom `GameConfig` and list the roles you want:

```python
from llm_werewolf.config import GameConfig

config = GameConfig(
    num_players=10,
    role_names=[
        "Werewolf",
        "AlphaWolf",
        "WhiteWolf",
        "Seer",
        "Witch",
        "Hunter",
        "Guard",
        "Villager",
        "Villager",
        "Villager",
    ],
)
```

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

We welcome contributions! You can help in many ways:

1. **Report issues**: File bugs or feature requests on the [Issues](https://github.com/Mai0313/LLMWereWolf/issues) page
2. **Open pull requests**: Fix bugs or add new features
3. **Improve documentation**: Enhance the README or code comments
4. **Share feedback**: Let us know about your experience

### Contribution Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to your branch (`git push origin feature/amazing-feature`)
5. Open a pull request

Please make sure your changes:

- Follow the project style guidelines (Ruff)
- Include appropriate tests
- Update related documentation

## Acknowledgements

This project is built on top of outstanding open-source tools:

- [Pydantic](https://pydantic.dev/) — Data validation and configuration
- [Textual](https://textual.textualize.io/) — Modern TUI framework
- [Rich](https://rich.readthedocs.io/) — Beautiful terminal rendering
- [OpenAI Python SDK](https://github.com/openai/openai-python) — LLM API client
- [uv](https://docs.astral.sh/uv/) — Fast Python package manager
- [Ruff](https://github.com/astral-sh/ruff) — Extremely fast Python linter

## Related Links

- [Project Homepage](https://github.com/Mai0313/LLMWereWolf)
- [Issue Tracker](https://github.com/Mai0313/LLMWereWolf/issues)
- [Documentation](https://mai0313.github.io/llm_werewolf) (in development)

## Changelog

See the [Releases](https://github.com/Mai0313/LLMWereWolf/releases) page for version history.
