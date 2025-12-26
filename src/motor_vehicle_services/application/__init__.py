"""Application layer for the Motor Vehicle Services bounded context.

The application layer orchestrates the domain layer and infrastructure.
It implements the CQRS pattern with separate command and query handlers.

Commands represent intentions to change state.
Queries represent requests for data without side effects.
"""

from .commands import (ChangeMotorVehicleStatusCommand, CreateMotorVehicleCommand,
                       DeleteMotorVehicleCommand, MotorVehicleCommandHandler,
                       UpdateMotorVehicleCommand, UpdateMotorVehicleMileageCommand)
from .queries import (GetMotorVehicleByVINQuery, GetMotorVehicleQuery,
                      ListMotorVehiclesByStatusQuery, ListMotorVehiclesQuery,
                      MotorVehicleQueryHandler, SearchMotorVehiclesQuery)

__all__ = [
    # Commands
    "CreateMotorVehicleCommand",
    "UpdateMotorVehicleCommand",
    "UpdateMotorVehicleMileageCommand",
    "ChangeMotorVehicleStatusCommand",
    "DeleteMotorVehicleCommand",
    "MotorVehicleCommandHandler",
    # Queries
    "GetMotorVehicleQuery",
    "GetMotorVehicleByVINQuery",
    "ListMotorVehiclesQuery",
    "ListMotorVehiclesByStatusQuery",
    "SearchMotorVehiclesQuery",
    "MotorVehicleQueryHandler",
]
