from typing import Any

from rich.text import Text
from textual.widgets import RichLog

from llm_werewolf.core.events import Event
from llm_werewolf.core.event_formatter import EventFormatter


class ChatPanel(RichLog):
    """Widget displaying the game chat/event history."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize the chat panel."""
        super().__init__(*args, **kwargs)
        self.events: list[Event] = []
        self._streaming_line_count: int = 0

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
        # Use the centralized event formatter
        text = EventFormatter.format_event(event, include_timestamp=True)
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

    def start_streaming_message(self, player_name: str, prefix: str = "") -> None:
        """Start a streaming message display.

        Args:
            player_name: Name of the player speaking.
            prefix: Optional prefix to display before the streaming content.
        """
        import datetime

        text = Text()
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        text.append(f"[{time_str}] ", style="dim")

        if prefix:
            text.append(prefix, style="cyan")
            text.append(" ")

        text.append(f"{player_name}: ", style="bold cyan")
        self.write(text)
        self._streaming_line_count = 1

    def update_streaming_message(self, chunk: str) -> None:
        """Update the current streaming message with a new chunk.

        Args:
            chunk: New text chunk to append.
        """
        # Remove the last line(s) added by streaming
        if self._streaming_line_count > 0:
            # RichLog doesn't have a direct way to remove lines, so we append chunks
            # We'll use a simpler approach: just append the chunk as plain text
            text = Text(chunk, style="cyan")
            self.write(text, scroll_end=True)

    def finish_streaming_message(self) -> None:
        """Finish the streaming message."""
        self._streaming_line_count = 0
