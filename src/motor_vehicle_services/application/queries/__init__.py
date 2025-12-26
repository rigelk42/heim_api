"""Query module for the Motor Vehicle Services application layer.

Queries represent requests for data without side effects.
This module exports query DTOs and their handlers.
"""

from .dtos import (GetMotorVehicleByVINQuery, GetMotorVehicleQuery,
                   ListMotorVehiclesByOwnerQuery, ListMotorVehiclesByStatusQuery,
                   ListMotorVehiclesQuery, SearchMotorVehiclesQuery)
from .handlers import MotorVehicleQueryHandler

__all__ = [
    "GetMotorVehicleQuery",
    "GetMotorVehicleByVINQuery",
    "ListMotorVehiclesQuery",
    "ListMotorVehiclesByStatusQuery",
    "ListMotorVehiclesByOwnerQuery",
    "SearchMotorVehiclesQuery",
    "MotorVehicleQueryHandler",
]
