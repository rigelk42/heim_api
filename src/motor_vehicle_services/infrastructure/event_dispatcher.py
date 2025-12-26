"""Event dispatcher for publishing domain events.

The event dispatcher allows handlers to subscribe to domain events
and be notified when those events occur.
"""

from collections import defaultdict
from typing import Callable

from motor_vehicle_services.domain.events import DomainEvent

EventHandler = Callable[[DomainEvent], None]


class EventDispatcher:
    """Dispatches domain events to registered handlers.

    This is a simple in-memory event dispatcher. In a production system,
    you might want to use a message queue or event bus.

    Example:
        dispatcher = EventDispatcher()
        dispatcher.subscribe(SomeEvent, handle_some_event)
        dispatcher.publish(SomeEvent(...))
    """

    _instance: "EventDispatcher | None" = None
    _handlers: dict[type[DomainEvent], list[EventHandler]]

    def __new__(cls) -> "EventDispatcher":
        """Singleton pattern to ensure one dispatcher instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = defaultdict(list)
        return cls._instance

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to.
            handler: The function to call when the event occurs.
        """
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type.

        Args:
            event_type: The type of event to unsubscribe from.
            handler: The handler function to remove.
        """
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribed handlers.

        Args:
            event: The domain event to publish.
        """
        for handler in self._handlers[type(event)]:
            handler(event)

    def clear(self) -> None:
        """Clear all registered handlers.

        Useful for testing.
        """
        self._handlers.clear()

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance.

        Useful for testing.
        """
        cls._instance = None
