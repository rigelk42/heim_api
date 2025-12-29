"""Query handlers for the Motor Vehicle Services application layer.

Query handlers process queries and return data without modifying state.
They provide read-only access to the domain.
"""

from django.db.models import QuerySet

from motor_vehicle_services.domain.exceptions import (
    MotorVehicleNotFound,
    TransactionNotFound,
)
from motor_vehicle_services.domain.models import MotorVehicle, Transaction
from motor_vehicle_services.infrastructure.repositories import (
    MotorVehicleRepository,
    TransactionRepository,
)

from .dtos import (
    GetMotorVehicleByVINQuery,
    GetMotorVehicleQuery,
    GetTransactionQuery,
    ListMotorVehiclesByOwnerQuery,
    ListMotorVehiclesByStatusQuery,
    ListMotorVehiclesQuery,
    ListTransactionsByCustomerQuery,
    ListTransactionsByVehicleQuery,
    ListTransactionsQuery,
    SearchMotorVehiclesQuery,
)


class MotorVehicleQueryHandler:
    """Handles all motor vehicle-related queries.

    This handler processes read operations for the MotorVehicle aggregate,
    providing access to vehicle data without modifying state.

    Attributes:
        repository: The repository used for data access.
    """

    def __init__(self, repository: MotorVehicleRepository | None = None):
        """Initialize the query handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new MotorVehicleRepository will be created.
        """
        self.repository = repository or MotorVehicleRepository()

    def handle_get(self, query: GetMotorVehicleQuery) -> MotorVehicle:
        """Retrieve a single motor vehicle by ID.

        Args:
            query: The get motor vehicle query.

        Returns:
            The requested MotorVehicle.

        Raises:
            MotorVehicleNotFound: If the vehicle does not exist.
        """
        vehicle = self.repository.get_by_id(query.vehicle_id)
        if not vehicle:
            raise MotorVehicleNotFound(query.vehicle_id)
        return vehicle

    def handle_get_by_vin(self, query: GetMotorVehicleByVINQuery) -> MotorVehicle:
        """Retrieve a motor vehicle by VIN.

        Args:
            query: The get by VIN query.

        Returns:
            The requested MotorVehicle.

        Raises:
            MotorVehicleNotFound: If the vehicle does not exist.
        """
        vehicle = self.repository.get_by_vin(query.vin)
        if not vehicle:
            raise MotorVehicleNotFound(query.vin)
        return vehicle

    def handle_list(self, query: ListMotorVehiclesQuery) -> QuerySet[MotorVehicle]:
        """List all motor vehicles.

        Args:
            query: The list motor vehicles query.

        Returns:
            A QuerySet of all vehicles.
        """
        return self.repository.get_all()

    def handle_list_by_status(
        self, query: ListMotorVehiclesByStatusQuery
    ) -> QuerySet[MotorVehicle]:
        """List motor vehicles by status.

        Args:
            query: The list by status query.

        Returns:
            A QuerySet of vehicles with the specified status.
        """
        return self.repository.get_by_status(query.status)

    def handle_search(self, query: SearchMotorVehiclesQuery) -> QuerySet[MotorVehicle]:
        """Search motor vehicles by VIN, make, model, or license plate.

        Args:
            query: The search motor vehicles query.

        Returns:
            A QuerySet of matching vehicles.
        """
        return self.repository.search(query.query)

    def handle_list_by_owner(
        self, query: ListMotorVehiclesByOwnerQuery
    ) -> QuerySet[MotorVehicle]:
        """List motor vehicles by owner.

        Args:
            query: The list by owner query.

        Returns:
            A QuerySet of vehicles owned by the specified customer.
        """
        return self.repository.get_by_owner(query.owner_id)


class TransactionQueryHandler:
    """Handles all transaction-related queries.

    This handler processes read operations for the Transaction entity,
    providing access to transaction data without modifying state.

    Attributes:
        repository: The repository used for data access.
    """

    def __init__(self, repository: TransactionRepository | None = None):
        """Initialize the query handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new TransactionRepository will be created.
        """
        self.repository = repository or TransactionRepository()

    def handle_get(self, query: GetTransactionQuery) -> Transaction:
        """Retrieve a single transaction by ID.

        Args:
            query: The get transaction query.

        Returns:
            The requested Transaction.

        Raises:
            TransactionNotFound: If the transaction does not exist.
        """
        transaction = self.repository.get_by_id(query.transaction_id)
        if not transaction:
            raise TransactionNotFound(query.transaction_id)
        return transaction

    def handle_list(self, query: ListTransactionsQuery) -> QuerySet[Transaction]:
        """List all transactions.

        Args:
            query: The list transactions query.

        Returns:
            A QuerySet of all transactions.
        """
        return self.repository.get_all()

    def handle_list_by_customer(
        self, query: ListTransactionsByCustomerQuery
    ) -> QuerySet[Transaction]:
        """List transactions by customer.

        Args:
            query: The list by customer query.

        Returns:
            A QuerySet of transactions for the specified customer.
        """
        return self.repository.get_by_customer(query.customer_id)

    def handle_list_by_vehicle(
        self, query: ListTransactionsByVehicleQuery
    ) -> QuerySet[Transaction]:
        """List transactions by vehicle.

        Args:
            query: The list by vehicle query.

        Returns:
            A QuerySet of transactions for the specified vehicle.
        """
        return self.repository.get_by_vehicle(query.vehicle_id)
