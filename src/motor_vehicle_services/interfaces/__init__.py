"""Interface layer for the Motor Vehicle Services bounded context.

The interface layer handles external communication:
- REST API views
- URL routing
- Django Admin integration
"""

from .views import (
    MotorVehicleByVINView,
    MotorVehicleDetailView,
    MotorVehicleListCreateView,
    MotorVehicleMileageView,
    MotorVehicleStatusView,
)

__all__ = [
    "MotorVehicleListCreateView",
    "MotorVehicleDetailView",
    "MotorVehicleByVINView",
    "MotorVehicleMileageView",
    "MotorVehicleStatusView",
]
