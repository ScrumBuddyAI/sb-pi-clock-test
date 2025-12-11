"""Domain enumerations for DeskClock.

This module defines enumerations for domain concepts that have a fixed
set of possible values. These enums ensure type safety and consistency
across the application.
"""

from enum import Enum


class UserRole(str, Enum):
    """User role within the application.

    Roles determine the level of access and permissions a user has.
    Inherits from str for easy serialization and comparison.
    """

    ADMIN = "admin"
    USER = "user"

    def __str__(self) -> str:
        """Return the string value of the role."""
        return self.value

    @property
    def display_name(self) -> str:
        """Return a human-readable display name."""
        return self.value.capitalize()


class UserStatus(str, Enum):
    """User account status.

    Status indicates whether a user can access the application and
    the state of their account.
    """

    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"

    def __str__(self) -> str:
        """Return the string value of the status."""
        return self.value

    @property
    def display_name(self) -> str:
        """Return a human-readable display name."""
        return self.value.capitalize()

    @property
    def can_access(self) -> bool:
        """Check if this status allows application access."""
        return self == UserStatus.ACTIVE
