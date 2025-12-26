from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from .value_objects import Email, PersonName, PhoneNumber

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Customer(models.Model):
    """
    Aggregate Root for the Customer bounded context.

    All access to Address entities must go through Customer methods.
    """

    id: int
    addresses: RelatedManager[Address]

    given_names = models.CharField(max_length=32)
    surnames = models.CharField(max_length=32)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "customer_management"
        db_table = "customers_customer"
        ordering = ["surnames", "given_names"]

    # --- Value Object accessors ---

    def get_name(self) -> PersonName:
        return PersonName(given_names=self.given_names, surnames=self.surnames)

    def set_name(self, name: PersonName) -> None:
        self.given_names = name.given_names
        self.surnames = name.surnames

    def get_email(self) -> Email:
        return Email(value=self.email)

    def set_email(self, email: Email) -> None:
        self.email = email.value

    def get_phone(self) -> PhoneNumber | None:
        if not self.phone:
            return None
        return PhoneNumber(value=self.phone)

    def set_phone(self, phone: PhoneNumber | None) -> None:
        self.phone = phone.value if phone else ""

    # --- Computed properties ---

    @property
    def full_name(self) -> str:
        return self.get_name().full_name

    def __str__(self):
        return self.get_name().formal_name

    # --- Aggregate Root: Address management ---

    def add_address(
        self,
        address_line_1: str,
        city: str,
        postal_code: str,
        country: str,
        address_line_2: str = "",
        state_province: str = "",
        address_type: str = "home",
        is_primary: bool = False,
    ) -> "Address":
        if is_primary:
            self.addresses.filter(is_primary=True).update(is_primary=False)

        return Address.objects.create(
            customer=self,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state_province=state_province,
            postal_code=postal_code,
            country=country,
            address_type=address_type,
            is_primary=is_primary,
        )

    def get_primary_address(self) -> "Address | None":
        return self.addresses.filter(is_primary=True).first()

    def get_addresses(self):
        return self.addresses.all()

    def remove_address(self, address_id: int) -> bool:
        deleted, _ = self.addresses.filter(id=address_id).delete()
        return deleted > 0


class Address(models.Model):
    """
    Entity within the Customer aggregate.

    Should only be created/modified through Customer aggregate root methods.
    """

    id: int

    ADDRESS_TYPES = [
        ("home", "Home"),
        ("work", "Work"),
        ("billing", "Billing"),
        ("shipping", "Shipping"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    address_line_1 = models.CharField(max_length=128)
    address_line_2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64)
    state_province = models.CharField(max_length=64, blank=True)
    postal_code = models.CharField(max_length=16)
    country = models.CharField(max_length=64)
    address_type = models.CharField(
        max_length=16, choices=ADDRESS_TYPES, default="home"
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "customer_management"
        db_table = "customers_address"
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.country}"
