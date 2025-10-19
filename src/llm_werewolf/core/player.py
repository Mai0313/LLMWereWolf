from enum import Enum

from pydantic import Field, BaseModel

from llm_werewolf.ai import AgentType
from llm_werewolf.core.roles.base import Role


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


class PlayerInfo(BaseModel):
    """Public information about a player."""

    player_id: str = Field(..., description="Unique player identifier")
    name: str = Field(..., description="Player name")
    is_alive: bool = Field(default=True, description="Whether player is alive")
    statuses: set[PlayerStatus] = Field(default_factory=set, description="Current player statuses")
    ai_model: str = Field(default="unknown", description="AI model name")


class Player:
    """Represents a player in the Werewolf game."""

    def __init__(
        self,
        player_id: str,
        name: str,
        role: Role,
        agent: AgentType | None = None,
        ai_model: str = "unknown",
    ) -> None:
        """Initialize a player.

        Args:
            player_id: Unique identifier for the player.
            name: Display name for the player.
            role: The role assigned to this player.
            agent: AI agent controlling this player (optional).
            ai_model: Name of the AI model being used.
        """
        self.player_id = player_id
        self.name = name
        self.role = role(self)
        self.agent = agent
        self.ai_model = ai_model

        self._alive = True
        self.statuses: set[PlayerStatus] = {PlayerStatus.ALIVE}
        self.lover_partner_id: str | None = None

        # Vote tracking
        self.can_vote_flag = True

    def is_alive(self) -> bool:
        """Check if the player is alive.

        Returns:
            bool: True if the player is alive.
        """
        return self._alive

    def kill(self) -> None:
        """Mark the player as dead."""
        self._alive = False
        self.statuses.discard(PlayerStatus.ALIVE)
        self.statuses.add(PlayerStatus.DEAD)

    def revive(self) -> None:
        """Revive the player (e.g., by Witch's save potion)."""
        self._alive = True
        self.statuses.discard(PlayerStatus.DEAD)
        self.statuses.add(PlayerStatus.ALIVE)

    def add_status(self, status: PlayerStatus) -> None:
        """Add a status to the player.

        Args:
            status: The status to add.
        """
        self.statuses.add(status)

    def remove_status(self, status: PlayerStatus) -> None:
        """Remove a status from the player.

        Args:
            status: The status to remove.
        """
        self.statuses.discard(status)

    def has_status(self, status: PlayerStatus) -> bool:
        """Check if the player has a specific status.

        Args:
            status: The status to check for.

        Returns:
            bool: True if the player has the status.
        """
        return status in self.statuses

    def can_vote(self) -> bool:
        """Check if the player can vote.

        Returns:
            bool: True if the player can vote.
        """
        return self._alive and self.can_vote_flag

    def disable_voting(self) -> None:
        """Disable the player's voting rights."""
        self.can_vote_flag = False
        self.add_status(PlayerStatus.NO_VOTE)

    def set_lover(self, partner_id: str) -> None:
        """Set this player as a lover with another player.

        Args:
            partner_id: The ID of the lover partner.
        """
        self.lover_partner_id = partner_id
        self.add_status(PlayerStatus.LOVER)

    def is_lover(self) -> bool:
        """Check if the player is a lover.

        Returns:
            bool: True if the player is a lover.
        """
        return self.has_status(PlayerStatus.LOVER)

    def get_public_info(self) -> PlayerInfo:
        """Get public information about the player.

        Returns:
            PlayerInfo: Public player information.
        """
        return PlayerInfo(
            player_id=self.player_id,
            name=self.name,
            is_alive=self._alive,
            statuses=self.statuses.copy(),
            ai_model=self.ai_model,
        )

    def get_role_name(self) -> str:
        """Get the player's role name.

        Returns:
            str: The role name.
        """
        return self.role.name

    def get_camp(self) -> str:
        """Get the player's camp.

        Returns:
            str: The camp name.
        """
        return self.role.camp.value

    def __str__(self) -> str:
        """String representation of the player.

        Returns:
            str: Player name and status.
        """
        status = "alive" if self._alive else "dead"
        return f"{self.name} ({status})"

    def __repr__(self) -> str:
        """Repr of the player.

        Returns:
            str: Player representation.
        """
        return f"Player(id={self.player_id}, name={self.name}, role={self.role.name})"
