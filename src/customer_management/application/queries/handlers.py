"""Query handlers for the Customer application layer.

Query handlers process queries and return data without modifying state.
They provide read-only access to the domain.
"""

from django.db.models import QuerySet

from customer_management.domain.exceptions import CustomerNotFound
from customer_management.domain.models import Address, Customer
from customer_management.infrastructure.repositories import CustomerRepository

from .dtos import (
    GetCustomerAddressesQuery,
    GetCustomerQuery,
    ListCustomersQuery,
    SearchCustomersQuery,
)


class CustomerQueryHandler:
    """Handles all customer-related queries.

    This handler processes read operations for the Customer aggregate,
    providing access to customer data without modifying state.

    Attributes:
        repository: The repository used for data access.
    """

    def __init__(self, repository: CustomerRepository | None = None):
        """Initialize the query handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new CustomerRepository will be created.
        """
        self.repository = repository or CustomerRepository()

    def handle_get(self, query: GetCustomerQuery) -> Customer:
        """Retrieve a single customer by ID.

        Args:
            query: The get customer query.

        Returns:
            The requested Customer.

        Raises:
            CustomerNotFound: If the customer does not exist.
        """
        customer = self.repository.get_by_id(query.customer_id)
        if not customer:
            raise CustomerNotFound(query.customer_id)
        return customer

    def handle_list(self, query: ListCustomersQuery) -> QuerySet[Customer]:
        """List all customers.

        Args:
            query: The list customers query.

        Returns:
            A QuerySet of all customers, ordered by surname.
        """
        return self.repository.get_all()

    def handle_search(self, query: SearchCustomersQuery) -> QuerySet[Customer]:
        """Search customers by name or email.

        Args:
            query: The search customers query.

        Returns:
            A QuerySet of matching customers.
        """
        return self.repository.search(query.query)

    def handle_get_addresses(
        self, query: GetCustomerAddressesQuery
    ) -> QuerySet[Address]:
        """Retrieve all addresses for a customer.

        Args:
            query: The get addresses query.

        Returns:
            A QuerySet of the customer's addresses.

        Raises:
            CustomerNotFound: If the customer does not exist.
        """
        customer = self.repository.get_by_id(query.customer_id)
        if not customer:
            raise CustomerNotFound(query.customer_id)
        return customer.get_addresses()
