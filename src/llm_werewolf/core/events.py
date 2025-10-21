from llm_werewolf.core.types import Event, EventType


class EventLogger:
    """Logs and manages game events."""

    def __init__(self) -> None:
        """Initialize the event logger."""
        self.events: list[Event] = []

    def log_event(self, event: Event) -> None:
        """Log an event.

        Args:
            event: The event to log.
        """
        self.events.append(event)

    def create_event(
        self,
        event_type: EventType,
        round_number: int,
        phase: str,
        message: str,
        data: dict | None = None,
        visible_to: list[str] | None = None,
    ) -> Event:
        """Create and log a new event.

        Args:
            event_type: Type of the event.
            round_number: Current round number.
            phase: Current game phase.
            message: Event message.
            data: Additional event data.
            visible_to: List of player IDs who can see this event.

        Returns:
            Event: The created event.
        """
        event = Event(
            event_type=event_type,
            round_number=round_number,
            phase=phase,
            message=message,
            data=data or {},
            visible_to=visible_to,
        )
        self.log_event(event)
        return event

    def get_events_for_player(self, player_id: str, since_round: int | None = None) -> list[Event]:
        """Get all events visible to a specific player.

        Args:
            player_id: The player ID.
            since_round: Only return events from this round onward.

        Returns:
            list[Event]: List of visible events.
        """
        events = [e for e in self.events if e.is_visible_to(player_id)]

        if since_round is not None:
            events = [e for e in events if e.round_number >= since_round]

        return events

    def get_recent_events(self, count: int = 10) -> list[Event]:
        """Get the most recent events.

        Args:
            count: Number of events to retrieve.

        Returns:
            list[Event]: Recent events.
        """
        return self.events[-count:]

    def get_events_by_type(
        self, event_type: EventType, round_number: int | None = None
    ) -> list[Event]:
        """Get all events of a specific type.

        Args:
            event_type: The event type to filter by.
            round_number: Optionally filter by round number.

        Returns:
            list[Event]: List of matching events.
        """
        events = [e for e in self.events if e.event_type == event_type]

        if round_number is not None:
            events = [e for e in events if e.round_number == round_number]

        return events

    def clear_events(self) -> None:
        """Clear all events."""
        self.events.clear()

    def get_event_count(self) -> int:
        """Get the total number of events.

        Returns:
            int: Number of events logged.
        """
        return len(self.events)
