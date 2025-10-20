# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM Werewolf is an AI-powered implementation of the Werewolf (Mafia) social deduction game. The project supports multiple LLM models, human players, and provides both a Terminal User Interface (TUI) using Textual and a console-based interface.

## Development Commands

### Dependency Management

```bash
# Install all dependencies (uses uv package manager)
uv sync

# Install specific dependency groups
uv sync --group dev          # Development tools
uv sync --group test         # Testing dependencies
uv sync --group docs         # Documentation tools
uv sync --all-groups        # Install everything
```

### Running the Game

```bash
# TUI mode (interactive terminal interface)
uv run llm-werewolf-tui configs/demo.yaml
uv run llm-werewolf-tui configs/players.yaml --debug

# Console mode (auto-play with text logs)
uv run llm-werewolf configs/demo.yaml

# Alternative aliases
uv run werewolf-tui configs/demo.yaml
uv run werewolf configs/demo.yaml
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/core/test_roles.py -v

# Run specific test function
uv run pytest tests/core/test_roles.py::test_werewolf_role -v

# Run tests in parallel (faster)
uv run pytest -n auto
```

### Code Quality

```bash
# Linting
uv run ruff check src/

# Auto-fix issues
uv run ruff check --fix src/

# Format code
uv run ruff format src/

# Type checking
uv run mypy src/

# Run all pre-commit hooks
uv run pre-commit run --all-files
# Or use make
make format
```

### Using Makefile

```bash
make help           # Show all available commands
make clean          # Clean auto-generated files
make format         # Run pre-commit hooks
make test           # Run all tests
make gen-docs       # Generate documentation
```

## Architecture Overview

### Core Game Flow

The game follows a structured phase-based loop managed by `GameEngine` (src/llm_werewolf/core/game_engine.py):

1. **Setup Phase**: Players assigned random roles, game state initialized
2. **Night Phase**: Roles with night abilities act in priority order (defined by `ActionPriority` enum)
3. **Day Discussion Phase**: Players discuss via their AI agents or human input
4. **Day Voting Phase**: Players vote to eliminate suspects
5. **Victory Check**: Evaluate win conditions after each phase

The engine coordinates all phases and uses `GameState` to track current state, deaths, votes, and role actions.

### Key Components

**Game State Management** (src/llm_werewolf/core/game_state.py):

- `GameState`: Central state manager tracking phase, round, deaths, votes, and night actions
- `GamePhase` enum: SETUP, NIGHT, DAY_DISCUSSION, DAY_VOTING, ENDED
- Provides query methods like `get_alive_players()`, `count_alive_by_camp()`, `get_vote_counts()`
- Maintains night action tracking (werewolf_target, witch actions, guard protection, etc.)

**Role System** (src/llm_werewolf/core/roles/):

- All roles inherit from abstract `Role` base class (base.py)
- Each role has a `RoleConfig` defining camp, priority, abilities, and constraints
- Three role categories:
  - Werewolf faction (werewolf.py): Werewolf, AlphaWolf, WhiteWolf, WolfBeauty, etc.
  - Villager faction (villager.py): Seer, Witch, Hunter, Guard, Elder, etc.
  - Neutral roles (neutral.py): Thief, Lover
- Roles implement `get_night_actions()` returning list of `Action` objects
- Priority system (`ActionPriority` enum) ensures actions execute in correct order (e.g., Guard before Werewolf before Witch)

**Role Registry** (src/llm_werewolf/core/role_registry.py):

- Centralized role management system
- `get_role_map()`: Returns mapping of role names to role classes
- `get_werewolf_roles()`: Returns set of werewolf role names
- `validate_role_names()`: Validates role configurations
- `create_roles()`: Creates role class list from role names
- Use this module when adding new roles or validating configurations

**Action System** (src/llm_werewolf/core/actions.py):

- Abstract `Action` base class with `validate()` and `execute()` methods
- Specific actions: WerewolfKillAction, WitchSaveAction, SeerCheckAction, VoteAction, etc.
- Actions modify `GameState` and return messages describing results
- Engine sorts actions by priority before execution

**Agent System** (src/llm_werewolf/ai/agents.py):

- Three agent types:
  - `LLMAgent`: Uses OpenAI-compatible API (GPT, Claude, DeepSeek, local models)
  - `HumanAgent`: Console input for human players
  - `DemoAgent`: Random canned responses for testing
- All agents implement `get_response(message: str) -> str` interface
- `create_agent()` factory function creates agents from `PlayerConfig`
- LLMAgent maintains chat_history for context across game phases

**Action Selection** (src/llm_werewolf/ai/action_selector.py):

- `ActionSelector` class provides structured prompts for AI decision-making
- `build_target_selection_prompt()`: Creates formatted prompts for selecting targets
- `parse_target_selection()`: Extracts player choices from AI responses
- Handles optional "SKIP" actions for roles with conditional abilities
- Used by night actions (Werewolf kills, Witch saves/poisons, Seer checks, etc.)

**Player Management** (src/llm_werewolf/core/player.py):

- `Player` class wraps agent, role, and state (alive, lover, voting ability)
- Each player has unique player_id, name, role instance, and agent reference
- Players are created with role assignments during `GameEngine.setup_game()`

**Configuration System** (src/llm_werewolf/core/config/):

- `GameConfig` (game_config.py): Defines game rules, timeouts, role composition
- `PlayerConfig` (imported from `llm_werewolf.ai`): Individual player configuration model
- `PlayersConfig` (imported from `llm_werewolf.ai`): YAML-loaded player list configurations
- `presets.py`: Predefined configurations (6-players, 9-players, 12-players, 15-players, expert, chaos)
- Presets selected via `preset` field in YAML config
- Access presets via `get_preset_by_name(preset_name)` function

**Event System** (src/llm_werewolf/core/events.py):

- `EventLogger` tracks all game events
- `EventType` enum: GAME_STARTED, PHASE_CHANGED, PLAYER_SPEECH, WEREWOLF_KILLED, etc.
- Events used for TUI updates and game history
- Engine calls `_log_event()` for significant actions

**Victory Conditions** (src/llm_werewolf/core/victory.py):

- `VictoryChecker` evaluates win conditions:
  - Villagers win: All werewolves eliminated
  - Werewolves win: Werewolves >= Villagers
  - Lovers win: Only two lovers remain (takes precedence)
- Checked after night phase and voting phase

### UI Architecture

**TUI** (src/llm_werewolf/ui/):

- Built with Textual framework (tui_app.py)
- Four main panels (components/):
  - `PlayerPanel`: Shows all players, status (alive/dead), indicators (protected, lover, marked)
  - `GamePanel`: Current phase, round number, faction counts, vote tallies
  - `ChatPanel`: Scrollable event log with color-coded messages
  - `DebugPanel`: Session info, config details, role assignments (toggleable with 'd' key)
- Real-time updates via `GameEngine.on_event` callback
- Controls: q=quit, d=toggle debug, n=manual next step, arrow keys=navigation

**Console** (cli.py):

- Auto-play mode with text output via Rich console
- No user interaction after start
- Uses same GameEngine but prints events instead of TUI updates

## Configuration System

### YAML Configuration Format

Configuration files (e.g., configs/players.yaml) use this structure:

```yaml
preset: 9-players           # Role preset name
show_debug: false           # TUI debug panel visibility

players:
  - name: Player Name
    model: gpt-4o           # "human", "demo", or LLM model name
    base_url: https://api.openai.com/v1  # Required for LLMs
    api_key_env: OPENAI_API_KEY          # Environment variable name
    temperature: 0.7        # Optional, default 0.7
    max_tokens: 500         # Optional, default 500
```

**Agent Type Selection**:

- `model: "human"` → HumanAgent (console input)
- `model: "demo"` → DemoAgent (random responses)
- `model: <model_name>` + `base_url` → LLMAgent (API calls)

**Preset Options**:

- `6-players`: 2 Werewolves, Seer, Witch, 2 Villagers
- `9-players`: 2 Werewolves, Seer, Witch, Hunter, Guard, 3 Villagers
- `12-players`: 3 Werewolves (inc. AlphaWolf), Seer, Witch, Hunter, Guard, Cupid, Idiot, 3 Villagers
- `15-players`: 4 Werewolves, expanded role set
- `expert`: Complex werewolf variations
- `chaos`: Uncommon role combinations

### Environment Variables

Create `.env` file (see .env.example):

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
XAI_API_KEY=xai-...
```

## Adding New Roles

1. Create role class in appropriate file (werewolf.py, villager.py, or neutral.py)
2. Inherit from `Role` base class
3. Implement required methods:
   - `get_config()`: Return `RoleConfig` with camp, priority, abilities
   - `get_night_actions(game_state)`: Return list of actions or empty list
4. Create corresponding `Action` subclass in actions.py if needed
5. **Add role to role registry** in `core/role_registry.py`:
   - Import the role class in `get_role_map()`
   - Add to the returned dictionary
   - If werewolf role, add to `get_werewolf_roles()` set

Example structure:

```python
class NewRole(Role):
    def get_config(self) -> RoleConfig:
        return RoleConfig(
            name="NewRole",
            camp=Camp.VILLAGER,
            description="Role description",
            priority=ActionPriority.SEER,
            can_act_night=True,
            max_uses=1,  # Optional
        )

    def get_night_actions(self, game_state: GameState) -> list[Action]:
        # Return actions or empty list
        return []
```

Then update `role_registry.py`:

```python
# In get_role_map()
from llm_werewolf.core.roles.villager import NewRole

return {
    # ... existing roles ...
    "NewRole": NewRole
}

# If it's a werewolf role, also update get_werewolf_roles()
```

## Testing Strategy

- Unit tests in tests/ mirror src/ structure
- Core game logic tests: tests/core/
- Config and agent tests: tests/config/, tests/ai/
- Integration tests: tests/integration/test_game_flow.py
- Use `pytest.mark.slow` for long-running tests
- Use `pytest.mark.skip_when_ci` to skip tests in CI/CD
- Minimum coverage target: 40% (configured in pyproject.toml)

## Important Implementation Details

**Action Priority**: Actions execute in priority order defined by `ActionPriority` enum. Guard protects before werewolves attack, werewolves attack before witch saves/poisons. This is critical for correct game logic.

**Death Resolution**: Deaths are resolved in `GameEngine.resolve_deaths()` after all night actions collected. Special cases handled:

- Witch save cancels werewolf kill
- Guard protection blocks werewolf kill
- Elder has 2 lives (survives first attack)
- Lover death triggers partner death (heartbreak)
- Idiot survives vote but loses voting rights

**AI Prompting**: The engine builds context for agents using `_build_discussion_context()` which includes:

- Player's role and name
- Current round and phase
- Recent deaths
- Alive players list
- Role-specific instructions

**Game State Transitions**: `GameState.next_phase()` advances phases and resets temporary state (votes, night actions, death sets) when moving from voting to next night phase.

## Common Pitfalls

- Player count MUST match preset num_players (validated at startup)
- All player names must be unique (validated in PlayersConfig)
- LLM models require both base_url and api_key_env fields
- API keys loaded from environment variables, not directly in YAML
- Role names in YAML are case-sensitive and must match role_map keys exactly in `role_registry.py`
- Actions must be added to `get_action_priority()` map in game_engine.py for correct ordering
- When adding werewolf roles, update BOTH `get_role_map()` AND `get_werewolf_roles()` in role_registry.py
- Import paths: Config is now at `llm_werewolf.core.config`, not `llm_werewolf.config`

## Code Style

- Uses Ruff for linting and formatting (configured in pyproject.toml)
- Google-style docstrings enforced by pydocstyle
- Type hints required for all functions (enforced by ruff ANN rules)
- Line length: 99 characters
- Use Pydantic models for configuration and data validation
- Prefer composition over inheritance where possible

## Logging and Observability

- **Logfire Integration**: Project uses Pydantic Logfire for structured logging
- Configuration in pyproject.toml under `[tool.logfire]`
- Default: `send_to_logfire = false` (logs only to console for local development)
- Logfire automatically logs errors in role actions and critical game events
- Import and use: `import logfire` then `logfire.error()`, `logfire.info()`, etc.

## Recent Refactoring (October 2025)

The codebase underwent significant restructuring:

1. **Config Module Reorganization**: Config moved from `src/llm_werewolf/config/` to `src/llm_werewolf/core/config/`
2. **Role Registry Addition**: New centralized `role_registry.py` module manages all role-related lookups and validation
3. **Import Path Updates**: Update imports to use `llm_werewolf.core.config` instead of `llm_werewolf.config`
4. **File Renames**: `role_presets.py` renamed to `presets.py`
5. **Agent Configuration**: `PlayerConfig` and `PlayersConfig` moved to `llm_werewolf.ai` module

When working with older code examples or documentation, be aware of these path changes.

**Correct import patterns:**

```python
# Correct (current)
from llm_werewolf.core.config import GameConfig, get_preset_by_name
from llm_werewolf.ai import PlayerConfig, PlayersConfig, create_agent

# Incorrect (old)
from llm_werewolf.config import GameConfig, get_preset_by_name
```
