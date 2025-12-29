"""Value objects for the Customer domain.

Value objects are immutable objects that are defined by their attributes
rather than by an identity. They encapsulate validation and behavior.
"""

import re
from dataclasses import dataclass
from datetime import datetime


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


@dataclass(frozen=True)
class CustomerId:
    """Represents a unique customer identifier.

    Format: C + YY + DDD + W + HH + MM + µµµ
        - C: Fixed prefix
        - YY: Last two digits of year
        - DDD: Day of year (001-366)
        - W: Day of week (A=Monday through G=Sunday)
        - HH: Hour (00-23)
        - MM: Minute (00-59)
        - µµµ: Microseconds (first 3 digits)

    Example: C25364F1435532 (2025, day 364, Friday, 14:35, microsecond 532)

    Attributes:
        value: The customer ID string.

    Raises:
        ValueError: If the customer ID format is invalid.
    """

    value: str

    _PATTERN = re.compile(r"^C\d{2}\d{3}[A-G]\d{2}\d{2}\d{3}$")
    _WEEKDAY_LETTERS = "ABCDEFG"  # Monday=A through Sunday=G

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid customer ID format: {self.value}")

    @classmethod
    def _is_valid(cls, customer_id: str) -> bool:
        return bool(cls._PATTERN.match(customer_id))

    @classmethod
    def generate(cls, timestamp: datetime | None = None) -> "CustomerId":
        """Generate a new unique customer ID based on the current timestamp.

        Args:
            timestamp: Optional datetime to use. Defaults to current UTC time.

        Returns:
            A new CustomerId instance.
        """
        if timestamp is None:
            timestamp = datetime.now()

        year = timestamp.strftime("%y")
        day_of_year = timestamp.strftime("%j")
        weekday_letter = cls._WEEKDAY_LETTERS[timestamp.weekday()]
        hour = timestamp.strftime("%H")
        minute = timestamp.strftime("%M")
        microsecond = str(timestamp.microsecond).zfill(6)[:3]

        value = f"C{year}{day_of_year}{weekday_letter}{hour}{minute}{microsecond}"
        return cls(value=value)

    def __str__(self) -> str:
        return self.value
