"""Value objects for the Motor Vehicle Services domain.

Value objects are immutable objects that are defined by their attributes
rather than by an identity. They encapsulate validation and behavior.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class VIN:
    """Represents a validated Vehicle Identification Number.

    A VIN is a unique 17-character code used to identify motor vehicles.

    Attributes:
        value: The VIN string (17 alphanumeric characters, excluding I, O, Q).

    Raises:
        ValueError: If the VIN format is invalid.
    """

    value: str

    def __post_init__(self):
        normalized = self._normalize(self.value)
        if not self._is_valid(normalized):
            raise ValueError(f"Invalid VIN: {self.value}")
        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(vin: str) -> str:
        """Normalize VIN to uppercase without spaces."""
        return vin.upper().replace(" ", "").replace("-", "")

    @staticmethod
    def _is_valid(vin: str) -> bool:
        """Validate VIN format (17 chars, no I, O, Q)."""
        if len(vin) != 17:
            return False
        pattern = r"^[A-HJ-NPR-Z0-9]{17}$"
        return bool(re.match(pattern, vin))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class LicensePlate:
    """Represents a vehicle license plate.

    Attributes:
        value: The license plate number.
        state_province: The issuing state or province (optional).

    Raises:
        ValueError: If the license plate is empty.
    """

    value: str
    state_province: str = ""

    def __post_init__(self):
        normalized = self.value.upper().strip()
        if not normalized:
            raise ValueError("License plate cannot be empty")
        object.__setattr__(self, "value", normalized)

    @property
    def full_plate(self) -> str:
        """Return the full plate with state/province if available."""
        if self.state_province:
            return f"{self.value} ({self.state_province})"
        return self.value

    def __str__(self) -> str:
        return self.full_plate


@dataclass(frozen=True)
class Mileage:
    """Represents a vehicle's mileage/odometer reading.

    Attributes:
        value: The mileage value in kilometers.
        unit: The unit of measurement ('km' or 'mi').

    Raises:
        ValueError: If the mileage is negative.
    """

    value: int
    unit: str = "km"

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Mileage cannot be negative")
        if self.unit not in ("km", "mi"):
            raise ValueError("Unit must be 'km' or 'mi'")

    @property
    def in_kilometers(self) -> int:
        """Return mileage in kilometers."""
        if self.unit == "mi":
            return int(self.value * 1.60934)
        return self.value

    @property
    def in_miles(self) -> int:
        """Return mileage in miles."""
        if self.unit == "km":
            return int(self.value * 0.621371)
        return self.value

    def __str__(self) -> str:
        return f"{self.value:,} {self.unit}"
