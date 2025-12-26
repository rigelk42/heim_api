"""Domain exceptions for the Motor Vehicle Services bounded context.

These exceptions represent business rule violations and domain-specific
error conditions.
"""


class MotorVehicleServiceException(Exception):
    """Base exception for all motor vehicle service domain errors."""

    pass


class MotorVehicleNotFound(MotorVehicleServiceException):
    """Raised when a motor vehicle cannot be found by the given identifier.

    Attributes:
        identifier: The vehicle ID or VIN that was not found.
    """

    def __init__(self, identifier: int | str):
        self.identifier = identifier
        super().__init__(f"Motor vehicle not found: {identifier}")


class MotorVehicleAlreadyExists(MotorVehicleServiceException):
    """Raised when attempting to create a vehicle with a duplicate VIN.

    Attributes:
        vin: The VIN that already exists.
    """

    def __init__(self, vin: str):
        self.vin = vin
        super().__init__(f"Motor vehicle with VIN {vin} already exists")


class InvalidMileageUpdate(MotorVehicleServiceException):
    """Raised when attempting to set mileage lower than current reading.

    Attributes:
        current_mileage: The current mileage reading.
        new_mileage: The attempted new mileage reading.
    """

    def __init__(self, current_mileage: int, new_mileage: int):
        self.current_mileage = current_mileage
        self.new_mileage = new_mileage
        super().__init__(
            f"Cannot set mileage to {new_mileage} km; "
            f"current mileage is {current_mileage} km"
        )
