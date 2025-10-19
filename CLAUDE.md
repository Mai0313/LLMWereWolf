# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM Werewolf is an AI-powered Werewolf (Mafia) game with support for multiple LLM models and a Terminal User Interface (TUI). The project enables AI agents from different LLM providers to play the classic social deduction game.

**Package name**: `llm_werewolf`
**Python support**: 3.10, 3.11, 3.12, 3.13
**Dependency manager**: `uv`
**Documentation**: MkDocs Material with mkdocstrings

## Common Development Commands

### Environment Setup

```bash
make uv-install           # Install uv (one-time setup)
uv sync                   # Install base dependencies
uv sync --group test      # Include test dependencies
uv sync --group docs      # Include docs dependencies
uv sync --group dev       # Include dev tools (pre-commit, poe, notebook)

# Optional LLM provider dependencies
uv sync --group llm-openai      # For OpenAI models
uv sync --group llm-anthropic   # For Claude models
uv sync --group llm-all         # For all supported LLM providers
```

### Running the Game

```bash
# Run with TUI (default, uses demo agents)
uv run llm-werewolf
uv run werewolf          # Alternative command

# Run with custom YAML configuration (recommended for real games)
uv run llm-werewolf --config players.yaml
uv run llm-werewolf --config players.yaml --preset 9-players

# Run with specific preset (demo mode)
uv run llm-werewolf --preset 9-players
uv run llm-werewolf --preset 12-players

# Run in console mode (no TUI)
uv run llm-werewolf --no-tui

# Enable debug panel
uv run llm-werewolf --debug

# View help
uv run llm-werewolf --help
```

**Player Configuration via YAML:**

Instead of using demo agents, you can configure custom AI players and human players using a YAML file:

1. Copy the example configuration:

   ```bash
   cp configs/players.yaml.example my-game.yaml
   ```

2. Edit the YAML file to specify your players:

   ```yaml
   preset: 9-players
   players:
     - name: GPT-4 Player
       model: gpt-4
       base_url: https://api.openai.com/v1
       api_key_env: OPENAI_API_KEY

     - name: Claude Player
       model: claude-3-5-sonnet-20241022
       base_url: https://api.anthropic.com/v1
       api_key_env: ANTHROPIC_API_KEY

     - name: Human Player
       model: human
   ```

3. Run with your configuration:

   ```bash
   uv run llm-werewolf --config my-game.yaml
   ```

**YAML Configuration Fields:**

- `name`: Display name for the player (must be unique)
- `model`: Model identifier (required):
  - `"human"`: Human player via console input
  - `"demo"`: Random response bot (for testing)
  - `<model_name>`: LLM model name (e.g., `"gpt-4"`, `"claude-3-5-sonnet-20241022"`, `"llama3"`)
- `base_url`: API endpoint (required for LLM models):
  - OpenAI: `https://api.openai.com/v1`
  - Anthropic: `https://api.anthropic.com/v1`
  - xAI (Grok): `https://api.x.ai/v1`
  - Local (Ollama): `http://localhost:11434/v1`
  - Any OpenAI-compatible API endpoint
- `api_key_env`: Environment variable name containing API key (required for most providers)
- `temperature`: LLM temperature 0.0-2.0 (default: 0.7)
- `max_tokens`: Maximum response tokens (default: 500)

**Note:** API keys are stored in `.env` file (see `.env.example`). The YAML file only references the environment variable names for security.

### Testing

```bash
make test                    # Run pytest with coverage
pytest                       # Direct pytest invocation
pytest -vv                   # Verbose output
pytest tests/core/test_roles.py -v  # Run specific test file
uv run pytest -n auto        # Run with parallel execution
pytest -k test_name          # Run specific test by name
```

### Code Quality

```bash
make format                  # Run all pre-commit hooks (ruff, mypy, etc.)
pre-commit run -a            # Same as make format
uv run ruff check src/       # Run linter
uv run ruff format src/      # Format code
uv run mypy src/             # Run type checker
```

### Documentation

```bash
make gen-docs                # Generate API docs from src/ and scripts/
uv run mkdocs serve          # Serve docs at http://localhost:9987
uv run poe docs              # Generate and serve (requires dev group)
```

### Maintenance

```bash
make clean                   # Remove caches, artifacts, generated docs
```

## Project Architecture

The codebase follows a modular architecture centered around the Werewolf game simulation:

### Core Game Architecture

The game engine operates through several interconnected components:

1. **GameEngine** (`core/game_engine.py`): Central orchestrator that manages game flow

   - Controls phase transitions (Night → Day → Voting)
   - Executes night actions in priority order
   - Handles victory condition checks
   - Emits events for UI updates via callback system

2. **GameState** (`core/game_state.py`): Maintains current game state

   - Tracks phase (Night/Day/Voting), round number
   - Manages player status (alive/dead)
   - Stores votes, night actions, and game history

3. **Player** (`core/player.py`): Represents individual game participants

   - Links to an AI agent via composition
   - Tracks role assignment, status, and action history
   - Provides interface for agent decision-making

4. **Role System** (`core/roles/`): Implements 20+ unique roles

   - Base class defines action priority and ability constraints
   - Three camps: Werewolf, Villager, Neutral
   - Each role has configurable `can_act_night`, `can_act_day`, `max_uses`
   - Priority system ensures correct execution order (Cupid → Guard → Werewolf → Witch → Seer)

5. **Event System** (`core/events.py`): Observable pattern for game events

   - EventType enum: NIGHT_START, DAY_START, PLAYER_DIED, VOTE_CAST, etc.
   - EventLogger maintains chronological game history
   - UI components subscribe to events for real-time updates

6. **Victory Conditions** (`core/victory.py`): Evaluates win conditions

   - Villagers win when all werewolves eliminated
   - Werewolves win when they equal/outnumber villagers
   - Lovers win when only two lovers remain

### AI Agent Interface

**Unified Agent System** (`ai/agents.py`):

All agent implementations are consolidated in a single file with a simplified architecture:

- `BaseAgent`: Base class with single required method: `get_response(message: str) -> str`
  - Input: String containing role info, game state, and action request
  - Output: String with agent's decision
  - Maintains conversation history automatically
- `DemoAgent`: Random choice agent (no LLM, for testing)
- `HumanAgent`: Console input for human players
- `LLMAgent`: Unified LLM agent using ChatCompletion API
  - Supports any OpenAI-compatible API endpoint
  - Single implementation replaces old provider-specific agents (`OpenAIAgent`, `AnthropicAgent`, etc.)
  - Configure via `base_url` parameter (OpenAI, Anthropic, xAI, local models, etc.)

**Factory Functions:**

- `create_agent(config: PlayerConfig) -> BaseAgent`: Creates agent from player config
- `load_players_config(yaml_path: Path) -> PlayersConfig`: Loads and validates YAML config

**Key Design Principle**: The agent interface is intentionally minimal. All LLM providers that support OpenAI's ChatCompletion API format can use the same `LLMAgent` class - just change the `base_url` and `api_key_env`. Future instances should maintain this abstraction.

### Configuration System

**GameConfig** (`config/game_config.py`):

- Pydantic model with validation
- Fields: `num_players`, `role_names`, `night_timeout`, `day_timeout`, `vote_timeout`
- Validators ensure: role count matches player count, at least one werewolf present

**Presets** (`config/role_presets.py`):

- Pre-configured game setups: `6-players`, `9-players`, `12-players`, `15-players`, `expert`, `chaos`
- Access via: `get_preset_by_name("9-players")` or `list_preset_names()`

**Player Configuration** (`ai/agents.py`):

- `PlayerConfig`: Pydantic model for individual player configuration
  - Validates `base_url` is provided for LLM models (not required for `human`/`demo`)
  - Determines agent type based on `model` field
- `PlayersConfig`: Root configuration containing list of players and optional preset
  - Validates all player names are unique
  - Can be loaded from YAML via `load_players_config(yaml_path)`

### TUI System

**Textual Framework** (`ui/tui_app.py`):

- Real-time game visualization with four panels:
  - Player Panel (left): Lists players, AI models, status
  - Game Panel (top center): Round, phase, statistics
  - Chat Panel (bottom center): Scrollable event log with player discussions
  - Debug Panel (right): Toggle with 'd' key
- Keyboard controls: 'q' to quit, 'd' to toggle debug panel, 'n' to advance to next step

**Components** (`ui/components/`):

- Each panel is a reusable Textual widget
- Updates driven by event callbacks from GameEngine
- Styled with Rich formatting for terminal output

### Source Layout

```
src/llm_werewolf/
├── ai/                  # AI agent implementations
│   ├── agents.py        # All agent implementations (BaseAgent, DemoAgent, HumanAgent, LLMAgent)
│   └── message.py       # Message formatting utilities
├── config/              # Game configurations
│   ├── game_config.py   # GameConfig Pydantic model
│   └── role_presets.py  # Preset configurations
├── core/                # Core game logic
│   ├── game_engine.py   # Main game orchestrator
│   ├── game_state.py    # State management
│   ├── player.py        # Player representation
│   ├── actions.py       # Action validation
│   ├── events.py        # Event system
│   ├── victory.py       # Win condition checker
│   └── roles/           # Role implementations
│       ├── base.py      # Role base class, Camp/Priority enums
│       ├── werewolf.py  # Werewolf camp roles
│       ├── villager.py  # Villager camp roles
│       └── neutral.py   # Neutral roles (Lovers, etc.)
├── ui/                  # TUI components
│   ├── tui_app.py       # Main Textual app
│   ├── styles.py        # CSS styling
│   └── components/      # Reusable widgets
├── utils/               # Utilities
│   ├── logger.py        # Logging setup
│   └── validator.py     # Input validation
└── cli.py               # CLI entry point
```

## Testing Infrastructure

- **Directory**: `tests/` (mirrors `src/` structure)
- **Coverage**: Minimum 40% required (`--cov-fail-under=40`)
- **Parallel execution**: Enabled via pytest-xdist (`-n=auto`)
- **Reports**: Generated in `.github/reports/` (coverage.xml, pytest_logs.log)
- **Async support**: `asyncio_mode = "auto"` for async test functions
- **Markers**:
  - `@pytest.mark.slow`: For slow tests
  - `@pytest.mark.skip_when_ci`: Skip in CI/CD

## Environment Configuration

Create `.env` file for LLM API keys (see `.env.example`):

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

## CI/CD Workflows

All workflows in `.github/workflows/`:

- **test.yml**: Runs pytest on Python 3.10-3.13 for PRs
- **code-quality-check.yml**: Runs pre-commit hooks on PRs
- **deploy.yml**: Deploys MkDocs to GitHub Pages
- **build_release.yml**: Builds package on tags, generates changelog
- **build_image.yml**: Builds Docker image to GHCR
- **release_drafter.yml**: Maintains draft releases from Conventional Commits
- **semantic-pull-request.yml**: Enforces Conventional Commit PR titles

## Code Style and Linting

- **Linter**: ruff with extensive rule sets
- **Line length**: 99 characters (Google Python Style Guide)
- **Naming**: snake_case (functions/vars), PascalCase (classes), UPPER_CASE (constants)
- **Type hints**: Required on public functions; mypy with Pydantic plugin enabled
- **Docstrings**: Google-style format
- **Per-file ignores**:
  - `tests/*`: Ignore S101 (assert), ANN (annotations), SLF001 (private access)
  - `*.ipynb`: Ignore T201 (print), F401 (unused imports), S105, F811, ANN, PERF, SLF
  - `examples/*.py`: Ignore UP, DOC, RUF, D, C, F401, T201

## Pydantic Models

This project uses **Pydantic v2** (currently v2.11.7). All Pydantic models MUST use Pydantic v2 syntax.

### Configuration Pattern

**CORRECT** (Pydantic v2):

```python
from pydantic import BaseModel, Field, ConfigDict


class MyModel(BaseModel):
    """My model description."""

    field_name: str = Field(..., description="Field description")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        frozen=True,  # Make model immutable if needed
        str_strip_whitespace=True,  # Example of other config options
    )
```

**INCORRECT** (Pydantic v1 - DO NOT USE):

```python
from typing import ClassVar
from pydantic import BaseModel, Field


class MyModel(BaseModel):
    """My model description."""

    field_name: str = Field(..., description="Field description")

    class Config:  # ❌ This is deprecated in Pydantic v2
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}
        frozen = True
```

### Common ConfigDict Options

- `json_encoders`: Custom JSON serialization for specific types
- `frozen`: Make model immutable (like dataclass frozen=True)
- `str_strip_whitespace`: Automatically strip whitespace from strings
- `validate_assignment`: Validate fields on assignment after initialization
- `arbitrary_types_allowed`: Allow arbitrary types in model fields
- `use_enum_values`: Use enum values instead of enum objects in dict/json

### Examples in Codebase

- `core/events.py`: Event model with datetime JSON encoding
- `config/game_config.py`: GameConfig with validation
- `ai/agents.py`: PlayerConfig and PlayersConfig models

### Migration Notes

If you encounter a Pydantic v1 style nested `Config` class:

1. Import `ConfigDict` from `pydantic`
2. Remove `from typing import ClassVar` if only used for Config
3. Replace nested `class Config:` with `model_config = ConfigDict(...)`
4. Remove `ClassVar[dict]` type annotations from `json_encoders`

This ensures compatibility with mkdocstrings documentation generation and Pydantic v2 best practices.

## Dependency Management

```bash
uv add <package>                    # Add production dependency
uv add <package> --group llm-openai # Add to optional group
uv remove <package>                 # Remove dependency
```

## Important Design Considerations

### When Adding New LLM Providers

**For OpenAI-Compatible APIs (Most Common):**

No code changes needed! Just configure in YAML:

1. Add player entry with `model`, `base_url`, and `api_key_env` fields
2. Set environment variable with API key in `.env`
3. The unified `LLMAgent` handles all OpenAI-compatible endpoints

**For Non-Compatible APIs (Rare):**

1. Create new agent class in `ai/agents.py` inheriting from `BaseAgent`
2. Implement only `get_response(message: str) -> str`
3. Update `create_agent()` factory function to handle new model type
4. Update `.env.example` with required environment variables
5. Optionally create dependency group in `pyproject.toml` under `[dependency-groups]`

### When Adding New Roles

1. Determine camp (Werewolf/Villager/Neutral)
2. Add role class to appropriate file in `core/roles/` (`werewolf.py`, `villager.py`, or `neutral.py`)
3. Inherit from `Role` base class and define `get_config()` method with:
   - Role name, camp, description
   - Correct `ActionPriority` (determines execution order during night phase)
   - Flags: `can_act_night`, `can_act_day`, `max_uses` (if ability has limited uses)
4. Implement `get_night_actions(game_state)` method (returns list of Action objects)
5. Register in `core/roles/__init__.py` (add to `__all__` and import statement)
6. Add to `role_map` dictionary in `config/game_config.py` (line ~145)
7. Add role name to validator in `config/game_config.py:validate_minimum_werewolves` if werewolf role
8. Optionally add to presets in `config/role_presets.py`
9. Update role list in README.md

### Game Flow Order

Each round follows this sequence:

1. **Night phase** (`GamePhase.NIGHT`):
   - PHASE_CHANGED event emitted
   - Players with night actions execute in priority order (see `ActionPriority` enum in `core/roles/base.py`)
   - Actions sorted and executed via `process_actions()` in game_engine.py
   - Deaths resolved via `resolve_deaths()` method
   - Victory check
2. **Day discussion phase** (`GamePhase.DAY_DISCUSSION`):
   - PHASE_CHANGED event emitted
   - Announce night deaths
   - Each alive player's agent generates speech via `get_response()` using `_build_discussion_context()`
   - PLAYER_SPEECH events logged
3. **Voting phase** (`GamePhase.DAY_VOTING`):
   - Players vote to eliminate a suspect
   - Process votes via `VoteAction`
   - Handle special cases (Idiot survives but loses voting rights)
   - Eliminate player with most votes
   - Victory check
4. **Phase advancement**: Call `game_state.next_phase()` to increment round and reset temporary state
5. Repeat until victory condition met or game manually ended

### Event Callback System

The GameEngine uses a callback pattern to notify the UI of game events:

- **Setting callback**: `engine.on_event = callback_function` (see `ui/tui_app.py`)
- **Event creation**: GameEngine calls `_log_event()` which creates an Event and calls the callback
- **Event types**: Defined in `EventType` enum (GAME_STARTED, PLAYER_DIED, VOTE_CAST, PLAYER_SPEECH, etc.)
- **Event visibility**: Events can be restricted to specific players via `visible_to` parameter
- **UI updates**: TUI components subscribe to events and update displays in real-time

This decouples game logic from UI, allowing console mode, TUI, or future web interfaces.

## Important Paths

- Source code: `src/llm_werewolf/`
- Tests: `tests/`
- Documentation: `docs/`
- Scripts: `scripts/`
- Examples: `examples/`
- Player configs: `configs/` (YAML player configuration files)
- CI reports: `.github/reports/`
- Cache directories: `.cache/` (pytest, ruff, mypy, logfire)
