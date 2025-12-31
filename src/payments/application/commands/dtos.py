"""Command DTOs for the Payments application layer.

Commands represent intentions to change state in the system.
They are immutable data structures that carry all information
needed to perform a write operation.
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreatePaymentCommand:
    """Command to create a new payment.

    Attributes:
        transaction_id: The UUID of the transaction.
        payment_method: Method of payment (CASH, CARD, CHECK, ACH, WIRE).
        amount: The payment amount.
        reference_number: External reference number (optional).
        notes: Optional notes about the payment.
    """

    transaction_id: UUID
    payment_method: str
    amount: Decimal
    reference_number: str = ""
    notes: str = ""


@dataclass(frozen=True)
class UpdatePaymentCommand:
    """Command to update an existing payment.

    Only non-None fields will be updated.

    Attributes:
        payment_id: The UUID of the payment to update.
        payment_method: New payment method (optional).
        amount: New amount (optional).
        reference_number: New reference number (optional).
        notes: New notes (optional).
    """

    payment_id: UUID
    payment_method: str | None = None
    amount: Decimal | None = None
    reference_number: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class DeletePaymentCommand:
    """Command to delete a payment.

    Attributes:
        payment_id: The UUID of the payment to delete.
    """

    payment_id: UUID


@dataclass(frozen=True)
class CompletePaymentCommand:
    """Command to mark a payment as completed.

    Attributes:
        payment_id: The UUID of the payment to complete.
    """

    payment_id: UUID


@dataclass(frozen=True)
class RefundPaymentCommand:
    """Command to refund a payment.

    Attributes:
        payment_id: The UUID of the payment to refund.
    """

    payment_id: UUID


@dataclass(frozen=True)
class CancelPaymentCommand:
    """Command to cancel a payment.

    Attributes:
        payment_id: The UUID of the payment to cancel.
    """

    payment_id: UUID
