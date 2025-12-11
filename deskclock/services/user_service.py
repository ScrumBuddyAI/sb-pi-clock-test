"""User management service.

This module provides the UserService which encapsulates all business
logic for user management operations. It enforces business rules and
coordinates between the domain and infrastructure layers.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from deskclock.domain.user import User
from deskclock.domain.enums import UserRole, UserStatus
from deskclock.infrastructure.user_repository import UserRepository


@dataclass
class UserServiceError:
    """Error result from a user service operation.

    Attributes:
        message: Human-readable error message.
        code: Error code for programmatic handling.
    """

    message: str
    code: str


@dataclass
class UserServiceResult:
    """Result of a user service operation.

    Attributes:
        success: Whether the operation succeeded.
        user: The affected user, if applicable.
        error: Error details if the operation failed.
    """

    success: bool
    user: Optional[User] = None
    error: Optional[UserServiceError] = None


class UserService:
    """Service for user management operations.

    This service provides methods for all user management use cases,
    including listing, creating, updating, and managing user roles
    and statuses. It enforces business rules such as:
    - Cannot remove the last active admin
    - Email addresses must be unique
    - Users cannot change their own role (enforced at UI level)

    Example:
        repository = UserRepository()
        service = UserService(repository)

        # List all users
        users = service.get_all_users()

        # Invite a new user
        result = service.invite_user("John Doe", "john@example.com", UserRole.USER)
        if result.success:
            print(f"Invited user: {result.user.name}")
    """

    def __init__(self, repository: Optional[UserRepository] = None) -> None:
        """Initialize the user service.

        Args:
            repository: User repository instance. Creates default if not provided.
        """
        self._repository = repository or UserRepository()

    def get_all_users(self) -> list[User]:
        """Get all users.

        Returns:
            List of all users, ordered by creation date (newest first).
        """
        return self._repository.get_all()

    def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user's unique identifier.

        Returns:
            The user if found, None otherwise.
        """
        return self._repository.get_by_id(user_id)

    def search_users(self, query: str) -> list[User]:
        """Search users by name or email.

        Args:
            query: Search query string.

        Returns:
            List of matching users.
        """
        return self._repository.search(query)

    def filter_by_role(self, role: UserRole) -> list[User]:
        """Filter users by role.

        Args:
            role: The role to filter by.

        Returns:
            List of users with the specified role.
        """
        return self._repository.filter_by_role(role)

    def filter_by_status(self, status: UserStatus) -> list[User]:
        """Filter users by status.

        Args:
            status: The status to filter by.

        Returns:
            List of users with the specified status.
        """
        return self._repository.filter_by_status(status)

    def invite_user(
        self,
        name: str,
        email: str,
        role: UserRole = UserRole.USER,
    ) -> UserServiceResult:
        """Invite a new user.

        Creates a new user with PENDING status. In a real application,
        this would also send an invitation email.

        Args:
            name: User's display name.
            email: User's email address.
            role: Initial role for the user.

        Returns:
            Result with the created user or error details.
        """
        # Validate email uniqueness
        existing = self._repository.get_by_email(email)
        if existing:
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message=f"A user with email {email} already exists",
                    code="EMAIL_EXISTS",
                ),
            )

        # Create user with pending status
        try:
            user = User(
                name=name.strip(),
                email=email.strip().lower(),
                role=role,
                status=UserStatus.PENDING,
            )
            self._repository.add(user)
            return UserServiceResult(success=True, user=user)
        except ValueError as e:
            return UserServiceResult(
                success=False,
                error=UserServiceError(message=str(e), code="VALIDATION_ERROR"),
            )

    def change_role(self, user_id: UUID, new_role: UserRole) -> UserServiceResult:
        """Change a user's role.

        Enforces the business rule that there must always be at least
        one active admin.

        Args:
            user_id: The user's unique identifier.
            new_role: The new role to assign.

        Returns:
            Result with the updated user or error details.
        """
        user = self._repository.get_by_id(user_id)
        if not user:
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="User not found",
                    code="USER_NOT_FOUND",
                ),
            )

        # Check if this would remove the last active admin
        if (
            user.role == UserRole.ADMIN
            and new_role != UserRole.ADMIN
            and user.status == UserStatus.ACTIVE
            and self._repository.count_active_admins() <= 1
        ):
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="Cannot change role: this is the last active admin",
                    code="LAST_ADMIN",
                ),
            )

        user.set_role(new_role)
        self._repository.update(user)
        return UserServiceResult(success=True, user=user)

    def activate_user(self, user_id: UUID) -> UserServiceResult:
        """Activate a user account.

        Args:
            user_id: The user's unique identifier.

        Returns:
            Result with the updated user or error details.
        """
        user = self._repository.get_by_id(user_id)
        if not user:
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="User not found",
                    code="USER_NOT_FOUND",
                ),
            )

        user.activate()
        self._repository.update(user)
        return UserServiceResult(success=True, user=user)

    def deactivate_user(self, user_id: UUID) -> UserServiceResult:
        """Deactivate a user account.

        Enforces the business rule that there must always be at least
        one active admin.

        Args:
            user_id: The user's unique identifier.

        Returns:
            Result with the updated user or error details.
        """
        user = self._repository.get_by_id(user_id)
        if not user:
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="User not found",
                    code="USER_NOT_FOUND",
                ),
            )

        # Check if this would remove the last active admin
        if (
            user.role == UserRole.ADMIN
            and user.status == UserStatus.ACTIVE
            and self._repository.count_active_admins() <= 1
        ):
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="Cannot deactivate: this is the last active admin",
                    code="LAST_ADMIN",
                ),
            )

        user.deactivate()
        self._repository.update(user)
        return UserServiceResult(success=True, user=user)

    def toggle_status(self, user_id: UUID) -> UserServiceResult:
        """Toggle a user's active/disabled status.

        Active users become disabled, disabled/pending users become active.

        Args:
            user_id: The user's unique identifier.

        Returns:
            Result with the updated user or error details.
        """
        user = self._repository.get_by_id(user_id)
        if not user:
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="User not found",
                    code="USER_NOT_FOUND",
                ),
            )

        if user.status == UserStatus.ACTIVE:
            return self.deactivate_user(user_id)
        else:
            return self.activate_user(user_id)

    def update_user(
        self,
        user_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> UserServiceResult:
        """Update user details.

        Args:
            user_id: The user's unique identifier.
            name: New name, or None to keep current.
            email: New email, or None to keep current.

        Returns:
            Result with the updated user or error details.
        """
        user = self._repository.get_by_id(user_id)
        if not user:
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="User not found",
                    code="USER_NOT_FOUND",
                ),
            )

        # Check email uniqueness if changing email
        if email and email.lower() != user.email.lower():
            existing = self._repository.get_by_email(email)
            if existing:
                return UserServiceResult(
                    success=False,
                    error=UserServiceError(
                        message=f"A user with email {email} already exists",
                        code="EMAIL_EXISTS",
                    ),
                )
            user.email = email.strip().lower()

        if name:
            user.name = name.strip()

        try:
            self._repository.update(user)
            return UserServiceResult(success=True, user=user)
        except ValueError as e:
            return UserServiceResult(
                success=False,
                error=UserServiceError(message=str(e), code="VALIDATION_ERROR"),
            )

    def delete_user(self, user_id: UUID) -> UserServiceResult:
        """Delete a user.

        Enforces the business rule that there must always be at least
        one active admin.

        Args:
            user_id: The user's unique identifier.

        Returns:
            Result indicating success or error details.
        """
        user = self._repository.get_by_id(user_id)
        if not user:
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="User not found",
                    code="USER_NOT_FOUND",
                ),
            )

        # Check if this would remove the last active admin
        if (
            user.role == UserRole.ADMIN
            and user.status == UserStatus.ACTIVE
            and self._repository.count_active_admins() <= 1
        ):
            return UserServiceResult(
                success=False,
                error=UserServiceError(
                    message="Cannot delete: this is the last active admin",
                    code="LAST_ADMIN",
                ),
            )

        self._repository.delete(user_id)
        return UserServiceResult(success=True, user=user)
