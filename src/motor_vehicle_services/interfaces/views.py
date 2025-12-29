"""REST API views for the Motor Vehicle Services bounded context.

Views handle HTTP requests and responses, translating between
the external API format and the application layer commands/queries.
"""

from datetime import datetime
from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from motor_vehicle_services.application import (
    CreateMotorVehicleCommand,
    CreateTransactionCommand,
    DeleteMotorVehicleCommand,
    DeleteTransactionCommand,
    GetMotorVehicleByVINQuery,
    GetMotorVehicleQuery,
    GetTransactionQuery,
    ListMotorVehiclesByOwnerQuery,
    ListMotorVehiclesQuery,
    ListTransactionsByCustomerQuery,
    ListTransactionsByVehicleQuery,
    ListTransactionsQuery,
    MotorVehicleCommandHandler,
    MotorVehicleQueryHandler,
    SearchMotorVehiclesQuery,
    TransactionCommandHandler,
    TransactionQueryHandler,
    TransferOwnershipCommand,
    UpdateMotorVehicleCommand,
    UpdateMotorVehicleMileageCommand,
    UpdateTransactionCommand,
)
from motor_vehicle_services.domain.exceptions import (
    MotorVehicleAlreadyExists,
    MotorVehicleNotFound,
    TransactionNotFound,
)


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
        "mileage_km": vehicle.mileage_km,
        "full_name": vehicle.full_name,
        "owner_id": vehicle.owner_id,
        "owner_name": vehicle.owner_name,
    }


class MotorVehicleListCreateView(APIView):
    """View for listing and creating motor vehicles."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

    def get(self, request):
        """List all motor vehicles, optionally filtered by search."""
        search = request.query_params.get("q")

        if search:
            query = SearchMotorVehiclesQuery(query=search)
            vehicles = self.query_handler.handle_search(query)
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
            mileage_km=request.data.get("mileage_km", 0),
            license_plate=request.data.get("license_plate", ""),
            license_plate_state=request.data.get("license_plate_state", ""),
            owner_id=request.data.get("owner_id"),
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


class MotorVehicleOwnerView(APIView):
    """View for transferring a motor vehicle's ownership."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = MotorVehicleCommandHandler()

    def patch(self, request, vehicle_id: int):
        """Transfer ownership of a motor vehicle."""
        new_owner_id = request.data.get("owner_id")

        command = TransferOwnershipCommand(
            vehicle_id=vehicle_id,
            new_owner_id=new_owner_id,
        )

        try:
            vehicle = self.command_handler.handle_transfer_ownership(command)
        except MotorVehicleNotFound:
            return Response(
                {"error": "Motor vehicle not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_serialize_vehicle(vehicle))


class MotorVehiclesByOwnerView(APIView):
    """View for listing motor vehicles by owner."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_handler = MotorVehicleQueryHandler()

    def get(self, request, owner_id: int):
        """List all vehicles owned by a customer."""
        query = ListMotorVehiclesByOwnerQuery(owner_id=owner_id)
        vehicles = self.query_handler.handle_list_by_owner(query)
        data = [_serialize_vehicle(v) for v in vehicles]
        return Response(data)


def _serialize_transaction(transaction) -> dict:
    """Serialize a Transaction to a dictionary."""
    return {
        "id": transaction.id,
        "customer_id": transaction.customer_id,
        "customer_name": (
            transaction.customer.full_name if transaction.customer else None
        ),
        "vehicle_id": transaction.vehicle_id,
        "vehicle_name": transaction.vehicle.full_name if transaction.vehicle else None,
        "transaction_type": transaction.transaction_type,
        "transaction_date": transaction.transaction_date.isoformat(),
        "transaction_amount": str(transaction.transaction_amount),
        "created_at": transaction.created_at.isoformat(),
        "updated_at": transaction.updated_at.isoformat(),
    }


class TransactionListCreateView(APIView):
    """View for listing and creating transactions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = TransactionCommandHandler()
        self.query_handler = TransactionQueryHandler()

    def get(self, request):
        """List all transactions."""
        query = ListTransactionsQuery()
        transactions = self.query_handler.handle_list(query)
        data = [_serialize_transaction(t) for t in transactions]
        return Response(data)

    def post(self, request):
        """Create a new transaction."""
        try:
            transaction_date = datetime.strptime(
                request.data.get("transaction_date", ""), "%Y-%m-%d"
            ).date()
        except ValueError:
            return Response(
                {"error": "Invalid transaction_date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction_amount = Decimal(str(request.data.get("transaction_amount", 0)))
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid transaction_amount."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = CreateTransactionCommand(
            customer_id=request.data.get("customer_id", 0),
            vehicle_id=request.data.get("vehicle_id", 0),
            transaction_type=request.data.get("transaction_type", "renew"),
            transaction_date=transaction_date,
            transaction_amount=transaction_amount,
        )

        try:
            transaction = self.command_handler.handle_create(command)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            _serialize_transaction(transaction), status=status.HTTP_201_CREATED
        )


class TransactionDetailView(APIView):
    """View for retrieving, updating, and deleting a transaction."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = TransactionCommandHandler()
        self.query_handler = TransactionQueryHandler()

    def get(self, request, transaction_id: int):
        """Retrieve a transaction by ID."""
        query = GetTransactionQuery(transaction_id=transaction_id)

        try:
            transaction = self.query_handler.handle_get(query)
        except TransactionNotFound:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(_serialize_transaction(transaction))

    def patch(self, request, transaction_id: int):
        """Update a transaction."""
        transaction_type = request.data.get("transaction_type")
        transaction_date = None
        transaction_amount = None

        if "transaction_date" in request.data:
            try:
                transaction_date = datetime.strptime(
                    request.data.get("transaction_date"), "%Y-%m-%d"
                ).date()
            except ValueError:
                return Response(
                    {"error": "Invalid transaction_date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if "transaction_amount" in request.data:
            try:
                transaction_amount = Decimal(
                    str(request.data.get("transaction_amount"))
                )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid transaction_amount."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        command = UpdateTransactionCommand(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            transaction_date=transaction_date,
            transaction_amount=transaction_amount,
        )

        try:
            transaction = self.command_handler.handle_update(command)
        except TransactionNotFound:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(_serialize_transaction(transaction))

    def delete(self, request, transaction_id: int):
        """Delete a transaction."""
        command = DeleteTransactionCommand(transaction_id=transaction_id)

        try:
            self.command_handler.handle_delete(command)
        except TransactionNotFound:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class TransactionsByCustomerView(APIView):
    """View for listing transactions by customer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_handler = TransactionQueryHandler()

    def get(self, request, customer_id: int):
        """List all transactions for a customer."""
        query = ListTransactionsByCustomerQuery(customer_id=customer_id)
        transactions = self.query_handler.handle_list_by_customer(query)
        data = [_serialize_transaction(t) for t in transactions]
        return Response(data)


class TransactionsByVehicleView(APIView):
    """View for listing transactions by vehicle."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_handler = TransactionQueryHandler()

    def get(self, request, vehicle_id: int):
        """List all transactions for a vehicle."""
        query = ListTransactionsByVehicleQuery(vehicle_id=vehicle_id)
        transactions = self.query_handler.handle_list_by_vehicle(query)
        data = [_serialize_transaction(t) for t in transactions]
        return Response(data)
