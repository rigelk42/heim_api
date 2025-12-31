"""Serializers for the Payments bounded context.

This module contains functions to serialize domain models
to dictionary representations for API responses.
"""

from payments.domain.models import Payment


def serialize_payment(payment: Payment) -> dict:
    """Serialize a Payment to a dictionary.

    Args:
        payment: The Payment instance to serialize.

    Returns:
        A dictionary containing the payment's data.
    """
    return {
        "payment_id": str(payment.payment_id),
        "transaction_id": str(payment.transaction_id),
        "payment_method": payment.payment_method,
        "payment_method_display": payment.get_payment_method_display(),
        "amount": str(payment.amount),
        "status": payment.status,
        "status_display": payment.get_status_display(),
        "reference_number": payment.reference_number,
        "notes": payment.notes,
        "is_completed": payment.is_completed,
        "is_refundable": payment.is_refundable,
        "created_at": payment.created_at.isoformat(),
        "updated_at": payment.updated_at.isoformat(),
    }
