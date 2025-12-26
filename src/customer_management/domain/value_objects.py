"""Value objects for the Customer domain.

Value objects are immutable objects that are defined by their attributes
rather than by an identity. They encapsulate validation and behavior.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Represents a validated email address.

    Attributes:
        value: The email address string.

    Raises:
        ValueError: If the email format is invalid.
    """

    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PhoneNumber:
    """Represents a normalized phone number.

    Phone numbers are automatically normalized by removing all non-digit
    characters except the leading '+' sign.

    Attributes:
        value: The normalized phone number string.
    """

    value: str

    def __post_init__(self):
        normalized = self._normalize(self.value)
        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(phone: str) -> str:
        return re.sub(r"[^\d+]", "", phone)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PersonName:
    """Represents a person's full name.

    Attributes:
        given_names: The person's given (first) names.
        surnames: The person's family names.

    Raises:
        ValueError: If given_names or surnames are empty.
    """

    given_names: str
    surnames: str

    def __post_init__(self):
        if not self.given_names or not self.given_names.strip():
            raise ValueError("Given names cannot be empty")
        if not self.surnames or not self.surnames.strip():
            raise ValueError("Surnames cannot be empty")

    @property
    def full_name(self) -> str:
        """Return the full name in 'Given Surnames' format."""
        return f"{self.given_names} {self.surnames}"

    @property
    def formal_name(self) -> str:
        """Return the name in formal 'Surnames, Given' format."""
        return f"{self.surnames}, {self.given_names}"

    def __str__(self) -> str:
        return self.full_name
