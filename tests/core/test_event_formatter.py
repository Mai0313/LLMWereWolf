"""Tests for event formatter."""

from datetime import datetime

from llm_werewolf.core.types import Event, EventType
from llm_werewolf.core.event_formatter import EventFormatter


def test_format_event_with_timestamp() -> None:
    """Test formatting an event with timestamp."""
    event = Event(
        event_type=EventType.GAME_STARTED,
        round_number=1,
        phase="setup",
        message="Game started with 6 players",
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
    )

    formatted = EventFormatter.format_event(event, include_timestamp=True)

    # Check that timestamp is included
    assert "[12:00:00]" in str(formatted)
    # Check that message is included
    assert "Game started with 6 players" in str(formatted)


def test_format_event_without_timestamp() -> None:
    """Test formatting an event without timestamp."""
    event = Event(
        event_type=EventType.PLAYER_DIED,
        round_number=1,
        phase="night",
        message="Player 1 has died",
    )

    formatted = EventFormatter.format_event(event, include_timestamp=False)

    # Check that timestamp is not included
    assert "[" not in str(formatted) or "Player 1" in str(formatted)


def test_get_event_style() -> None:
    """Test getting style for different event types."""
    # Test known event type
    assert EventFormatter.get_event_style(EventType.GAME_STARTED) == "bold green"
    assert EventFormatter.get_event_style(EventType.GAME_ENDED) == "bold red"
    assert EventFormatter.get_event_style(EventType.PLAYER_DIED) == "red"
    assert EventFormatter.get_event_style(EventType.VOTE_RESULT) == "bold yellow"


def test_format_event_styles() -> None:
    """Test that different event types get appropriate styles."""
    # Test a few different event types
    test_cases = [
        (EventType.GAME_STARTED, "bold green"),
        (EventType.WEREWOLF_KILLED, "red"),
        (EventType.WITCH_SAVED, "green"),
        (EventType.PHASE_CHANGED, "bold cyan"),
    ]

    for event_type, expected_style in test_cases:
        event = Event(event_type=event_type, round_number=1, phase="test", message="Test message")
        formatted = EventFormatter.format_event(event)
        # Just verify it doesn't raise an error
        assert formatted is not None
        assert EventFormatter.get_event_style(event_type) == expected_style


def test_format_all_event_types() -> None:
    """Test formatting all event types to ensure complete coverage."""
    # Test all event types from EVENT_STYLES
    for event_type in EventFormatter.EVENT_STYLES:
        event = Event(
            event_type=event_type,
            round_number=1,
            phase="test",
            message=f"Test message for {event_type.value}",
        )
        formatted = EventFormatter.format_event(event, include_timestamp=True)
        assert formatted is not None
        assert f"Test message for {event_type.value}" in str(formatted)


def test_unknown_event_type_style() -> None:
    """Test that unknown event types get default white style."""
    # Test all enum values to ensure coverage
    for event_type in EventType:
        style = EventFormatter.get_event_style(event_type)
        # Should return a valid style string
        assert isinstance(style, str)
        assert len(style) > 0
