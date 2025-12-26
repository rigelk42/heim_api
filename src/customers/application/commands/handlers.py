from customers.domain.exceptions import CustomerAlreadyExists, CustomerNotFound
from customers.domain.models import Address, Customer
from customers.domain.value_objects import Email, PersonName, PhoneNumber
from customers.infrastructure.repositories import CustomerRepository

from .dtos import (AddCustomerAddressCommand, CreateCustomerCommand,
                   DeleteCustomerCommand, RemoveCustomerAddressCommand,
                   UpdateCustomerCommand, UpdateCustomerEmailCommand)


class CustomerCommandHandler:
    def __init__(self, repository: CustomerRepository | None = None):
        self.repository = repository or CustomerRepository()

    def handle_create(self, command: CreateCustomerCommand) -> Customer:
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
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        self.repository.delete(customer)

    def handle_add_address(self, command: AddCustomerAddressCommand) -> Address:
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
        customer = self.repository.get_by_id(command.customer_id)
        if not customer:
            raise CustomerNotFound(command.customer_id)

        return customer.remove_address(command.address_id)
