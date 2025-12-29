"""Repository implementations for the Motor Vehicle Services domain.

Repositories abstract data access and provide a collection-like interface
for working with domain entities. They hide the details of data persistence.
"""

from datetime import date
from decimal import Decimal

from django.db.models import Q, QuerySet

from motor_vehicle_services.domain.models import MotorVehicle, Transaction


class MotorVehicleRepository:
    """Repository for MotorVehicle aggregate persistence.

    Provides methods for storing, retrieving, and querying MotorVehicle entities.
    This implementation uses Django's ORM for data access.
    """

    def get_all(self) -> QuerySet[MotorVehicle]:
        """Retrieve all motor vehicles.

        Returns:
            A QuerySet of all vehicles, ordered by year (desc), make, model.
        """
        return MotorVehicle.objects.all()

    def get_by_id(self, vehicle_id: int) -> MotorVehicle | None:
        """Retrieve a motor vehicle by ID.

        Args:
            vehicle_id: The ID of the vehicle to retrieve.

        Returns:
            The MotorVehicle if found, None otherwise.
        """
        return MotorVehicle.objects.filter(id=vehicle_id).first()

    def get_by_vin(self, vin: str) -> MotorVehicle | None:
        """Retrieve a motor vehicle by VIN.

        Args:
            vin: The Vehicle Identification Number to search for.

        Returns:
            The MotorVehicle if found, None otherwise.
        """
        return MotorVehicle.objects.filter(vin=vin.upper()).first()

    def get_by_license_plate(self, license_plate: str) -> MotorVehicle | None:
        """Retrieve a motor vehicle by license plate.

        Args:
            license_plate: The license plate to search for.

        Returns:
            The MotorVehicle if found, None otherwise.
        """
        return MotorVehicle.objects.filter(license_plate=license_plate.upper()).first()

    def get_by_owner(self, owner_id: int) -> QuerySet[MotorVehicle]:
        """Retrieve all motor vehicles owned by a specific customer.

        Args:
            owner_id: The ID of the customer.

        Returns:
            A QuerySet of vehicles owned by this customer.
        """
        return MotorVehicle.objects.filter(owner_id=owner_id)

    def search(self, query: str) -> QuerySet[MotorVehicle]:
        """Search motor vehicles by VIN, make, model, or license plate.

        Performs a case-insensitive partial match.

        Args:
            query: The search string.

        Returns:
            A QuerySet of matching vehicles.
        """
        return MotorVehicle.objects.filter(
            Q(vin__icontains=query)
            | Q(make__icontains=query)
            | Q(model__icontains=query)
            | Q(license_plate__icontains=query)
        )

    def save(self, vehicle: MotorVehicle) -> MotorVehicle:
        """Save an existing motor vehicle.

        Validates the vehicle before saving.

        Args:
            vehicle: The vehicle to save.

        Returns:
            The saved MotorVehicle.

        Raises:
            ValidationError: If the vehicle data is invalid.
        """
        vehicle.full_clean()
        vehicle.save()
        return vehicle

    def create(
        self,
        vin: str,
        make: str,
        model: str,
        year: int,
        mileage_km: int = 0,
        license_plate: str = "",
        license_plate_state: str = "",
        owner_id: int | None = None,
    ) -> MotorVehicle:
        """Create a new motor vehicle.

        Args:
            vin: Vehicle Identification Number.
            make: Vehicle manufacturer.
            model: Vehicle model name.
            year: Model year.
            mileage_km: Current mileage in kilometers.
            license_plate: License plate number.
            license_plate_state: License plate issuing state.
            owner_id: ID of the owning customer.

        Returns:
            The newly created MotorVehicle.

        Raises:
            ValidationError: If the vehicle data is invalid.
        """
        vehicle = MotorVehicle(
            vin=vin.upper(),
            make=make,
            model=model,
            year=year,
            mileage_km=mileage_km,
            license_plate=license_plate.upper() if license_plate else "",
            license_plate_state=license_plate_state,
            owner_id=owner_id,
        )
        vehicle.full_clean()
        vehicle.save()
        return vehicle

    def delete(self, vehicle: MotorVehicle) -> None:
        """Delete a motor vehicle.

        Args:
            vehicle: The vehicle to delete.
        """
        vehicle.delete()


class TransactionRepository:
    """Repository for Transaction entity persistence.

    Provides methods for storing, retrieving, and querying Transaction entities.
    This implementation uses Django's ORM for data access.
    """

    def get_all(self) -> QuerySet[Transaction]:
        """Retrieve all transactions.

        Returns:
            A QuerySet of all transactions, ordered by transaction date (desc).
        """
        return Transaction.objects.all()

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Retrieve a transaction by ID.

        Args:
            transaction_id: The ID of the transaction to retrieve.

        Returns:
            The Transaction if found, None otherwise.
        """
        return Transaction.objects.filter(id=transaction_id).first()

    def get_by_customer(self, customer_id: int) -> QuerySet[Transaction]:
        """Retrieve all transactions for a specific customer.

        Args:
            customer_id: The ID of the customer.

        Returns:
            A QuerySet of transactions for this customer.
        """
        return Transaction.objects.filter(customer_id=customer_id)

    def get_by_vehicle(self, vehicle_id: int) -> QuerySet[Transaction]:
        """Retrieve all transactions for a specific vehicle.

        Args:
            vehicle_id: The ID of the vehicle.

        Returns:
            A QuerySet of transactions for this vehicle.
        """
        return Transaction.objects.filter(vehicle_id=vehicle_id)

    def save(self, transaction: Transaction) -> Transaction:
        """Save an existing transaction.

        Args:
            transaction: The transaction to save.

        Returns:
            The saved Transaction.

        Raises:
            ValidationError: If the transaction data is invalid.
        """
        transaction.full_clean()
        transaction.save()
        return transaction

    def create(
        self,
        customer_id: int,
        vehicle_id: int,
        transaction_date: date,
        transaction_amount: Decimal,
    ) -> Transaction:
        """Create a new transaction.

        Args:
            customer_id: The ID of the customer.
            vehicle_id: The ID of the vehicle.
            transaction_date: The date of the transaction.
            transaction_amount: The transaction amount.

        Returns:
            The newly created Transaction.

        Raises:
            ValidationError: If the transaction data is invalid.
        """
        transaction = Transaction(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            transaction_date=transaction_date,
            transaction_amount=transaction_amount,
        )
        transaction.full_clean()
        transaction.save()
        return transaction

    def delete(self, transaction: Transaction) -> None:
        """Delete a transaction.

        Args:
            transaction: The transaction to delete.
        """
        transaction.delete()
