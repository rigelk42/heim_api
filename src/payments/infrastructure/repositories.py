"""Repository implementations for the Payments domain.

Repositories abstract data access and provide a collection-like interface
for working with domain entities. They hide the details of data persistence.
"""

from decimal import Decimal
from uuid import UUID

from django.db.models import QuerySet

from payments.domain.models import Payment


class PaymentRepository:
    """Repository for Payment aggregate persistence.

    Provides methods for storing, retrieving, and querying Payment entities.
    This implementation uses Django's ORM for data access.
    """

    def get_all(self) -> QuerySet[Payment]:
        """Retrieve all payments.

        Returns:
            A QuerySet of all payments, ordered by created_at (desc).
        """
        return Payment.objects.all()

    def get_by_id(self, payment_id: UUID) -> Payment | None:
        """Retrieve a payment by ID.

        Args:
            payment_id: The UUID of the payment to retrieve.

        Returns:
            The Payment if found, None otherwise.
        """
        return Payment.objects.filter(payment_id=payment_id).first()

    def get_by_transaction(self, transaction_id: UUID) -> QuerySet[Payment]:
        """Retrieve all payments for a specific transaction.

        Args:
            transaction_id: The UUID of the transaction.

        Returns:
            A QuerySet of payments for this transaction.
        """
        return Payment.objects.filter(transaction_id=transaction_id)

    def save(self, payment: Payment) -> Payment:
        """Save an existing payment.

        Args:
            payment: The payment to save.

        Returns:
            The saved Payment.

        Raises:
            ValidationError: If the payment data is invalid.
        """
        payment.full_clean()
        payment.save()
        return payment

    def create(
        self,
        transaction_id: UUID,
        payment_method: str,
        amount: Decimal,
        status: str = "PENDING",
        reference_number: str = "",
        notes: str = "",
    ) -> Payment:
        """Create a new payment.

        Args:
            transaction_id: The UUID of the transaction.
            payment_method: The payment method.
            amount: The payment amount.
            status: The payment status (default: PENDING).
            reference_number: External reference number.
            notes: Optional notes.

        Returns:
            The newly created Payment.

        Raises:
            ValidationError: If the payment data is invalid.
        """
        payment = Payment(
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            status=status,
            reference_number=reference_number,
            notes=notes,
        )
        payment.full_clean()
        payment.save()
        return payment

    def delete(self, payment: Payment) -> None:
        """Delete a payment.

        Args:
            payment: The payment to delete.
        """
        payment.delete()
