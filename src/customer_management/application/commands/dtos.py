"""Command DTOs for the Customer application layer.

Commands represent intentions to change state in the system.
They are immutable data structures that carry all information
needed to perform a write operation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCustomerCommand:
    """Command to create a new customer.

    Attributes:
        given_names: The customer's given (first) names.
        surnames: The customer's family names.
        email: The customer's email address (must be unique).
        phone: The customer's phone number (optional).
    """

    given_names: str
    surnames: str
    email: str
    phone: str = ""


@dataclass(frozen=True)
class UpdateCustomerCommand:
    """Command to update an existing customer's details.

    Only non-None fields will be updated.

    Attributes:
        customer_id: The ID of the customer to update.
        given_names: New given names (optional).
        surnames: New surnames (optional).
        phone: New phone number (optional).
    """

    customer_id: int
    given_names: str | None = None
    surnames: str | None = None
    phone: str | None = None


@dataclass(frozen=True)
class UpdateCustomerEmailCommand:
    """Command to update a customer's email address.

    Email updates are handled separately due to uniqueness constraints.

    Attributes:
        customer_id: The ID of the customer to update.
        email: The new email address.
    """

    customer_id: int
    email: str


@dataclass(frozen=True)
class DeleteCustomerCommand:
    """Command to delete a customer.

    Attributes:
        customer_id: The ID of the customer to delete.
    """

    customer_id: int


@dataclass(frozen=True)
class AddCustomerAddressCommand:
    """Command to add an address to a customer.

    Attributes:
        customer_id: The ID of the customer.
        address_line_1: Primary address line.
        city: City name.
        postal_code: Postal/ZIP code.
        country: Country name.
        address_line_2: Secondary address line (optional).
        state_province: State or province (optional).
        address_type: Type of address - home, work, billing, shipping.
        is_primary: Whether this is the primary address.
    """

    customer_id: int
    address_line_1: str
    city: str
    postal_code: str
    country: str
    address_line_2: str = ""
    state_province: str = ""
    address_type: str = "home"
    is_primary: bool = False


@dataclass(frozen=True)
class RemoveCustomerAddressCommand:
    """Command to remove an address from a customer.

    Attributes:
        customer_id: The ID of the customer.
        address_id: The ID of the address to remove.
    """

    customer_id: int
    address_id: int
