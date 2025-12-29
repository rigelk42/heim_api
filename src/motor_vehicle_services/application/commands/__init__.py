"""Command module for the Motor Vehicle Services application layer.

Commands represent intentions to change state in the system.
This module exports command DTOs and their handlers.
"""

from .dtos import (
    CreateMotorVehicleCommand,
    CreateTransactionCommand,
    DeleteMotorVehicleCommand,
    DeleteTransactionCommand,
    TransferOwnershipCommand,
    UpdateMotorVehicleCommand,
    UpdateTransactionCommand,
)
from .handlers import MotorVehicleCommandHandler, TransactionCommandHandler

__all__ = [
    "CreateMotorVehicleCommand",
    "UpdateMotorVehicleCommand",
    "DeleteMotorVehicleCommand",
    "TransferOwnershipCommand",
    "MotorVehicleCommandHandler",
    "CreateTransactionCommand",
    "UpdateTransactionCommand",
    "DeleteTransactionCommand",
    "TransactionCommandHandler",
]
