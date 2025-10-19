from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.containers import Vertical, Horizontal

from llm_werewolf.core.events import Event
from llm_werewolf.ui.components import ChatPanel, GamePanel, DebugPanel, PlayerPanel
from llm_werewolf.core.game_engine import GameEngine


class WerewolfTUI(App):
    """Textual TUI application for the Werewolf game."""

    CSS = """
    Screen {
        background: $surface;
    }

    #left_panel {
        width: 30%;
        height: 100%;
    }

    #middle_panel {
        width: 45%;
        height: 100%;
    }

    #right_panel {
        width: 25%;
        height: 100%;
    }

    PlayerPanel {
        height: 100%;
        border: solid $primary;
        background: $panel;
    }

    GamePanel {
        height: 50%;
        border: solid $secondary;
        background: $panel;
    }

    ChatPanel {
        height: 50%;
        border: solid $success;
        background: $panel;
    }

    DebugPanel {
        height: 100%;
        border: solid $accent;
        background: $panel;
    }
    """

    BINDINGS: ClassVar = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("d", "toggle_debug", "Toggle Debug"),
        ("n", "next_step", "Next Step"),
    ]

    def __init__(self, game_engine: GameEngine | None = None, show_debug: bool = True) -> None:
        """Initialize the TUI application.

        Args:
            game_engine: The game engine to display.
            show_debug: Whether to show the debug panel.
        """
        super().__init__()
        self.game_engine = game_engine
        self.show_debug_flag = show_debug

        # Component references
        self.player_panel: PlayerPanel | None = None
        self.game_panel: GamePanel | None = None
        self.chat_panel: ChatPanel | None = None
        self.debug_panel: DebugPanel | None = None

    def compose(self) -> ComposeResult:
        """Compose the TUI layout.

        Yields:
            Textual widgets for the UI.
        """
        yield Header(show_clock=True)

        with Horizontal():
            # Left panel: Players
            with Vertical(id="left_panel"):
                self.player_panel = PlayerPanel()
                yield self.player_panel

            # Middle panel: Game status (top) and Chat (bottom)
            with Vertical(id="middle_panel"):
                self.game_panel = GamePanel()
                yield self.game_panel

                self.chat_panel = ChatPanel()
                yield self.chat_panel

            # Right panel: Debug info
            if self.show_debug_flag:
                with Vertical(id="right_panel"):
                    self.debug_panel = DebugPanel()
                    yield self.debug_panel

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.title = "🐺 Werewolf Game"
        self.sub_title = "AI-Powered Werewolf"

        # Initialize with game engine if provided
        if self.game_engine and self.game_engine.game_state:
            self.update_game_state()

            # Set up event callback
            self.game_engine.on_event = self.on_game_event

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
        # Add event to chat panel
        if self.chat_panel:
            self.chat_panel.add_event(event)

        # Update all panels
        self.update_game_state()

    def action_toggle_debug(self) -> None:
        """Toggle the debug panel visibility."""
        if self.debug_panel:
            self.debug_panel.visible = not self.debug_panel.visible

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
        """Add an error to the debug panel.

        Args:
            error: The error message.
        """
        if self.debug_panel:
            self.debug_panel.add_error(error)
        if self.chat_panel:
            self.chat_panel.add_system_message(f"ERROR: {error}")


def run_tui(game_engine: GameEngine, show_debug: bool = True) -> None:
    """Run the TUI application.

    Args:
        game_engine: The game engine to display.
        show_debug: Whether to show the debug panel.
    """
    app = WerewolfTUI(game_engine=game_engine, show_debug=show_debug)
    app.run()
