from django.db import models

from heim_utils.utils import generate_customer_id


class Customer(models.Model):
    """
    Represents a customer in the Heim system.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=14, unique=True, editable=False, primary_key=True)
    email = models.EmailField(max_length=256, unique=True)
    first_name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=False)
    last_name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer_id = generate_customer_id()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - {self.customer_id}"
