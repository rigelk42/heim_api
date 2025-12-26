from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCustomerCommand:
    given_names: str
    surnames: str
    email: str
    phone: str = ""


@dataclass(frozen=True)
class UpdateCustomerCommand:
    customer_id: int
    given_names: str | None = None
    surnames: str | None = None
    phone: str | None = None


@dataclass(frozen=True)
class UpdateCustomerEmailCommand:
    customer_id: int
    email: str


@dataclass(frozen=True)
class DeleteCustomerCommand:
    customer_id: int


@dataclass(frozen=True)
class AddCustomerAddressCommand:
    customer_id: int
    address_line_1: str
    city: str
    postal_code: str
    country: str
    address_line_2: str = ""
    state_province: str = ""
    address_type: str = "home"
    is_primary: bool = False


@dataclass(frozen=True)
class RemoveCustomerAddressCommand:
    customer_id: int
    address_id: int
