from typing import Any

from rich.text import Text
from textual.widgets import RichLog

from llm_werewolf.core.events import Event


class ChatPanel(RichLog):
    """Widget displaying the game chat/event history."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize the chat panel."""
        super().__init__(*args, **kwargs)
        self.events: list[Event] = []

    def add_event(self, event: Event) -> None:
        """Add an event to the chat history.

        Args:
            event: The event to add.
        """
        self.events.append(event)
        self.display_event(event)

    def display_event(self, event: Event) -> None:
        """Display an event in the chat panel.

        Args:
            event: The event to display.
        """
        # Create formatted message based on event type
        text = Text()

        # Timestamp
        time_str = event.timestamp.strftime("%H:%M:%S")
        text.append(f"[{time_str}] ", style="dim")

        # Event type icon
        event_icons = {
            "game_started": "🎮",
            "game_ended": "🏁",
            "phase_changed": "⏰",
            "player_died": "💀",
            "werewolf_killed": "🐺",
            "witch_saved": "💊",
            "witch_poisoned": "☠️",
            "vote_cast": "🗳️",
            "vote_result": "📊",
            "player_eliminated": "❌",
            "player_speech": "💬",
            "player_discussion": "🗨️",
            "message": "📢",
            "error": "⚠️",
        }
        icon = event_icons.get(event.event_type.value, "i")
        text.append(f"{icon} ", style="bold")

        # Message content with color based on event type
        message_styles = {
            "game_started": "bold green",
            "game_ended": "bold red",
            "phase_changed": "bold cyan",
            "player_died": "red",
            "werewolf_killed": "red",
            "witch_saved": "green",
            "vote_cast": "yellow",
            "vote_result": "bold yellow",
            "player_eliminated": "bold red",
            "player_speech": "cyan",
            "player_discussion": "blue",
            "error": "bold red",
        }
        style = message_styles.get(event.event_type.value, "white")
        text.append(event.message, style=style)

        self.write(text)

    def add_system_message(self, message: str) -> None:
        """Add a system message to the chat.

        Args:
            message: The message to add.
        """
        text = Text()
        text.append("i  ", style="bold cyan")
        text.append(message, style="italic cyan")
        self.write(text)

    def add_player_message(self, player_name: str, message: str) -> None:
        """Add a player message to the chat.

        Args:
            player_name: Name of the player.
            message: The message content.
        """
        text = Text()
        text.append(f"{player_name}: ", style="bold")
        text.append(message)
        self.write(text)

    def clear_history(self) -> None:
        """Clear the chat history."""
        self.events.clear()
        self.clear()
