"""Tests for Motor Vehicle Services command handlers."""

from django.test import TestCase

from customer_management.domain.models import Customer
from motor_vehicle_services.application import (ChangeMotorVehicleStatusCommand,
                                                CreateMotorVehicleCommand,
                                                DeleteMotorVehicleCommand,
                                                MotorVehicleCommandHandler,
                                                TransferOwnershipCommand,
                                                UpdateMotorVehicleCommand,
                                                UpdateMotorVehicleMileageCommand)
from motor_vehicle_services.domain import (MotorVehicle, MotorVehicleAlreadyExists,
                                           MotorVehicleNotFound)


class CreateMotorVehicleCommandTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()

    def test_create_vehicle_success(self):
        command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
            color="Blue",
            fuel_type="petrol",
            transmission="automatic",
            mileage_km=50000,
        )

        vehicle = self.handler.handle_create(command)

        self.assertEqual(vehicle.vin, "1HGCM82633A004352")
        self.assertEqual(vehicle.make, "Honda")
        self.assertEqual(vehicle.model, "Accord")
        self.assertEqual(vehicle.year, 2020)
        self.assertEqual(vehicle.color, "Blue")
        self.assertEqual(vehicle.fuel_type, "petrol")
        self.assertEqual(vehicle.transmission, "automatic")
        self.assertEqual(vehicle.mileage_km, 50000)
        self.assertEqual(vehicle.status, "active")
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
            color="Blue",
            fuel_type="petrol",
            transmission="manual",
        )
        self.vehicle = self.handler.handle_create(create_command)

    def test_update_vehicle_color(self):
        command = UpdateMotorVehicleCommand(
            vehicle_id=self.vehicle.id,
            color="Red",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.color, "Red")
        self.assertEqual(updated.fuel_type, "petrol")  # Unchanged

    def test_update_vehicle_fuel_type(self):
        command = UpdateMotorVehicleCommand(
            vehicle_id=self.vehicle.id,
            fuel_type="hybrid",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.fuel_type, "hybrid")

    def test_update_vehicle_transmission(self):
        command = UpdateMotorVehicleCommand(
            vehicle_id=self.vehicle.id,
            transmission="automatic",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.transmission, "automatic")

    def test_update_vehicle_license_plate(self):
        command = UpdateMotorVehicleCommand(
            vehicle_id=self.vehicle.id,
            license_plate="xyz789",
            license_plate_state="NY",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.license_plate, "XYZ789")  # Uppercased
        self.assertEqual(updated.license_plate_state, "NY")

    def test_update_vehicle_multiple_fields(self):
        command = UpdateMotorVehicleCommand(
            vehicle_id=self.vehicle.id,
            color="Green",
            fuel_type="electric",
            transmission="automatic",
        )

        updated = self.handler.handle_update(command)

        self.assertEqual(updated.color, "Green")
        self.assertEqual(updated.fuel_type, "electric")
        self.assertEqual(updated.transmission, "automatic")

    def test_update_vehicle_not_found_raises(self):
        command = UpdateMotorVehicleCommand(
            vehicle_id=9999,
            color="Red",
        )

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_update(command)


class UpdateMotorVehicleMileageCommandTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()
        create_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
            mileage_km=50000,
        )
        self.vehicle = self.handler.handle_create(create_command)

    def test_update_mileage_success(self):
        command = UpdateMotorVehicleMileageCommand(
            vehicle_id=self.vehicle.id,
            mileage_km=55000,
        )

        updated = self.handler.handle_update_mileage(command)

        self.assertEqual(updated.mileage_km, 55000)

    def test_update_mileage_same_value_success(self):
        command = UpdateMotorVehicleMileageCommand(
            vehicle_id=self.vehicle.id,
            mileage_km=50000,
        )

        updated = self.handler.handle_update_mileage(command)

        self.assertEqual(updated.mileage_km, 50000)

    def test_update_mileage_lower_than_current_raises(self):
        command = UpdateMotorVehicleMileageCommand(
            vehicle_id=self.vehicle.id,
            mileage_km=40000,  # Less than current 50000
        )

        with self.assertRaises(ValueError) as context:
            self.handler.handle_update_mileage(command)

        self.assertIn("cannot be less than", str(context.exception))

    def test_update_mileage_vehicle_not_found_raises(self):
        command = UpdateMotorVehicleMileageCommand(
            vehicle_id=9999,
            mileage_km=60000,
        )

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_update_mileage(command)


class ChangeMotorVehicleStatusCommandTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()
        create_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.vehicle = self.handler.handle_create(create_command)

    def test_change_status_to_sold(self):
        command = ChangeMotorVehicleStatusCommand(
            vehicle_id=self.vehicle.id,
            status="sold",
        )

        updated = self.handler.handle_change_status(command)

        self.assertEqual(updated.status, "sold")

    def test_change_status_to_scrapped(self):
        command = ChangeMotorVehicleStatusCommand(
            vehicle_id=self.vehicle.id,
            status="scrapped",
        )

        updated = self.handler.handle_change_status(command)

        self.assertEqual(updated.status, "scrapped")

    def test_change_status_to_stolen(self):
        command = ChangeMotorVehicleStatusCommand(
            vehicle_id=self.vehicle.id,
            status="stolen",
        )

        updated = self.handler.handle_change_status(command)

        self.assertEqual(updated.status, "stolen")

    def test_change_status_back_to_active(self):
        # First mark as stolen
        stolen_command = ChangeMotorVehicleStatusCommand(
            vehicle_id=self.vehicle.id,
            status="stolen",
        )
        self.handler.handle_change_status(stolen_command)

        # Then reactivate
        active_command = ChangeMotorVehicleStatusCommand(
            vehicle_id=self.vehicle.id,
            status="active",
        )
        updated = self.handler.handle_change_status(active_command)

        self.assertEqual(updated.status, "active")

    def test_change_status_invalid_status_raises(self):
        command = ChangeMotorVehicleStatusCommand(
            vehicle_id=self.vehicle.id,
            status="invalid_status",
        )

        with self.assertRaises(ValueError) as context:
            self.handler.handle_change_status(command)

        self.assertIn("Invalid status", str(context.exception))

    def test_change_status_vehicle_not_found_raises(self):
        command = ChangeMotorVehicleStatusCommand(
            vehicle_id=9999,
            status="sold",
        )

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_change_status(command)


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
        command = DeleteMotorVehicleCommand(vehicle_id=self.vehicle.id)

        self.handler.handle_delete(command)

        self.assertEqual(MotorVehicle.objects.count(), 0)

    def test_delete_vehicle_not_found_raises(self):
        command = DeleteMotorVehicleCommand(vehicle_id=9999)

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_delete(command)


class CreateMotorVehicleWithOwnerTest(TestCase):
    def setUp(self):
        self.handler = MotorVehicleCommandHandler()
        self.customer = Customer.objects.create(
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
            owner_id=self.customer.id,
        )

        vehicle = self.handler.handle_create(command)

        self.assertEqual(vehicle.owner_id, self.customer.id)
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
            given_names="John",
            surnames="Doe",
            email="john.doe@example.com",
        )
        self.customer2 = Customer.objects.create(
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
            vehicle_id=self.vehicle.id,
            new_owner_id=self.customer1.id,
        )

        updated = self.handler.handle_transfer_ownership(command)

        self.assertEqual(updated.owner_id, self.customer1.id)
        self.assertEqual(updated.owner_name, "John Doe")

    def test_transfer_ownership_to_another_customer(self):
        # First assign to customer1
        assign_command = TransferOwnershipCommand(
            vehicle_id=self.vehicle.id,
            new_owner_id=self.customer1.id,
        )
        self.handler.handle_transfer_ownership(assign_command)

        # Then transfer to customer2
        transfer_command = TransferOwnershipCommand(
            vehicle_id=self.vehicle.id,
            new_owner_id=self.customer2.id,
        )
        updated = self.handler.handle_transfer_ownership(transfer_command)

        self.assertEqual(updated.owner_id, self.customer2.id)
        self.assertEqual(updated.owner_name, "Jane Smith")

    def test_remove_ownership(self):
        # First assign to customer
        assign_command = TransferOwnershipCommand(
            vehicle_id=self.vehicle.id,
            new_owner_id=self.customer1.id,
        )
        self.handler.handle_transfer_ownership(assign_command)

        # Then remove ownership
        remove_command = TransferOwnershipCommand(
            vehicle_id=self.vehicle.id,
            new_owner_id=None,
        )
        updated = self.handler.handle_transfer_ownership(remove_command)

        self.assertIsNone(updated.owner_id)
        self.assertIsNone(updated.owner_name)

    def test_transfer_ownership_vehicle_not_found_raises(self):
        command = TransferOwnershipCommand(
            vehicle_id=9999,
            new_owner_id=self.customer1.id,
        )

        with self.assertRaises(MotorVehicleNotFound):
            self.handler.handle_transfer_ownership(command)

    def test_transfer_ownership_customer_not_found_raises(self):
        command = TransferOwnershipCommand(
            vehicle_id=self.vehicle.id,
            new_owner_id=9999,
        )

        with self.assertRaises(ValueError) as context:
            self.handler.handle_transfer_ownership(command)

        self.assertIn("not found", str(context.exception))
