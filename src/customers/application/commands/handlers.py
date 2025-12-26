"""Command handlers for the Customer application layer.

Command handlers process commands and execute the corresponding
business operations. They coordinate between the domain layer
and infrastructure layer.
"""

from customers.domain.events import (CustomerAddressAdded, CustomerAddressRemoved,
                                     CustomerCreated, CustomerDeleted,
                                     CustomerEmailChanged, CustomerUpdated)
from customers.domain.exceptions import CustomerAlreadyExists, CustomerNotFound
from customers.domain.models import Address, Customer
from customers.domain.value_objects import Email, PersonName, PhoneNumber
from customers.infrastructure.event_dispatcher import EventDispatcher
from customers.infrastructure.repositories import CustomerRepository

from .dtos import (AddCustomerAddressCommand, CreateCustomerCommand,
                   DeleteCustomerCommand, RemoveCustomerAddressCommand,
                   UpdateCustomerCommand, UpdateCustomerEmailCommand)


class CustomerCommandHandler:
    """Handles all customer-related commands.

    This handler processes write operations for the Customer aggregate,
    including creating, updating, and deleting customers and their addresses.
    Domain events are published after each successful operation.

    Attributes:
        repository: The repository used for data persistence.
        event_dispatcher: The dispatcher for publishing domain events.
    """

    def __init__(
        self,
        repository: CustomerRepository | None = None,
        event_dispatcher: EventDispatcher | None = None,
    ):
        """Initialize the command handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new CustomerRepository will be created.
            event_dispatcher: Optional event dispatcher. If not provided,
                the singleton EventDispatcher will be used.
        """
        self.repository = repository or CustomerRepository()
        self.event_dispatcher = event_dispatcher or EventDispatcher()

    def handle_create(self, command: CreateCustomerCommand) -> Customer:
        """Create a new customer.

        Publishes a CustomerCreated event on success.

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

        customer = self.repository.create(
            given_names=name.given_names,
            surnames=name.surnames,
            email=email.value,
            phone=phone.value if phone else "",
        )

        self.event_dispatcher.publish(
            CustomerCreated(
                customer_id=customer.id,
                email=customer.email,
                given_names=customer.given_names,
                surnames=customer.surnames,
            )
        )

        return customer

    def handle_update(self, command: UpdateCustomerCommand) -> Customer:
        """Update an existing customer's details.

        Publishes a CustomerUpdated event on success.

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

        changes: list[tuple[str, str | None]] = []

        if command.given_names is not None or command.surnames is not None:
            name = PersonName(
                given_names=command.given_names or customer.given_names,
                surnames=command.surnames or customer.surnames,
            )
            if command.given_names is not None:
                changes.append(("given_names", command.given_names))
            if command.surnames is not None:
                changes.append(("surnames", command.surnames))
            customer.set_name(name)

        if command.phone is not None:
            phone = PhoneNumber(value=command.phone) if command.phone else None
            changes.append(("phone", phone.value if phone else ""))
            customer.set_phone(phone)

        customer = self.repository.save(customer)

        if changes:
            self.event_dispatcher.publish(
                CustomerUpdated(
                    customer_id=customer.id,
                    changes=tuple(changes),
                )
            )

        return customer

    def handle_update_email(self, command: UpdateCustomerEmailCommand) -> Customer:
        """Update a customer's email address.

        Publishes a CustomerEmailChanged event on success.

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

        old_email = customer.email

        if self.repository.get_by_email(email.value):
            raise CustomerAlreadyExists(email.value)

        customer.set_email(email)
        customer = self.repository.save(customer)

        self.event_dispatcher.publish(
            CustomerEmailChanged(
                customer_id=customer.id,
                old_email=old_email,
                new_email=customer.email,
            )
        )

        return customer

    def handle_delete(self, command: DeleteCustomerCommand) -> None:
        """Delete a customer.

        Publishes a CustomerDeleted event on success.

        Args:
            command: The delete customer command.

        Raises:
            CustomerNotFound: If the customer does not exist.
        """
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        customer_id = customer.id
        email = customer.email

        self.repository.delete(customer)

        self.event_dispatcher.publish(
            CustomerDeleted(
                customer_id=customer_id,
                email=email,
            )
        )

    def handle_add_address(self, command: AddCustomerAddressCommand) -> Address:
        """Add an address to a customer.

        Publishes a CustomerAddressAdded event on success.

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

        address = customer.add_address(
            address_line_1=command.address_line_1,
            address_line_2=command.address_line_2,
            city=command.city,
            state_province=command.state_province,
            postal_code=command.postal_code,
            country=command.country,
            address_type=command.address_type,
            is_primary=command.is_primary,
        )

        self.event_dispatcher.publish(
            CustomerAddressAdded(
                customer_id=customer.id,
                address_id=address.id,
                address_type=address.address_type,
                is_primary=address.is_primary,
            )
        )

        return address

    def handle_remove_address(self, command: RemoveCustomerAddressCommand) -> bool:
        """Remove an address from a customer.

        Publishes a CustomerAddressRemoved event on success.

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

        removed = customer.remove_address(command.address_id)

        if removed:
            self.event_dispatcher.publish(
                CustomerAddressRemoved(
                    customer_id=customer.id,
                    address_id=command.address_id,
                )
            )

        return removed
