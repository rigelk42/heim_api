from django.db.models import QuerySet

from customers.domain.exceptions import CustomerNotFound
from customers.domain.models import Address, Customer
from customers.infrastructure.repositories import CustomerRepository

from .dtos import (GetCustomerAddressesQuery, GetCustomerQuery, ListCustomersQuery,
                   SearchCustomersQuery)


class CustomerQueryHandler:
    def __init__(self, repository: CustomerRepository | None = None):
        self.repository = repository or CustomerRepository()

    def handle_get(self, query: GetCustomerQuery) -> Customer:
        customer = self.repository.get_by_id(query.customer_id)
        if not customer:
            raise CustomerNotFound(query.customer_id)
        return customer

    def handle_list(self, query: ListCustomersQuery) -> QuerySet[Customer]:
        return self.repository.get_all()

    def handle_search(self, query: SearchCustomersQuery) -> QuerySet[Customer]:
        return self.repository.search(query.query)

    def handle_get_addresses(
        self, query: GetCustomerAddressesQuery
    ) -> QuerySet[Address]:
        customer = self.repository.get_by_id(query.customer_id)
        if not customer:
            raise CustomerNotFound(query.customer_id)
        return customer.get_addresses()
