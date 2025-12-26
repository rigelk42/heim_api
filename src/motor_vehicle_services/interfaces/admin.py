"""Django Admin configuration for the Motor Vehicle Services bounded context."""

from django.contrib import admin

from motor_vehicle_services.domain.models import MotorVehicle


@admin.register(MotorVehicle)
class MotorVehicleAdmin(admin.ModelAdmin):
    list_display = [
        "vin",
        "make",
        "model",
        "year",
        "color",
        "license_plate",
        "status",
        "mileage_km",
        "created_at",
    ]
    list_filter = ["status", "fuel_type", "transmission", "make", "year"]
    search_fields = ["vin", "make", "model", "license_plate"]
    ordering = ["-year", "make", "model"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Identification", {"fields": ("vin", "license_plate", "license_plate_state")}),
        ("Vehicle Details", {"fields": ("make", "model", "year", "color")}),
        (
            "Specifications",
            {"fields": ("fuel_type", "transmission", "engine_capacity_cc")},
        ),
        ("Status", {"fields": ("status", "mileage_km")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
