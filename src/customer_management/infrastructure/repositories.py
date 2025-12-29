"""Repository implementations for the Customer domain.

Repositories abstract data access and provide a collection-like interface
for working with domain entities. They hide the details of data persistence.
"""

from django.db.models import Q, QuerySet

from customer_management.domain.models import Customer


class CustomerRepository:
    """Repository for Customer aggregate persistence.

    Provides methods for storing, retrieving, and querying Customer entities.
    This implementation uses Django's ORM for data access.
    """

    def get_all(self) -> QuerySet[Customer]:
        """Retrieve all customers.

        Returns:
            A QuerySet of all customers, ordered by surname.
        """
        return Customer.objects.all()

    def get_by_id(self, customer_id: str) -> Customer | None:
        """Retrieve a customer by ID.

        Args:
            customer_id: The ID of the customer to retrieve.

        Returns:
            The Customer if found, None otherwise.
        """
        return Customer.objects.filter(customer_id=customer_id).first()

    def get_by_email(self, email: str) -> Customer | None:
        """Retrieve a customer by email address.

        Args:
            email: The email address to search for.

        Returns:
            The Customer if found, None otherwise.
        """
        return Customer.objects.filter(email=email).first()

    def search(self, query: str) -> QuerySet[Customer]:
        """Search customers by name or email.

        Performs a case-insensitive partial match on given_names,
        surnames, and email fields.

        Args:
            query: The search string.

        Returns:
            A QuerySet of matching customers.
        """
        return Customer.objects.filter(
            Q(given_names__icontains=query)
            | Q(surnames__icontains=query)
            | Q(email__icontains=query)
        )

    def save(self, customer: Customer) -> Customer:
        """Save an existing customer.

        Validates the customer before saving.

        Args:
            customer: The customer to save.

        Returns:
            The saved Customer.

        Raises:
            ValidationError: If the customer data is invalid.
        """
        customer.full_clean()
        customer.save()
        return customer

    def create(
        self,
        given_names: str,
        surnames: str,
        email: str,
        phone: str = "",
    ) -> Customer:
        """Create a new customer.

        Args:
            given_names: The customer's given names.
            surnames: The customer's surnames.
            email: The customer's email address.
            phone: The customer's phone number (optional).

        Returns:
            The newly created Customer.

        Raises:
            ValidationError: If the customer data is invalid.
        """
        customer = Customer(
            given_names=given_names,
            surnames=surnames,
            email=email,
            phone=phone,
        )
        customer.full_clean()
        customer.save()
        return customer

    def delete(self, customer: Customer) -> None:
        """Delete a customer.

        Args:
            customer: The customer to delete.
        """
        customer.delete()
