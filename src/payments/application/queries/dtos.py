"""Query DTOs for the Payments application layer.

Queries represent requests for data without side effects.
They are immutable data structures that carry all information
needed to perform a read operation.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetPaymentQuery:
    """Query to retrieve a single payment by ID.

    Attributes:
        payment_id: The UUID of the payment to retrieve.
    """

    payment_id: UUID


@dataclass(frozen=True)
class ListPaymentsQuery:
    """Query to list all payments.

    Returns payments ordered by created_at (desc).
    """

    pass


@dataclass(frozen=True)
class ListPaymentsByTransactionQuery:
    """Query to list all payments for a specific transaction.

    Attributes:
        transaction_id: The UUID of the transaction.
    """

    transaction_id: UUID
