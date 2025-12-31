"""Tests for Payment command handlers."""

from decimal import Decimal

from django.test import TestCase

from customer_management.domain.models import Customer
from motor_vehicle_services.domain.models import MotorVehicle, Transaction
from payments.application import (
    CancelPaymentCommand,
    CompletePaymentCommand,
    CreatePaymentCommand,
    DeletePaymentCommand,
    PaymentCommandHandler,
    RefundPaymentCommand,
    UpdatePaymentCommand,
)
from payments.domain.exceptions import InvalidPaymentState, PaymentNotFound
from payments.domain.models import Payment


class CreatePaymentCommandTest(TestCase):
    """Tests for CreatePaymentCommand handler."""

    def setUp(self):
        self.handler = PaymentCommandHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200001",
            given_names="John",
            surnames="Doe",
            email="john.doe@example.com",
        )
        self.vehicle = MotorVehicle.objects.create(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.transaction = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            transaction_type="RNW",
            transaction_date="2025-01-01",
            transaction_amount=Decimal("150.00"),
        )

    def test_create_payment_success(self):
        command = CreatePaymentCommand(
            transaction_id=self.transaction.transaction_id,
            payment_method="CASH",
            amount=Decimal("150.00"),
        )

        payment = self.handler.handle_create(command)

        self.assertIsNotNone(payment.payment_id)
        self.assertEqual(payment.transaction_id, self.transaction.transaction_id)
        self.assertEqual(payment.payment_method, "CASH")
        self.assertEqual(payment.amount, Decimal("150.00"))
        self.assertEqual(payment.status, "PENDING")
        self.assertEqual(Payment.objects.count(), 1)

    def test_create_payment_with_reference_number(self):
        command = CreatePaymentCommand(
            transaction_id=self.transaction.transaction_id,
            payment_method="CHECK",
            amount=Decimal("150.00"),
            reference_number="CHK-12345",
        )

        payment = self.handler.handle_create(command)

        self.assertEqual(payment.reference_number, "CHK-12345")

    def test_create_payment_with_notes(self):
        command = CreatePaymentCommand(
            transaction_id=self.transaction.transaction_id,
            payment_method="CASH",
            amount=Decimal("150.00"),
            notes="Exact change provided",
        )

        payment = self.handler.handle_create(command)

        self.assertEqual(payment.notes, "Exact change provided")

    def test_create_payment_invalid_transaction_raises(self):
        import uuid

        command = CreatePaymentCommand(
            transaction_id=uuid.uuid4(),  # Non-existent transaction
            payment_method="CASH",
            amount=Decimal("150.00"),
        )

        with self.assertRaises(ValueError) as context:
            self.handler.handle_create(command)

        self.assertIn("not found", str(context.exception))


class UpdatePaymentCommandTest(TestCase):
    """Tests for UpdatePaymentCommand handler."""

    def setUp(self):
        self.handler = PaymentCommandHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200002",
            given_names="Jane",
            surnames="Smith",
            email="jane.smith@example.com",
        )
        self.vehicle = MotorVehicle.objects.create(
            vin="1HGCM82633A004353",
            make="Toyota",
            model="Camry",
            year=2021,
        )
        self.transaction = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            transaction_type="RNW",
            transaction_date="2025-01-01",
            transaction_amount=Decimal("200.00"),
        )
        self.payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("200.00"),
        )

    def test_update_payment_method(self):
        command = UpdatePaymentCommand(
            payment_id=self.payment.payment_id,
            payment_method="CARD",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.payment_method, "CARD")

    def test_update_payment_amount(self):
        command = UpdatePaymentCommand(
            payment_id=self.payment.payment_id,
            amount=Decimal("250.00"),
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.amount, Decimal("250.00"))

    def test_update_payment_reference_number(self):
        command = UpdatePaymentCommand(
            payment_id=self.payment.payment_id,
            reference_number="REF-67890",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.reference_number, "REF-67890")

    def test_update_payment_not_found_raises(self):
        import uuid

        command = UpdatePaymentCommand(
            payment_id=uuid.uuid4(),
            payment_method="CARD",
        )

        with self.assertRaises(PaymentNotFound):
            self.handler.handle_update(command)


class DeletePaymentCommandTest(TestCase):
    """Tests for DeletePaymentCommand handler."""

    def setUp(self):
        self.handler = PaymentCommandHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200003",
            given_names="Bob",
            surnames="Wilson",
            email="bob.wilson@example.com",
        )
        self.vehicle = MotorVehicle.objects.create(
            vin="1HGCM82633A004354",
            make="Ford",
            model="Focus",
            year=2019,
        )
        self.transaction = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            transaction_type="TNSF",
            transaction_date="2025-01-01",
            transaction_amount=Decimal("300.00"),
        )
        self.payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("300.00"),
        )

    def test_delete_payment_success(self):
        command = DeletePaymentCommand(payment_id=self.payment.payment_id)

        self.handler.handle_delete(command)

        self.assertEqual(Payment.objects.count(), 0)

    def test_delete_payment_not_found_raises(self):
        import uuid

        command = DeletePaymentCommand(payment_id=uuid.uuid4())

        with self.assertRaises(PaymentNotFound):
            self.handler.handle_delete(command)


class CompletePaymentCommandTest(TestCase):
    """Tests for CompletePaymentCommand handler."""

    def setUp(self):
        self.handler = PaymentCommandHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200004",
            given_names="Alice",
            surnames="Brown",
            email="alice.brown@example.com",
        )
        self.vehicle = MotorVehicle.objects.create(
            vin="1HGCM82633A004355",
            make="Chevrolet",
            model="Malibu",
            year=2022,
        )
        self.transaction = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            transaction_type="RNW",
            transaction_date="2025-01-01",
            transaction_amount=Decimal("250.00"),
        )

    def test_complete_payment_success(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("250.00"),
            status="PENDING",
        )
        command = CompletePaymentCommand(payment_id=payment.payment_id)

        completed = self.handler.handle_complete(command)

        self.assertEqual(completed.status, "COMPLETED")

    def test_complete_payment_not_pending_raises(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("250.00"),
            status="COMPLETED",
        )
        command = CompletePaymentCommand(payment_id=payment.payment_id)

        with self.assertRaises(InvalidPaymentState):
            self.handler.handle_complete(command)

    def test_complete_payment_not_found_raises(self):
        import uuid

        command = CompletePaymentCommand(payment_id=uuid.uuid4())

        with self.assertRaises(PaymentNotFound):
            self.handler.handle_complete(command)


class RefundPaymentCommandTest(TestCase):
    """Tests for RefundPaymentCommand handler."""

    def setUp(self):
        self.handler = PaymentCommandHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200005",
            given_names="Charlie",
            surnames="Davis",
            email="charlie.davis@example.com",
        )
        self.vehicle = MotorVehicle.objects.create(
            vin="1HGCM82633A004356",
            make="Nissan",
            model="Altima",
            year=2023,
        )
        self.transaction = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            transaction_type="RNW",
            transaction_date="2025-01-01",
            transaction_amount=Decimal("175.00"),
        )

    def test_refund_payment_success(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("175.00"),
            status="COMPLETED",
        )
        command = RefundPaymentCommand(payment_id=payment.payment_id)

        refunded = self.handler.handle_refund(command)

        self.assertEqual(refunded.status, "REFUNDED")

    def test_refund_payment_not_completed_raises(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("175.00"),
            status="PENDING",
        )
        command = RefundPaymentCommand(payment_id=payment.payment_id)

        with self.assertRaises(InvalidPaymentState):
            self.handler.handle_refund(command)

    def test_refund_payment_not_found_raises(self):
        import uuid

        command = RefundPaymentCommand(payment_id=uuid.uuid4())

        with self.assertRaises(PaymentNotFound):
            self.handler.handle_refund(command)


class CancelPaymentCommandTest(TestCase):
    """Tests for CancelPaymentCommand handler."""

    def setUp(self):
        self.handler = PaymentCommandHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200006",
            given_names="Diana",
            surnames="Evans",
            email="diana.evans@example.com",
        )
        self.vehicle = MotorVehicle.objects.create(
            vin="1HGCM82633A004357",
            make="Hyundai",
            model="Sonata",
            year=2024,
        )
        self.transaction = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            transaction_type="RNW",
            transaction_date="2025-01-01",
            transaction_amount=Decimal("225.00"),
        )

    def test_cancel_payment_success(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="ACH",
            amount=Decimal("225.00"),
            status="PENDING",
        )
        command = CancelPaymentCommand(payment_id=payment.payment_id)

        cancelled = self.handler.handle_cancel(command)

        self.assertEqual(cancelled.status, "CANCELLED")

    def test_cancel_payment_not_pending_raises(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="ACH",
            amount=Decimal("225.00"),
            status="COMPLETED",
        )
        command = CancelPaymentCommand(payment_id=payment.payment_id)

        with self.assertRaises(InvalidPaymentState):
            self.handler.handle_cancel(command)

    def test_cancel_payment_not_found_raises(self):
        import uuid

        command = CancelPaymentCommand(payment_id=uuid.uuid4())

        with self.assertRaises(PaymentNotFound):
            self.handler.handle_cancel(command)
