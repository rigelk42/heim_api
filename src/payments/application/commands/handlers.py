"""Command handlers for the Payments application layer.

Command handlers process commands and execute the corresponding
business operations. They coordinate between the domain layer
and infrastructure layer.
"""

from payments.domain.exceptions import InvalidPaymentState, PaymentNotFound
from payments.domain.models import Payment
from payments.infrastructure.repositories import PaymentRepository

from .dtos import (
    CancelPaymentCommand,
    CompletePaymentCommand,
    CreatePaymentCommand,
    DeletePaymentCommand,
    RefundPaymentCommand,
    UpdatePaymentCommand,
)


class PaymentCommandHandler:
    """Handles all payment-related commands.

    This handler processes write operations for the Payment aggregate,
    including creating, updating, and deleting payments.

    Attributes:
        repository: The repository used for data persistence.
    """

    def __init__(self, repository: PaymentRepository | None = None):
        """Initialize the command handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new PaymentRepository will be created.
        """
        self.repository = repository or PaymentRepository()

    def handle_create(self, command: CreatePaymentCommand) -> Payment:
        """Create a new payment.

        Args:
            command: The create payment command.

        Returns:
            The newly created Payment.

        Raises:
            ValueError: If the transaction does not exist.
        """
        from motor_vehicle_services.domain.models import Transaction

        transaction = Transaction.objects.filter(
            transaction_id=command.transaction_id
        ).first()
        if not transaction:
            raise ValueError(f"Transaction with ID {command.transaction_id} not found")

        payment = self.repository.create(
            transaction_id=command.transaction_id,
            payment_method=command.payment_method,
            amount=command.amount,
            reference_number=command.reference_number,
            notes=command.notes,
        )

        return payment

    def handle_update(self, command: UpdatePaymentCommand) -> Payment:
        """Update an existing payment.

        Args:
            command: The update payment command.

        Returns:
            The updated Payment.

        Raises:
            PaymentNotFound: If the payment does not exist.
        """
        payment = self.repository.get_by_id(command.payment_id)
        if not payment:
            raise PaymentNotFound(command.payment_id)

        if command.payment_method is not None:
            payment.payment_method = command.payment_method

        if command.amount is not None:
            payment.amount = command.amount

        if command.reference_number is not None:
            payment.reference_number = command.reference_number

        if command.notes is not None:
            payment.notes = command.notes

        payment = self.repository.save(payment)

        return payment

    def handle_delete(self, command: DeletePaymentCommand) -> None:
        """Delete a payment.

        Args:
            command: The delete payment command.

        Raises:
            PaymentNotFound: If the payment does not exist.
        """
        payment = self.repository.get_by_id(command.payment_id)
        if not payment:
            raise PaymentNotFound(command.payment_id)

        self.repository.delete(payment)

    def handle_complete(self, command: CompletePaymentCommand) -> Payment:
        """Mark a payment as completed.

        Args:
            command: The complete payment command.

        Returns:
            The updated Payment.

        Raises:
            PaymentNotFound: If the payment does not exist.
            InvalidPaymentState: If the payment cannot be completed.
        """
        payment = self.repository.get_by_id(command.payment_id)
        if not payment:
            raise PaymentNotFound(command.payment_id)

        if payment.status != "PENDING":
            raise InvalidPaymentState(command.payment_id, payment.status, "complete")

        payment.complete()
        payment = self.repository.save(payment)

        return payment

    def handle_refund(self, command: RefundPaymentCommand) -> Payment:
        """Refund a payment.

        Args:
            command: The refund payment command.

        Returns:
            The updated Payment.

        Raises:
            PaymentNotFound: If the payment does not exist.
            InvalidPaymentState: If the payment cannot be refunded.
        """
        payment = self.repository.get_by_id(command.payment_id)
        if not payment:
            raise PaymentNotFound(command.payment_id)

        if not payment.is_refundable:
            raise InvalidPaymentState(command.payment_id, payment.status, "refund")

        payment.refund()
        payment = self.repository.save(payment)

        return payment

    def handle_cancel(self, command: CancelPaymentCommand) -> Payment:
        """Cancel a payment.

        Args:
            command: The cancel payment command.

        Returns:
            The updated Payment.

        Raises:
            PaymentNotFound: If the payment does not exist.
            InvalidPaymentState: If the payment cannot be cancelled.
        """
        payment = self.repository.get_by_id(command.payment_id)
        if not payment:
            raise PaymentNotFound(command.payment_id)

        if payment.status != "PENDING":
            raise InvalidPaymentState(command.payment_id, payment.status, "cancel")

        payment.cancel()
        payment = self.repository.save(payment)

        return payment
