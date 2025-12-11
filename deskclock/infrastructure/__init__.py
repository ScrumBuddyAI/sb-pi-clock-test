"""Infrastructure layer for DeskClock.

This package contains implementations for data persistence, external
service integrations, and other infrastructure concerns. Components
in this layer implement interfaces defined in the domain or service
layers.
"""

from deskclock.infrastructure.user_repository import UserRepository

__all__ = [
    "UserRepository",
]
