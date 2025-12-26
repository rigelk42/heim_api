"""Domain models for the Motor Vehicle Services bounded context.

This module contains the Aggregate Roots and Entities for the domain.
Aggregate Roots are the main entry points for accessing and modifying
related entities. All modifications to entities within an aggregate
must go through the Aggregate Root.
"""

from __future__ import annotations

from django.db import models

from .value_objects import VIN, LicensePlate, Mileage


class MotorVehicle(models.Model):
    """Aggregate Root for the Motor Vehicle bounded context.

    Represents a motor vehicle with its identifying information,
    specifications, and current status.
    """

    id: int

    FUEL_TYPES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
        ("lpg", "LPG"),
    ]

    TRANSMISSION_TYPES = [
        ("manual", "Manual"),
        ("automatic", "Automatic"),
        ("cvt", "CVT"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("sold", "Sold"),
        ("scrapped", "Scrapped"),
        ("stolen", "Stolen"),
    ]

    # Owner relationship
    owner = models.ForeignKey(
        "customer_management.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
    )

    # Identification
    vin = models.CharField(max_length=17, unique=True)
    license_plate = models.CharField(max_length=16, blank=True)
    license_plate_state = models.CharField(max_length=32, blank=True)

    # Vehicle details
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=32, blank=True)

    # Specifications
    fuel_type = models.CharField(max_length=16, choices=FUEL_TYPES, default="petrol")
    transmission = models.CharField(
        max_length=16, choices=TRANSMISSION_TYPES, default="manual"
    )
    engine_capacity_cc = models.PositiveIntegerField(null=True, blank=True)

    # Current state
    mileage_km = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "motor_vehicle_services"
        db_table = "motor_vehicles"
        ordering = ["-year", "make", "model"]

    # --- Value Object accessors ---

    def get_vin(self) -> VIN:
        """Return the VIN as a value object."""
        return VIN(value=self.vin)

    def set_vin(self, vin: VIN) -> None:
        """Set the VIN from a value object."""
        self.vin = vin.value

    def get_license_plate(self) -> LicensePlate | None:
        """Return the license plate as a value object."""
        if not self.license_plate:
            return None
        return LicensePlate(
            value=self.license_plate, state_province=self.license_plate_state
        )

    def set_license_plate(self, plate: LicensePlate | None) -> None:
        """Set the license plate from a value object."""
        if plate is None:
            self.license_plate = ""
            self.license_plate_state = ""
        else:
            self.license_plate = plate.value
            self.license_plate_state = plate.state_province

    def get_mileage(self) -> Mileage:
        """Return the mileage as a value object."""
        return Mileage(value=self.mileage_km, unit="km")

    def set_mileage(self, mileage: Mileage) -> None:
        """Set the mileage from a value object (converts to km)."""
        self.mileage_km = mileage.in_kilometers

    # --- Computed properties ---

    @property
    def full_name(self) -> str:
        """Return the full vehicle name (year make model)."""
        return f"{self.year} {self.make} {self.model}"

    @property
    def is_active(self) -> bool:
        """Check if the vehicle is currently active."""
        return self.status == "active"

    @property
    def owner_name(self) -> str | None:
        """Return the owner's full name if assigned."""
        if self.owner:
            return self.owner.full_name
        return None

    def __str__(self) -> str:
        return f"{self.full_name} ({self.vin})"

    # --- Domain operations ---

    def update_mileage(self, new_mileage: Mileage) -> None:
        """Update the vehicle's mileage.

        Args:
            new_mileage: The new mileage reading.

        Raises:
            ValueError: If the new mileage is less than the current mileage.
        """
        new_km = new_mileage.in_kilometers
        if new_km < self.mileage_km:
            raise ValueError(
                f"New mileage ({new_km} km) cannot be less than "
                f"current mileage ({self.mileage_km} km)"
            )
        self.mileage_km = new_km

    def mark_as_sold(self) -> None:
        """Mark the vehicle as sold."""
        self.status = "sold"

    def mark_as_scrapped(self) -> None:
        """Mark the vehicle as scrapped."""
        self.status = "scrapped"

    def mark_as_stolen(self) -> None:
        """Mark the vehicle as stolen."""
        self.status = "stolen"

    def reactivate(self) -> None:
        """Reactivate the vehicle (e.g., recovered from theft)."""
        self.status = "active"
