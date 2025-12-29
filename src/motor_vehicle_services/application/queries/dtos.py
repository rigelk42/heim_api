"""Query DTOs for the Motor Vehicle Services application layer.

Queries represent requests for data without side effects.
They are immutable data structures that carry all information
needed to perform a read operation.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetMotorVehicleQuery:
    """Query to retrieve a single motor vehicle by VIN.

    Attributes:
        vin: The VIN of the vehicle to retrieve.
    """

    vin: str


@dataclass(frozen=True)
class ListMotorVehiclesQuery:
    """Query to list all motor vehicles.

    Returns vehicles ordered by year (desc), make, model.
    """

    pass


@dataclass(frozen=True)
class SearchMotorVehiclesQuery:
    """Query to search motor vehicles by VIN, make, model, or license plate.

    The search is case-insensitive and matches partial strings.

    Attributes:
        query: The search string.
    """

    query: str


@dataclass(frozen=True)
class ListMotorVehiclesByOwnerQuery:
    """Query to list all motor vehicles owned by a specific customer.

    Attributes:
        owner_id: The customer_id of the owner.
    """

    owner_id: str


@dataclass(frozen=True)
class GetTransactionQuery:
    """Query to retrieve a single transaction by ID.

    Attributes:
        transaction_id: The UUID of the transaction to retrieve.
    """

    transaction_id: UUID


@dataclass(frozen=True)
class ListTransactionsQuery:
    """Query to list all transactions.

    Returns transactions ordered by transaction date (desc).
    """

    pass


@dataclass(frozen=True)
class ListTransactionsByCustomerQuery:
    """Query to list all transactions for a specific customer.

    Attributes:
        customer_id: The customer_id of the customer.
    """

    customer_id: str


@dataclass(frozen=True)
class ListTransactionsByVehicleQuery:
    """Query to list all transactions for a specific vehicle.

    Attributes:
        vin: The VIN of the vehicle.
    """

    vin: str
