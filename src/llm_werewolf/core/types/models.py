"""Pydantic model definitions for the LLM Werewolf game.

This module contains all shared data models to avoid circular import issues.
"""

from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict

from llm_werewolf.core.types.enums import Camp, EventType, GamePhase, PlayerStatus, ActionPriority


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


class Event(BaseModel):
    """Represents a game event."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    event_type: EventType = Field(..., description="Type of the event")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the event occurred"
    )
    round_number: int = Field(..., description="Round number when event occurred")
    phase: str = Field(..., description="Game phase when event occurred")
    message: str = Field(..., description="Human-readable event message")
    data: dict = Field(default_factory=dict, description="Additional event data")
    visible_to: list[str] | None = Field(
        None, description="Player IDs who can see this event (None = all)"
    )

    def is_visible_to(self, player_id: str) -> bool:
        """Check if this event is visible to a specific player.

        Args:
            player_id: The player ID to check.

        Returns:
            bool: True if the event is visible to the player.
        """
        if self.visible_to is None:
            return True
        return player_id in self.visible_to

    def get_public_message(self) -> str:
        """Get the public version of the event message.

        Returns:
            str: The public message.
        """
        return self.message
