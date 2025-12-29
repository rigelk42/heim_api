"""URL routing for the Motor Vehicle Services bounded context."""

from django.urls import path

from . import views

app_name = "motor_vehicle_services"

urlpatterns = [
    # Motor Vehicle endpoints
    path("", views.MotorVehicleListCreateView.as_view(), name="list-create"),
    path("<str:vin>/", views.MotorVehicleDetailView.as_view(), name="detail"),
    path(
        "<str:vin>/owner/",
        views.MotorVehicleOwnerView.as_view(),
        name="owner",
    ),
    path(
        "owner/<str:owner_id>/",
        views.MotorVehiclesByOwnerView.as_view(),
        name="by-owner",
    ),
    # Transaction endpoints
    path(
        "transactions/",
        views.TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "transactions/<uuid:transaction_id>/",
        views.TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path(
        "transactions/customer/<str:customer_id>/",
        views.TransactionsByCustomerView.as_view(),
        name="transactions-by-customer",
    ),
    path(
        "transactions/vehicle/<str:vin>/",
        views.TransactionsByVehicleView.as_view(),
        name="transactions-by-vehicle",
    ),
]
