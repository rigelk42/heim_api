"""Re-export views for Django compatibility.

This module re-exports views from the interfaces layer to maintain
Django's expected app structure.
"""

from motor_vehicle_services.interfaces.views import (
    MotorVehicleByVINView, MotorVehicleDetailView, MotorVehicleListCreateView,
    MotorVehicleMileageView, MotorVehicleStatusView)

__all__ = [
    "MotorVehicleListCreateView",
    "MotorVehicleDetailView",
    "MotorVehicleByVINView",
    "MotorVehicleMileageView",
    "MotorVehicleStatusView",
]
