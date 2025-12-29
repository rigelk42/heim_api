"""Interface layer for the Motor Vehicle Services bounded context.

The interface layer handles external communication:
- REST API views
- URL routing
- Django Admin integration
"""

from .views import (
    MotorVehicleDetailView,
    MotorVehicleListCreateView,
)

__all__ = [
    "MotorVehicleListCreateView",
    "MotorVehicleDetailView",
]
