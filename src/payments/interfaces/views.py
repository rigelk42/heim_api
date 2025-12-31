"""REST API views for the Payments bounded context.

Views handle HTTP requests and responses, translating between
the external API format and the application layer commands/queries.
"""

from decimal import Decimal
from uuid import UUID

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.application import (
    CancelPaymentCommand,
    CompletePaymentCommand,
    CreatePaymentCommand,
    DeletePaymentCommand,
    GetPaymentQuery,
    ListPaymentsByTransactionQuery,
    ListPaymentsQuery,
    PaymentCommandHandler,
    PaymentQueryHandler,
    RefundPaymentCommand,
    UpdatePaymentCommand,
)
from payments.domain.exceptions import InvalidPaymentState, PaymentNotFound
from payments.interfaces.serializers import serialize_payment


class PaymentListCreateView(APIView):
    """View for listing and creating payments."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = PaymentCommandHandler()
        self.query_handler = PaymentQueryHandler()

    def get(self, request):
        """List all payments."""
        query = ListPaymentsQuery()
        payments = self.query_handler.handle_list(query)
        data = [serialize_payment(p) for p in payments]
        return Response(data)

    def post(self, request):
        """Create a new payment."""
        try:
            transaction_id = UUID(request.data.get("transaction_id", ""))
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid transaction_id format. Must be a valid UUID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = Decimal(str(request.data.get("amount", 0)))
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = CreatePaymentCommand(
            transaction_id=transaction_id,
            payment_method=request.data.get("payment_method", "CASH"),
            amount=amount,
            reference_number=request.data.get("reference_number", ""),
            notes=request.data.get("notes", ""),
        )

        try:
            payment = self.command_handler.handle_create(command)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serialize_payment(payment), status=status.HTTP_201_CREATED)


class PaymentDetailView(APIView):
    """View for retrieving, updating, and deleting a payment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = PaymentCommandHandler()
        self.query_handler = PaymentQueryHandler()

    def get(self, request, payment_id: str):
        """Retrieve a payment by ID."""
        try:
            uuid_id = UUID(payment_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid payment_id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = GetPaymentQuery(payment_id=uuid_id)

        try:
            payment = self.query_handler.handle_get(query)
        except PaymentNotFound:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(serialize_payment(payment))

    def patch(self, request, payment_id: str):
        """Update a payment."""
        try:
            uuid_id = UUID(payment_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid payment_id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = None
        if "amount" in request.data:
            try:
                amount = Decimal(str(request.data.get("amount")))
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid amount."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        command = UpdatePaymentCommand(
            payment_id=uuid_id,
            payment_method=request.data.get("payment_method"),
            amount=amount,
            reference_number=request.data.get("reference_number"),
            notes=request.data.get("notes"),
        )

        try:
            payment = self.command_handler.handle_update(command)
        except PaymentNotFound:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(serialize_payment(payment))

    def delete(self, request, payment_id: str):
        """Delete a payment."""
        try:
            uuid_id = UUID(payment_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid payment_id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = DeletePaymentCommand(payment_id=uuid_id)

        try:
            self.command_handler.handle_delete(command)
        except PaymentNotFound:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentCompleteView(APIView):
    """View for completing a payment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = PaymentCommandHandler()

    def post(self, request, payment_id: str):
        """Mark a payment as completed."""
        try:
            uuid_id = UUID(payment_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid payment_id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = CompletePaymentCommand(payment_id=uuid_id)

        try:
            payment = self.command_handler.handle_complete(command)
        except PaymentNotFound:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except InvalidPaymentState as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serialize_payment(payment))


class PaymentRefundView(APIView):
    """View for refunding a payment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = PaymentCommandHandler()

    def post(self, request, payment_id: str):
        """Refund a payment."""
        try:
            uuid_id = UUID(payment_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid payment_id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = RefundPaymentCommand(payment_id=uuid_id)

        try:
            payment = self.command_handler.handle_refund(command)
        except PaymentNotFound:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except InvalidPaymentState as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serialize_payment(payment))


class PaymentCancelView(APIView):
    """View for cancelling a payment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_handler = PaymentCommandHandler()

    def post(self, request, payment_id: str):
        """Cancel a payment."""
        try:
            uuid_id = UUID(payment_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid payment_id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = CancelPaymentCommand(payment_id=uuid_id)

        try:
            payment = self.command_handler.handle_cancel(command)
        except PaymentNotFound:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except InvalidPaymentState as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serialize_payment(payment))


class PaymentsByTransactionView(APIView):
    """View for listing payments by transaction."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_handler = PaymentQueryHandler()

    def get(self, request, transaction_id: str):
        """List all payments for a transaction."""
        try:
            uuid_id = UUID(transaction_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid transaction_id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = ListPaymentsByTransactionQuery(transaction_id=uuid_id)
        payments = self.query_handler.handle_list_by_transaction(query)
        data = [serialize_payment(p) for p in payments]
        return Response(data)
