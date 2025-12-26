"""REST API views for the Motor Vehicle Services bounded context.

Views handle HTTP requests and responses, translating between
the external API format and the application layer commands/queries.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from motor_vehicle_services.application import (ChangeMotorVehicleStatusCommand,
                                                CreateMotorVehicleCommand,
                                                DeleteMotorVehicleCommand,
                                                GetMotorVehicleByVINQuery,
                                                GetMotorVehicleQuery,
                                                ListMotorVehiclesByStatusQuery,
                                                ListMotorVehiclesQuery,
                                                MotorVehicleCommandHandler,
                                                MotorVehicleQueryHandler,
                                                SearchMotorVehiclesQuery,
                                                UpdateMotorVehicleCommand,
                                                UpdateMotorVehicleMileageCommand)
from motor_vehicle_services.domain.exceptions import (MotorVehicleAlreadyExists,
                                                      MotorVehicleNotFound)


def _serialize_vehicle(vehicle) -> dict:
    """Serialize a MotorVehicle to a dictionary."""
    return {
        "id": vehicle.id,
        "vin": vehicle.vin,
        "license_plate": vehicle.license_plate,
        "license_plate_state": vehicle.license_plate_state,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "color": vehicle.color,
        "fuel_type": vehicle.fuel_type,
        "transmission": vehicle.transmission,
        "engine_capacity_cc": vehicle.engine_capacity_cc,
        "mileage_km": vehicle.mileage_km,
        "status": vehicle.status,
        "full_name": vehicle.full_name,
    }


class MotorVehicleListCreateView(APIView):
    """View for listing and creating motor vehicles."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

    def get(self, request):
        """List all motor vehicles, optionally filtered by search or status."""
        search = request.query_params.get("q")
        status_filter = request.query_params.get("status")

        if search:
            query = SearchMotorVehiclesQuery(query=search)
            vehicles = self.query_handler.handle_search(query)
        elif status_filter:
            query = ListMotorVehiclesByStatusQuery(status=status_filter)
            vehicles = self.query_handler.handle_list_by_status(query)
        else:
            query = ListMotorVehiclesQuery()
            vehicles = self.query_handler.handle_list(query)

        data = [_serialize_vehicle(v) for v in vehicles]
        return Response(data)

    def post(self, request):
        """Create a new motor vehicle."""
        command = CreateMotorVehicleCommand(
            vin=request.data.get("vin", ""),
            make=request.data.get("make", ""),
            model=request.data.get("model", ""),
            year=request.data.get("year", 0),
            color=request.data.get("color", ""),
            fuel_type=request.data.get("fuel_type", "petrol"),
            transmission=request.data.get("transmission", "manual"),
            engine_capacity_cc=request.data.get("engine_capacity_cc"),
            mileage_km=request.data.get("mileage_km", 0),
            license_plate=request.data.get("license_plate", ""),
            license_plate_state=request.data.get("license_plate_state", ""),
        )

        try:
            vehicle = self.command_handler.handle_create(command)
        except MotorVehicleAlreadyExists as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_serialize_vehicle(vehicle), status=status.HTTP_201_CREATED)


class MotorVehicleDetailView(APIView):
    """View for retrieving, updating, and deleting a motor vehicle."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

    def get(self, request, vehicle_id: int):
        """Retrieve a motor vehicle by ID."""
        query = GetMotorVehicleQuery(vehicle_id=vehicle_id)

        try:
            vehicle = self.query_handler.handle_get(query)
        except MotorVehicleNotFound:
            return Response(
                {"error": "Motor vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(_serialize_vehicle(vehicle))

    def patch(self, request, vehicle_id: int):
        """Update a motor vehicle's details."""
        command = UpdateMotorVehicleCommand(
            vehicle_id=vehicle_id,
            color=request.data.get("color"),
            fuel_type=request.data.get("fuel_type"),
            transmission=request.data.get("transmission"),
            engine_capacity_cc=request.data.get("engine_capacity_cc"),
            license_plate=request.data.get("license_plate"),
            license_plate_state=request.data.get("license_plate_state"),
        )

        try:
            vehicle = self.command_handler.handle_update(command)
        except MotorVehicleNotFound:
            return Response(
                {"error": "Motor vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_serialize_vehicle(vehicle))

    def delete(self, request, vehicle_id: int):
        """Delete a motor vehicle."""
        command = DeleteMotorVehicleCommand(vehicle_id=vehicle_id)

        try:
            self.command_handler.handle_delete(command)
        except MotorVehicleNotFound:
            return Response(
                {"error": "Motor vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MotorVehicleByVINView(APIView):
    """View for retrieving a motor vehicle by VIN."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_handler = MotorVehicleQueryHandler()

    def get(self, request, vin: str):
        """Retrieve a motor vehicle by VIN."""
        query = GetMotorVehicleByVINQuery(vin=vin)

        try:
            vehicle = self.query_handler.handle_get_by_vin(query)
        except MotorVehicleNotFound:
            return Response(
                {"error": "Motor vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(_serialize_vehicle(vehicle))


class MotorVehicleMileageView(APIView):
    """View for updating a motor vehicle's mileage."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = MotorVehicleCommandHandler()

    def patch(self, request, vehicle_id: int):
        """Update the mileage of a motor vehicle."""
        mileage_km = request.data.get("mileage_km")
        if mileage_km is None:
            return Response(
                {"error": "mileage_km is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        command = UpdateMotorVehicleMileageCommand(
            vehicle_id=vehicle_id,
            mileage_km=mileage_km,
        )

        try:
            vehicle = self.command_handler.handle_update_mileage(command)
        except MotorVehicleNotFound:
            return Response(
                {"error": "Motor vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_serialize_vehicle(vehicle))


class MotorVehicleStatusView(APIView):
    """View for changing a motor vehicle's status."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = MotorVehicleCommandHandler()

    def patch(self, request, vehicle_id: int):
        """Change the status of a motor vehicle."""
        new_status = request.data.get("status")
        if new_status is None:
            return Response(
                {"error": "status is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        command = ChangeMotorVehicleStatusCommand(
            vehicle_id=vehicle_id,
            status=new_status,
        )

        try:
            vehicle = self.command_handler.handle_change_status(command)
        except MotorVehicleNotFound:
            return Response(
                {"error": "Motor vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_serialize_vehicle(vehicle))
