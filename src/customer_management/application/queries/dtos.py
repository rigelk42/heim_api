"""Query DTOs for the Customer application layer.

Queries represent requests for data without side effects.
They are immutable data structures that carry all information
needed to perform a read operation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetCustomerQuery:
    """Query to retrieve a single customer by ID.

    Attributes:
        customer_id: The ID of the customer to retrieve.
    """

    customer_id: str


@dataclass(frozen=True)
class ListCustomersQuery:
    """Query to list all customers.

    Returns customers ordered by surname, then given names.
    """

    pass


@dataclass(frozen=True)
class SearchCustomersQuery:
    """Query to search customers by name or email.

    The search is case-insensitive and matches partial strings
    in given_names, surnames, or email fields.

    Attributes:
        query: The search string.
    """

    query: str


@dataclass(frozen=True)
class GetCustomerAddressesQuery:
    """Query to retrieve all addresses for a customer.

    Attributes:
        customer_id: The ID of the customer.
    """

    customer_id: str
