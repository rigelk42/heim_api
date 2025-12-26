"""Domain layer for the Motor Vehicle Services bounded context.

The domain layer contains the core business logic and rules.
It includes:
- Models (Aggregate Roots and Entities)
- Value Objects
- Domain Events
- Domain Exceptions
"""

from .events import (DomainEvent, MotorVehicleCreated, MotorVehicleDeleted,
                     MotorVehicleMileageUpdated, MotorVehicleStatusChanged,
                     MotorVehicleUpdated)
from .exceptions import (InvalidMileageUpdate, MotorVehicleAlreadyExists,
                         MotorVehicleNotFound, MotorVehicleServiceException)
from .models import MotorVehicle
from .value_objects import VIN, LicensePlate, Mileage

__all__ = [
    # Models
    "MotorVehicle",
    # Value Objects
    "VIN",
    "LicensePlate",
    "Mileage",
    # Events
    "DomainEvent",
    "MotorVehicleCreated",
    "MotorVehicleUpdated",
    "MotorVehicleMileageUpdated",
    "MotorVehicleStatusChanged",
    "MotorVehicleDeleted",
    # Exceptions
    "MotorVehicleServiceException",
    "MotorVehicleNotFound",
    "MotorVehicleAlreadyExists",
    "InvalidMileageUpdate",
]
