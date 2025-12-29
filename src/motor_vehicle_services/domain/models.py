"""Domain models for the Motor Vehicle Services bounded context.

This module contains the Aggregate Roots and Entities for the domain.
Aggregate Roots are the main entry points for accessing and modifying
related entities. All modifications to entities within an aggregate
must go through the Aggregate Root.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models

from .value_objects import VIN, LicensePlate


class MotorVehicle(models.Model):
    """Aggregate Root for the Motor Vehicle bounded context.

    Represents a motor vehicle with its identifying information.

    Attributes:
        owner: The customer who owns this vehicle (optional).
        vin: Vehicle Identification Number (17 characters, unique).
        license_plate: License plate number.
        license_plate_state: State/province that issued the license plate.
        make: Vehicle manufacturer (e.g., Honda, Toyota).
        model: Vehicle model name (e.g., Accord, Camry).
        year: Model year.
        created_at: Timestamp when the vehicle was registered.
        updated_at: Timestamp when the vehicle was last updated.
    """

    # Owner relationship
    owner = models.ForeignKey(
        "customer_management.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
    )

    # Identification (VIN is primary key)
    vin = models.CharField(max_length=17, primary_key=True)
    license_plate = models.CharField(max_length=16, blank=True)
    license_plate_state = models.CharField(max_length=32, blank=True)

    # Vehicle details
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.PositiveIntegerField()

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

    # --- Computed properties ---

    @property
    def full_name(self) -> str:
        """Return the full vehicle name (year make model)."""
        return f"{self.year} {self.make} {self.model}"

    @property
    def owner_name(self) -> str | None:
        """Return the owner's full name if assigned."""
        if self.owner:
            return self.owner.full_name
        return None

    def __str__(self) -> str:
        return f"{self.full_name} ({self.vin})"


class Transaction(models.Model):
    """Represents a transaction involving a customer and a vehicle.

    Tracks transactions such as renewals, transfers, and credential replacements.

    Attributes:
        transaction_id: Unique identifier for the transaction (UUID).
        customer: The customer involved in the transaction.
        vehicle: The vehicle involved in the transaction.
        transaction_type: Type of transaction (RNW, TNSF, RNWRDF, TNSFRDF,
            DUPTTL, RPLCRD, TNSFCLR, LNSL, NTRL).
        transaction_date: The date of the transaction.
        transaction_amount: The monetary amount of the transaction.
        bz_partner_fee: BZ Partner fee amount.
        broker_fee: Broker fee amount.
        service_fee: Service fee amount.
        dmv_fee: DMV fee amount.
        discount: Discount amount.
        created_at: Timestamp when the transaction was created.
        updated_at: Timestamp when the transaction was last updated.
    """

    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    TRANSACTION_TYPES = [
        ("RNW", "Renew"),
        ("TNSF", "Transfer"),
        ("RNWRDF", "Renew RDF"),
        ("TNSFRDF", "Transfer RDF"),
        ("DUPTTL", "Duplicate Title"),
        ("RPLCRD", "Replacement Credentials"),
        ("TNSFCLR", "Transfer Clear"),
        ("LNSL", "Lien Sale"),
        ("NTRL", "Notice of Transfer and Release of Liability"),
    ]

    customer = models.ForeignKey(
        "customer_management.Customer",
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    vehicle = models.ForeignKey(
        MotorVehicle,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        max_length=32, choices=TRANSACTION_TYPES, default="RNW"
    )
    transaction_date = models.DateField()
    transaction_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Fee fields
    bz_partner_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    broker_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    service_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    dmv_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "motor_vehicle_services"
        db_table = "motor_vehicle_transactions"
        ordering = ["-transaction_date"]

    @property
    def total_fees(self):
        """Return the sum of all fees."""
        return self.bz_partner_fee + self.broker_fee + self.service_fee + self.dmv_fee

    def __str__(self) -> str:
        """Return a string representation of the transaction."""
        return f"Transaction {self.transaction_id} - {self.customer} - {self.vehicle}"
