"""Event formatter for consistent event display across CLI and TUI."""

from typing import ClassVar

from rich.text import Text

from llm_werewolf.core.types import Event, EventType


class EventFormatter:
    """Formats game events for display with consistent styling."""

    # Event type to style mapping (shared by CLI and TUI)
    EVENT_STYLES: ClassVar[dict[EventType, str]] = {
        EventType.GAME_STARTED: "bold green",
        EventType.GAME_ENDED: "bold red",
        EventType.PHASE_CHANGED: "bold cyan",
        EventType.ROUND_STARTED: "bold blue",
        EventType.PLAYER_DIED: "red",
        EventType.PLAYER_REVIVED: "green",
        EventType.ROLE_REVEALED: "magenta",
        EventType.ROLE_ACTING: "dim cyan",
        EventType.WEREWOLF_KILLED: "red",
        EventType.WITCH_SAVED: "green",
        EventType.WITCH_POISONED: "red",
        EventType.SEER_CHECKED: "blue",
        EventType.GUARD_PROTECTED: "green",
        EventType.LOVERS_LINKED: "magenta",
        EventType.LOVER_DIED: "red",
        EventType.HUNTER_REVENGE: "yellow",
        EventType.KNIGHT_DUEL: "yellow",
        EventType.VOTE_CAST: "yellow",
        EventType.VOTE_RESULT: "bold yellow",
        EventType.PLAYER_ELIMINATED: "bold red",
        EventType.SHERIFF_CAMPAIGN_STARTED: "bold gold1",
        EventType.SHERIFF_CANDIDATE_SPEECH: "gold1",
        EventType.SHERIFF_VOTE_CAST: "yellow",
        EventType.SHERIFF_ELECTED: "bold gold1",
        EventType.SHERIFF_TIE: "yellow",
        EventType.SHERIFF_BADGE_TRANSFERRED: "gold1",
        EventType.SHERIFF_BADGE_TORN: "dim gold1",
        EventType.PLAYER_SPEECH: "cyan",
        EventType.PLAYER_DISCUSSION: "blue",
        EventType.MESSAGE: "dim italic",
        EventType.ERROR: "bold red",
    }

    @classmethod
    def format_event(cls, event: Event, include_timestamp: bool = True) -> Text:
        """Format an event as Rich Text with appropriate styling.

        Args:
            event: The event to format.
            include_timestamp: Whether to include timestamp in the output.

        Returns:
            Text: Formatted Rich Text object.
        """
        text = Text()

        # Add timestamp if requested
        if include_timestamp:
            time_str = event.timestamp.strftime("%H:%M:%S")
            text.append(f"[{time_str}] ", style="dim")

        # Get style for this event type (default to white if not found)
        style = cls.EVENT_STYLES.get(event.event_type, "white")

        # Add the message with appropriate style
        text.append(event.message, style=style)

        return text

    @classmethod
    def get_event_style(cls, event_type: EventType) -> str:
        """Get the style for a specific event type.

        Args:
            event_type: The event type.

        Returns:
            str: The style string for Rich formatting.
        """
        return cls.EVENT_STYLES.get(event_type, "white")
