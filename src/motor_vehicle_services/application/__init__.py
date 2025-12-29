"""Application layer for the Motor Vehicle Services bounded context.

The application layer orchestrates the domain layer and infrastructure.
It implements the CQRS pattern with separate command and query handlers.

Commands represent intentions to change state.
Queries represent requests for data without side effects.
"""

from .commands import (
    CreateMotorVehicleCommand,
    CreateTransactionCommand,
    DeleteMotorVehicleCommand,
    DeleteTransactionCommand,
    MotorVehicleCommandHandler,
    TransactionCommandHandler,
    TransferOwnershipCommand,
    UpdateMotorVehicleCommand,
    UpdateTransactionCommand,
)
from .queries import (
    GetMotorVehicleQuery,
    GetTransactionQuery,
    ListMotorVehiclesByOwnerQuery,
    ListMotorVehiclesQuery,
    ListTransactionsByCustomerQuery,
    ListTransactionsByVehicleQuery,
    ListTransactionsQuery,
    MotorVehicleQueryHandler,
    SearchMotorVehiclesQuery,
    TransactionQueryHandler,
)

__all__ = [
    # Motor Vehicle Commands
    "CreateMotorVehicleCommand",
    "UpdateMotorVehicleCommand",
    "DeleteMotorVehicleCommand",
    "TransferOwnershipCommand",
    "MotorVehicleCommandHandler",
    # Motor Vehicle Queries
    "GetMotorVehicleQuery",
    "ListMotorVehiclesQuery",
    "ListMotorVehiclesByOwnerQuery",
    "SearchMotorVehiclesQuery",
    "MotorVehicleQueryHandler",
    # Transaction Commands
    "CreateTransactionCommand",
    "UpdateTransactionCommand",
    "DeleteTransactionCommand",
    "TransactionCommandHandler",
    # Transaction Queries
    "GetTransactionQuery",
    "ListTransactionsQuery",
    "ListTransactionsByCustomerQuery",
    "ListTransactionsByVehicleQuery",
    "TransactionQueryHandler",
]
