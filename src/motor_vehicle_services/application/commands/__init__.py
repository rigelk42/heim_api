"""Command module for the Motor Vehicle Services application layer.

Commands represent intentions to change state in the system.
This module exports command DTOs and their handlers.
"""

from .dtos import (ChangeMotorVehicleStatusCommand, CreateMotorVehicleCommand,
                   DeleteMotorVehicleCommand, UpdateMotorVehicleCommand,
                   UpdateMotorVehicleMileageCommand)
from .handlers import MotorVehicleCommandHandler

__all__ = [
    "CreateMotorVehicleCommand",
    "UpdateMotorVehicleCommand",
    "UpdateMotorVehicleMileageCommand",
    "ChangeMotorVehicleStatusCommand",
    "DeleteMotorVehicleCommand",
    "MotorVehicleCommandHandler",
]
