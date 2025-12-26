"""URL routing for the Motor Vehicle Services bounded context."""

from django.urls import path

from . import views

app_name = "motor_vehicle_services"

urlpatterns = [
    path("", views.MotorVehicleListCreateView.as_view(), name="list-create"),
    path("<int:vehicle_id>/", views.MotorVehicleDetailView.as_view(), name="detail"),
    path(
        "<int:vehicle_id>/mileage/",
        views.MotorVehicleMileageView.as_view(),
        name="mileage",
    ),
    path(
        "<int:vehicle_id>/status/",
        views.MotorVehicleStatusView.as_view(),
        name="status",
    ),
    path(
        "<int:vehicle_id>/owner/",
        views.MotorVehicleOwnerView.as_view(),
        name="owner",
    ),
    path("vin/<str:vin>/", views.MotorVehicleByVINView.as_view(), name="by-vin"),
    path(
        "owner/<int:owner_id>/",
        views.MotorVehiclesByOwnerView.as_view(),
        name="by-owner",
    ),
]
