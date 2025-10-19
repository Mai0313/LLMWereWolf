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

An AI Werewolf game that supports multiple LLM models, with a beautiful Terminal User Interface (TUI).

Other languages: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## Features

- 🎮 **Complete Game Logic**: Full implementation of Werewolf rules with 20+ roles.
- 🤖 **LLM Integration**: Unified agent interface for easy integration with any LLM (OpenAI, Anthropic, DeepSeek, local models, etc.).
- 🖥️ **Beautiful TUI**: Real-time game visualization using the Textual framework, supporting an interactive terminal interface.
- 👤 **Human Players**: Supports mixed games with human players and AIs.
- ⚙️ **Configurable**: Flexibly configure players and game parameters through YAML configuration files.
- 📊 **Event System**: Complete event logging and game state tracking.
- 🧪 **Fully Tested**: High code coverage and a complete test suite.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# Install dependencies
uv sync
```

### Running the Game

The project offers two execution modes, selectable through different command-line entries:

**TUI Mode (Interactive Terminal Interface):**

```bash
# Start TUI with the built-in demo configuration (using demo agents for testing)
uv run llm-werewolf-tui configs/demo.yaml

# Use LLM player configuration (requires setting API keys first)
uv run llm-werewolf-tui configs/players.yaml

# Show the debug panel
uv run llm-werewolf-tui configs/demo.yaml --debug

# If the package is installed globally
llm-werewolf-tui configs/demo.yaml

# Using the werewolf-tui alias
uv run werewolf-tui configs/demo.yaml
```

**Console Mode (Pure Text Logs):**

```bash
# Use Console mode (automatic execution)
uv run llm-werewolf configs/demo.yaml

# Or use the alias
uv run werewolf configs/demo.yaml
```

YAML Configuration File Options:

- `preset: <preset-name>`: Specifies the role preset configuration (e.g., `6-players`, `9-players`, `12-players`, `15-players`, `expert`, `chaos`).
- `show_debug: true`: Shows the TUI debug panel (can be overridden by the `--debug` command-line argument).
- `players: [...]`: Defines the list of players.

### Environment Configuration

Create a `.env` file to configure LLM API keys:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# xAI (Grok)
XAI_API_KEY=xai-...

# Local models (Ollama, etc.) do not require an API key
# Just set the base_url in the YAML file
```

## Supported Roles

### Werewolf Faction 🐺

- **Werewolf**: Standard werewolf that kills collectively at night.
- **AlphaWolf**: Can take a player with them when eliminated.
- **WhiteWolf**: Can kill another werewolf every other night to become a lone wolf.
- **WolfBeauty**: Charms a player; if the Wolf Beauty dies, the charmed player also dies.
- **GuardianWolf**: Can protect one werewolf each night.
- **HiddenWolf**: Appears as a villager to the Seer.
- **BloodMoonApostle**: Can be converted into a werewolf.
- **NightmareWolf**: Can block a player's ability.

### Villager Faction 👥

- **Villager**: A regular villager with no special abilities.
- **Seer**: Can check one player's identity (werewolf or villager) each night.
- **Witch**: Has a healing potion and a poison potion (each for one-time use).
- **Hunter**: Can take a player with them when eliminated.
- **Guard**: Can protect one player from a werewolf attack each night.
- **Idiot**: If voted out, reveals their identity and survives but loses voting rights.
- **Elder**: Requires two attacks to be killed.
- **Knight**: Can duel a player once per game.
- **Magician**: Can swap the roles of two players once.
- **Cupid**: Links two players as lovers on the first night.
- **Raven**: Marks a player to receive an extra vote.
- **GraveyardKeeper**: Can check the identity of dead players.

### Neutral Roles 👻

- **Thief**: Can choose a role from two extra role cards on the first night.
- **Lover**: Linked by Cupid; if one dies, the other dies of a broken heart.

## Configuration

### Using Preset Configurations

Adjust the `preset` field in the configuration file to apply a built-in role combination. Options include:

- `6-players`: Beginner game (6 players) - 2 Werewolves + Seer, Witch, 2 Villagers.
- `9-players`: Standard game (9 players) - 2 Werewolves + Seer, Witch, Hunter, Guard, 3 Villagers.
- `12-players`: Advanced game (12 players) - 3 Werewolves (including AlphaWolf) + Seer, Witch, Hunter, Guard, Cupid, Idiot, 3 Villagers.
- `15-players`: Full game (15 players) - 4 Werewolves (including AlphaWolf, WhiteWolf) + Seer, Witch, Hunter, Guard, Cupid, Idiot, Elder, Raven, 3 Villagers.
- `expert`: Expert configuration (12 players) - Complex role combination with various special werewolves.
- `chaos`: Chaotic role combination (10 players) - Uncommon role pairings, suitable for advanced players.

### Custom Configuration

#### Player Configuration File

```bash
# Start from the demo configuration (all demo agents)
cp configs/demo.yaml my-game.yaml

# Or start from a template that supports LLMs
cp configs/players.yaml my-game.yaml

# Edit the configuration file
# configs/players.yaml contains field descriptions and examples
```

Example `my-game.yaml`:

```yaml
preset: 6-players        # Choose a preset configuration
show_debug: false        # Whether to show the debug panel (for TUI mode)

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

  - name: DeepSeek Thinker
    model: deepseek-reasoner
    base_url: https://api.deepseek.com/v1
    api_key_env: DEEPSEEK_API_KEY
    temperature: 0.7
    max_tokens: 500

  - name: Human Player
    model: human          # Human player

  - name: Local Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # Local models do not need api_key_env

  - name: Test Bot
    model: demo           # Simple agent for testing
```

**Configuration Description:**

- `preset`: Required, determines the game's role configuration and number of players.
- `show_debug`: Optional, defaults to `false`, used to show the debug panel in TUI mode.
- `players`: Required, list of players, the number must match `num_players` in the preset.

**Player Configuration Fields:**

- `name`: Player's display name.
- `model`: Model type.
  - `human`: Human player (input via terminal).
  - `demo`: Simple agent for testing (random responses).
  - LLM model name: e.g., `gpt-4o`, `claude-3-5-sonnet-20241022`, `llama3`.
- `base_url`: API endpoint (required for LLM models).
- `api_key_env`: Environment variable name (required for authenticated endpoints).
- `temperature`: Optional, defaults to 0.7.
- `max_tokens`: Optional, defaults to 500.

**Supported Model Types:**

- **OpenAI-Compatible API**: Any model that supports the OpenAI Chat Completions format.
- **Human Player**: `model: human`
- **Test Agent**: `model: demo`

**Local Model Example:**

If using a local model like Ollama, you can omit `api_key_env`:

```yaml
  - name: Ollama Llama3
    model: llama3
    base_url: http://localhost:11434/v1
    temperature: 0.7
    max_tokens: 500
```

## Agent System

### Built-in Agent Types

This project provides three built-in agent types:

1. **LLMAgent**: Supports any LLM model with an OpenAI-compatible API.
2. **HumanAgent**: Human player input via the terminal.
3. **DemoAgent**: A simple agent for testing (random responses).

### Using Agents via YAML Configuration

The recommended way is to configure agents through a YAML file (see the [Configuration](#configuration) section).

### Programmatic Usage of Agents

If you need to create agents directly in Python code:

```python
from llm_werewolf.ai import LLMAgent, HumanAgent, DemoAgent, create_agent, PlayerConfig
from llm_werewolf.core import GameEngine
from llm_werewolf.config import get_preset_by_name

# Method 1: Directly create agent instances
llm_agent = LLMAgent(
    model_name="gpt-4o",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    temperature=0.7,
    max_tokens=500,
)

human_agent = HumanAgent(model_name="human")
demo_agent = DemoAgent(model_name="demo")

# Method 2: Create from a configuration object (automatically loads API key from environment variables)
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

Since it uses an OpenAI-compatible API, the following providers can be used:

- **OpenAI**: GPT-4, GPT-4o, GPT-3.5-turbo, etc.
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, etc.
- **DeepSeek**: DeepSeek-Reasoner, DeepSeek-Chat, etc.
- **xAI**: Grok series models.
- **Local Models**: Ollama, LM Studio, vLLM, etc.
- **Other Compatible APIs**: Any service that supports the OpenAI Chat Completions format.

### Implementing a Custom Agent

To integrate a custom LLM provider, you just need to implement a simple agent protocol:

```python
class MyCustomAgent:
    """Example of a custom agent implementation."""

    def __init__(self, client: YourLLMClient) -> None:
        self.client = client
        self.model_name = "my-custom-model"
        self._history: list[dict[str, str]] = []

    def get_response(self, message: str) -> str:
        """Get a response from the LLM.

        Args:
            message: User message or game prompt.

        Returns:
            str: The LLM's response.
        """
        self._history.append({"role": "user", "content": message})
        reply = self.client.generate(message, history=self._history)
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        """Optional: Clear the conversation history before a new game starts."""
        self._history.clear()
```

**Required Interface:**

- `model_name` (attribute): A string for the model name.
- `get_response(message: str) -> str` (method): Receives a message and returns a response.

**Optional Methods:**

- `reset()`: Clears the agent's internal state (conversation history, etc.).
- `add_to_history(role: str, content: str)`: Manually adds to the conversation history.
- `get_history() -> list[dict[str, str]]`: Gets the conversation history.

You can pass your custom agent directly into `GameEngine.setup_game()`.

## TUI Interface

The TUI (Terminal User Interface) provides real-time game visualization with a modern terminal interface, built with the [Textual](https://textual.textualize.io/) framework.

### Interface Preview

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐺 Werewolf Game                                                       AI-Powered Werewolf     │
│ q Quit  d Toggle Debug  n Next Step                                             [00:02:34]     │
├──────────────────────┬─────────────────────────────────────────┬───────────────────────────────┤
│                      │ ╭───── Game Status ─────╮               │                               │
│    Players           │ │ 🌙 Round 2 - Night    │               │    Debug Info                 │
│ ──────────────────   │ │                       │               │ ───────────────────────────   │
│ Name      Model      │ │ Total Players: 8/9    │               │ Session ID:                   │
│           Status     │ │ Werewolves:    2      │               │   ww_20251019_163022          │
│ ──────────────────   │ │ Villagers:     6      │               │                               │
│ Alice     gpt-4o     │ ╰─────────────────────╯                 │ Config: players.yaml          │
│           ✓ 🛡️      │                                          │                               │
│ Bob       claude     │                                          │ Players: 9                    │
│           ✓          │                                          │ AI: 7  Human: 1  Demo: 1      │
│ Charlie   llama3     │                                          │                               │
│           ✓          │                                          │ Roles:                        │
│ David     deepseek   │ ╭──── Events / Chat ────╮               │  - Werewolf x2                │
│           ✓ ❤️       │ │ [00:02:28] 🎮 Game Start│               │  - Seer x1                    │
│ Eve       grok       │ │ [00:02:29] ⏰ Phase: Night│               │  - Witch x1                   │
│           ✓ ❤️       │ │ [00:02:30] 🐺 Werewolves Discuss│       │  - Hunter x1                  │
│ Frank     human      │ │            Target       │               │  - Guard x1                   │
│           ✓          │ │ [00:02:31] ⏰ Phase: Day│               │  - Villager x3                │
│ Grace     claude     │ │ [00:02:32] 💀 Iris Died│               │                               │
│           ✓          │ │ [00:02:33] 💬 Alice:  │               │ Night Timeout: 60s            │
│ Henry     demo       │ │            "I think Bob │               │ Day Timeout: 300s             │
│           ✓          │ │            is suspicious" │               │ Vote Timeout: 60s             │
│ Iris      demo       │ │ [00:02:34] 💬 Bob:    │               │                               │
│           ✗          │ │            "I'm a villager!│           │ Errors: 0                     │
│                      │ │            Alice is trying │           │                               │
│                      │ │            to deflect"    │           │ Source: YAML Config           │
│                      │ │ [00:02:35] 💬 Charlie: │               │                               │
│                      │ │            "Last night's death│       │                               │
│                      │ │            pattern is strange"│       │                               │
│                      │ ╰───────────────────────╯               │                               │
│                      │                                          │                               │
└──────────────────────┴──────────────────────────────────────────┴───────────────────────────────┘
```

### Panel Descriptions

#### Player Panel (Left)

Displays information for all players:

- **Name**: Player's display name.
- **Model**: The AI model used, or `human`/`demo`.
- **Status Indicators**:
  - ✓: Alive
  - ✗: Dead
  - 🛡️: Protected by the Guard
  - ❤️: In a lover relationship
  - ☠️: Poisoned by the Witch
  - 🔴: Marked by the Raven

#### Game Panel (Top Center)

Displays the current game status:

- **Round and Phase**:
  - 🌙 Night Phase
  - ☀️ Day Discussion Phase
  - 🗳️ Voting Phase
  - 🏁 Game Over
- **Player Statistics**: Number of surviving players by faction.
- **Vote Count** (during voting phase): Shows the number of votes each player has received.

#### Chat Panel (Bottom Center)

A scrollable event log showing all events and dialogue in the game:

- 💬 **Player Speech**: AI-generated discussions, accusations, and defenses.
- 🎮 **Game Events**: Game start, phase changes, etc.
- ⏰ **Phase Changes**: Night, Day, Voting, etc.
- 💀 **Death Events**: Player death notifications.
- 🐺 **Werewolf Actions**: Werewolf discussions at night.
- 🔮 **Skill Usage**: Records of each role's skill usage.

Events are color-coded by importance for quick identification of key information.

#### Debug Panel (Right, Optional)

Toggle with the 'd' key, contains:

- Session ID
- Configuration file source
- Player count and type statistics
- Role assignments
- Time limit settings
- Error tracking

### TUI Controls

- **q**: Quit the game.
- **d**: Toggle the debug panel display (or use the `--debug` argument to open it by default).
- **n**: Manually proceed to the next step (for debugging).
- **Mouse Wheel**: Scroll through the chat history.
- **Arrow Keys**: Move between focusable components.

### Console Mode

If you prefer not to use the TUI, you can use the `llm-werewolf` or `werewolf` command, and the game will run automatically with output as plain text logs in the terminal.

## Game Flow

1. **Preparation Phase**: Players are randomly assigned roles.
2. **Night Phase**: Roles with night abilities act in order of priority.
3. **Day Discussion**: Players discuss and share information.
4. **Day Voting**: Players vote to eliminate a suspect.
5. **Victory Check**: The game checks if any faction has won.
6. Repeat steps 2-5 until victory conditions are met.

## Victory Conditions

The game checks for victory conditions at the end of each phase:

- **Villager Faction Wins**: All werewolves are eliminated.
- **Werewolf Faction Wins**: The number of werewolves is greater than or equal to the number of villagers.
- **Lovers Win**: Only the two lovers remain alive (lover victory takes precedence over faction victory).

## Development

### Development Environment Setup

```bash
# Clone the project
git clone https://github.com/Mai0313/LLMWereWolf.git
cd LLMWereWolf

# Install all dependencies (including development and test dependencies)
uv sync --all-groups

# Or install selectively
uv sync                     # Only base dependencies (LLM support included)
uv sync --group dev         # Development dependencies
uv sync --group test        # Test dependencies
uv sync --group docs        # Documentation generation dependencies
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run and show coverage
uv run pytest --cov=src --cov-report=term-missing

# Run a specific test file
uv run pytest tests/core/test_roles.py -v

# Run a specific test function
uv run pytest tests/core/test_roles.py::test_werewolf_role -v

# Run tests in parallel (faster)
uv run pytest -n auto
```

### Code Quality

```bash
# Run Ruff linter check
uv run ruff check src/

# Automatically fix fixable issues
uv run ruff check --fix src/

# Format the code
uv run ruff format src/

# Check types (if mypy is configured)
uv run mypy src/
```

### Using Pre-commit

The project includes a pre-commit configuration to automatically check code quality before committing:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Manually run all hooks
uv run pre-commit run --all-files
```

### Using Makefile

The project provides a Makefile to simplify common operations:

```bash
# See all available commands
make help

# Clean auto-generated files
make clean

# Run code formatting (pre-commit)
make format

# Run all tests
make test

# Generate documentation (requires creating the docs directory first)
make gen-docs
```

**Note**: The `gen-docs` command requires the `./scripts/gen_docs.py` script and the docs directory. This command may not work if your project's documentation system is not yet set up.

## Project Architecture

The project uses a modular architecture with clear responsibilities for each module:

```
src/llm_werewolf/
├── cli.py                 # Command-line entry point
├── ai/                    # Agent system
│   ├── agents.py         # LLM/Human/Demo agent implementations
│   └── message.py        # Message processing
├── config/               # Configuration system
│   ├── game_config.py    # Game configuration model
│   └── role_presets.py   # Role preset configurations
├── core/                 # Core game logic
│   ├── game_engine.py    # Game engine
│   ├── game_state.py     # Game state management
│   ├── player.py         # Player class
│   ├── actions.py        # Action system
│   ├── events.py         # Event system
│   ├── victory.py        # Victory condition checking
│   └── roles/            # Role implementations
│       ├── base.py       # Base role class
│       ├── werewolf.py   # Werewolf faction roles
│       ├── villager.py   # Villager faction roles
│       └── neutral.py    # Neutral roles
├── ui/                   # User interface
│   ├── tui_app.py        # TUI application
│   ├── styles.py         # TUI styles
│   └── components/       # TUI components
│       ├── player_panel.py
│       ├── game_panel.py
│       ├── chat_panel.py
│       └── debug_panel.py
└── utils/                # Utility functions
    └── validator.py      # Validation tools
```

### Module Descriptions

- **cli.py**: Command-line interface, responsible for loading configurations and starting the game.
- **ai/**: Agent system, implementing various AI agents and the human player interface.
- **config/**: Configuration system, containing game parameters and role presets.
- **core/**: Core game logic, including roles, players, game state, actions, and the event system.
- **ui/**: Terminal user interface, based on the Textual framework.
- **utils/**: General utility functions.

## System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Linux, macOS, Windows
- **Terminal**: A modern terminal that supports ANSI colors and Unicode (for TUI).

### Main Dependencies

- **pydantic** (≥2.12.3): Data validation and settings management.
- **textual** (≥6.3.0): TUI framework.
- **rich** (≥14.2.0): Terminal formatting.
- **openai** (≥2.5.0): OpenAI API client (for LLM integration).
- **python-dotenv** (≥1.1.1): Environment variable management.
- **pyyaml** (≥6.0.3): YAML configuration file parsing.
- **fire** (≥0.7.1): Command-line interface.
- **logfire** (≥4.13.2): Structured logging.

## FAQ

### How do I add more players?

Edit your YAML configuration file, adjust the `preset` to match the number of players, and add player configurations to the `players` list. Remember that the number of players must match `num_players` in the preset.

### Can I mix different LLM models?

Yes! You can use different LLM providers and models in the same game, for example, using GPT-4, Claude, and a local Llama model simultaneously.

### How do I let a human player join the game?

In the YAML configuration, set a player's `model` to `human`. During the game, that player will need to respond via terminal input.

### How do I set up a local model (Ollama)?

Make sure Ollama is running, then set it up in the YAML file:

```yaml
  - name: Ollama Player
    model: llama3
    base_url: http://localhost:11434/v1
```

You do not need to set `api_key_env`.

### What if the game is too fast or too slow?

You can customize the `GameConfig` to adjust the time limits for each phase:

```python
from llm_werewolf.config import GameConfig

config = GameConfig(
    num_players=9,
    role_names=[...],
    night_timeout=90,  # 90 seconds for the night phase
    day_timeout=600,  # 600 seconds for day discussion
    vote_timeout=90,  # 90 seconds for the voting phase
)
```

### How do I customize the role combination?

Create a custom `GameConfig` and specify the roles you want:

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

Contributions are welcome! You can participate in the following ways:

1. **Report Issues**: Report bugs or suggest features on the [Issues](https://github.com/Mai0313/LLMWereWolf/issues) page.
2. **Submit Pull Requests**: Fix bugs or add new features.
3. **Improve Documentation**: Help improve the README and code comments.
4. **Share Feedback**: Tell us about your experience using the project.

### Contribution Flow

1. Fork this project.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

Please ensure your code:

- Follows the project's code style (using Ruff).
- Includes appropriate tests.
- Updates relevant documentation.

## Acknowledgements

This project is built with these excellent open-source tools:

- [Pydantic](https://pydantic.dev/) - Data validation and settings management.
- [Textual](https://textual.textualize.io/) - Modern TUI framework.
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output.
- [OpenAI Python SDK](https://github.com/openai/openai-python) - LLM API client.
- [uv](https://docs.astral.sh/uv/) - A fast Python package manager.
- [Ruff](https://github.com/astral-sh/ruff) - An extremely fast Python linter.

## Related Links

- [Project Homepage](https://github.com/Mai0313/LLMWereWolf)
- [Issue Tracker](https://github.com/Mai0313/LLMWereWolf/issues)

## Changelog

Please see the [Releases](https://github.com/Mai0313/LLMWereWolf/releases) page for the version update history.
