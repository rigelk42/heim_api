from django.contrib import admin

from customers.domain.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["given_names", "surnames", "email", "phone", "created_at"]
    search_fields = ["given_names", "surnames", "email"]
    list_filter = ["created_at"]
