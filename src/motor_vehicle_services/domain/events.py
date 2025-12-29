"""Domain events for the Motor Vehicle Services bounded context.

Domain events represent something meaningful that happened in the domain.
They are immutable records of past occurrences that other parts of the
system can react to.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events.

    Attributes:
        event_id: Unique identifier for this event instance.
        occurred_at: Timestamp when the event occurred.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def event_type(self) -> str:
        """Return the event type name."""
        return self.__class__.__name__


@dataclass(frozen=True)
class MotorVehicleCreated(DomainEvent):
    """Event raised when a new motor vehicle is registered.

    Attributes:
        vin: The vehicle identification number.
        make: The vehicle manufacturer.
        model: The vehicle model.
        year: The model year.
    """

    vin: str = ""
    make: str = ""
    model: str = ""
    year: int = 0


@dataclass(frozen=True)
class MotorVehicleUpdated(DomainEvent):
    """Event raised when a motor vehicle's details are updated.

    Attributes:
        vin: The VIN of the updated vehicle.
        changes: Tuple of field names to new values.
    """

    vin: str = ""
    changes: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class MotorVehicleMileageUpdated(DomainEvent):
    """Event raised when a vehicle's mileage is updated.

    Attributes:
        vin: The VIN of the vehicle.
        old_mileage_km: The previous mileage in kilometers.
        new_mileage_km: The new mileage in kilometers.
    """

    vin: str = ""
    old_mileage_km: int = 0
    new_mileage_km: int = 0


@dataclass(frozen=True)
class MotorVehicleOwnerChanged(DomainEvent):
    """Event raised when a vehicle's owner changes.

    Attributes:
        vin: The VIN of the vehicle.
        old_owner_id: The ID of the previous owner (None if unassigned).
        new_owner_id: The ID of the new owner (None if unassigned).
    """

    vin: str = ""
    old_owner_id: str | None = None
    new_owner_id: str | None = None


@dataclass(frozen=True)
class MotorVehicleDeleted(DomainEvent):
    """Event raised when a motor vehicle is deleted.

    Attributes:
        vin: The vehicle identification number.
    """

    vin: str = ""
