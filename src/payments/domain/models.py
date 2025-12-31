"""Domain models for the Payments bounded context.

This module contains the Aggregate Roots and Entities for the domain.
"""

from __future__ import annotations

import uuid

from django.db import models


class Payment(models.Model):
    """Aggregate Root for the Payments bounded context.

    Represents a payment made for a transaction.

    Attributes:
        payment_id: Unique identifier for the payment (UUID).
        transaction: The transaction this payment is for.
        payment_method: Method of payment (CASH, CARD, CHECK, etc.).
        amount: The payment amount.
        status: Current status of the payment.
        reference_number: External reference number (e.g., check number, card auth).
        notes: Optional notes about the payment.
        created_at: Timestamp when the payment was created.
        updated_at: Timestamp when the payment was last updated.
    """

    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    PAYMENT_METHODS = [
        ("CASH", "Cash"),
        ("CARD", "Credit/Debit Card"),
        ("CHECK", "Check"),
        ("ACH", "ACH Transfer"),
        ("WIRE", "Wire Transfer"),
    ]

    PAYMENT_STATUSES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
        ("CANCELLED", "Cancelled"),
    ]

    transaction = models.ForeignKey(
        "motor_vehicle_services.Transaction",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    payment_method = models.CharField(
        max_length=16, choices=PAYMENT_METHODS, default="CASH"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=16, choices=PAYMENT_STATUSES, default="PENDING"
    )
    reference_number = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "payments"
        db_table = "payments_payment"
        ordering = ["-created_at"]

    @property
    def is_completed(self) -> bool:
        """Return True if the payment is completed."""
        return self.status == "COMPLETED"

    @property
    def is_refundable(self) -> bool:
        """Return True if the payment can be refunded."""
        return self.status == "COMPLETED"

    def complete(self) -> None:
        """Mark the payment as completed."""
        self.status = "COMPLETED"

    def refund(self) -> None:
        """Mark the payment as refunded."""
        if not self.is_refundable:
            raise ValueError("Payment cannot be refunded")
        self.status = "REFUNDED"

    def cancel(self) -> None:
        """Mark the payment as cancelled."""
        if self.status != "PENDING":
            raise ValueError("Only pending payments can be cancelled")
        self.status = "CANCELLED"

    def __str__(self) -> str:
        return f"Payment {self.payment_id} - {self.amount} ({self.status})"
