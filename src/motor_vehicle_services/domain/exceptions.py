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


class TransactionNotFound(MotorVehicleServiceException):
    """Raised when a transaction cannot be found by the given identifier.

    Attributes:
        identifier: The transaction ID that was not found.
    """

    def __init__(self, identifier: int):
        self.identifier = identifier
        super().__init__(f"Transaction not found: {identifier}")
