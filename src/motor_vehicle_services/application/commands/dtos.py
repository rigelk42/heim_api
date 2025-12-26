"""Command DTOs for the Motor Vehicle Services application layer.

Commands represent intentions to change state in the system.
They are immutable data structures that carry all information
needed to perform a write operation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateMotorVehicleCommand:
    """Command to register a new motor vehicle.

    Attributes:
        vin: Vehicle Identification Number (17 characters).
        make: Vehicle manufacturer.
        model: Vehicle model name.
        year: Model year.
        color: Vehicle color (optional).
        fuel_type: Fuel type - petrol, diesel, electric, hybrid, lpg.
        transmission: Transmission type - manual, automatic, cvt.
        engine_capacity_cc: Engine capacity in cubic centimeters (optional).
        mileage_km: Current mileage in kilometers.
        license_plate: License plate number (optional).
        license_plate_state: Issuing state/province (optional).
    """

    vin: str
    make: str
    model: str
    year: int
    color: str = ""
    fuel_type: str = "petrol"
    transmission: str = "manual"
    engine_capacity_cc: int | None = None
    mileage_km: int = 0
    license_plate: str = ""
    license_plate_state: str = ""


@dataclass(frozen=True)
class UpdateMotorVehicleCommand:
    """Command to update a motor vehicle's details.

    Only non-None fields will be updated.

    Attributes:
        vehicle_id: The ID of the vehicle to update.
        color: New color (optional).
        fuel_type: New fuel type (optional).
        transmission: New transmission type (optional).
        engine_capacity_cc: New engine capacity (optional).
        license_plate: New license plate (optional).
        license_plate_state: New license plate state (optional).
    """

    vehicle_id: int
    color: str | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    engine_capacity_cc: int | None = None
    license_plate: str | None = None
    license_plate_state: str | None = None


@dataclass(frozen=True)
class UpdateMotorVehicleMileageCommand:
    """Command to update a vehicle's mileage.

    Attributes:
        vehicle_id: The ID of the vehicle to update.
        mileage_km: The new mileage in kilometers.
    """

    vehicle_id: int
    mileage_km: int


@dataclass(frozen=True)
class ChangeMotorVehicleStatusCommand:
    """Command to change a vehicle's status.

    Attributes:
        vehicle_id: The ID of the vehicle.
        status: The new status - active, sold, scrapped, stolen.
    """

    vehicle_id: int
    status: str


@dataclass(frozen=True)
class DeleteMotorVehicleCommand:
    """Command to delete a motor vehicle.

    Attributes:
        vehicle_id: The ID of the vehicle to delete.
    """

    vehicle_id: int
