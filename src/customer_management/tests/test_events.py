from django.test import TestCase

from customer_management.application import (
    AddCustomerAddressCommand,
    CreateCustomerCommand,
    CustomerCommandHandler,
    DeleteCustomerCommand,
    RemoveCustomerAddressCommand,
    UpdateCustomerCommand,
    UpdateCustomerEmailCommand,
)
from customer_management.domain import (
    CustomerAddressAdded,
    CustomerAddressRemoved,
    CustomerCreated,
    CustomerDeleted,
    CustomerEmailChanged,
    CustomerUpdated,
)
from customer_management.infrastructure import EventDispatcher


class EventDispatcherTest(TestCase):
    def setUp(self):
        EventDispatcher.reset_instance()
        self.dispatcher = EventDispatcher()
        self.received_events = []

    def tearDown(self):
        EventDispatcher.reset_instance()

    def test_subscribe_and_publish(self):
        def handler(event):
            self.received_events.append(event)

        self.dispatcher.subscribe(CustomerCreated, handler)
        event = CustomerCreated(customer_id="C25363A1435532", email="test@example.com")
        self.dispatcher.publish(event)

        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0], event)

    def test_multiple_handlers(self):
        handler1_events = []
        handler2_events = []

        self.dispatcher.subscribe(CustomerCreated, lambda e: handler1_events.append(e))
        self.dispatcher.subscribe(CustomerCreated, lambda e: handler2_events.append(e))

        event = CustomerCreated(customer_id="C25363A1435532", email="test@example.com")
        self.dispatcher.publish(event)

        self.assertEqual(len(handler1_events), 1)
        self.assertEqual(len(handler2_events), 1)

    def test_unsubscribe(self):
        def handler(event):
            self.received_events.append(event)

        self.dispatcher.subscribe(CustomerCreated, handler)
        self.dispatcher.unsubscribe(CustomerCreated, handler)

        event = CustomerCreated(customer_id="C25363A1435532", email="test@example.com")
        self.dispatcher.publish(event)

        self.assertEqual(len(self.received_events), 0)

    def test_singleton_pattern(self):
        dispatcher1 = EventDispatcher()
        dispatcher2 = EventDispatcher()
        self.assertIs(dispatcher1, dispatcher2)

    def test_clear_handlers(self):
        def handler(event):
            self.received_events.append(event)

        self.dispatcher.subscribe(CustomerCreated, handler)
        self.dispatcher.clear()

        event = CustomerCreated(customer_id="C25363A1435532", email="test@example.com")
        self.dispatcher.publish(event)

        self.assertEqual(len(self.received_events), 0)


class CommandHandlerEventsTest(TestCase):
    def setUp(self):
        EventDispatcher.reset_instance()
        self.dispatcher = EventDispatcher()
        self.received_events = []
        self.handler = CustomerCommandHandler(event_dispatcher=self.dispatcher)

        # Subscribe to all events
        self.dispatcher.subscribe(
            CustomerCreated, lambda e: self.received_events.append(e)
        )
        self.dispatcher.subscribe(
            CustomerUpdated, lambda e: self.received_events.append(e)
        )
        self.dispatcher.subscribe(
            CustomerEmailChanged, lambda e: self.received_events.append(e)
        )
        self.dispatcher.subscribe(
            CustomerDeleted, lambda e: self.received_events.append(e)
        )
        self.dispatcher.subscribe(
            CustomerAddressAdded, lambda e: self.received_events.append(e)
        )
        self.dispatcher.subscribe(
            CustomerAddressRemoved, lambda e: self.received_events.append(e)
        )

    def tearDown(self):
        EventDispatcher.reset_instance()

    def test_create_customer_publishes_event(self):
        command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )

        customer = self.handler.handle_create(command)

        self.assertEqual(len(self.received_events), 1)
        event = self.received_events[0]
        self.assertIsInstance(event, CustomerCreated)
        self.assertEqual(event.customer_id, customer.customer_id)
        self.assertEqual(event.email, "john@example.com")
        self.assertEqual(event.given_names, "John")
        self.assertEqual(event.surnames, "Doe")

    def test_update_customer_publishes_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)
        self.received_events.clear()

        update_command = UpdateCustomerCommand(
            customer_id=customer.customer_id,
            given_names="Johnny",
        )
        self.handler.handle_update(update_command)

        self.assertEqual(len(self.received_events), 1)
        event = self.received_events[0]
        self.assertIsInstance(event, CustomerUpdated)
        self.assertEqual(event.customer_id, customer.customer_id)
        self.assertIn(("given_names", "Johnny"), event.changes)

    def test_update_customer_no_changes_no_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)
        self.received_events.clear()

        update_command = UpdateCustomerCommand(customer_id=customer.customer_id)
        self.handler.handle_update(update_command)

        self.assertEqual(len(self.received_events), 0)

    def test_update_email_publishes_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)
        self.received_events.clear()

        email_command = UpdateCustomerEmailCommand(
            customer_id=customer.customer_id,
            email="johnny@example.com",
        )
        self.handler.handle_update_email(email_command)

        self.assertEqual(len(self.received_events), 1)
        event = self.received_events[0]
        self.assertIsInstance(event, CustomerEmailChanged)
        self.assertEqual(event.customer_id, customer.customer_id)
        self.assertEqual(event.old_email, "john@example.com")
        self.assertEqual(event.new_email, "johnny@example.com")

    def test_update_email_same_email_no_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)
        self.received_events.clear()

        email_command = UpdateCustomerEmailCommand(
            customer_id=customer.customer_id,
            email="john@example.com",
        )
        self.handler.handle_update_email(email_command)

        self.assertEqual(len(self.received_events), 0)

    def test_delete_customer_publishes_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)
        customer_id = customer.customer_id
        self.received_events.clear()

        delete_command = DeleteCustomerCommand(customer_id=customer_id)
        self.handler.handle_delete(delete_command)

        self.assertEqual(len(self.received_events), 1)
        event = self.received_events[0]
        self.assertIsInstance(event, CustomerDeleted)
        self.assertEqual(event.customer_id, customer_id)
        self.assertEqual(event.email, "john@example.com")

    def test_add_address_publishes_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)
        self.received_events.clear()

        address_command = AddCustomerAddressCommand(
            customer_id=customer.customer_id,
            address_line_1="123 Main St",
            city="New York",
            postal_code="10001",
            country="USA",
            address_type="home",
            is_primary=True,
        )
        address = self.handler.handle_add_address(address_command)

        self.assertEqual(len(self.received_events), 1)
        event = self.received_events[0]
        self.assertIsInstance(event, CustomerAddressAdded)
        self.assertEqual(event.customer_id, customer.customer_id)
        self.assertEqual(event.address_id, address.id)
        self.assertEqual(event.address_type, "home")
        self.assertTrue(event.is_primary)

    def test_remove_address_publishes_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)

        address_command = AddCustomerAddressCommand(
            customer_id=customer.customer_id,
            address_line_1="123 Main St",
            city="New York",
            postal_code="10001",
            country="USA",
        )
        address = self.handler.handle_add_address(address_command)
        self.received_events.clear()

        remove_command = RemoveCustomerAddressCommand(
            customer_id=customer.customer_id,
            address_id=address.id,
        )
        self.handler.handle_remove_address(remove_command)

        self.assertEqual(len(self.received_events), 1)
        event = self.received_events[0]
        self.assertIsInstance(event, CustomerAddressRemoved)
        self.assertEqual(event.customer_id, customer.customer_id)
        self.assertEqual(event.address_id, address.id)

    def test_remove_nonexistent_address_no_event(self):
        create_command = CreateCustomerCommand(
            given_names="John",
            surnames="Doe",
            email="john@example.com",
        )
        customer = self.handler.handle_create(create_command)
        self.received_events.clear()

        remove_command = RemoveCustomerAddressCommand(
            customer_id=customer.customer_id,
            address_id=9999,
        )
        self.handler.handle_remove_address(remove_command)

        self.assertEqual(len(self.received_events), 0)
