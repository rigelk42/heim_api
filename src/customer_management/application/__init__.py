from .commands import (
    AddCustomerAddressCommand,
    CreateCustomerCommand,
    CustomerCommandHandler,
    DeleteCustomerCommand,
    RemoveCustomerAddressCommand,
    UpdateCustomerCommand,
    UpdateCustomerEmailCommand,
)
from .queries import (
    CustomerQueryHandler,
    GetCustomerAddressesQuery,
    GetCustomerQuery,
    ListCustomersQuery,
    SearchCustomersQuery,
)

__all__ = [
    # Commands
    "CreateCustomerCommand",
    "UpdateCustomerCommand",
    "UpdateCustomerEmailCommand",
    "DeleteCustomerCommand",
    "AddCustomerAddressCommand",
    "RemoveCustomerAddressCommand",
    "CustomerCommandHandler",
    # Queries
    "GetCustomerQuery",
    "ListCustomersQuery",
    "SearchCustomersQuery",
    "GetCustomerAddressesQuery",
    "CustomerQueryHandler",
]
