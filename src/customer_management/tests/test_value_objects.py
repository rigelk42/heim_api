from datetime import datetime
from unittest import TestCase

from customer_management.domain import CustomerId


class CustomerIdGenerationTest(TestCase):
    def test_generate_returns_customer_id_instance(self):
        customer_id = CustomerId.generate()

        self.assertIsInstance(customer_id, CustomerId)

    def test_generate_creates_14_character_id(self):
        customer_id = CustomerId.generate()

        self.assertEqual(len(customer_id.value), 14)

    def test_generate_starts_with_c_prefix(self):
        customer_id = CustomerId.generate()

        self.assertTrue(customer_id.value.startswith("C"))

    def test_generate_with_specific_timestamp(self):
        # Monday, December 29, 2025 at 14:35:00.532000
        timestamp = datetime(2025, 12, 29, 14, 35, 0, 532000)

        customer_id = CustomerId.generate(timestamp)

        # C + 25 (year) + 363 (day) + A (Monday) + 14 (hour) + 35 (min) + 532 (µs)
        self.assertEqual(customer_id.value, "C25363A1435532")

    def test_generate_weekday_letters(self):
        # Test all weekdays (Monday=A through Sunday=G)
        weekday_tests = [
            (datetime(2025, 12, 29, 12, 0, 0, 0), "A"),  # Monday
            (datetime(2025, 12, 30, 12, 0, 0, 0), "B"),  # Tuesday
            (datetime(2025, 12, 31, 12, 0, 0, 0), "C"),  # Wednesday
            (datetime(2026, 1, 1, 12, 0, 0, 0), "D"),  # Thursday
            (datetime(2026, 1, 2, 12, 0, 0, 0), "E"),  # Friday
            (datetime(2026, 1, 3, 12, 0, 0, 0), "F"),  # Saturday
            (datetime(2026, 1, 4, 12, 0, 0, 0), "G"),  # Sunday
        ]

        for timestamp, expected_letter in weekday_tests:
            customer_id = CustomerId.generate(timestamp)
            # Weekday letter is at position 6 (after C + YY + DDD)
            actual_letter = customer_id.value[6]
            weekday_name = timestamp.strftime("%A")
            self.assertEqual(
                actual_letter,
                expected_letter,
                f"Expected {expected_letter} for {weekday_name}, got {actual_letter}",
            )

    def test_generate_pads_day_of_year(self):
        # January 1st should be day 001
        timestamp = datetime(2025, 1, 1, 12, 0, 0, 0)

        customer_id = CustomerId.generate(timestamp)

        # Day of year is at positions 3-5
        day_of_year = customer_id.value[3:6]
        self.assertEqual(day_of_year, "001")

    def test_generate_pads_hour(self):
        # 9 AM should be 09
        timestamp = datetime(2025, 6, 15, 9, 30, 0, 0)

        customer_id = CustomerId.generate(timestamp)

        # Hour is at positions 7-8
        hour = customer_id.value[7:9]
        self.assertEqual(hour, "09")

    def test_generate_pads_minute(self):
        # 5 minutes should be 05
        timestamp = datetime(2025, 6, 15, 12, 5, 0, 0)

        customer_id = CustomerId.generate(timestamp)

        # Minute is at positions 9-10
        minute = customer_id.value[9:11]
        self.assertEqual(minute, "05")

    def test_generate_pads_microseconds(self):
        # 5000 microseconds should be 005 (first 3 digits)
        timestamp = datetime(2025, 6, 15, 12, 30, 0, 5000)

        customer_id = CustomerId.generate(timestamp)

        # Microseconds is at positions 11-13
        microseconds = customer_id.value[11:14]
        self.assertEqual(microseconds, "005")

    def test_generate_uses_current_time_when_no_timestamp(self):
        now = datetime.now()
        customer_id = CustomerId.generate()

        # Extract year from ID
        year = int(customer_id.value[1:3])

        self.assertEqual(year, now.year % 100)


class CustomerIdValidationTest(TestCase):
    def test_valid_customer_id_accepted(self):
        customer_id = CustomerId("C25363A1435532")

        self.assertEqual(customer_id.value, "C25363A1435532")

    def test_invalid_prefix_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            CustomerId("X25363A1435532")

        self.assertIn("Invalid customer ID format", str(context.exception))

    def test_invalid_length_raises_value_error(self):
        with self.assertRaises(ValueError):
            CustomerId("C25363A143553")  # Too short (13 chars)

        with self.assertRaises(ValueError):
            CustomerId("C25363A14355321")  # Too long (15 chars)

    def test_invalid_weekday_letter_raises_value_error(self):
        with self.assertRaises(ValueError):
            CustomerId("C25363H1435532")  # H is not valid (only A-G)

    def test_non_numeric_components_raise_value_error(self):
        with self.assertRaises(ValueError):
            CustomerId("C2536XA1435532")  # X in day of year

    def test_lowercase_prefix_raises_value_error(self):
        with self.assertRaises(ValueError):
            CustomerId("c25363A1435532")

    def test_lowercase_weekday_raises_value_error(self):
        with self.assertRaises(ValueError):
            CustomerId("C25363a1435532")


class CustomerIdStringRepresentationTest(TestCase):
    def test_str_returns_value(self):
        customer_id = CustomerId("C25363A1435532")

        self.assertEqual(str(customer_id), "C25363A1435532")

    def test_generated_id_str_matches_value(self):
        customer_id = CustomerId.generate()

        self.assertEqual(str(customer_id), customer_id.value)


class CustomerIdImmutabilityTest(TestCase):
    def test_customer_id_is_frozen(self):
        customer_id = CustomerId("C25363A1435532")

        with self.assertRaises(AttributeError):
            customer_id.value = "C25363B1435532"
