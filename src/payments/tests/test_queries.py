"""Tests for Payment query handlers."""

from decimal import Decimal

from django.test import TestCase

from customer_management.domain.models import Customer
from motor_vehicle_services.domain.models import MotorVehicle, Transaction
from payments.application import (
    GetPaymentQuery,
    ListPaymentsByTransactionQuery,
    ListPaymentsQuery,
    PaymentQueryHandler,
)
from payments.domain.exceptions import PaymentNotFound
from payments.domain.models import Payment


class GetPaymentQueryTest(TestCase):
    """Tests for GetPaymentQuery handler."""

    def setUp(self):
        self.handler = PaymentQueryHandler()
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
        self.payment = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("150.00"),
        )

    def test_get_payment_success(self):
        query = GetPaymentQuery(payment_id=self.payment.payment_id)

        result = self.handler.handle_get(query)

        self.assertEqual(result.payment_id, self.payment.payment_id)
        self.assertEqual(result.payment_method, "CASH")
        self.assertEqual(result.amount, Decimal("150.00"))

    def test_get_payment_not_found_raises(self):
        import uuid

        query = GetPaymentQuery(payment_id=uuid.uuid4())

        with self.assertRaises(PaymentNotFound):
            self.handler.handle_get(query)


class ListPaymentsQueryTest(TestCase):
    """Tests for ListPaymentsQuery handler."""

    def setUp(self):
        self.handler = PaymentQueryHandler()
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

    def test_list_payments_empty(self):
        query = ListPaymentsQuery()

        result = self.handler.handle_list(query)

        self.assertEqual(list(result), [])

    def test_list_payments_returns_all(self):
        Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("100.00"),
        )
        Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("100.00"),
        )
        query = ListPaymentsQuery()

        result = self.handler.handle_list(query)

        self.assertEqual(result.count(), 2)

    def test_list_payments_ordered_by_created_at_desc(self):
        payment1 = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CASH",
            amount=Decimal("50.00"),
        )
        payment2 = Payment.objects.create(
            transaction=self.transaction,
            payment_method="CARD",
            amount=Decimal("150.00"),
        )
        query = ListPaymentsQuery()

        result = list(self.handler.handle_list(query))

        # Most recent first
        self.assertEqual(result[0].payment_id, payment2.payment_id)
        self.assertEqual(result[1].payment_id, payment1.payment_id)


class ListPaymentsByTransactionQueryTest(TestCase):
    """Tests for ListPaymentsByTransactionQuery handler."""

    def setUp(self):
        self.handler = PaymentQueryHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200003",
            given_names="Bob",
            surnames="Wilson",
            email="bob.wilson@example.com",
        )
        self.vehicle1 = MotorVehicle.objects.create(
            vin="1HGCM82633A004354",
            make="Ford",
            model="Focus",
            year=2019,
        )
        self.vehicle2 = MotorVehicle.objects.create(
            vin="1HGCM82633A004355",
            make="Chevrolet",
            model="Malibu",
            year=2022,
        )
        self.transaction1 = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle1,
            transaction_type="RNW",
            transaction_date="2025-01-01",
            transaction_amount=Decimal("300.00"),
        )
        self.transaction2 = Transaction.objects.create(
            customer=self.customer,
            vehicle=self.vehicle2,
            transaction_type="TNSF",
            transaction_date="2025-01-02",
            transaction_amount=Decimal("400.00"),
        )

    def test_list_payments_by_transaction_returns_only_matching(self):
        # Create payments for transaction1
        Payment.objects.create(
            transaction=self.transaction1,
            payment_method="CASH",
            amount=Decimal("150.00"),
        )
        Payment.objects.create(
            transaction=self.transaction1,
            payment_method="CARD",
            amount=Decimal("150.00"),
        )
        # Create payment for transaction2
        Payment.objects.create(
            transaction=self.transaction2,
            payment_method="CHECK",
            amount=Decimal("400.00"),
        )

        query = ListPaymentsByTransactionQuery(
            transaction_id=self.transaction1.transaction_id
        )

        result = self.handler.handle_list_by_transaction(query)

        self.assertEqual(result.count(), 2)
        for payment in result:
            self.assertEqual(payment.transaction_id, self.transaction1.transaction_id)

    def test_list_payments_by_transaction_empty_when_no_payments(self):
        query = ListPaymentsByTransactionQuery(
            transaction_id=self.transaction1.transaction_id
        )

        result = self.handler.handle_list_by_transaction(query)

        self.assertEqual(result.count(), 0)

    def test_list_payments_by_nonexistent_transaction_returns_empty(self):
        import uuid

        query = ListPaymentsByTransactionQuery(transaction_id=uuid.uuid4())

        result = self.handler.handle_list_by_transaction(query)

        self.assertEqual(result.count(), 0)
