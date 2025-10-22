"""Tests for core/events.py module."""

from llm_werewolf.core.types import Event, EventType
from llm_werewolf.core.events import EventLogger


class TestEventLogger:
    """Tests for EventLogger class."""

    def test_initialization(self) -> None:
        """Test EventLogger initialization."""
        logger = EventLogger()
        assert logger.events == []
        assert logger.get_event_count() == 0

    def test_log_event(self) -> None:
        """Test logging a single event."""
        logger = EventLogger()
        event = Event(
            event_type=EventType.GAME_STARTED,
            round_number=1,
            phase="setup",
            message="Game started",
        )

        logger.log_event(event)

        assert len(logger.events) == 1
        assert logger.events[0] == event
        assert logger.get_event_count() == 1

    def test_create_event(self) -> None:
        """Test creating and logging an event."""
        logger = EventLogger()

        event = logger.create_event(
            event_type=EventType.GAME_STARTED,
            round_number=1,
            phase="setup",
            message="Game started with 6 players",
        )

        assert event is not None
        assert event.event_type == EventType.GAME_STARTED
        assert event.round_number == 1
        assert event.phase == "setup"
        assert event.message == "Game started with 6 players"
        assert len(logger.events) == 1
        assert logger.get_event_count() == 1

    def test_create_event_with_data(self) -> None:
        """Test creating an event with additional data."""
        logger = EventLogger()

        event = logger.create_event(
            event_type=EventType.PLAYER_DIED,
            round_number=2,
            phase="night",
            message="Alice died",
            data={"player_id": "p1", "cause": "werewolf"},
        )

        assert event.data == {"player_id": "p1", "cause": "werewolf"}
        assert logger.get_event_count() == 1

    def test_create_event_with_visibility(self) -> None:
        """Test creating an event with visibility restrictions."""
        logger = EventLogger()

        event = logger.create_event(
            event_type=EventType.PLAYER_SPEECH,
            round_number=2,
            phase="night",
            message="Werewolves discuss",
            visible_to=["p1", "p2"],
        )

        assert event.visible_to == ["p1", "p2"]
        assert logger.get_event_count() == 1

    def test_get_events_for_player_public(self) -> None:
        """Test getting public events for a player."""
        logger = EventLogger()

        # Public event (no visibility restriction)
        logger.create_event(
            event_type=EventType.GAME_STARTED,
            round_number=1,
            phase="setup",
            message="Game started",
        )

        events = logger.get_events_for_player("p1")
        assert len(events) == 1

    def test_get_events_for_player_private(self) -> None:
        """Test getting private events for a player."""
        logger = EventLogger()

        # Private event (visible only to p1 and p2)
        logger.create_event(
            event_type=EventType.PLAYER_SPEECH,
            round_number=1,
            phase="night",
            message="Werewolf discussion",
            visible_to=["p1", "p2"],
        )

        # p1 should see it
        events_p1 = logger.get_events_for_player("p1")
        assert len(events_p1) == 1

        # p3 should not see it
        events_p3 = logger.get_events_for_player("p3")
        assert len(events_p3) == 0

    def test_get_events_for_player_since_round(self) -> None:
        """Test getting events for a player since a specific round."""
        logger = EventLogger()

        logger.create_event(
            event_type=EventType.GAME_STARTED, round_number=1, phase="setup", message="Round 1"
        )
        logger.create_event(
            event_type=EventType.PHASE_CHANGED, round_number=2, phase="night", message="Round 2"
        )
        logger.create_event(
            event_type=EventType.PHASE_CHANGED, round_number=3, phase="day", message="Round 3"
        )

        # Get events from round 2 onward
        events = logger.get_events_for_player("p1", since_round=2)
        assert len(events) == 2
        assert events[0].round_number == 2
        assert events[1].round_number == 3

    def test_get_recent_events(self) -> None:
        """Test getting recent events."""
        logger = EventLogger()

        # Add 5 events
        for i in range(5):
            logger.create_event(
                event_type=EventType.PLAYER_DISCUSSION,
                round_number=1,
                phase="day",
                message=f"Message {i}",
            )

        # Get last 3 events
        recent = logger.get_recent_events(count=3)
        assert len(recent) == 3
        assert recent[0].message == "Message 2"
        assert recent[1].message == "Message 3"
        assert recent[2].message == "Message 4"

    def test_get_recent_events_more_than_available(self) -> None:
        """Test getting more recent events than available."""
        logger = EventLogger()

        # Add 3 events
        for i in range(3):
            logger.create_event(
                event_type=EventType.PLAYER_DISCUSSION,
                round_number=1,
                phase="day",
                message=f"Message {i}",
            )

        # Request 10 events, should return all 3
        recent = logger.get_recent_events(count=10)
        assert len(recent) == 3

    def test_get_events_by_type(self) -> None:
        """Test getting events by type."""
        logger = EventLogger()

        logger.create_event(
            event_type=EventType.PLAYER_DIED, round_number=1, phase="night", message="Death 1"
        )
        logger.create_event(
            event_type=EventType.PLAYER_DISCUSSION,
            round_number=1,
            phase="day",
            message="Discussion",
        )
        logger.create_event(
            event_type=EventType.PLAYER_DIED, round_number=2, phase="night", message="Death 2"
        )

        # Get all death events
        death_events = logger.get_events_by_type(EventType.PLAYER_DIED)
        assert len(death_events) == 2
        assert death_events[0].message == "Death 1"
        assert death_events[1].message == "Death 2"

    def test_get_events_by_type_with_round(self) -> None:
        """Test getting events by type and round."""
        logger = EventLogger()

        logger.create_event(
            event_type=EventType.PLAYER_DIED, round_number=1, phase="night", message="Death R1"
        )
        logger.create_event(
            event_type=EventType.PLAYER_DIED, round_number=2, phase="night", message="Death R2"
        )
        logger.create_event(
            event_type=EventType.PLAYER_DISCUSSION,
            round_number=1,
            phase="day",
            message="Discussion",
        )

        # Get death events from round 1 only
        death_events_r1 = logger.get_events_by_type(EventType.PLAYER_DIED, round_number=1)
        assert len(death_events_r1) == 1
        assert death_events_r1[0].message == "Death R1"

    def test_clear_events(self) -> None:
        """Test clearing all events."""
        logger = EventLogger()

        # Add some events
        for i in range(5):
            logger.create_event(
                event_type=EventType.PLAYER_DISCUSSION,
                round_number=1,
                phase="day",
                message=f"Message {i}",
            )

        assert logger.get_event_count() == 5

        # Clear events
        logger.clear_events()

        assert logger.get_event_count() == 0
        assert len(logger.events) == 0

    def test_get_event_count(self) -> None:
        """Test getting event count."""
        logger = EventLogger()

        assert logger.get_event_count() == 0

        logger.create_event(
            event_type=EventType.GAME_STARTED, round_number=1, phase="setup", message="Start"
        )
        assert logger.get_event_count() == 1

        logger.create_event(
            event_type=EventType.PHASE_CHANGED, round_number=1, phase="night", message="Night"
        )
        assert logger.get_event_count() == 2

    def test_multiple_operations(self) -> None:
        """Test multiple operations in sequence."""
        logger = EventLogger()

        # Create events
        for i in range(10):
            logger.create_event(
                event_type=EventType.PLAYER_DISCUSSION if i % 2 == 0 else EventType.PLAYER_DIED,
                round_number=i // 3 + 1,
                phase="day" if i % 2 == 0 else "night",
                message=f"Event {i}",
            )

        # Test event count
        assert logger.get_event_count() == 10

        # Test filtering by type
        discussions = logger.get_events_by_type(EventType.PLAYER_DISCUSSION)
        assert len(discussions) == 5

        deaths = logger.get_events_by_type(EventType.PLAYER_DIED)
        assert len(deaths) == 5

        # Test filtering by round
        round_1_events = logger.get_events_for_player("p1", since_round=2)
        assert all(e.round_number >= 2 for e in round_1_events)

        # Test recent events
        recent = logger.get_recent_events(count=5)
        assert len(recent) == 5
        assert recent[-1].message == "Event 9"
