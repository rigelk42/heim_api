"""Command DTOs for the Motor Vehicle Services application layer.

Commands represent intentions to change state in the system.
They are immutable data structures that carry all information
needed to perform a write operation.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreateMotorVehicleCommand:
    """Command to register a new motor vehicle.

    Attributes:
        vin: Vehicle Identification Number (17 characters).
        make: Vehicle manufacturer.
        model: Vehicle model name.
        year: Model year.
        license_plate: License plate number (optional).
        license_plate_state: Issuing state/province (optional).
        owner_id: ID of the customer who owns this vehicle (optional).
    """

    vin: str
    make: str
    model: str
    year: int
    license_plate: str = ""
    license_plate_state: str = ""
    owner_id: str | None = None


@dataclass(frozen=True)
class UpdateMotorVehicleCommand:
    """Command to update a motor vehicle's details.

    Only non-None fields will be updated.

    Attributes:
        vin: The VIN of the vehicle to update.
        license_plate: New license plate (optional).
        license_plate_state: New license plate state (optional).
    """

    vin: str
    license_plate: str | None = None
    license_plate_state: str | None = None


@dataclass(frozen=True)
class DeleteMotorVehicleCommand:
    """Command to delete a motor vehicle.

    Attributes:
        vin: The VIN of the vehicle to delete.
    """

    vin: str


@dataclass(frozen=True)
class TransferOwnershipCommand:
    """Command to transfer a vehicle's ownership to a new owner.

    Attributes:
        vin: The VIN of the vehicle.
        new_owner_id: The ID of the new owner (None to unassign).
    """

    vin: str
    new_owner_id: str | None = None


@dataclass(frozen=True)
class CreateTransactionCommand:
    """Command to create a new transaction.

    Attributes:
        customer_id: The ID of the customer.
        vin: The VIN of the vehicle.
        transaction_type: Type of transaction (renew, transfer, etc.).
        transaction_date: The date of the transaction.
        transaction_amount: The transaction amount.
    """

    customer_id: str
    vin: str
    transaction_type: str
    transaction_date: date
    transaction_amount: Decimal


@dataclass(frozen=True)
class UpdateTransactionCommand:
    """Command to update an existing transaction.

    Only non-None fields will be updated.

    Attributes:
        transaction_id: The UUID of the transaction to update.
        transaction_type: New transaction type (optional).
        transaction_date: New transaction date (optional).
        transaction_amount: New transaction amount (optional).
    """

    transaction_id: UUID
    transaction_type: str | None = None
    transaction_date: date | None = None
    transaction_amount: Decimal | None = None


@dataclass(frozen=True)
class DeleteTransactionCommand:
    """Command to delete a transaction.

    Attributes:
        transaction_id: The UUID of the transaction to delete.
    """

    transaction_id: UUID
