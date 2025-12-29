"""Query module for the Motor Vehicle Services application layer.

Queries represent requests for data without side effects.
This module exports query DTOs and their handlers.
"""

from .dtos import (
    GetMotorVehicleByVINQuery,
    GetMotorVehicleQuery,
    GetTransactionQuery,
    ListMotorVehiclesByOwnerQuery,
    ListMotorVehiclesByStatusQuery,
    ListMotorVehiclesQuery,
    ListTransactionsByCustomerQuery,
    ListTransactionsByVehicleQuery,
    ListTransactionsQuery,
    SearchMotorVehiclesQuery,
)
from .handlers import MotorVehicleQueryHandler, TransactionQueryHandler

__all__ = [
    "GetMotorVehicleQuery",
    "GetMotorVehicleByVINQuery",
    "ListMotorVehiclesQuery",
    "ListMotorVehiclesByStatusQuery",
    "ListMotorVehiclesByOwnerQuery",
    "SearchMotorVehiclesQuery",
    "MotorVehicleQueryHandler",
    "GetTransactionQuery",
    "ListTransactionsQuery",
    "ListTransactionsByCustomerQuery",
    "ListTransactionsByVehicleQuery",
    "TransactionQueryHandler",
]
