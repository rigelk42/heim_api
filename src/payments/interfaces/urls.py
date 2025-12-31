"""URL configuration for the Payments API."""

from django.urls import path

from .views import (
    PaymentCancelView,
    PaymentCompleteView,
    PaymentDetailView,
    PaymentListCreateView,
    PaymentRefundView,
    PaymentsByTransactionView,
)

app_name = "payments"

urlpatterns = [
    path("", PaymentListCreateView.as_view(), name="payment-list-create"),
    path("<str:payment_id>/", PaymentDetailView.as_view(), name="payment-detail"),
    path(
        "<str:payment_id>/complete/",
        PaymentCompleteView.as_view(),
        name="payment-complete",
    ),
    path(
        "<str:payment_id>/refund/",
        PaymentRefundView.as_view(),
        name="payment-refund",
    ),
    path(
        "<str:payment_id>/cancel/",
        PaymentCancelView.as_view(),
        name="payment-cancel",
    ),
    path(
        "transaction/<str:transaction_id>/",
        PaymentsByTransactionView.as_view(),
        name="payments-by-transaction",
    ),
]
