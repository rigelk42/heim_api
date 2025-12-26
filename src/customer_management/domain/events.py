"""Domain events for the Customer bounded context.

Domain events represent something meaningful that happened in the domain.
They are immutable records of past occurrences that other parts of the
system can react to.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events.

    Attributes:
        event_id: Unique identifier for this event instance.
        occurred_at: Timestamp when the event occurred.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def event_type(self) -> str:
        """Return the event type name."""
        return self.__class__.__name__


@dataclass(frozen=True)
class CustomerCreated(DomainEvent):
    """Event raised when a new customer is created.

    Attributes:
        customer_id: The ID of the created customer.
        email: The customer's email address.
        given_names: The customer's given names.
        surnames: The customer's surnames.
    """

    customer_id: int = 0
    email: str = ""
    given_names: str = ""
    surnames: str = ""


@dataclass(frozen=True)
class CustomerUpdated(DomainEvent):
    """Event raised when a customer's details are updated.

    Attributes:
        customer_id: The ID of the updated customer.
        changes: Dictionary of field names to new values.
    """

    customer_id: int = 0
    changes: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class CustomerEmailChanged(DomainEvent):
    """Event raised when a customer's email address is changed.

    Attributes:
        customer_id: The ID of the customer.
        old_email: The previous email address.
        new_email: The new email address.
    """

    customer_id: int = 0
    old_email: str = ""
    new_email: str = ""


@dataclass(frozen=True)
class CustomerDeleted(DomainEvent):
    """Event raised when a customer is deleted.

    Attributes:
        customer_id: The ID of the deleted customer.
        email: The customer's email address (for reference).
    """

    customer_id: int = 0
    email: str = ""


@dataclass(frozen=True)
class CustomerAddressAdded(DomainEvent):
    """Event raised when an address is added to a customer.

    Attributes:
        customer_id: The ID of the customer.
        address_id: The ID of the new address.
        address_type: The type of address (home, work, etc.).
        is_primary: Whether this is the primary address.
    """

    customer_id: int = 0
    address_id: int = 0
    address_type: str = ""
    is_primary: bool = False


@dataclass(frozen=True)
class CustomerAddressRemoved(DomainEvent):
    """Event raised when an address is removed from a customer.

    Attributes:
        customer_id: The ID of the customer.
        address_id: The ID of the removed address.
    """

    customer_id: int = 0
    address_id: int = 0
