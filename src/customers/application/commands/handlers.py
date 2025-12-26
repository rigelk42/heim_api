"""Command handlers for the Customer application layer.

Command handlers process commands and execute the corresponding
business operations. They coordinate between the domain layer
and infrastructure layer.
"""

from customers.domain.exceptions import CustomerAlreadyExists, CustomerNotFound
from customers.domain.models import Address, Customer
from customers.domain.value_objects import Email, PersonName, PhoneNumber
from customers.infrastructure.repositories import CustomerRepository

from .dtos import (AddCustomerAddressCommand, CreateCustomerCommand,
                   DeleteCustomerCommand, RemoveCustomerAddressCommand,
                   UpdateCustomerCommand, UpdateCustomerEmailCommand)


class CustomerCommandHandler:
    """Handles all customer-related commands.

    This handler processes write operations for the Customer aggregate,
    including creating, updating, and deleting customers and their addresses.

    Attributes:
        repository: The repository used for data persistence.
    """

    def __init__(self, repository: CustomerRepository | None = None):
        """Initialize the command handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new CustomerRepository will be created.
        """
        self.repository = repository or CustomerRepository()

    def handle_create(self, command: CreateCustomerCommand) -> Customer:
        """Create a new customer.

        Args:
            command: The create customer command.

        Returns:
            The newly created Customer.

        Raises:
            CustomerAlreadyExists: If a customer with the email already exists.
            ValueError: If the name or email is invalid.
        """
        name = PersonName(given_names=command.given_names, surnames=command.surnames)
        email = Email(value=command.email)
        phone = PhoneNumber(value=command.phone) if command.phone else None

        if self.repository.get_by_email(email.value):
            raise CustomerAlreadyExists(email.value)

        return self.repository.create(
            given_names=name.given_names,
            surnames=name.surnames,
            email=email.value,
            phone=phone.value if phone else "",
        )

    def handle_update(self, command: UpdateCustomerCommand) -> Customer:
        """Update an existing customer's details.

        Args:
            command: The update customer command.

        Returns:
            The updated Customer.

        Raises:
            CustomerNotFound: If the customer does not exist.
            ValueError: If the new name is invalid.
        """
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        if command.given_names is not None or command.surnames is not None:
            name = PersonName(
                given_names=command.given_names or customer.given_names,
                surnames=command.surnames or customer.surnames,
            )
            customer.set_name(name)

        if command.phone is not None:
            phone = PhoneNumber(value=command.phone) if command.phone else None
            customer.set_phone(phone)

        return self.repository.save(customer)

    def handle_update_email(self, command: UpdateCustomerEmailCommand) -> Customer:
        """Update a customer's email address.

        Args:
            command: The update email command.

        Returns:
            The updated Customer.

        Raises:
            CustomerNotFound: If the customer does not exist.
            CustomerAlreadyExists: If the new email is already in use.
            ValueError: If the email format is invalid.
        """
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        email = Email(value=command.email)

        if customer.email == email.value:
            return customer

        if self.repository.get_by_email(email.value):
            raise CustomerAlreadyExists(email.value)

        customer.set_email(email)
        return self.repository.save(customer)

    def handle_delete(self, command: DeleteCustomerCommand) -> None:
        """Delete a customer.

        Args:
            command: The delete customer command.

        Raises:
            CustomerNotFound: If the customer does not exist.
        """
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        self.repository.delete(customer)

    def handle_add_address(self, command: AddCustomerAddressCommand) -> Address:
        """Add an address to a customer.

        If is_primary is True, any existing primary address will be
        marked as non-primary.

        Args:
            command: The add address command.

        Returns:
            The newly created Address.

        Raises:
            CustomerNotFound: If the customer does not exist.
        """
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        return customer.add_address(
            address_line_1=command.address_line_1,
            address_line_2=command.address_line_2,
            city=command.city,
            state_province=command.state_province,
            postal_code=command.postal_code,
            country=command.country,
            address_type=command.address_type,
            is_primary=command.is_primary,
        )

    def handle_remove_address(self, command: RemoveCustomerAddressCommand) -> bool:
        """Remove an address from a customer.

        Args:
            command: The remove address command.

        Returns:
            True if the address was removed, False if not found.

        Raises:
            CustomerNotFound: If the customer does not exist.
        """
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        return customer.remove_address(command.address_id)
