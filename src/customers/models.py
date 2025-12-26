from django.db import models


class Customer(models.Model):
    given_names = models.CharField(max_length=32)
    surnames = models.CharField(max_length=32)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.surnames}, {self.given_names}"

    class Meta:
        ordering = ["surnames", "given_names"]
