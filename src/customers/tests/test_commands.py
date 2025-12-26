from django.test import TestCase

from customers.application import (
    AddCustomerAddressCommand,
    CreateCustomerCommand,
    CustomerCommandHandler,
    DeleteCustomerCommand,
    RemoveCustomerAddressCommand,
    UpdateCustomerCommand,
    UpdateCustomerEmailCommand,
)
from customers.domain import Customer, CustomerAlreadyExists, CustomerNotFound


class CreateCustomerCommandTest(TestCase):
    def setUp(self):
        self.handler = CustomerCommandHandler()

    def test_create_customer_success(self):
        command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
            phone="123-456-7890",
        )

        customer = self.handler.handle_create(command)

        self.assertEqual(customer.given_names, "John")
        self.assertEqual(customer.surnames, "Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertEqual(customer.phone, "1234567890")  # Normalized
        self.assertEqual(Customer.objects.count(), 1)

    def test_create_customer_duplicate_email_raises(self):
        command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.handler.handle_create(command)

        duplicate_command = CreateCustomerCommand(
            given_names="Jane",
            surnames="Doe",
            email="john@example.com",
        )

        with self.assertRaises(CustomerAlreadyExists):
            self.handler.handle_create(duplicate_command)

    def test_create_customer_invalid_email_raises(self):
        command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="invalid-email",
        )

        with self.assertRaises(ValueError):
            self.handler.handle_create(command)

    def test_create_customer_empty_name_raises(self):
        command = CreateCustomerCommand(
            given_names="",
            surnames="Doe",
            email="john@example.com",
        )

        with self.assertRaises(ValueError):
            self.handler.handle_create(command)


class UpdateCustomerCommandTest(TestCase):
    def setUp(self):
        self.handler = CustomerCommandHandler()
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.customer = self.handler.handle_create(create_command)

    def test_update_customer_given_names(self):
        command = UpdateCustomerCommand(
            customer_id=self.customer.id,
            given_names="Johnny",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.given_names, "Johnny")
        self.assertEqual(updated.surnames, "Doe")

    def test_update_customer_surnames(self):
        command = UpdateCustomerCommand(
            customer_id=self.customer.id,
            surnames="Smith",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.given_names, "John")
        self.assertEqual(updated.surnames, "Smith")

    def test_update_customer_phone(self):
        command = UpdateCustomerCommand(
            customer_id=self.customer.id,
            phone="555-1234",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.phone, "5551234")

    def test_update_customer_not_found_raises(self):
        command = UpdateCustomerCommand(
            customer_id=9999,
            given_names="Johnny",
        )

        with self.assertRaises(CustomerNotFound):
            self.handler.handle_update(command)


class UpdateCustomerEmailCommandTest(TestCase):
    def setUp(self):
        self.handler = CustomerCommandHandler()
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.customer = self.handler.handle_create(create_command)

    def test_update_email_success(self):
        command = UpdateCustomerEmailCommand(
            customer_id=self.customer.id,
            email="johnny@example.com",
        )

        updated = self.handler.handle_update_email(command)

        self.assertEqual(updated.email, "johnny@example.com")

    def test_update_email_same_email_no_change(self):
        command = UpdateCustomerEmailCommand(
            customer_id=self.customer.id,
            email="john@example.com",
        )

        updated = self.handler.handle_update_email(command)

        self.assertEqual(updated.email, "john@example.com")

    def test_update_email_duplicate_raises(self):
        other_command = CreateCustomerCommand(
            given_names="Jane",
            surnames="Doe",
            email="jane@example.com",
        )
        self.handler.handle_create(other_command)

        command = UpdateCustomerEmailCommand(
            customer_id=self.customer.id,
            email="jane@example.com",
        )

        with self.assertRaises(CustomerAlreadyExists):
            self.handler.handle_update_email(command)


class DeleteCustomerCommandTest(TestCase):
    def setUp(self):
        self.handler = CustomerCommandHandler()
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.customer = self.handler.handle_create(create_command)

    def test_delete_customer_success(self):
        command = DeleteCustomerCommand(customer_id=self.customer.id)

        self.handler.handle_delete(command)

        self.assertEqual(Customer.objects.count(), 0)

    def test_delete_customer_not_found_raises(self):
        command = DeleteCustomerCommand(customer_id=9999)

        with self.assertRaises(CustomerNotFound):
            self.handler.handle_delete(command)


class AddCustomerAddressCommandTest(TestCase):
    def setUp(self):
        self.handler = CustomerCommandHandler()
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.customer = self.handler.handle_create(create_command)

    def test_add_address_success(self):
        command = AddCustomerAddressCommand(
            customer_id=self.customer.id,
            address_line_1="123 Main St",
            address_line_2="Apt 4B",
            city="New York",
            state_province="NY",
            postal_code="10001",
            country="USA",
        )

        address = self.handler.handle_add_address(command)

        self.assertEqual(address.address_line_1, "123 Main St")
        self.assertEqual(address.address_line_2, "Apt 4B")
        self.assertEqual(address.city, "New York")
        self.assertEqual(address.state_province, "NY")
        self.assertEqual(address.postal_code, "10001")
        self.assertEqual(address.country, "USA")
        self.assertEqual(address.customer_id, self.customer.id)

    def test_add_primary_address_clears_previous_primary(self):
        first_command = AddCustomerAddressCommand(
            customer_id=self.customer.id,
            address_line_1="123 Main St",
            city="New York",
            postal_code="10001",
            country="USA",
            is_primary=True,
        )
        first_address = self.handler.handle_add_address(first_command)

        second_command = AddCustomerAddressCommand(
            customer_id=self.customer.id,
            address_line_1="456 Oak Ave",
            city="Boston",
            postal_code="02101",
            country="USA",
            is_primary=True,
        )
        second_address = self.handler.handle_add_address(second_command)

        first_address.refresh_from_db()
        self.assertFalse(first_address.is_primary)
        self.assertTrue(second_address.is_primary)

    def test_add_address_customer_not_found_raises(self):
        command = AddCustomerAddressCommand(
            customer_id=9999,
            address_line_1="123 Main St",
            city="New York",
            postal_code="10001",
            country="USA",
        )

        with self.assertRaises(CustomerNotFound):
            self.handler.handle_add_address(command)


class RemoveCustomerAddressCommandTest(TestCase):
    def setUp(self):
        self.handler = CustomerCommandHandler()
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.customer = self.handler.handle_create(create_command)

        add_address_command = AddCustomerAddressCommand(
            customer_id=self.customer.id,
            address_line_1="123 Main St",
            city="New York",
            postal_code="10001",
            country="USA",
        )
        self.address = self.handler.handle_add_address(add_address_command)

    def test_remove_address_success(self):
        command = RemoveCustomerAddressCommand(
            customer_id=self.customer.id,
            address_id=self.address.id,
        )

        result = self.handler.handle_remove_address(command)

        self.assertTrue(result)
        self.assertEqual(self.customer.addresses.count(), 0)

    def test_remove_address_not_found_returns_false(self):
        command = RemoveCustomerAddressCommand(
            customer_id=self.customer.id,
            address_id=9999,
        )

        result = self.handler.handle_remove_address(command)

        self.assertFalse(result)

    def test_remove_address_customer_not_found_raises(self):
        command = RemoveCustomerAddressCommand(
            customer_id=9999,
            address_id=self.address.id,
        )

        with self.assertRaises(CustomerNotFound):
            self.handler.handle_remove_address(command)
