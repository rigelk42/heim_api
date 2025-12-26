"""Tests for Motor Vehicle Services query handlers."""

from django.test import TestCase

from customer_management.domain.models import Customer
from motor_vehicle_services.application import (CreateMotorVehicleCommand,
                                                GetMotorVehicleByVINQuery,
                                                GetMotorVehicleQuery,
                                                ListMotorVehiclesByOwnerQuery,
                                                ListMotorVehiclesByStatusQuery,
                                                ListMotorVehiclesQuery,
                                                MotorVehicleCommandHandler,
                                                MotorVehicleQueryHandler,
                                                SearchMotorVehiclesQuery,
                                                TransferOwnershipCommand)
from motor_vehicle_services.domain import MotorVehicleNotFound


class GetMotorVehicleQueryTest(TestCase):
    def setUp(self):
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

        create_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.vehicle = self.command_handler.handle_create(create_command)

    def test_get_vehicle_success(self):
        query = GetMotorVehicleQuery(vehicle_id=self.vehicle.id)

        result = self.query_handler.handle_get(query)

        self.assertEqual(result.id, self.vehicle.id)
        self.assertEqual(result.vin, "1HGCM82633A004352")
        self.assertEqual(result.make, "Honda")
        self.assertEqual(result.model, "Accord")
        self.assertEqual(result.year, 2020)

    def test_get_vehicle_not_found_raises(self):
        query = GetMotorVehicleQuery(vehicle_id=9999)

        with self.assertRaises(MotorVehicleNotFound):
            self.query_handler.handle_get(query)


class GetMotorVehicleByVINQueryTest(TestCase):
    def setUp(self):
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

        create_command = CreateMotorVehicleCommand(
            vin="1HGCM82633A004352",
            make="Honda",
            model="Accord",
            year=2020,
        )
        self.vehicle = self.command_handler.handle_create(create_command)

    def test_get_vehicle_by_vin_success(self):
        query = GetMotorVehicleByVINQuery(vin="1HGCM82633A004352")

        result = self.query_handler.handle_get_by_vin(query)

        self.assertEqual(result.id, self.vehicle.id)
        self.assertEqual(result.vin, "1HGCM82633A004352")

    def test_get_vehicle_by_vin_case_insensitive(self):
        query = GetMotorVehicleByVINQuery(vin="1hgcm82633a004352")  # lowercase

        result = self.query_handler.handle_get_by_vin(query)

        self.assertEqual(result.id, self.vehicle.id)

    def test_get_vehicle_by_vin_not_found_raises(self):
        query = GetMotorVehicleByVINQuery(vin="XXXXXXXXXXXXXXXXX")

        with self.assertRaises(MotorVehicleNotFound):
            self.query_handler.handle_get_by_vin(query)


class ListMotorVehiclesQueryTest(TestCase):
    def setUp(self):
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

    def test_list_vehicles_empty(self):
        query = ListMotorVehiclesQuery()

        result = self.query_handler.handle_list(query)

        self.assertEqual(result.count(), 0)

    def test_list_vehicles_returns_all(self):
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="1HGCM82633A004352",
                make="Honda",
                model="Accord",
                year=2020,
            )
        )
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="2T1BURHE5JC123456",
                make="Toyota",
                model="Corolla",
                year=2018,
            )
        )

        query = ListMotorVehiclesQuery()

        result = self.query_handler.handle_list(query)

        self.assertEqual(result.count(), 2)

    def test_list_vehicles_ordered_by_year_desc(self):
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="1HGCM82633A004352",
                make="Honda",
                model="Accord",
                year=2018,
            )
        )
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="2T1BURHE5JC123456",
                make="Toyota",
                model="Corolla",
                year=2022,
            )
        )

        query = ListMotorVehiclesQuery()

        result = list(self.query_handler.handle_list(query))

        self.assertEqual(result[0].year, 2022)
        self.assertEqual(result[1].year, 2018)


class ListMotorVehiclesByStatusQueryTest(TestCase):
    def setUp(self):
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

        # Create vehicles with different statuses
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="1HGCM82633A004352",
                make="Honda",
                model="Accord",
                year=2020,
            )
        )
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="2T1BURHE5JC123456",
                make="Toyota",
                model="Corolla",
                year=2018,
            )
        )
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="3VWDP7AJ5DM123456",
                make="Volkswagen",
                model="Jetta",
                year=2019,
            )
        )

    def test_list_by_status_active(self):
        query = ListMotorVehiclesByStatusQuery(status="active")

        result = self.query_handler.handle_list_by_status(query)

        self.assertEqual(result.count(), 3)  # All are active by default

    def test_list_by_status_sold(self):
        # Mark one as sold
        from motor_vehicle_services.application import ChangeMotorVehicleStatusCommand

        vehicles = list(self.query_handler.handle_list(ListMotorVehiclesQuery()))
        self.command_handler.handle_change_status(
            ChangeMotorVehicleStatusCommand(vehicle_id=vehicles[0].id, status="sold")
        )

        query = ListMotorVehiclesByStatusQuery(status="sold")

        result = self.query_handler.handle_list_by_status(query)

        self.assertEqual(result.count(), 1)

    def test_list_by_status_no_results(self):
        query = ListMotorVehiclesByStatusQuery(status="stolen")

        result = self.query_handler.handle_list_by_status(query)

        self.assertEqual(result.count(), 0)


class SearchMotorVehiclesQueryTest(TestCase):
    def setUp(self):
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="1HGCM82633A004352",
                make="Honda",
                model="Accord",
                year=2020,
                license_plate="ABC123",
            )
        )
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="2T1BURHE5JC123456",
                make="Toyota",
                model="Corolla",
                year=2018,
                license_plate="XYZ789",
            )
        )
        self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="3VWDP7AJ5DM123456",
                make="Honda",
                model="Civic",
                year=2019,
                license_plate="DEF456",
            )
        )

    def test_search_by_vin(self):
        query = SearchMotorVehiclesQuery(query="1HGCM82633A004352")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().model, "Accord")

    def test_search_by_partial_vin(self):
        query = SearchMotorVehiclesQuery(query="HGCM")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)

    def test_search_by_make(self):
        query = SearchMotorVehiclesQuery(query="Honda")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 2)  # Accord and Civic

    def test_search_by_model(self):
        query = SearchMotorVehiclesQuery(query="Corolla")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().make, "Toyota")

    def test_search_by_license_plate(self):
        query = SearchMotorVehiclesQuery(query="ABC123")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().model, "Accord")

    def test_search_by_partial_license_plate(self):
        query = SearchMotorVehiclesQuery(query="XYZ")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().model, "Corolla")

    def test_search_case_insensitive(self):
        query = SearchMotorVehiclesQuery(query="honda")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 2)

    def test_search_no_results(self):
        query = SearchMotorVehiclesQuery(query="Ferrari")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 0)


class ListMotorVehiclesByOwnerQueryTest(TestCase):
    def setUp(self):
        self.command_handler = MotorVehicleCommandHandler()
        self.query_handler = MotorVehicleQueryHandler()

        # Create customers
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

        # Create vehicles
        self.vehicle1 = self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="1HGCM82633A004352",
                make="Honda",
                model="Accord",
                year=2020,
            )
        )
        self.vehicle2 = self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="2T1BURHE5JC123456",
                make="Toyota",
                model="Corolla",
                year=2018,
            )
        )
        self.vehicle3 = self.command_handler.handle_create(
            CreateMotorVehicleCommand(
                vin="3VWDP7AJ5DM123456",
                make="Volkswagen",
                model="Jetta",
                year=2019,
            )
        )

        # Assign vehicles to owners
        self.command_handler.handle_transfer_ownership(
            TransferOwnershipCommand(
                vehicle_id=self.vehicle1.id,
                new_owner_id=self.customer1.id,
            )
        )
        self.command_handler.handle_transfer_ownership(
            TransferOwnershipCommand(
                vehicle_id=self.vehicle2.id,
                new_owner_id=self.customer1.id,
            )
        )
        self.command_handler.handle_transfer_ownership(
            TransferOwnershipCommand(
                vehicle_id=self.vehicle3.id,
                new_owner_id=self.customer2.id,
            )
        )

    def test_list_by_owner_returns_owned_vehicles(self):
        query = ListMotorVehiclesByOwnerQuery(owner_id=self.customer1.id)

        result = self.query_handler.handle_list_by_owner(query)

        self.assertEqual(result.count(), 2)
        vins = [v.vin for v in result]
        self.assertIn("1HGCM82633A004352", vins)
        self.assertIn("2T1BURHE5JC123456", vins)

    def test_list_by_owner_returns_single_vehicle(self):
        query = ListMotorVehiclesByOwnerQuery(owner_id=self.customer2.id)

        result = self.query_handler.handle_list_by_owner(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().vin, "3VWDP7AJ5DM123456")

    def test_list_by_owner_no_vehicles(self):
        # Create a customer with no vehicles
        customer3 = Customer.objects.create(
            given_names="Bob",
            surnames="Wilson",
            email="bob.wilson@example.com",
        )

        query = ListMotorVehiclesByOwnerQuery(owner_id=customer3.id)

        result = self.query_handler.handle_list_by_owner(query)

        self.assertEqual(result.count(), 0)

    def test_list_by_owner_nonexistent_customer(self):
        query = ListMotorVehiclesByOwnerQuery(owner_id=9999)

        result = self.query_handler.handle_list_by_owner(query)

        self.assertEqual(result.count(), 0)
