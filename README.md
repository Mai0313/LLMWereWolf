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
uv run llm-werewolf-tui configs/gpt-5-chaos.yaml

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

### Environment Configuration

Copy [`.env.example`](.env.example) to `.env` and fill in the API keys for the providers your players use:

```bash
cp .env.example .env
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
- **WhiteLoverWolf**: A special werewolf variant that can form lover relationships.

## Configuration

### Automatic Role Assignment

The game automatically generates balanced role compositions based on the number of players (6-20). No need to manually configure presets!

The roles and timeouts for each player count are defined in [`presets.py`](src/llm_werewolf/core/config/presets.py).

### Custom Configuration

#### Player Configuration File

```bash
# Start from the demo configuration (all demo agents)
cp configs/demo.yaml my-game.yaml

# Or start from a template that supports LLMs
cp configs/gpt-5-chaos.yaml my-game.yaml

# Edit the configuration file
```

Example `my-game.yaml`:

```yaml
language: en-US          # Language code (en-US, zh-TW, zh-CN)

players:
  # The game will automatically assign roles based on the number of players

  - name: GPT-4o Detective
    model: gpt-4o
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: GPT-4o-mini Player
    model: gpt-4o-mini
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: GPT-4 Analyst
    model: gpt-4
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY

  - name: Claude Sonnet
    model: claude-sonnet-4-20250514
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY

  - name: DeepSeek Thinker
    model: deepseek-reasoner
    base_url: https://api.deepseek.com/v1
    api_key_env: DEEPSEEK_API_KEY

  - name: Claude Haiku
    model: claude-haiku-4-5-20251001
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY

  - name: Human Player
    model: human          # Human player

  - name: Local Llama
    model: llama3
    base_url: http://localhost:11434/v1
    # Local models do not need api_key_env

  - name: Test Bot
    model: demo           # Simple agent for testing
```

Every field, with its default and whether it is required, is defined in [`player_config.py`](src/llm_werewolf/core/config/player_config.py).

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
```

## TUI Interface

The TUI (Terminal User Interface) provides real-time game visualization with a modern terminal interface, built with the [Textual](https://textual.textualize.io/) framework.

### Panel Descriptions

#### Player Panel (Top Left)

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

#### Game Panel (Top Right)

Displays the current game status:

- **Round and Phase**:
    - 🌙 Night Phase
    - ☀️ Day Discussion Phase
    - 🗳️ Voting Phase
    - 🏁 Game Over
- **Player Statistics**: Number of surviving players by faction.
- **Vote Count** (during voting phase): Shows the number of votes each player has received.

#### Chat Panel (Bottom)

A scrollable event log showing all events and dialogue in the game:

- 💬 **Player Speech**: AI-generated discussions, accusations, and defenses.
- 🎮 **Game Events**: Game start, phase changes, etc.
- ⏰ **Phase Changes**: Night, Day, Voting, etc.
- 💀 **Death Events**: Player death notifications.
- 🐺 **Werewolf Actions**: Werewolf discussions at night.
- 🔮 **Skill Usage**: Records of each role's skill usage.

Events are color-coded by importance for quick identification of key information.

### TUI Controls

- **q**: Quit the game.
- **Mouse Wheel**: Scroll through the chat history.
- **Arrow Keys**: Move between focusable components.

The game runs automatically once started - no manual intervention is required.

### Console Mode

If you prefer not to use the TUI, you can use the `llm-werewolf` or `werewolf` command, and the game will run automatically with output as plain text logs in the terminal.

Console mode displays real-time status indicators to help you track game progress:

- 🎬 **Night Phase**: Shows each role taking action (e.g., `🎬 Seer(gpt-4) is acting...`)
- 💬 **Day Discussion**: Shows each player preparing their speech (e.g., `💬 Alice(gpt-4) is thinking...`)
- 🗳️ **Voting Phase**: Shows each player preparing their vote (e.g., `🗳️ Bob(gpt-4) is thinking about voting...`)

These indicators help you understand the game is waiting for LLM API responses, not frozen. LLM responses typically take several seconds to tens of seconds.

**Console Mode Example Output:**

```
🎮 Game Starting with 9 players...
📋 Role Assignment Complete
   - Werewolf x2
   - Seer x1
   - Witch x1
   - Hunter x1
   - Guard x1
   - Villager x3

🌙 === Round 1: Night Phase ===
🐺 Werewolves are discussing their target...
🎬 Guard(gpt-4o) is acting...
   → Guard protected Alice
🎬 Seer(claude-sonnet) is acting...
   → Seer checked Bob: Villager
🎬 Werewolf(gpt-4o-mini) is acting...
   → Werewolves killed Charlie
🎬 Witch(deepseek-reasoner) is acting...
   → Witch used save potion on Charlie

☀️ === Round 1: Day Phase ===
💬 Alice(gpt-4o) is thinking...
💬 Alice: "Last night was quiet, but we need to find the werewolves."
💬 Bob(claude-sonnet) is thinking...
💬 Bob: "I noticed David acting suspicious yesterday."
...

🗳️ === Voting Phase ===
🗳️ Alice(gpt-4o) is thinking about voting...
   → Alice voted for David
🗳️ Bob(claude-sonnet) is thinking about voting...
   → Bob voted for David
...

📊 Vote Results:
   David: 5 votes
   Eve: 3 votes
   Frank: 1 vote

💀 David was eliminated (Villager)

🏁 === Game Over ===
🎉 Werewolves Win!
   Remaining: Werewolf x2, Villager x2
```

## Game Flow

1. **Preparation Phase**: Players are randomly assigned roles.
2. **Night Phase**:
    - 🌙 **Narrator**: "Night falls, everyone close your eyes..."
    - 🐺 **Werewolf Discussion**: Multiple werewolves discuss who to eliminate (skipped if only one werewolf)
    - 🐺 **Werewolf Vote**: Werewolves vote for their target
    - 🎬 **Other Roles Act**: Other roles with night abilities act in priority order (Seer, Witch, Guard, etc.)
    - 🌙 **Narrator**: "Werewolves, close your eyes..."
3. **Sheriff Election** (first round only):
    - 🎖️ Players decide whether to run, and candidates give campaign speeches
    - 🗳️ Everyone votes for a sheriff, whose vote counts as 1.5 from then on
4. **Day Discussion**:
    - ☀️ **Narrator**: "The sun rises, everyone open your eyes..."
    - 💬 Players speak in turn, discussing and sharing information
5. **Day Voting**:
    - 🗳️ Players vote to eliminate a suspect
6. **Victory Check**: The game checks if any faction has won.
7. Repeat steps 2-6 until victory conditions are met.

## Victory Conditions

The game checks for victory conditions at the end of each phase:

- **Villager Faction Wins**: All werewolves are eliminated.
- **Werewolf Faction Wins**: The number of werewolves is greater than or equal to the number of villagers.
- **Lovers Win**: Only the two lovers remain alive (lover victory takes precedence over faction victory).

## System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Linux, macOS, Windows
- **Terminal**: A modern terminal that supports ANSI colors and Unicode (for TUI).

### Main Dependencies

See `dependencies` in [`pyproject.toml`](pyproject.toml).

## FAQ

### How do I add more players?

Edit your YAML configuration file and add player configurations to the `players` list. The game will automatically generate balanced role compositions based on the total number of players (6-20 supported).

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

### How do I customize game settings?

The game automatically generates balanced role compositions based on player count (6-20). Role assignments and timeouts are automatically adjusted as the number of players increases. For advanced customization of the role generation logic, see `create_game_config_from_player_count()` in `src/llm_werewolf/core/config/presets.py`.

## License

This project is licensed under the [MIT License](LICENSE).

## Development

Contributor setup, tests, the contribution flow, an architecture overview, and how to capture TUI screenshots live in [CONTRIBUTING.md](./.github/CONTRIBUTING.md).

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
