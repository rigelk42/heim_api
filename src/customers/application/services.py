from django.db.models import QuerySet

from customers.domain.exceptions import CustomerAlreadyExists, CustomerNotFound
from customers.domain.models import Address, Customer
from customers.domain.value_objects import Email, PersonName, PhoneNumber
from customers.infrastructure.repositories import CustomerRepository


class CustomerService:
    def __init__(self, repository: CustomerRepository | None = None):
        self.repository = repository or CustomerRepository()

    def get_customers(self) -> QuerySet[Customer]:
        return self.repository.get_all()

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.repository.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFound(customer_id)
        return customer

    def search_customers(self, query: str) -> QuerySet[Customer]:
        return self.repository.search(query)

    def create_customer(
        self,
        given_names: str,
        surnames: str,
        email: str,
        phone: str = "",
    ) -> Customer:
        # Validate using value objects
        name = PersonName(given_names=given_names, surnames=surnames)
        email_vo = Email(value=email)
        phone_vo = PhoneNumber(value=phone) if phone else None

        if self.repository.get_by_email(email_vo.value):
            raise CustomerAlreadyExists(email_vo.value)

        return self.repository.create(
            given_names=name.given_names,
            surnames=name.surnames,
            email=email_vo.value,
            phone=phone_vo.value if phone_vo else "",
        )

    def update_customer(
        self,
        customer_id: int,
        given_names: str | None = None,
        surnames: str | None = None,
        phone: str | None = None,
    ) -> Customer:
        customer = self.get_customer(customer_id)

        if given_names is not None or surnames is not None:
            name = PersonName(
                given_names=given_names or customer.given_names,
                surnames=surnames or customer.surnames,
            )
            customer.set_name(name)

        if phone is not None:
            phone_vo = PhoneNumber(value=phone) if phone else None
            customer.set_phone(phone_vo)

        return self.repository.save(customer)

    def update_customer_email(self, customer_id: int, email: str) -> Customer:
        customer = self.get_customer(customer_id)
        email_vo = Email(value=email)

        if customer.email == email_vo.value:
            return customer

        if self.repository.get_by_email(email_vo.value):
            raise CustomerAlreadyExists(email_vo.value)

        customer.set_email(email_vo)
        return self.repository.save(customer)

    def delete_customer(self, customer_id: int) -> None:
        customer = self.get_customer(customer_id)
        self.repository.delete(customer)

    # --- Address management (through aggregate root) ---

    def add_customer_address(
        self,
        customer_id: int,
        address_line_1: str,
        city: str,
        postal_code: str,
        country: str,
        address_line_2: str = "",
        state_province: str = "",
        address_type: str = "home",
        is_primary: bool = False,
    ) -> Address:
        customer = self.get_customer(customer_id)
        return customer.add_address(
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state_province=state_province,
            postal_code=postal_code,
            country=country,
            address_type=address_type,
            is_primary=is_primary,
        )

    def get_customer_addresses(self, customer_id: int) -> QuerySet[Address]:
        customer = self.get_customer(customer_id)
        return customer.get_addresses()

    def remove_customer_address(self, customer_id: int, address_id: int) -> bool:
        customer = self.get_customer(customer_id)
        return customer.remove_address(address_id)
