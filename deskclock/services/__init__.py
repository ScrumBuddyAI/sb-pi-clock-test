"""Service layer for DeskClock.

This package contains application services that orchestrate domain
logic and coordinate between the domain and infrastructure layers.
Services encapsulate business rules and use cases.
"""

from deskclock.services.user_service import UserService

__all__ = [
    "UserService",
]
