"""Repository implementations for the Motor Vehicle Services domain.

Repositories abstract data access and provide a collection-like interface
for working with domain entities. They hide the details of data persistence.
"""

from django.db.models import Q, QuerySet

from motor_vehicle_services.domain.models import MotorVehicle


class MotorVehicleRepository:
    """Repository for MotorVehicle aggregate persistence.

    Provides methods for storing, retrieving, and querying MotorVehicle entities.
    This implementation uses Django's ORM for data access.
    """

    def get_all(self) -> QuerySet[MotorVehicle]:
        """Retrieve all motor vehicles.

        Returns:
            A QuerySet of all vehicles, ordered by year (desc), make, model.
        """
        return MotorVehicle.objects.all()

    def get_by_id(self, vehicle_id: int) -> MotorVehicle | None:
        """Retrieve a motor vehicle by ID.

        Args:
            vehicle_id: The ID of the vehicle to retrieve.

        Returns:
            The MotorVehicle if found, None otherwise.
        """
        return MotorVehicle.objects.filter(id=vehicle_id).first()

    def get_by_vin(self, vin: str) -> MotorVehicle | None:
        """Retrieve a motor vehicle by VIN.

        Args:
            vin: The Vehicle Identification Number to search for.

        Returns:
            The MotorVehicle if found, None otherwise.
        """
        return MotorVehicle.objects.filter(vin=vin.upper()).first()

    def get_by_license_plate(self, license_plate: str) -> MotorVehicle | None:
        """Retrieve a motor vehicle by license plate.

        Args:
            license_plate: The license plate to search for.

        Returns:
            The MotorVehicle if found, None otherwise.
        """
        return MotorVehicle.objects.filter(license_plate=license_plate.upper()).first()

    def get_by_status(self, status: str) -> QuerySet[MotorVehicle]:
        """Retrieve all motor vehicles with a specific status.

        Args:
            status: The status to filter by (active, sold, scrapped, stolen).

        Returns:
            A QuerySet of matching vehicles.
        """
        return MotorVehicle.objects.filter(status=status)

    def search(self, query: str) -> QuerySet[MotorVehicle]:
        """Search motor vehicles by VIN, make, model, or license plate.

        Performs a case-insensitive partial match.

        Args:
            query: The search string.

        Returns:
            A QuerySet of matching vehicles.
        """
        return MotorVehicle.objects.filter(
            Q(vin__icontains=query)
            | Q(make__icontains=query)
            | Q(model__icontains=query)
            | Q(license_plate__icontains=query)
        )

    def save(self, vehicle: MotorVehicle) -> MotorVehicle:
        """Save an existing motor vehicle.

        Validates the vehicle before saving.

        Args:
            vehicle: The vehicle to save.

        Returns:
            The saved MotorVehicle.

        Raises:
            ValidationError: If the vehicle data is invalid.
        """
        vehicle.full_clean()
        vehicle.save()
        return vehicle

    def create(
        self,
        vin: str,
        make: str,
        model: str,
        year: int,
        color: str = "",
        fuel_type: str = "petrol",
        transmission: str = "manual",
        engine_capacity_cc: int | None = None,
        mileage_km: int = 0,
        license_plate: str = "",
        license_plate_state: str = "",
    ) -> MotorVehicle:
        """Create a new motor vehicle.

        Args:
            vin: Vehicle Identification Number.
            make: Vehicle manufacturer.
            model: Vehicle model name.
            year: Model year.
            color: Vehicle color.
            fuel_type: Fuel type.
            transmission: Transmission type.
            engine_capacity_cc: Engine capacity in cc.
            mileage_km: Current mileage in kilometers.
            license_plate: License plate number.
            license_plate_state: License plate issuing state.

        Returns:
            The newly created MotorVehicle.

        Raises:
            ValidationError: If the vehicle data is invalid.
        """
        vehicle = MotorVehicle(
            vin=vin.upper(),
            make=make,
            model=model,
            year=year,
            color=color,
            fuel_type=fuel_type,
            transmission=transmission,
            engine_capacity_cc=engine_capacity_cc,
            mileage_km=mileage_km,
            license_plate=license_plate.upper() if license_plate else "",
            license_plate_state=license_plate_state,
        )
        vehicle.full_clean()
        vehicle.save()
        return vehicle

    def delete(self, vehicle: MotorVehicle) -> None:
        """Delete a motor vehicle.

        Args:
            vehicle: The vehicle to delete.
        """
        vehicle.delete()
