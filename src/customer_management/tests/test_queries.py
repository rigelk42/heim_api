from django.test import TestCase

from customer_management.application import (AddCustomerAddressCommand,
                                             CreateCustomerCommand,
                                             CustomerCommandHandler,
                                             CustomerQueryHandler,
                                             GetCustomerAddressesQuery,
                                             GetCustomerQuery,
                                             ListCustomersQuery,
                                             SearchCustomersQuery)
from customer_management.domain import CustomerNotFound


class GetCustomerQueryTest(TestCase):
    def setUp(self):
        self.command_handler = CustomerCommandHandler()
        self.query_handler = CustomerQueryHandler()

        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.customer = self.command_handler.handle_create(create_command)

    def test_get_customer_success(self):
        query = GetCustomerQuery(customer_id=self.customer.id)

        result = self.query_handler.handle_get(query)

        self.assertEqual(result.id, self.customer.id)
        self.assertEqual(result.given_names, "John")
        self.assertEqual(result.surnames, "Doe")
        self.assertEqual(result.email, "john@example.com")

    def test_get_customer_not_found_raises(self):
        query = GetCustomerQuery(customer_id=9999)

        with self.assertRaises(CustomerNotFound):
            self.query_handler.handle_get(query)


class ListCustomersQueryTest(TestCase):
    def setUp(self):
        self.command_handler = CustomerCommandHandler()
        self.query_handler = CustomerQueryHandler()

    def test_list_customers_empty(self):
        query = ListCustomersQuery()

        result = self.query_handler.handle_list(query)

        self.assertEqual(result.count(), 0)

    def test_list_customers_returns_all(self):
        self.command_handler.handle_create(
            CreateCustomerCommand(
                given_names="John",
                surnames="Doe",
                email="john@example.com",
            )
        )
        self.command_handler.handle_create(
            CreateCustomerCommand(
                given_names="Jane",
                surnames="Smith",
                email="jane@example.com",
            )
        )

        query = ListCustomersQuery()

        result = self.query_handler.handle_list(query)

        self.assertEqual(result.count(), 2)

    def test_list_customers_ordered_by_surname(self):
        self.command_handler.handle_create(
            CreateCustomerCommand(
                given_names="John",
                surnames="Zebra",
                email="john@example.com",
            )
        )
        self.command_handler.handle_create(
            CreateCustomerCommand(
                given_names="Jane",
                surnames="Alpha",
                email="jane@example.com",
            )
        )

        query = ListCustomersQuery()

        result = list(self.query_handler.handle_list(query))

        self.assertEqual(result[0].surnames, "Alpha")
        self.assertEqual(result[1].surnames, "Zebra")


class SearchCustomersQueryTest(TestCase):
    def setUp(self):
        self.command_handler = CustomerCommandHandler()
        self.query_handler = CustomerQueryHandler()

        self.command_handler.handle_create(
            CreateCustomerCommand(
                given_names="John",
                surnames="Doe",
                email="john@example.com",
            )
        )
        self.command_handler.handle_create(
            CreateCustomerCommand(
                given_names="Jane",
                surnames="Smith",
                email="jane@example.com",
            )
        )
        self.command_handler.handle_create(
            CreateCustomerCommand(
                given_names="Bob",
                surnames="Johnson",
                email="bob@company.com",
            )
        )

    def test_search_by_given_name(self):
        query = SearchCustomersQuery(query="John")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 2)  # John Doe and Bob Johnson

    def test_search_by_surname(self):
        query = SearchCustomersQuery(query="Smith")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().surnames, "Smith")

    def test_search_by_email(self):
        query = SearchCustomersQuery(query="company.com")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().given_names, "Bob")

    def test_search_case_insensitive(self):
        query = SearchCustomersQuery(query="JANE")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().given_names, "Jane")

    def test_search_no_results(self):
        query = SearchCustomersQuery(query="xyz123")

        result = self.query_handler.handle_search(query)

        self.assertEqual(result.count(), 0)


class GetCustomerAddressesQueryTest(TestCase):
    def setUp(self):
        self.command_handler = CustomerCommandHandler()
        self.query_handler = CustomerQueryHandler()

        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        self.customer = self.command_handler.handle_create(create_command)

    def test_get_addresses_empty(self):
        query = GetCustomerAddressesQuery(customer_id=self.customer.id)

        result = self.query_handler.handle_get_addresses(query)

        self.assertEqual(result.count(), 0)

    def test_get_addresses_returns_all(self):
        self.command_handler.handle_add_address(
            AddCustomerAddressCommand(
                customer_id=self.customer.id,
                address_line_1="123 Main St",
                city="New York",
                postal_code="10001",
                country="USA",
            )
        )
        self.command_handler.handle_add_address(
            AddCustomerAddressCommand(
                customer_id=self.customer.id,
                address_line_1="456 Oak Ave",
                city="Boston",
                postal_code="02101",
                country="USA",
            )
        )

        query = GetCustomerAddressesQuery(customer_id=self.customer.id)

        result = self.query_handler.handle_get_addresses(query)

        self.assertEqual(result.count(), 2)

    def test_get_addresses_customer_not_found_raises(self):
        query = GetCustomerAddressesQuery(customer_id=9999)

        with self.assertRaises(CustomerNotFound):
            self.query_handler.handle_get_addresses(query)
