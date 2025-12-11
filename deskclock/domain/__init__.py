"""Domain layer for DeskClock.

This package contains core domain entities and value objects that represent
the business concepts of the application. Domain objects are independent
of infrastructure concerns like databases or UI frameworks.
"""

from deskclock.domain.enums import UserRole, UserStatus
from deskclock.domain.user import User

__all__ = [
    "User",
    "UserRole",
    "UserStatus",
]
