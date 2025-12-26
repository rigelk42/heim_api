"""Infrastructure layer for the Motor Vehicle Services bounded context.

The infrastructure layer provides implementations for external concerns:
- Repositories for data persistence
- Event dispatchers for publishing domain events
- External service integrations
"""

from .event_dispatcher import EventDispatcher
from .repositories import MotorVehicleRepository

__all__ = ["MotorVehicleRepository", "EventDispatcher"]
