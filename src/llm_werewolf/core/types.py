"""Core type definitions for the LLM Werewolf game.

This module contains all shared type definitions including enums and data models
to avoid circular import issues between player, game_state, and roles modules.
"""

from enum import Enum

from pydantic import Field, BaseModel

# ============================================================================
# Enum Definitions
# ============================================================================


class Camp(str, Enum):
    """Enum representing the different camps in the game."""

    WEREWOLF = "werewolf"
    VILLAGER = "villager"
    NEUTRAL = "neutral"


class ActionPriority(int, Enum):
    """Enum representing the priority order of night actions."""

    # Higher number = earlier execution
    CUPID = 100  # Cupid acts first (only on night 1)
    THIEF = 95  # Thief chooses role (only on night 1)
    GUARD = 90  # Guard protects someone
    WEREWOLF = 80  # Werewolves kill
    WHITE_WOLF = 75  # White wolf kills another wolf
    WITCH = 70  # Witch uses potions
    SEER = 60  # Seer checks someone
    GRAVEYARD_KEEPER = 50  # Graveyard keeper checks if dead
    RAVEN = 40  # Raven marks someone for extra vote


class GamePhase(str, Enum):
    """Enum representing the different phases of the game."""

    SETUP = "setup"  # Game initialization
    NIGHT = "night"  # Night phase (role actions)
    DAY_DISCUSSION = "day_discussion"  # Day phase (discussion)
    DAY_VOTING = "day_voting"  # Day phase (voting)
    ENDED = "ended"  # Game has ended


class PlayerStatus(str, Enum):
    """Enum representing special statuses a player can have."""

    ALIVE = "alive"
    DEAD = "dead"
    PROTECTED = "protected"  # Protected by Guard
    POISONED = "poisoned"  # Poisoned by Witch
    SAVED = "saved"  # Saved by Witch
    CHARMED = "charmed"  # Charmed by Wolf Beauty
    BLOCKED = "blocked"  # Blocked by Nightmare Wolf
    MARKED = "marked"  # Marked by Raven
    REVEALED = "revealed"  # Idiot revealed
    NO_VOTE = "no_vote"  # Lost voting rights (Idiot)
    LOVER = "lover"  # Is in love


class ActionType(str, Enum):
    """Enum representing different types of actions."""

    # Night actions
    WEREWOLF_KILL = "werewolf_kill"
    WITCH_SAVE = "witch_save"
    WITCH_POISON = "witch_poison"
    SEER_CHECK = "seer_check"
    GUARD_PROTECT = "guard_protect"
    CUPID_LINK = "cupid_link"
    RAVEN_MARK = "raven_mark"
    WHITE_WOLF_KILL = "white_wolf_kill"
    WOLF_BEAUTY_CHARM = "wolf_beauty_charm"
    NIGHTMARE_BLOCK = "nightmare_block"

    # Day actions
    VOTE = "vote"
    HUNTER_SHOOT = "hunter_shoot"
    KNIGHT_DUEL = "knight_duel"
    ALPHA_WOLF_SHOOT = "alpha_wolf_shoot"

    # Special actions
    THIEF_CHOOSE = "thief_choose"
    MAGICIAN_SWAP = "magician_swap"


# ============================================================================
# Pydantic Data Models
# ============================================================================


class RoleConfig(BaseModel):
    """Configuration for a role."""

    name: str = Field(..., description="Name of the role")
    camp: Camp = Field(..., description="Camp this role belongs to")
    description: str = Field(..., description="Description of the role's abilities")
    priority: ActionPriority | None = Field(None, description="Night action priority")
    can_act_night: bool = Field(default=False, description="Can perform night actions")
    can_act_day: bool = Field(default=False, description="Can perform day actions")
    max_uses: int | None = Field(None, description="Max times ability can be used")


class GameStateInfo(BaseModel):
    """Public information about the game state."""

    phase: GamePhase = Field(..., description="Current game phase")
    round_number: int = Field(..., description="Current round number")
    total_players: int = Field(..., description="Total number of players")
    alive_players: int = Field(..., description="Number of alive players")
    werewolves_alive: int = Field(..., description="Number of alive werewolves")
    villagers_alive: int = Field(..., description="Number of alive villagers")


class PlayerInfo(BaseModel):
    """Public information about a player."""

    player_id: str = Field(..., description="Unique player identifier")
    name: str = Field(..., description="Player name")
    is_alive: bool = Field(default=True, description="Whether player is alive")
    statuses: set[PlayerStatus] = Field(default_factory=set, description="Current player statuses")
    ai_model: str = Field(default="unknown", description="AI model name")
