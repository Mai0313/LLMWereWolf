from typing import Any

from rich.table import Table
from textual.widgets import Static

from llm_werewolf.core.game_state import GameState


class PlayerPanel(Static):
    """Widget displaying the list of players and their status."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize the player panel."""
        super().__init__(*args, **kwargs)
        self.game_state: GameState | None = None

    def set_game_state(self, game_state: GameState) -> None:
        """Set the game state to display.

        Args:
            game_state: The current game state.
        """
        self.game_state = game_state
        self.refresh_display()

    def refresh_display(self) -> None:
        """Refresh the display with current game state."""
        if not self.game_state:
            self.update("No game in progress")
            return

        table = Table(title="Players", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Model", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Role", style="yellow")

        for player in self.game_state.players:
            # Determine status icon
            if player.is_alive():
                status_icon = "✓"
                status_style = "green"
            else:
                status_icon = "✗"
                status_style = "red"

            # Show role only if dead (or for debugging)
            role_display = player.get_role_name() if not player.is_alive() else "?"

            # Add special status indicators
            status_text = status_icon
            if player.has_status("protected"):
                status_text += " 🛡️"
            if player.has_status("poisoned"):
                status_text += " ☠️"
            if player.has_status("marked"):
                status_text += " 🔴"
            if player.has_status("lover"):
                status_text += " ❤️"

            table.add_row(
                player.name,
                player.ai_model,
                f"[{status_style}]{status_text}[/{status_style}]",
                role_display,
            )

        self.update(table)

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.refresh_display()
