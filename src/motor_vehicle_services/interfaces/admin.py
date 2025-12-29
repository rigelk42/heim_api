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
        "created_at",
    ]
    list_filter = ["make", "year"]
    search_fields = ["vin", "make", "model", "license_plate"]
    ordering = ["-year", "make", "model"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Identification", {"fields": ("vin", "license_plate", "license_plate_state")}),
        ("Vehicle Details", {"fields": ("make", "model", "year")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_id",
        "customer",
        "vehicle",
        "transaction_type",
        "transaction_date",
        "transaction_amount",
        "created_at",
    ]
    list_filter = ["transaction_type", "transaction_date"]
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
        (
            "Transaction Details",
            {"fields": ("customer", "vehicle", "transaction_type")},
        ),
        ("Financial", {"fields": ("transaction_date", "transaction_amount")}),
        (
            "Fees",
            {
                "fields": (
                    "bz_partner_fee",
                    "broker_fee",
                    "service_fee",
                    "dmv_fee",
                    "discount",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
