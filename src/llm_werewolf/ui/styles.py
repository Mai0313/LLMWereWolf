from rich.style import Style

# Color scheme for different camps
CAMP_COLORS = {"werewolf": "red", "villager": "green", "neutral": "yellow"}

# Status colors
STATUS_COLORS = {
    "alive": "green",
    "dead": "grey50",
    "protected": "blue",
    "poisoned": "purple",
    "charmed": "magenta",
    "marked": "orange1",
}

# Phase colors
PHASE_COLORS = {
    "setup": "cyan",
    "night": "blue",
    "day_discussion": "yellow",
    "day_voting": "orange1",
    "ended": "red",
}

# Styles for Rich text
STYLE_WEREWOLF = Style(color="red", bold=True)
STYLE_VILLAGER = Style(color="green", bold=True)
STYLE_NEUTRAL = Style(color="yellow", bold=True)
STYLE_DEAD = Style(color="grey50", strike=True)
STYLE_SYSTEM = Style(color="cyan", italic=True)
STYLE_ERROR = Style(color="red", bold=True)
STYLE_SUCCESS = Style(color="green", bold=True)
STYLE_WARNING = Style(color="yellow")

# CSS for Textual components
TUI_CSS = """
Screen {
    background: $surface;
}

#player_panel {
    width: 25%;
    height: 100%;
    border: solid $primary;
    background: $panel;
}

#game_panel {
    width: 50%;
    height: 50%;
    border: solid $secondary;
    background: $panel;
}

#debug_panel {
    width: 25%;
    height: 100%;
    border: solid $accent;
    background: $panel;
}

#chat_panel {
    width: 50%;
    height: 50%;
    border: solid $success;
    background: $panel;
}

.panel_title {
    text-style: bold;
    background: $boost;
    color: $text;
    padding: 0 1;
}

.alive {
    color: $success;
}

.dead {
    color: $error;
    text-style: strike;
}

.werewolf {
    color: red;
    text-style: bold;
}

.villager {
    color: green;
    text-style: bold;
}

.neutral {
    color: yellow;
    text-style: bold;
}

.night {
    background: #1a1a2e;
    color: #ffffff;
}

.day {
    background: #f0f0f0;
    color: #000000;
}
"""


def get_camp_color(camp: str) -> str:
    """Get color for a camp.

    Args:
        camp: The camp name.

    Returns:
        str: The color name.
    """
    return CAMP_COLORS.get(camp, "white")


def get_status_color(status: str) -> str:
    """Get color for a status.

    Args:
        status: The status name.

    Returns:
        str: The color name.
    """
    return STATUS_COLORS.get(status, "white")


def get_phase_color(phase: str) -> str:
    """Get color for a game phase.

    Args:
        phase: The phase name.

    Returns:
        str: The color name.
    """
    return PHASE_COLORS.get(phase, "white")
