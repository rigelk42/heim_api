"""Re-export domain models for Django compatibility.

This module re-exports models from the domain layer to maintain
Django's expected app structure.
"""

from motor_vehicle_services.domain.models import MotorVehicle

__all__ = ["MotorVehicle"]
