"""Domain exceptions for the Customer bounded context.

These exceptions represent business rule violations and domain-specific
error conditions.
"""


class CustomerException(Exception):
    """Base exception for all customer domain errors."""

    pass


class CustomerNotFound(CustomerException):
    """Raised when a customer cannot be found by the given identifier.

    Attributes:
        identifier: The customer ID or other identifier that was not found.
    """

    def __init__(self, identifier: int | str):
        self.identifier = identifier
        super().__init__(f"Customer not found: {identifier}")


class CustomerAlreadyExists(CustomerException):
    """Raised when attempting to create a customer with a duplicate email.

    Attributes:
        email: The email address that already exists.
    """

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Customer with email {email} already exists")
