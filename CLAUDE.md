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

# Run with specific preset
uv run llm-werewolf --preset 9-players
uv run llm-werewolf --preset 12-players

# Run in console mode (no TUI)
uv run llm-werewolf --no-tui

# Enable debug panel
uv run llm-werewolf --debug

# View help
uv run llm-werewolf --help
```

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

**Abstract Agent Pattern** (`ai/base_agent.py`):

- `BaseAgent`: Abstract base class with single required method: `get_response(message: str) -> str`
- Input: String containing role info, game state, and action request
- Output: String with agent's decision
- Optional: `initialize()`, `reset()`, conversation history management

**Implementations** (`ai/llm_agents.py`):

- `DemoAgent`: Simple random choice agent (no LLM)
- `HumanAgent`: Console input for human players
- `OpenAIAgent`: OpenAI GPT models
- `AnthropicAgent`: Anthropic Claude models
- `GenericLLMAgent`: Any OpenAI-compatible API
- Factory function: `create_agent_from_config()` auto-loads from `.env`

**Key Design Principle**: The agent interface is intentionally minimal to support any LLM provider. Future instances should maintain this abstraction when adding new agent types.

### Configuration System

**GameConfig** (`config/game_config.py`):

- Pydantic model with validation
- Fields: `num_players`, `role_names`, `night_timeout`, `day_timeout`, `vote_timeout`
- Validators ensure: role count matches player count, at least one werewolf present

**Presets** (`config/role_presets.py`):

- Pre-configured game setups: `6-players`, `9-players`, `12-players`, `15-players`, `expert`, `chaos`
- Access via: `get_preset_by_name("9-players")` or `list_preset_names()`

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
│   ├── base_agent.py    # Abstract interface
│   ├── llm_agents.py    # LLM provider implementations
│   └── message.py       # Message formatting utilities
├── config/              # Game configurations
│   ├── game_config.py   # GameConfig Pydantic model
│   ├── llm_config.py    # LLM provider settings
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

## Dependency Management

```bash
uv add <package>                    # Add production dependency
uv add <package> --group llm-openai # Add to optional group
uv remove <package>                 # Remove dependency
```

## Important Design Considerations

### When Adding New LLM Providers

1. Inherit from `BaseAgent` in `ai/llm_agents.py`
2. Implement only `get_response(message: str) -> str`
3. Add provider configuration to `config/llm_config.py`
4. Update `.env.example` with required environment variables
5. Create optional dependency group in `pyproject.toml` under `[dependency-groups]`

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
- CI reports: `.github/reports/`
- Cache directories: `.cache/` (pytest, ruff, mypy, logfire)
