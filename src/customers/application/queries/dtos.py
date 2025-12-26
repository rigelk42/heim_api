from dataclasses import dataclass


@dataclass(frozen=True)
class GetCustomerQuery:
    customer_id: int


@dataclass(frozen=True)
class ListCustomersQuery:
    pass


@dataclass(frozen=True)
class SearchCustomersQuery:
    query: str


@dataclass(frozen=True)
class GetCustomerAddressesQuery:
    customer_id: int
