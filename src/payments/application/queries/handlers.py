"""Query handlers for the Payments application layer.

Query handlers process queries and return data without modifying state.
They provide read-only access to the domain.
"""

from django.db.models import QuerySet

from payments.domain.exceptions import PaymentNotFound
from payments.domain.models import Payment
from payments.infrastructure.repositories import PaymentRepository

from .dtos import (
    GetPaymentQuery,
    ListPaymentsByTransactionQuery,
    ListPaymentsQuery,
)


class PaymentQueryHandler:
    """Handles all payment-related queries.

    This handler processes read operations for the Payment aggregate,
    providing access to payment data without modifying state.

    Attributes:
        repository: The repository used for data access.
    """

    def __init__(self, repository: PaymentRepository | None = None):
        """Initialize the query handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new PaymentRepository will be created.
        """
        self.repository = repository or PaymentRepository()

    def handle_get(self, query: GetPaymentQuery) -> Payment:
        """Retrieve a single payment by ID.

        Args:
            query: The get payment query.

        Returns:
            The requested Payment.

        Raises:
            PaymentNotFound: If the payment does not exist.
        """
        payment = self.repository.get_by_id(query.payment_id)
        if not payment:
            raise PaymentNotFound(query.payment_id)
        return payment

    def handle_list(self, query: ListPaymentsQuery) -> QuerySet[Payment]:
        """List all payments.

        Args:
            query: The list payments query.

        Returns:
            A QuerySet of all payments.
        """
        return self.repository.get_all()

    def handle_list_by_transaction(
        self, query: ListPaymentsByTransactionQuery
    ) -> QuerySet[Payment]:
        """List payments by transaction.

        Args:
            query: The list by transaction query.

        Returns:
            A QuerySet of payments for the specified transaction.
        """
        return self.repository.get_by_transaction(query.transaction_id)
