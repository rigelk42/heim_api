"""Domain exceptions for the Payments bounded context.

These exceptions represent business rule violations and domain-specific
error conditions.
"""


class PaymentServiceException(Exception):
    """Base exception for all payment service domain errors."""

    pass


class PaymentNotFound(PaymentServiceException):
    """Raised when a payment cannot be found by the given identifier.

    Attributes:
        identifier: The payment UUID that was not found.
    """

    def __init__(self, identifier):
        self.identifier = identifier
        super().__init__(f"Payment not found: {identifier}")


class InvalidPaymentState(PaymentServiceException):
    """Raised when a payment operation is invalid for the current state.

    Attributes:
        payment_id: The payment UUID.
        current_state: The current payment status.
        operation: The attempted operation.
    """

    def __init__(self, payment_id, current_state: str, operation: str):
        self.payment_id = payment_id
        self.current_state = current_state
        self.operation = operation
        super().__init__(
            f"Cannot {operation} payment {payment_id} in state {current_state}"
        )
