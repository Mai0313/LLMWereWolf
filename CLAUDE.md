# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM Werewolf is an AI-powered implementation of the Werewolf social deduction game. The project supports multiple LLM models through a unified agent interface and provides both a console mode (auto-play) and an interactive Terminal User Interface (TUI) built with Textual.

## Common Commands

### Development & Testing

```bash
# Install dependencies
uv sync

# Run tests (requires pytest)
pytest                                     # Run all tests
pytest tests/core/test_player.py          # Run specific test file
pytest -k test_name                       # Run specific test by name
pytest -vv                                # Verbose output
make test                                  # Alias for pytest

# Linting and formatting
pre-commit run -a                         # Run all pre-commit hooks
make fmt                                  # Alias for pre-commit

# Generate documentation
make gen-docs                             # Generate API docs from source
uv run ./scripts/gen_docs.py --source ./src --output ./docs/Reference gen_docs

# Clean build artifacts
make clean                                # Remove generated files, cache, etc.
```

### Running the Game

```bash
# TUI Mode (Interactive Terminal Interface)
uv run llm-werewolf-tui configs/demo.yaml           # Demo agents (no API key needed)
uv run llm-werewolf-tui configs/gpt-5-chaos.yaml.yaml        # LLM agents (requires API keys)

# Console Mode (Auto-play with text logs)
uv run llm-werewolf configs/demo.yaml
uv run werewolf configs/demo.yaml                   # Alias

# If installed globally
llm-werewolf-tui configs/demo.yaml
llm-werewolf configs/demo.yaml
```

### Configuration

Create `.env` file with API keys:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
XAI_API_KEY=xai-...
```

## Architecture

### Core Game Architecture

The game follows a modular architecture with clear separation of concerns:

**Game Engine Flow:**

1. `GameEngine` (`core/engine/game_engine.py`) orchestrates the entire game loop
   - Composed of multiple mixins for clean separation of concerns:
     - `GameEngineBase` (`core/engine/base.py`): Core initialization, event handling, and game loop
     - `NightPhaseMixin` (`core/engine/night_phase.py`): Night phase execution logic
     - `DayPhaseMixin` (`core/engine/day_phase.py`): Day discussion phase logic
     - `VotingPhaseMixin` (`core/engine/voting_phase.py`): Voting phase logic
     - `DeathHandlerMixin` (`core/engine/death_handler.py`): Death-related logic (werewolf kills, lover deaths, etc.)
     - `ActionProcessorMixin` (`core/engine/action_processor.py`): Processing game actions
2. `GameState` (`core/game_state.py`) maintains current game state (players, round, phase)
3. `EventLogger` (`core/events.py`) tracks all game events for display/debugging
4. `EventFormatter` (`core/event_formatter.py`) provides centralized event formatting for consistent display
5. `VictoryChecker` (`core/victory.py`) evaluates win conditions after each phase
6. `ActionSelector` (`core/action_selector.py`) prompts agents and selects valid actions

**Phase Execution:**

- Night Phase: Roles act in priority order (see `ActionPriority` enum in `core/types/enums.py`)
- Day Discussion: All living players discuss via their agents
- Day Voting: Players vote; highest vote count is eliminated
- Victory Check: After each phase, checks for faction victory or lover victory

**Action System:**
The action system (`core/actions/`) separates action logic from role definitions:

- `BaseAction` (`actions/base.py`): Base class for all actions with validation and execution
- `CommonActions` (`actions/common.py`): Shared actions like voting and discussion
- `VillagerActions` (`actions/villager.py`): Villager faction-specific actions
- `WerewolfActions` (`actions/werewolf.py`): Werewolf faction-specific actions
- Actions are returned from role's `get_night_actions()` method and executed by the game engine
- `ActionSelector` (`core/action_selector.py`): Helper class for building prompts and parsing agent responses for target selection, yes/no questions, and multi-target selections

**Agent System:**
The agent system is designed for extensibility:

- `BaseAgent` (`core/agent.py`): Protocol defining `get_response(message: str) -> str`
- `LLMAgent` (`ai/agents.py`): OpenAI-compatible API client wrapper
- `HumanAgent` (`core/agent.py`): Console input for human players
- `DemoAgent` (`core/agent.py`): Random canned responses for testing

**Configuration System:**

- `GameConfig` (`core/config/game_config.py`): Role composition, timeouts, and game rules
- `create_game_config_from_player_count()` (`core/config/presets.py`): Automatically generates balanced role configurations based on player count (6-20)
- `PlayersConfig` (`ai/agents.py`): YAML-based player configuration with agent types
- `create_agent()` factory function routes model types to appropriate agent classes

### Role System

All roles inherit from `Role` (`core/roles/base.py`) which provides:

- `get_config()`: Returns `RoleConfig` (name, camp, description, priority)
- `can_act_tonight()`: Determines if role can act in current round
- `perform_action()`: Executes role-specific night action
- `validate_action()`: Validates action before execution

Roles are organized by faction:

- **Werewolf Faction** (`core/roles/werewolf.py`): Werewolf, AlphaWolf, WhiteWolf, WolfBeauty, etc.
- **Villager Faction** (`core/roles/villager.py`): Seer, Witch, Hunter, Guard, etc.
- **Neutral Roles** (`core/roles/neutral.py`): Thief, Lover, etc.

**Action Priority System:**
Night actions execute in order defined by `ActionPriority` enum (0=highest priority):

1. CUPID (0): Links lovers
2. THIEF (1): Chooses role
3. GUARD (2): Protects player
4. WEREWOLF (3): Kills target
5. WITCH (4): Uses potions
6. SEER (5): Checks identity
7. (etc., see `core/types/enums.py`)

### UI System

**TUI Architecture** (`ui/tui_app.py`):

- Built with Textual framework
- Components (`ui/components/`):
  - `PlayerPanel`: Shows all players with status indicators (alive/dead/protected/lover/poisoned)
  - `GamePanel`: Displays round, phase, faction counts, and vote tallies
  - `ChatPanel`: Scrollable event log with colored messages
- Event-driven: `GameEngine.on_event` callback pushes events to TUI in real-time
- Footer displays session ID and uptime

**Event System:**

- All game events are `Event` objects with type, message, round, phase, and optional data
- `EventType` enum defines all event types (GAME_STARTED, PLAYER_DIED, ROLE_ACTION, etc.)
- Console mode prints events directly; TUI displays them in ChatPanel

## Avoiding Circular Imports

**Important**: This codebase follows strict principles to avoid circular import dependencies through proper architecture design, not through workarounds.

### The Right Way: Protocol-Based Architecture

All type definitions are centralized in `core/types/`:

- **`types/enums.py`**: All enum types (Camp, GamePhase, ActionType, etc.)
- **`types/models.py`**: Data models (Event, PlayerInfo, RoleConfig, VictoryResult, etc.)
- **`types/protocols.py`**: Protocol definitions for structural typing (PlayerProtocol, RoleProtocol, GameStateProtocol, ActionProtocol, AgentProtocol)

Other modules import from `types/` and use Protocols to define interfaces without creating circular dependencies.

### What NOT to Do

**❌ Do NOT use `TYPE_CHECKING` to hide circular imports:**

```python
# BAD: This only hides the problem, doesn't solve it
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_werewolf.core.player import Player


def process_player(player: "Player") -> None:  # String annotation
    pass
```

**❌ Do NOT use string annotations (forward references) to avoid imports:**

```python
# BAD: String annotations mask circular dependency issues
def get_players(self) -> "list[Player]":
    pass
```

**❌ Do NOT import concrete classes inside functions:**

```python
# BAD: Function-level imports are a code smell
def validate(self) -> bool:
    from llm_werewolf.core.roles.villager import Witch

    return isinstance(self.actor.role, Witch)
```

### The Correct Approach

**✅ Use Protocols for type hints:**

```python
# GOOD: Import Protocol at module level
from llm_werewolf.core.types import PlayerProtocol


def process_player(player: PlayerProtocol) -> None:
    pass
```

**✅ Check role behavior by attributes or name:**

```python
# GOOD: Check by attribute existence
if hasattr(self.actor.role, "has_save_potion"):
    self.actor.role.has_save_potion = False

# GOOD: Check by role name
if self.target.role.name == "HiddenWolf":
    result = "villager"
```

**✅ Import concrete classes only where actually needed:**

```python
# GOOD: Import concrete class in implementation file
from llm_werewolf.core.player import Player
from llm_werewolf.core.game_state import GameState


# Use Protocols in type hints for parameters
def setup_game(self, players: list[AgentProtocol], roles: list[RoleProtocol]) -> None:
    # Create concrete instances inside the function
    player = Player(player_id=id, name=name, role=role, agent=agent)
```

### Architecture Rules

1. **Types layer** (`core/types/`): Contains all shared types, enums, models, and protocols. No dependencies on other core modules.

2. **Data layer** (`core/player.py`, `core/game_state.py`): Implements core data structures. Only imports from types layer.

3. **Logic layer** (`core/roles/`, `core/actions/`, `core/engine/`): Implements game logic. Imports from types and data layers. Uses Protocols for cross-module dependencies.

4. **Always verify**: After refactoring, verify no circular imports exist:

   ```bash
   uv run python -c "from llm_werewolf.core import player, game_state, roles, actions, engine; print('✅ No circular imports!')"
   ```

### Benefits of This Approach

- ✅ No hidden dependencies through `TYPE_CHECKING`
- ✅ Clear architectural layers
- ✅ Better IDE support and type checking
- ✅ Easier to test and maintain
- ✅ No runtime surprises from circular imports

## Key Implementation Details

### Discussion Context Management

The game engine maintains two separate discussion histories for context:

- `public_discussion_history`: Available to all players during day discussion
- `werewolf_discussion_history`: Only available to werewolves during night discussion

These are managed in `GameEngineBase` and help agents maintain coherent conversations by having access to previous statements.

### Adding a New Role

1. Create role class in appropriate file (`core/roles/werewolf.py`, `core/roles/villager.py`, `core/roles/neutral.py`)
2. Inherit from `Role` (`core/roles/base.py`) and implement:
   - `get_config()`: Return `RoleConfig` with name, camp, description, priority
   - `get_night_actions()`: **Required** - All roles must implement this method. If the role has no night actions, return an empty list `[]`. If the role has night actions, return a list of `Action` objects from `core/actions/`.
3. Register in `core/role_registry.py` ROLE_CLASSES dict
4. Optionally update the automatic role assignment logic in `create_game_config_from_player_count()` (`core/config/presets.py`) if you want this role to be auto-assigned for specific player counts
5. Add tests in `tests/core/test_roles.py`

**Note**: The `get_night_actions()` method is an abstract method that **must** be implemented by all roles. This design forces developers to explicitly consider whether a role has night abilities, preventing bugs where developers forget to implement night actions for roles that should have them. Roles without night abilities (like Villager, Hunter, Idiot) should return an empty list.

### Adding a New Agent Type

1. Create agent class inheriting from `BaseAgent`
2. Implement `get_response(message: str) -> str` method
3. Update `create_agent()` factory in `ai/agents.py` to route to new agent type
4. Update `PlayerConfig.model` field validator if needed
5. Add tests in `tests/ai/test_base_agent.py`

### Game State Management

- `GameState` is the single source of truth for player status
- Players track their status through boolean flags: `is_alive`, `is_protected`, `is_poisoned`, `is_charmed`, `revealed_as_idiot`
- Actions are executed through the action system, returning effect descriptions
- `ActionProcessorMixin` in `GameEngine` applies action results by updating player states
- Status effects (protected, poisoned, charmed) are cleared at phase boundaries by the respective phase mixins

### Language Support

- Game supports multilingual prompts via `language` config field (en-US, zh-TW, zh-CN)
- `Locale` class (`core/locale.py`) manages localized strings with fallback to English
- LLMAgent appends language instruction to all prompts: "Please respond in {language}"
- Event messages are formatted through `EventFormatter` with support for localization

## Testing

Test organization:

- `tests/core/`: Core game logic tests (players, roles, game state)
- `tests/ai/`: Agent system tests
- `tests/config/`: Configuration loading tests
- `tests/integration/`: Full game flow integration tests

Coverage target: 40% minimum (see `pyproject.toml`)

## Dependencies

Critical dependencies:

- **pydantic** (≥2.12.3): Data validation for all models
- **textual** (≥6.3.0): TUI framework
- **openai** (≥2.5.0): API client (works with any OpenAI-compatible endpoint)
- **fire** (≥0.7.1): CLI argument parsing
- **logfire** (≥4.13.2): Structured logging

## Code Quality

- Uses **Ruff** for linting/formatting (config in `pyproject.toml`)
- Line length: 99 characters (Google Python Style Guide)
- Docstring convention: Google style
- Type hints required (enforced by mypy in pre-commit)
- Pre-commit hooks run on all commits (Ruff, mypy, shellcheck, mdformat, etc.)
