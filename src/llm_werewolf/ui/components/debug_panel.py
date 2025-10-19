import uuid
from typing import Any
from datetime import datetime

from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from textual.widgets import Static

from llm_werewolf.config.game_config import GameConfig


class DebugPanel(Static):
    """Widget displaying debug and system information."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize the debug panel."""
        super().__init__(*args, **kwargs)
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
        self.config: GameConfig | None = None
        self.error_log: list[str] = []

    def set_config(self, config: GameConfig) -> None:
        """Set the game configuration.

        Args:
            config: The game configuration.
        """
        self.config = config
        self.refresh_display()

    def add_error(self, error: str) -> None:
        """Add an error to the log.

        Args:
            error: The error message.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.error_log.append(f"[{timestamp}] {error}")
        # Keep only last 10 errors
        if len(self.error_log) > 10:
            self.error_log.pop(0)
        self.refresh_display()

    def refresh_display(self) -> None:
        """Refresh the debug display."""
        # Session info
        session_table = Table(show_header=False, box=None, padding=(0, 1))
        session_table.add_column("Label", style="dim")
        session_table.add_column("Value", style="bold cyan")

        session_table.add_row("Session ID:", self.session_id)
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        session_table.add_row("Uptime:", uptime_str)

        # Config info
        config_content = Text()
        if self.config:
            config_content.append(f"Players: {self.config.num_players}\n")
            config_content.append(f"Night timeout: {self.config.night_timeout}s\n")
            config_content.append(f"Day timeout: {self.config.day_timeout}s\n")
            config_content.append(f"Vote timeout: {self.config.vote_timeout}s\n")
            config_content.append(f"Show roles: {self.config.show_role_on_death}\n")
        else:
            config_content.append("No config loaded", style="dim")

        # Error log
        error_content = Text()
        if self.error_log:
            for error in self.error_log[-5:]:  # Show last 5 errors
                error_content.append(f"{error}\n", style="red")
        else:
            error_content.append("No errors", style="dim green")

        # Combine all sections
        content = Text()
        content.append("Session Info\n", style="bold yellow")
        content.append(session_table)
        content.append("\n\n")
        content.append("Configuration\n", style="bold yellow")
        content.append(config_content)
        content.append("\n")
        content.append("Recent Errors\n", style="bold yellow")
        content.append(error_content)

        panel = Panel(content, title="Debug Info", border_style="yellow")
        self.update(panel)

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.refresh_display()

        # Set up periodic refresh
        self.set_interval(1.0, self.refresh_display)
