"""Tests for Motor Vehicle Services command handlers."""

from django.test import TestCase

from customer_management.domain.models import Customer
from motor_vehicle_services.application import (
    CreateMotorVehicleCommand,
    DeleteMotorVehicleCommand,
    MotorVehicleCommandHandler,
    TransferOwnershipCommand,
    UpdateMotorVehicleCommand,
)
from motor_vehicle_services.domain import (
    MotorVehicle,
    MotorVehicleAlreadyExists,
    MotorVehicleNotFound,
)


class CreateMotorVehicleCommandTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()

    def test_create_vehicle_success(self):
        command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )

        vehicle = self.handler.handle_create(command)

        self.assertEqual(vehicle.vin, "1HGCM82633A004352")
        self.assertEqual(vehicle.make, "Honda")
        self.assertEqual(vehicle.model, "Accord")
        self.assertEqual(vehicle.year, 2020)
        self.assertEqual(MotorVehicle.objects.count(), 1)

    def test_create_vehicle_with_license_plate(self):
        command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
            license_plate="abc123",
            license_plate_state="CA",
        )

        vehicle = self.handler.handle_create(command)

        self.assertEqual(vehicle.license_plate, "ABC123")  # Uppercased
        self.assertEqual(vehicle.license_plate_state, "CA")

    def test_create_vehicle_vin_normalized_to_uppercase(self):
        command = CreateMotorVehicleCommand(
            vin="1hgcm82633a004352",  # lowercase
            make="Honda",
            model="Accord",
            year=2020,
        )

        vehicle = self.handler.handle_create(command)

        self.assertEqual(vehicle.vin, "1HGCM82633A004352")

    def test_create_vehicle_duplicate_vin_raises(self):
        command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.handler.handle_create(command)

        duplicate_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Toyota",
            model="Camry",
            year=2021,
        )

        with self.assertRaises(MotorVehicleAlreadyExists):
            self.handler.handle_create(duplicate_command)

    def test_create_vehicle_invalid_vin_raises(self):
        command = CreateMotorVehicleCommand(
            vin="INVALID",  # Too short
            make="Honda",
            model="Accord",
            year=2020,
        )

        with self.assertRaises(ValueError):
            self.handler.handle_create(command)

    def test_create_vehicle_vin_with_invalid_characters_raises(self):
        command = CreateMotorVehicleCommand(
            vin="1HGCM82633A00435I",  # Contains 'I' which is invalid
            make="Honda",
            model="Accord",
            year=2020,
        )

        with self.assertRaises(ValueError):
            self.handler.handle_create(command)


class UpdateMotorVehicleCommandTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()
        create_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.vehicle = self.handler.handle_create(create_command)

    def test_update_vehicle_license_plate(self):
        command = UpdateMotorVehicleCommand(
            vin=self.vehicle.vin,
            license_plate="xyz789",
            license_plate_state="NY",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.license_plate, "XYZ789")  # Uppercased
        self.assertEqual(updated.license_plate_state, "NY")

    def test_update_vehicle_not_found_raises(self):
        command = UpdateMotorVehicleCommand(
            vin="XXXXXXXXXXXXXXXXX",
            license_plate="ABC123",
        )

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_update(command)


class DeleteMotorVehicleCommandTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()
        create_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.vehicle = self.handler.handle_create(create_command)

    def test_delete_vehicle_success(self):
        command = DeleteMotorVehicleCommand(vin=self.vehicle.vin)

        self.handler.handle_delete(command)

        self.assertEqual(MotorVehicle.objects.count(), 0)

    def test_delete_vehicle_not_found_raises(self):
        command = DeleteMotorVehicleCommand(vin="XXXXXXXXXXXXXXXXX")

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_delete(command)


class CreateMotorVehicleWithOwnerTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()
        self.customer = Customer.objects.create(
            customer_id="C25001A1200001",
            given_names="John",
            surnames="Doe",
            email="john.doe@example.com",
        )

    def test_create_vehicle_with_owner(self):
        command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
            owner_id=self.customer.customer_id,
        )

        vehicle = self.handler.handle_create(command)

        self.assertEqual(vehicle.owner_id, self.customer.customer_id)
        self.assertEqual(vehicle.owner_name, "John Doe")

    def test_create_vehicle_without_owner(self):
        command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )

        vehicle = self.handler.handle_create(command)

        self.assertIsNone(vehicle.owner_id)
        self.assertIsNone(vehicle.owner_name)


class TransferOwnershipCommandTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()
        self.customer1 = Customer.objects.create(
            customer_id="C25001A1200002",
            given_names="John",
            surnames="Doe",
            email="john.doe@example.com",
        )
        self.customer2 = Customer.objects.create(
            customer_id="C25001A1200003",
            given_names="Jane",
            surnames="Smith",
            email="jane.smith@example.com",
        )
        create_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.vehicle = self.handler.handle_create(create_command)

    def test_transfer_ownership_to_customer(self):
        command = TransferOwnershipCommand(
            vin=self.vehicle.vin,
            new_owner_id=self.customer1.customer_id,
        )

        updated = self.handler.handle_transfer_ownership(command)

        self.assertEqual(updated.owner_id, self.customer1.customer_id)
        self.assertEqual(updated.owner_name, "John Doe")

    def test_transfer_ownership_to_another_customer(self):
        # First assign to customer1
        assign_command = TransferOwnershipCommand(
            vin=self.vehicle.vin,
            new_owner_id=self.customer1.customer_id,
        )
        self.handler.handle_transfer_ownership(assign_command)

        # Then transfer to customer2
        transfer_command = TransferOwnershipCommand(
            vin=self.vehicle.vin,
            new_owner_id=self.customer2.customer_id,
        )
        updated = self.handler.handle_transfer_ownership(transfer_command)

        self.assertEqual(updated.owner_id, self.customer2.customer_id)
        self.assertEqual(updated.owner_name, "Jane Smith")

    def test_remove_ownership(self):
        # First assign to customer
        assign_command = TransferOwnershipCommand(
            vin=self.vehicle.vin,
            new_owner_id=self.customer1.customer_id,
        )
        self.handler.handle_transfer_ownership(assign_command)

        # Then remove ownership
        remove_command = TransferOwnershipCommand(
            vin=self.vehicle.vin,
            new_owner_id=None,
        )
        updated = self.handler.handle_transfer_ownership(remove_command)

        self.assertIsNone(updated.owner_id)
        self.assertIsNone(updated.owner_name)

    def test_transfer_ownership_vehicle_not_found_raises(self):
        command = TransferOwnershipCommand(
            vin="XXXXXXXXXXXXXXXXX",
            new_owner_id=self.customer1.customer_id,
        )

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_transfer_ownership(command)

    def test_transfer_ownership_customer_not_found_raises(self):
        command = TransferOwnershipCommand(
            vin=self.vehicle.vin,
            new_owner_id="NONEXISTENT12345",
        )

        with self.assertRaises(ValueError) as context:
            self.handler.handle_transfer_ownership(command)

        self.assertIn("not found", str(context.exception))
