"""Django Admin configuration for the Motor Vehicle Services bounded context."""

from django.contrib import admin

from motor_vehicle_services.domain.models import MotorVehicle, Transaction


@admin.register(MotorVehicle)
class MotorVehicleAdmin(admin.ModelAdmin):
    list_display = [
        "vin",
        "make",
        "model",
        "year",
        "license_plate",
        "mileage_km",
        "created_at",
    ]
    list_filter = ["make", "year"]
    search_fields = ["vin", "make", "model", "license_plate"]
    ordering = ["-year", "make", "model"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Identification", {"fields": ("vin", "license_plate", "license_plate_state")}),
        ("Vehicle Details", {"fields": ("make", "model", "year")}),
        ("Mileage", {"fields": ("mileage_km",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer",
        "vehicle",
        "transaction_date",
        "transaction_amount",
        "created_at",
    ]
    list_filter = ["transaction_date"]
    search_fields = [
        "customer__first_name",
        "customer__last_name",
        "vehicle__vin",
        "vehicle__make",
        "vehicle__model",
    ]
    ordering = ["-transaction_date"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["customer", "vehicle"]

    fieldsets = (
        ("Transaction Details", {"fields": ("customer", "vehicle")}),
        ("Financial", {"fields": ("transaction_date", "transaction_amount")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
