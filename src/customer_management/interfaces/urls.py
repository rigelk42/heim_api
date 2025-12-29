from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.CustomerListCreateView.as_view(), name="list-create"),
    path("<str:customer_id>/", views.CustomerDetailView.as_view(), name="detail"),
]
