"""Re-export admin configuration for Django compatibility.

This module re-exports admin configuration from the interfaces layer
to maintain Django's expected app structure.
"""

from motor_vehicle_services.interfaces.admin import MotorVehicleAdmin, TransactionAdmin

__all__ = ["MotorVehicleAdmin", "TransactionAdmin"]
