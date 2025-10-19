from typing import Any

from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from textual.widgets import Static

from llm_werewolf.core.game_state import GameState


class GamePanel(Static):
    """Widget displaying the current game status."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize the game panel."""
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

        # Phase icon
        phase_icons = {
            "setup": "⚙️",
            "night": "🌙",
            "day_discussion": "☀️",
            "day_voting": "🗳️",
            "ended": "🏁",
        }
        phase_icon = phase_icons.get(self.game_state.phase.value, "❓")

        # Create main info text
        title = Text()
        title.append(f"{phase_icon} ", style="bold")
        title.append(f"Round {self.game_state.round_number}", style="bold yellow")
        title.append(" - ")
        title.append(self.game_state.phase.value.replace("_", " ").title(), style="bold cyan")

        # Create statistics table
        stats_table = Table(show_header=False, box=None, padding=(0, 1))
        stats_table.add_column("Label", style="dim")
        stats_table.add_column("Value", style="bold")

        alive_players = len(self.game_state.get_alive_players())
        total_players = len(self.game_state.players)
        werewolves = self.game_state.count_alive_by_camp("werewolf")
        villagers = self.game_state.count_alive_by_camp("villager")

        stats_table.add_row("Total Players:", f"{alive_players}/{total_players}")
        stats_table.add_row(
            "Werewolves:", f"[red]{werewolves}[/red]" if werewolves > 0 else "[dim]0[/dim]"
        )
        stats_table.add_row(
            "Villagers:", f"[green]{villagers}[/green]" if villagers > 0 else "[dim]0[/dim]"
        )

        # Render stats table to string
        from io import StringIO

        from rich.console import Console

        console = Console(file=StringIO(), width=40)
        console.print(stats_table)
        stats_content = console.file.getvalue()

        # Vote counts (if in voting phase)
        vote_content = ""
        if self.game_state.phase.value == "day_voting":
            vote_counts = self.game_state.get_vote_counts()
            if vote_counts:
                vote_table = Table(
                    title="Vote Counts", show_header=True, header_style="bold magenta"
                )
                vote_table.add_column("Player", style="cyan")
                vote_table.add_column("Votes", style="yellow", justify="right")

                for player_id, count in sorted(
                    vote_counts.items(), key=lambda x: x[1], reverse=True
                ):
                    player = self.game_state.get_player(player_id)
                    if player:
                        vote_table.add_row(player.name, str(count))

                console = Console(file=StringIO(), width=40)
                console.print(vote_table)
                vote_content = console.file.getvalue()

        # Combine all content
        content = Text.assemble(title, "\n\n")
        content.append(stats_content)

        if vote_content:
            content.append("\n")
            content.append(vote_content)

        panel = Panel(content, title="Game Status", border_style="cyan")
        self.update(panel)

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.refresh_display()
