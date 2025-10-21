import uuid
from typing import ClassVar
from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.containers import Vertical, Horizontal

from llm_werewolf.core.engine import GameEngine
from llm_werewolf.core.events import Event
from llm_werewolf.ui.components import ChatPanel, GamePanel, PlayerPanel


class WerewolfTUI(App):
    """Textual TUI application for the Werewolf game."""

    CSS = """
    Screen {
        background: $surface;
    }

    #top_container {
        height: 35%;
        width: 100%;
    }

    #bottom_container {
        height: 65%;
        width: 100%;
    }

    #player_section {
        width: 66%;
        height: 100%;
    }

    #game_section {
        width: 34%;
        height: 100%;
    }

    PlayerPanel {
        height: 100%;
        border: solid $primary;
        background: $panel;
    }

    GamePanel {
        height: 100%;
        border: solid $secondary;
        background: $panel;
    }

    ChatPanel {
        height: 100%;
        border: solid $success;
        background: $panel;
    }
    """

    BINDINGS: ClassVar = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("n", "next_step", "Next Step"),
    ]

    def __init__(self, game_engine: GameEngine | None = None) -> None:
        """Initialize the TUI application.

        Args:
            game_engine: The game engine to display.
        """
        super().__init__()
        self.game_engine = game_engine
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()

        self.player_panel: PlayerPanel | None = None
        self.game_panel: GamePanel | None = None
        self.chat_panel: ChatPanel | None = None

    def compose(self) -> ComposeResult:
        """Compose the TUI layout.

        Layout:
        - Top (35%): Players (left 2/3) | Game Status (right 1/3)
        - Bottom (65%): Chat/Terminal Output (full width)

        Yields:
            Textual widgets for the UI.
        """
        yield Header(show_clock=True)

        # Top container: Players and Game Status side by side
        with Horizontal(id="top_container"):
            with Vertical(id="player_section"):
                self.player_panel = PlayerPanel()
                yield self.player_panel

            with Vertical(id="game_section"):
                self.game_panel = GamePanel()
                yield self.game_panel

        # Bottom container: Chat/Terminal output
        with Vertical(id="bottom_container"):
            self.chat_panel = ChatPanel()
            yield self.chat_panel

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.title = "🐺 Werewolf Game"
        self.sub_title = f"AI-Powered Werewolf | Session: {self.session_id}"

        if self.game_engine and self.game_engine.game_state:
            self.update_game_state()

            self.game_engine.on_event = self.on_game_event

        # Update footer with uptime every second
        self.set_interval(1.0, self.update_footer)

    def update_footer(self) -> None:
        """Update the footer with current uptime."""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.sub_title = f"AI-Powered Werewolf | Session: {self.session_id} | Uptime: {uptime_str}"

    def update_game_state(self) -> None:
        """Update all panels with current game state."""
        if not self.game_engine or not self.game_engine.game_state:
            return

        if self.player_panel:
            self.player_panel.set_game_state(self.game_engine.game_state)

        if self.game_panel:
            self.game_panel.set_game_state(self.game_engine.game_state)

    def on_game_event(self, event: Event) -> None:
        """Handle a game event.

        Args:
            event: The game event.
        """
        if self.chat_panel:
            self.chat_panel.add_event(event)

        self.update_game_state()

    def action_next_step(self) -> None:
        """Advance the game by one step."""
        if self.game_engine:
            messages = self.game_engine.step()
            for msg in messages:
                self.add_system_message(msg)
            self.update_game_state()

    def add_system_message(self, message: str) -> None:
        """Add a system message to the chat.

        Args:
            message: The message to add.
        """
        if self.chat_panel:
            self.chat_panel.add_system_message(message)

    def add_error(self, error: str) -> None:
        """Add an error message to the chat.

        Args:
            error: The error message.
        """
        if self.chat_panel:
            self.chat_panel.add_system_message(f"ERROR: {error}")


def run_tui(game_engine: GameEngine) -> None:
    """Run the TUI application.

    Args:
        game_engine: The game engine to display.
    """
    app = WerewolfTUI(game_engine=game_engine)
    app.run()
