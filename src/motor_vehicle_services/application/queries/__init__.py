"""Query module for the Motor Vehicle Services application layer.

Queries represent requests for data without side effects.
This module exports query DTOs and their handlers.
"""

from .dtos import (
    GetMotorVehicleQuery,
    GetTransactionQuery,
    ListMotorVehiclesByOwnerQuery,
    ListMotorVehiclesQuery,
    ListTransactionsByCustomerQuery,
    ListTransactionsByVehicleQuery,
    ListTransactionsQuery,
    SearchMotorVehiclesQuery,
)
from .handlers import MotorVehicleQueryHandler, TransactionQueryHandler

__all__ = [
    "GetMotorVehicleQuery",
    "ListMotorVehiclesQuery",
    "ListMotorVehiclesByOwnerQuery",
    "SearchMotorVehiclesQuery",
    "MotorVehicleQueryHandler",
    "GetTransactionQuery",
    "ListTransactionsQuery",
    "ListTransactionsByCustomerQuery",
    "ListTransactionsByVehicleQuery",
    "TransactionQueryHandler",
]
