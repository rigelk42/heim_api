"""Tests for Payment model."""

from decimal import Decimal

from django.test import TestCase

from customer_management.domain.models import Customer
from motor_vehicle_services.domain.models import MotorVehicle, Transaction
from payments.domain.models import Payment


class PaymentModelTest(TestCase):
    """Tests for the Payment model."""

    def setUp(self):
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

    def test_create_payment(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("150.00"),
        )

        self.assertIsNotNone(payment.payment_id)
        self.assertEqual(payment.transaction, self.transaction)
        self.assertEqual(payment.payment_method, "CASH")
        self.assertEqual(payment.amount, Decimal("150.00"))
        self.assertEqual(payment.status, "PENDING")

    def test_payment_default_status_is_pending(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("100.00"),
        )

        self.assertEqual(payment.status, "PENDING")

    def test_payment_str_representation(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("150.00"),
        )

        expected = f"Payment {payment.payment_id} - 150.00 (PENDING)"
        self.assertEqual(str(payment), expected)


class PaymentStatusPropertiesTest(TestCase):
    """Tests for Payment status properties."""

    def setUp(self):
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

    def test_is_completed_false_when_pending(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("100.00"),
            status="PENDING",
        )

        self.assertFalse(payment.is_completed)

    def test_is_completed_true_when_completed(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("100.00"),
            status="COMPLETED",
        )

        self.assertTrue(payment.is_completed)

    def test_is_refundable_true_when_completed(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("100.00"),
            status="COMPLETED",
        )

        self.assertTrue(payment.is_refundable)

    def test_is_refundable_false_when_pending(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("100.00"),
            status="PENDING",
        )

        self.assertFalse(payment.is_refundable)

    def test_is_refundable_false_when_already_refunded(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("100.00"),
            status="REFUNDED",
        )

        self.assertFalse(payment.is_refundable)


class PaymentStatusTransitionsTest(TestCase):
    """Tests for Payment status transition methods."""

    def setUp(self):
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

    def test_complete_changes_status_to_completed(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("300.00"),
            status="PENDING",
        )

        payment.complete()

        self.assertEqual(payment.status, "COMPLETED")

    def test_refund_changes_status_to_refunded(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("300.00"),
            status="COMPLETED",
        )

        payment.refund()

        self.assertEqual(payment.status, "REFUNDED")

    def test_refund_raises_when_not_refundable(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("300.00"),
            status="PENDING",
        )

        with self.assertRaises(ValueError) as context:
            payment.refund()

        self.assertIn("cannot be refunded", str(context.exception))

    def test_cancel_changes_status_to_cancelled(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("300.00"),
            status="PENDING",
        )

        payment.cancel()

        self.assertEqual(payment.status, "CANCELLED")

    def test_cancel_raises_when_not_pending(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("300.00"),
            status="COMPLETED",
        )

        with self.assertRaises(ValueError) as context:
            payment.cancel()

        self.assertIn("pending payments", str(context.exception))


class PaymentMethodChoicesTest(TestCase):
    """Tests for Payment method choices."""

    def setUp(self):
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

    def test_cash_payment_method(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("250.00"),
        )

        self.assertEqual(payment.get_payment_method_display(), "Cash")

    def test_card_payment_method(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("250.00"),
        )

        self.assertEqual(payment.get_payment_method_display(), "Credit/Debit Card")

    def test_check_payment_method(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CHECK",
            amount=Decimal("250.00"),
        )

        self.assertEqual(payment.get_payment_method_display(), "Check")

    def test_ach_payment_method(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="ACH",
            amount=Decimal("250.00"),
        )

        self.assertEqual(payment.get_payment_method_display(), "ACH Transfer")

    def test_wire_payment_method(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="WIRE",
            amount=Decimal("250.00"),
        )

        self.assertEqual(payment.get_payment_method_display(), "Wire Transfer")


class PaymentOptionalFieldsTest(TestCase):
    """Tests for Payment optional fields."""

    def setUp(self):
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

    def test_payment_with_reference_number(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CHECK",
            amount=Decimal("175.00"),
            reference_number="CHK-12345",
        )

        self.assertEqual(payment.reference_number, "CHK-12345")

    def test_payment_with_notes(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("175.00"),
            notes="Customer paid in exact change",
        )

        self.assertEqual(payment.notes, "Customer paid in exact change")

    def test_payment_optional_fields_default_to_empty(self):
        payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("175.00"),
        )

        self.assertEqual(payment.reference_number, "")
        self.assertEqual(payment.notes, "")
