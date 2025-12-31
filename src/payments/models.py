"""Re-export domain models for Django compatibility.

This module re-exports models from the domain layer to maintain
Django's expected app structure.
"""

from payments.domain.models import Payment

__all__ = ["Payment"]
