"""User repository implementation.

This module provides an in-memory implementation of user data storage.
In a production application, this would be replaced with a database-backed
implementation (e.g., SQLAlchemy with SQLite).
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from deskclock.domain.user import User
from deskclock.domain.enums import UserRole, UserStatus


class UserRepository:
    """In-memory repository for User entities.

    This implementation stores users in memory for demonstration purposes.
    It provides CRUD operations and query methods for user management.

    In production, this class would implement a repository interface
    and use SQLAlchemy or another ORM for persistence.
    """

    def __init__(self) -> None:
        """Initialize the repository with sample data."""
        self._users: dict[UUID, User] = {}
        self._load_sample_data()

    def _load_sample_data(self) -> None:
        """Load sample users for demonstration."""
        now = datetime.now()

        # Sample users with various roles and statuses
        sample_users = [
            User(
                name="Alice Johnson",
                email="alice@example.com",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                created_at=now - timedelta(days=90),
                last_login=now - timedelta(hours=2),
            ),
            User(
                name="Bob Smith",
                email="bob@example.com",
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                created_at=now - timedelta(days=60),
                last_login=now - timedelta(days=1),
            ),
            User(
                name="Carol Williams",
                email="carol@example.com",
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                created_at=now - timedelta(days=45),
                last_login=now - timedelta(hours=5),
            ),
            User(
                name="David Brown",
                email="david@example.com",
                role=UserRole.USER,
                status=UserStatus.DISABLED,
                created_at=now - timedelta(days=30),
                last_login=now - timedelta(days=15),
            ),
            User(
                name="Eva Martinez",
                email="eva@example.com",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                created_at=now - timedelta(days=20),
                last_login=now - timedelta(minutes=30),
            ),
            User(
                name="Frank Garcia",
                email="frank@example.com",
                role=UserRole.USER,
                status=UserStatus.PENDING,
                created_at=now - timedelta(days=2),
                last_login=None,
            ),
            User(
                name="Grace Lee",
                email="grace@example.com",
                role=UserRole.USER,
                status=UserStatus.PENDING,
                created_at=now - timedelta(hours=12),
                last_login=None,
            ),
        ]

        for user in sample_users:
            self._users[user.id] = user

    def get_all(self) -> list[User]:
        """Get all users.

        Returns:
            List of all users, ordered by creation date (newest first).
        """
        return sorted(
            self._users.values(),
            key=lambda u: u.created_at,
            reverse=True,
        )

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user's unique identifier.

        Returns:
            The user if found, None otherwise.
        """
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address.

        Args:
            email: The email address to search for.

        Returns:
            The user if found, None otherwise.
        """
        email_lower = email.lower()
        for user in self._users.values():
            if user.email.lower() == email_lower:
                return user
        return None

    def add(self, user: User) -> User:
        """Add a new user.

        Args:
            user: The user to add.

        Returns:
            The added user.

        Raises:
            ValueError: If a user with the same email already exists.
        """
        if self.get_by_email(user.email):
            raise ValueError(f"User with email {user.email} already exists")
        self._users[user.id] = user
        return user

    def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: The user with updated data.

        Returns:
            The updated user.

        Raises:
            ValueError: If the user does not exist.
        """
        if user.id not in self._users:
            raise ValueError(f"User with ID {user.id} not found")
        self._users[user.id] = user
        return user

    def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID.

        Args:
            user_id: The user's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def search(self, query: str) -> list[User]:
        """Search users by name or email.

        Args:
            query: Search query string.

        Returns:
            List of users matching the query.
        """
        if not query:
            return self.get_all()

        query_lower = query.lower()
        results = []
        for user in self._users.values():
            if query_lower in user.name.lower() or query_lower in user.email.lower():
                results.append(user)

        return sorted(results, key=lambda u: u.created_at, reverse=True)

    def filter_by_role(self, role: UserRole) -> list[User]:
        """Filter users by role.

        Args:
            role: The role to filter by.

        Returns:
            List of users with the specified role.
        """
        return [u for u in self.get_all() if u.role == role]

    def filter_by_status(self, status: UserStatus) -> list[User]:
        """Filter users by status.

        Args:
            status: The status to filter by.

        Returns:
            List of users with the specified status.
        """
        return [u for u in self.get_all() if u.status == status]

    def count_by_role(self, role: UserRole) -> int:
        """Count users with a specific role.

        Args:
            role: The role to count.

        Returns:
            Number of users with the role.
        """
        return len(self.filter_by_role(role))

    def count_active_admins(self) -> int:
        """Count active admin users.

        Returns:
            Number of active admins.
        """
        return len(
            [
                u
                for u in self._users.values()
                if u.role == UserRole.ADMIN and u.status == UserStatus.ACTIVE
            ]
        )
