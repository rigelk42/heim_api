"""Command handlers for the Motor Vehicle Services application layer.

Command handlers process commands and execute the corresponding
business operations. They coordinate between the domain layer
and infrastructure layer.
"""

from motor_vehicle_services.domain.events import (MotorVehicleCreated,
                                                  MotorVehicleDeleted,
                                                  MotorVehicleMileageUpdated,
                                                  MotorVehicleOwnerChanged,
                                                  MotorVehicleStatusChanged,
                                                  MotorVehicleUpdated)
from motor_vehicle_services.domain.exceptions import (MotorVehicleAlreadyExists,
                                                      MotorVehicleNotFound)
from motor_vehicle_services.domain.models import MotorVehicle
from motor_vehicle_services.domain.value_objects import VIN
from motor_vehicle_services.infrastructure.event_dispatcher import EventDispatcher
from motor_vehicle_services.infrastructure.repositories import MotorVehicleRepository

from .dtos import (ChangeMotorVehicleStatusCommand, CreateMotorVehicleCommand,
                   DeleteMotorVehicleCommand, TransferOwnershipCommand,
                   UpdateMotorVehicleCommand, UpdateMotorVehicleMileageCommand)


class MotorVehicleCommandHandler:
    """Handles all motor vehicle-related commands.

    This handler processes write operations for the MotorVehicle aggregate,
    including creating, updating, and deleting vehicles.
    Domain events are published after each successful operation.

    Attributes:
        repository: The repository used for data persistence.
        event_dispatcher: The dispatcher for publishing domain events.
    """

    def __init__(
        self,
        repository: MotorVehicleRepository | None = None,
        event_dispatcher: EventDispatcher | None = None,
    ):
        """Initialize the command handler.

        Args:
            repository: Optional repository instance. If not provided,
                a new MotorVehicleRepository will be created.
            event_dispatcher: Optional event dispatcher. If not provided,
                the singleton EventDispatcher will be used.
        """
        self.repository = repository or MotorVehicleRepository()
        self.event_dispatcher = event_dispatcher or EventDispatcher()

    def handle_create(self, command: CreateMotorVehicleCommand) -> MotorVehicle:
        """Create a new motor vehicle.

        Publishes a MotorVehicleCreated event on success.

        Args:
            command: The create motor vehicle command.

        Returns:
            The newly created MotorVehicle.

        Raises:
            MotorVehicleAlreadyExists: If a vehicle with the VIN already exists.
            ValueError: If the VIN is invalid.
        """
        vin = VIN(value=command.vin)

        if self.repository.get_by_vin(vin.value):
            raise MotorVehicleAlreadyExists(vin.value)

        vehicle = self.repository.create(
            vin=vin.value,
            make=command.make,
            model=command.model,
            year=command.year,
            color=command.color,
            fuel_type=command.fuel_type,
            transmission=command.transmission,
            engine_capacity_cc=command.engine_capacity_cc,
            mileage_km=command.mileage_km,
            license_plate=command.license_plate,
            license_plate_state=command.license_plate_state,
            owner_id=command.owner_id,
        )

        self.event_dispatcher.publish(
            MotorVehicleCreated(
                vehicle_id=vehicle.id,
                vin=vehicle.vin,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
            )
        )

        return vehicle

    def handle_update(self, command: UpdateMotorVehicleCommand) -> MotorVehicle:
        """Update an existing motor vehicle's details.

        Publishes a MotorVehicleUpdated event on success.

        Args:
            command: The update motor vehicle command.

        Returns:
            The updated MotorVehicle.

        Raises:
            MotorVehicleNotFound: If the vehicle does not exist.
        """
        vehicle = self.repository.get_by_id(command.vehicle_id)
        if not vehicle:
            raise MotorVehicleNotFound(command.vehicle_id)

        changes: list[tuple[str, str | int | None]] = []

        if command.color is not None:
            changes.append(("color", command.color))
            vehicle.color = command.color

        if command.fuel_type is not None:
            changes.append(("fuel_type", command.fuel_type))
            vehicle.fuel_type = command.fuel_type

        if command.transmission is not None:
            changes.append(("transmission", command.transmission))
            vehicle.transmission = command.transmission

        if command.engine_capacity_cc is not None:
            changes.append(("engine_capacity_cc", command.engine_capacity_cc))
            vehicle.engine_capacity_cc = command.engine_capacity_cc

        if command.license_plate is not None:
            changes.append(("license_plate", command.license_plate))
            vehicle.license_plate = command.license_plate.upper()

        if command.license_plate_state is not None:
            changes.append(("license_plate_state", command.license_plate_state))
            vehicle.license_plate_state = command.license_plate_state

        vehicle = self.repository.save(vehicle)

        if changes:
            self.event_dispatcher.publish(
                MotorVehicleUpdated(
                    vehicle_id=vehicle.id,
                    changes=tuple(changes),
                )
            )

        return vehicle

    def handle_update_mileage(
        self, command: UpdateMotorVehicleMileageCommand
    ) -> MotorVehicle:
        """Update a motor vehicle's mileage.

        Publishes a MotorVehicleMileageUpdated event on success.

        Args:
            command: The update mileage command.

        Returns:
            The updated MotorVehicle.

        Raises:
            MotorVehicleNotFound: If the vehicle does not exist.
            ValueError: If the new mileage is less than current.
        """
        vehicle = self.repository.get_by_id(command.vehicle_id)
        if not vehicle:
            raise MotorVehicleNotFound(command.vehicle_id)

        old_mileage = vehicle.mileage_km

        if command.mileage_km < old_mileage:
            raise ValueError(
                f"New mileage ({command.mileage_km} km) cannot be less than "
                f"current mileage ({old_mileage} km)"
            )

        vehicle.mileage_km = command.mileage_km
        vehicle = self.repository.save(vehicle)

        self.event_dispatcher.publish(
            MotorVehicleMileageUpdated(
                vehicle_id=vehicle.id,
                old_mileage_km=old_mileage,
                new_mileage_km=vehicle.mileage_km,
            )
        )

        return vehicle

    def handle_change_status(
        self, command: ChangeMotorVehicleStatusCommand
    ) -> MotorVehicle:
        """Change a motor vehicle's status.

        Publishes a MotorVehicleStatusChanged event on success.

        Args:
            command: The change status command.

        Returns:
            The updated MotorVehicle.

        Raises:
            MotorVehicleNotFound: If the vehicle does not exist.
            ValueError: If the status is invalid.
        """
        vehicle = self.repository.get_by_id(command.vehicle_id)
        if not vehicle:
            raise MotorVehicleNotFound(command.vehicle_id)

        valid_statuses = ["active", "sold", "scrapped", "stolen"]
        if command.status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{command.status}'. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )

        old_status = vehicle.status
        vehicle.status = command.status
        vehicle = self.repository.save(vehicle)

        if old_status != command.status:
            self.event_dispatcher.publish(
                MotorVehicleStatusChanged(
                    vehicle_id=vehicle.id,
                    old_status=old_status,
                    new_status=vehicle.status,
                )
            )

        return vehicle

    def handle_delete(self, command: DeleteMotorVehicleCommand) -> None:
        """Delete a motor vehicle.

        Publishes a MotorVehicleDeleted event on success.

        Args:
            command: The delete motor vehicle command.

        Raises:
            MotorVehicleNotFound: If the vehicle does not exist.
        """
        vehicle = self.repository.get_by_id(command.vehicle_id)
        if not vehicle:
            raise MotorVehicleNotFound(command.vehicle_id)

        vehicle_id = vehicle.id
        vin = vehicle.vin

        self.repository.delete(vehicle)

        self.event_dispatcher.publish(
            MotorVehicleDeleted(
                vehicle_id=vehicle_id,
                vin=vin,
            )
        )

    def handle_transfer_ownership(
        self, command: TransferOwnershipCommand
    ) -> MotorVehicle:
        """Transfer a vehicle's ownership to a new owner.

        Publishes a MotorVehicleOwnerChanged event on success.

        Args:
            command: The transfer ownership command.

        Returns:
            The updated MotorVehicle.

        Raises:
            MotorVehicleNotFound: If the vehicle does not exist.
        """
        vehicle = self.repository.get_by_id(command.vehicle_id)
        if not vehicle:
            raise MotorVehicleNotFound(command.vehicle_id)

        old_owner_id = vehicle.owner_id if vehicle.owner else None

        if command.new_owner_id is not None:
            from customer_management.domain.models import Customer

            owner = Customer.objects.filter(id=command.new_owner_id).first()
            if not owner:
                raise ValueError(f"Customer with ID {command.new_owner_id} not found")
            vehicle.owner = owner
        else:
            vehicle.owner = None

        vehicle = self.repository.save(vehicle)

        new_owner_id = vehicle.owner_id if vehicle.owner else None

        if old_owner_id != new_owner_id:
            self.event_dispatcher.publish(
                MotorVehicleOwnerChanged(
                    vehicle_id=vehicle.id,
                    old_owner_id=old_owner_id,
                    new_owner_id=new_owner_id,
                )
            )

        return vehicle
