"""User domain entity.

This module defines the User entity which represents a user account
in the application. Users can have different roles and statuses
that affect their access and capabilities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from deskclock.domain.enums import UserRole, UserStatus


@dataclass
class User:
    """A user account in the application.

    Users are identified by a unique ID and have associated profile
    information, role, and status. The role determines permissions
    while status determines access ability.

    Attributes:
        id: Unique identifier for the user.
        name: User's display name.
        email: User's email address (unique).
        role: User's role determining permissions.
        status: User's account status.
        created_at: When the user account was created.
        last_login: When the user last logged in, or None if never.
    """

    name: str
    email: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate user data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("User name cannot be empty")
        if not self.email or not self.email.strip():
            raise ValueError("User email cannot be empty")
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    @property
    def is_admin(self) -> bool:
        """Check if the user has admin role."""
        return self.role == UserRole.ADMIN

    @property
    def is_active(self) -> bool:
        """Check if the user account is active."""
        return self.status == UserStatus.ACTIVE

    @property
    def can_access(self) -> bool:
        """Check if the user can access the application."""
        return self.status.can_access

    def activate(self) -> None:
        """Activate the user account."""
        self.status = UserStatus.ACTIVE

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.status = UserStatus.DISABLED

    def set_role(self, role: UserRole) -> None:
        """Set the user's role.

        Args:
            role: The new role to assign.
        """
        self.role = role

    def record_login(self) -> None:
        """Record the current time as the last login."""
        self.last_login = datetime.now()
