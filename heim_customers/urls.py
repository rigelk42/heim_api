from django.urls import path

from .views import get_customers

urlpatterns = [
    path("api/customers/", get_customers, name="get_customers"),
]
