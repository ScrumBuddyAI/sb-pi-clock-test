"""User Management Dialogs.

This module provides dialog components for user management operations
using the Brunelly design system. All dialogs preserve existing business
rules and validation logic while providing a consistent visual design.

Dialogs:
- InviteUserDialog: Invite a new user with name, email, and role
- EditUserDialog: Edit user name and email
- ChangeRoleDialog: Change a user's role with last-admin protection
- ToggleStatusDialog: Activate/deactivate a user with confirmation
"""

import re
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from deskclock.domain.user import User
from deskclock.domain.enums import UserRole, UserStatus
from deskclock.services.user_service import UserService
from deskclock.ui.brunelly import (
    BrunellyDialog,
    BrunellyTextInput,
    BrunellySelect,
    BrunellyFormField,
    BrunellyBanner,
    BannerVariant,
)
from deskclock.ui.brunelly.buttons import ButtonVariant
from deskclock.ui.brunelly.dialogs import DialogSize
from deskclock.ui.brunelly.forms import ValidationState
from deskclock.ui.brunelly.theme import ColorPalette, Spacing, TypographyScale


# Email validation regex pattern
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _validate_email(email: str) -> tuple[bool, str]:
    """Validate email format.

    Args:
        email: Email address to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not email:
        return False, "Email is required"
    if not EMAIL_PATTERN.match(email):
        return False, "Please enter a valid email address"
    return True, ""


def _validate_name(name: str) -> tuple[bool, str]:
    """Validate user name.

    Args:
        name: Name to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not name or not name.strip():
        return False, "Name is required"
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    return True, ""


class InviteUserDialog(BrunellyDialog):
    """Dialog for inviting a new user.

    Provides form fields for name, email, and role selection with
    real-time validation and error display.

    Signals:
        user_invited: Emitted when a user is successfully invited.
                      Contains the UserServiceResult.

    Example:
        dialog = InviteUserDialog(user_service, parent=main_window)
        dialog.user_invited.connect(on_user_invited)
        dialog.exec()
    """

    user_invited = Signal(object)  # UserServiceResult

    def __init__(
        self,
        user_service: UserService,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the invite dialog.

        Args:
            user_service: User service for creating users.
            parent: Parent widget.
        """
        super().__init__(
            title="Invite User",
            size=DialogSize.MEDIUM,
            parent=parent,
        )
        self._service = user_service
        self._setup_form()
        self._setup_actions()

    def _setup_form(self) -> None:
        """Set up the invite form."""
        form = QWidget()
        layout = QVBoxLayout(form)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.BASE)

        # Description
        description = QLabel(
            "Send an invitation to join your project. "
            "They'll receive an email with instructions to get started."
        )
        description.setWordWrap(True)
        description.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_600};
                font-size: {TypographyScale.BODY.font_size}px;
                margin-bottom: {Spacing.SM}px;
            }}
        """)
        layout.addWidget(description)

        # Name field
        self._name_field = BrunellyFormField(
            label="Name",
            required=True,
            helper_text="The user's display name",
        )
        self._name_input = BrunellyTextInput(placeholder="Enter full name")
        self._name_field.set_input(self._name_input)
        self._name_input.value_changed.connect(self._on_name_changed)
        layout.addWidget(self._name_field)

        # Email field
        self._email_field = BrunellyFormField(
            label="Email",
            required=True,
            helper_text="We'll send the invitation to this address",
        )
        self._email_input = BrunellyTextInput(placeholder="email@example.com")
        self._email_field.set_input(self._email_input)
        self._email_input.value_changed.connect(self._on_email_changed)
        layout.addWidget(self._email_field)

        # Role field
        self._role_field = BrunellyFormField(
            label="Role",
            required=True,
        )
        role_options = [(role.value, role.display_name) for role in UserRole]
        self._role_select = BrunellySelect(
            options=role_options,
            initial_value=UserRole.USER.value,
        )
        self._role_field.set_input(self._role_select)
        layout.addWidget(self._role_field)

        # Error banner (hidden initially)
        self._error_banner: Optional[BrunellyBanner] = None
        self._error_container = QVBoxLayout()
        self._error_container.setContentsMargins(0, Spacing.SM, 0, 0)
        layout.addLayout(self._error_container)

        layout.addStretch()
        self.set_content(form)

        # Set initial focus
        self._name_input.setFocus()

    def _setup_actions(self) -> None:
        """Set up dialog action buttons."""
        self.add_action("Cancel", ButtonVariant.SECONDARY, self.reject)
        self._submit_btn = self.add_action(
            "Send Invite", ButtonVariant.PRIMARY, self._on_submit
        )

    def _on_name_changed(self, name: str) -> None:
        """Handle name input change."""
        self._name_field.clear_error()
        self._clear_error_banner()

    def _on_email_changed(self, email: str) -> None:
        """Handle email input change."""
        self._email_field.clear_error()
        self._clear_error_banner()

    def _validate_form(self) -> bool:
        """Validate all form fields.

        Returns:
            True if form is valid.
        """
        is_valid = True

        # Validate name
        name_valid, name_error = _validate_name(self._name_input.get_value())
        if not name_valid:
            self._name_field.set_error(name_error)
            is_valid = False

        # Validate email
        email_valid, email_error = _validate_email(self._email_input.get_value())
        if not email_valid:
            self._email_field.set_error(email_error)
            is_valid = False

        return is_valid

    def _show_error_banner(self, message: str) -> None:
        """Show error banner."""
        self._clear_error_banner()
        self._error_banner = BrunellyBanner(
            message=message,
            variant=BannerVariant.ERROR,
            dismissible=True,
        )
        self._error_container.addWidget(self._error_banner)

    def _clear_error_banner(self) -> None:
        """Clear any existing error banner."""
        if self._error_banner:
            self._error_banner.deleteLater()
            self._error_banner = None

    def _on_submit(self) -> None:
        """Handle form submission."""
        # Clear previous errors
        self._name_field.clear_error()
        self._email_field.clear_error()
        self._clear_error_banner()

        # Validate form
        if not self._validate_form():
            return

        # Get form values
        name = self._name_input.get_value().strip()
        email = self._email_input.get_value().strip()
        role_value = self._role_select.get_value()
        role = UserRole(role_value) if role_value else UserRole.USER

        # Call service
        result = self._service.invite_user(name, email, role)

        if result.success:
            self.user_invited.emit(result)
            self.accept()
        else:
            # Handle specific error codes
            if result.error and result.error.code == "EMAIL_EXISTS":
                self._email_field.set_error(result.error.message)
                self._email_input.set_validation_state(ValidationState.INVALID)
            else:
                error_msg = (
                    result.error.message if result.error else "Failed to invite user"
                )
                self._show_error_banner(error_msg)


class EditUserDialog(BrunellyDialog):
    """Dialog for editing user details.

    Provides form fields for name and email with validation.

    Signals:
        user_updated: Emitted when user is successfully updated.
                      Contains the UserServiceResult.

    Example:
        dialog = EditUserDialog(user, user_service, parent=main_window)
        dialog.user_updated.connect(on_user_updated)
        dialog.exec()
    """

    user_updated = Signal(object)  # UserServiceResult

    def __init__(
        self,
        user: User,
        user_service: UserService,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the edit dialog.

        Args:
            user: User to edit.
            user_service: User service for updates.
            parent: Parent widget.
        """
        super().__init__(
            title="Edit User",
            size=DialogSize.MEDIUM,
            parent=parent,
        )
        self._user = user
        self._service = user_service
        self._setup_form()
        self._setup_actions()

    def _setup_form(self) -> None:
        """Set up the edit form."""
        form = QWidget()
        layout = QVBoxLayout(form)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.BASE)

        # User info header
        info_label = QLabel(f"Editing: {self._user.email}")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_500};
                font-size: {TypographyScale.BODY_SMALL.font_size}px;
                margin-bottom: {Spacing.SM}px;
            }}
        """)
        layout.addWidget(info_label)

        # Name field
        self._name_field = BrunellyFormField(
            label="Name",
            required=True,
        )
        self._name_input = BrunellyTextInput(
            placeholder="Enter full name",
            initial_value=self._user.name,
        )
        self._name_field.set_input(self._name_input)
        self._name_input.value_changed.connect(self._on_name_changed)
        layout.addWidget(self._name_field)

        # Email field
        self._email_field = BrunellyFormField(
            label="Email",
            required=True,
        )
        self._email_input = BrunellyTextInput(
            placeholder="email@example.com",
            initial_value=self._user.email,
        )
        self._email_field.set_input(self._email_input)
        self._email_input.value_changed.connect(self._on_email_changed)
        layout.addWidget(self._email_field)

        # Error banner (hidden initially)
        self._error_banner: Optional[BrunellyBanner] = None
        self._error_container = QVBoxLayout()
        self._error_container.setContentsMargins(0, Spacing.SM, 0, 0)
        layout.addLayout(self._error_container)

        layout.addStretch()
        self.set_content(form)

        # Set initial focus
        self._name_input.setFocus()
        self._name_input.selectAll()

    def _setup_actions(self) -> None:
        """Set up dialog action buttons."""
        self.add_action("Cancel", ButtonVariant.SECONDARY, self.reject)
        self._submit_btn = self.add_action(
            "Save Changes", ButtonVariant.PRIMARY, self._on_submit
        )

    def _on_name_changed(self, name: str) -> None:
        """Handle name input change."""
        self._name_field.clear_error()
        self._clear_error_banner()

    def _on_email_changed(self, email: str) -> None:
        """Handle email input change."""
        self._email_field.clear_error()
        self._clear_error_banner()

    def _validate_form(self) -> bool:
        """Validate all form fields."""
        is_valid = True

        name_valid, name_error = _validate_name(self._name_input.get_value())
        if not name_valid:
            self._name_field.set_error(name_error)
            is_valid = False

        email_valid, email_error = _validate_email(self._email_input.get_value())
        if not email_valid:
            self._email_field.set_error(email_error)
            is_valid = False

        return is_valid

    def _show_error_banner(self, message: str) -> None:
        """Show error banner."""
        self._clear_error_banner()
        self._error_banner = BrunellyBanner(
            message=message,
            variant=BannerVariant.ERROR,
            dismissible=True,
        )
        self._error_container.addWidget(self._error_banner)

    def _clear_error_banner(self) -> None:
        """Clear any existing error banner."""
        if self._error_banner:
            self._error_banner.deleteLater()
            self._error_banner = None

    def _on_submit(self) -> None:
        """Handle form submission."""
        self._name_field.clear_error()
        self._email_field.clear_error()
        self._clear_error_banner()

        if not self._validate_form():
            return

        name = self._name_input.get_value().strip()
        email = self._email_input.get_value().strip()

        # Only pass changed values
        new_name = name if name != self._user.name else None
        new_email = email if email.lower() != self._user.email.lower() else None

        # If nothing changed, just close
        if not new_name and not new_email:
            self.accept()
            return

        result = self._service.update_user(
            self._user.id, name=new_name, email=new_email
        )

        if result.success:
            self.user_updated.emit(result)
            self.accept()
        else:
            if result.error and result.error.code == "EMAIL_EXISTS":
                self._email_field.set_error(result.error.message)
                self._email_input.set_validation_state(ValidationState.INVALID)
            else:
                error_msg = (
                    result.error.message if result.error else "Failed to update user"
                )
                self._show_error_banner(error_msg)


class ChangeRoleDialog(BrunellyDialog):
    """Dialog for changing a user's role.

    Shows current role, allows selection of new role, and warns about
    last-admin constraints.

    Signals:
        role_changed: Emitted when role is successfully changed.
                      Contains the UserServiceResult.

    Example:
        dialog = ChangeRoleDialog(user, new_role, user_service, parent=main_window)
        dialog.role_changed.connect(on_role_changed)
        dialog.exec()
    """

    role_changed = Signal(object)  # UserServiceResult

    def __init__(
        self,
        user: User,
        new_role: UserRole,
        user_service: UserService,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the change role dialog.

        Args:
            user: User to modify.
            new_role: New role to assign.
            user_service: User service for role changes.
            parent: Parent widget.
        """
        super().__init__(
            title="Change Role",
            size=DialogSize.SMALL,
            parent=parent,
        )
        self._user = user
        self._new_role = new_role
        self._service = user_service
        self._setup_content()
        self._setup_actions()

    def _setup_content(self) -> None:
        """Set up the dialog content."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.BASE)

        # User info
        user_label = QLabel(f"User: {self._user.name}")
        user_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_700};
                font-size: {TypographyScale.BODY.font_size}px;
                font-weight: {TypographyScale.LABEL.font_weight};
            }}
        """)
        layout.addWidget(user_label)

        # Role change display
        change_row = QHBoxLayout()
        change_row.setSpacing(Spacing.SM)

        current_label = QLabel(f"Current role: {self._user.role.display_name}")
        current_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_600};
                font-size: {TypographyScale.BODY.font_size}px;
            }}
        """)
        change_row.addWidget(current_label)

        arrow_label = QLabel("\u2192")  # Right arrow
        arrow_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_400};
                font-size: {TypographyScale.BODY.font_size}px;
            }}
        """)
        change_row.addWidget(arrow_label)

        new_label = QLabel(self._new_role.display_name)
        new_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.PRIMARY_600};
                font-size: {TypographyScale.BODY.font_size}px;
                font-weight: {TypographyScale.LABEL.font_weight};
            }}
        """)
        change_row.addWidget(new_label)
        change_row.addStretch()

        layout.addLayout(change_row)

        # Warning for admin demotion
        if (
            self._user.role == UserRole.ADMIN
            and self._new_role != UserRole.ADMIN
            and self._user.status == UserStatus.ACTIVE
        ):
            warning = BrunellyBanner(
                message="Changing this admin to a regular user may affect project management capabilities.",
                variant=BannerVariant.WARNING,
            )
            layout.addWidget(warning)

        # Confirmation message
        confirm_label = QLabel(
            f"Are you sure you want to change {self._user.name}'s role to {self._new_role.display_name}?"
        )
        confirm_label.setWordWrap(True)
        confirm_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_600};
                font-size: {TypographyScale.BODY.font_size}px;
                margin-top: {Spacing.SM}px;
            }}
        """)
        layout.addWidget(confirm_label)

        # Error container
        self._error_banner: Optional[BrunellyBanner] = None
        self._error_container = QVBoxLayout()
        self._error_container.setContentsMargins(0, Spacing.SM, 0, 0)
        layout.addLayout(self._error_container)

        self.set_content(content)

    def _setup_actions(self) -> None:
        """Set up dialog action buttons."""
        self.add_action("Cancel", ButtonVariant.SECONDARY, self.reject)
        self.add_action("Change Role", ButtonVariant.PRIMARY, self._on_submit)

    def _show_error_banner(self, message: str) -> None:
        """Show error banner."""
        if self._error_banner:
            self._error_banner.deleteLater()
        self._error_banner = BrunellyBanner(
            message=message,
            variant=BannerVariant.ERROR,
            dismissible=True,
        )
        self._error_container.addWidget(self._error_banner)

    def _on_submit(self) -> None:
        """Handle role change submission."""
        result = self._service.change_role(self._user.id, self._new_role)

        if result.success:
            self.role_changed.emit(result)
            self.accept()
        else:
            error_msg = (
                result.error.message if result.error else "Failed to change role"
            )
            self._show_error_banner(error_msg)


class ToggleStatusDialog(BrunellyDialog):
    """Dialog for activating or deactivating a user.

    Shows confirmation with appropriate warnings for admin users.

    Signals:
        status_changed: Emitted when status is successfully changed.
                        Contains the UserServiceResult.

    Example:
        dialog = ToggleStatusDialog(user, user_service, parent=main_window)
        dialog.status_changed.connect(on_status_changed)
        dialog.exec()
    """

    status_changed = Signal(object)  # UserServiceResult

    def __init__(
        self,
        user: User,
        user_service: UserService,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the toggle status dialog.

        Args:
            user: User to modify.
            user_service: User service for status changes.
            parent: Parent widget.
        """
        self._user = user
        self._service = user_service
        self._is_activating = user.status != UserStatus.ACTIVE

        title = "Activate User" if self._is_activating else "Deactivate User"
        super().__init__(
            title=title,
            size=DialogSize.SMALL,
            parent=parent,
        )

        self._setup_content()
        self._setup_actions()

    def _setup_content(self) -> None:
        """Set up the dialog content."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.BASE)

        # User info
        user_label = QLabel(f"User: {self._user.name} ({self._user.email})")
        user_label.setWordWrap(True)
        user_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_700};
                font-size: {TypographyScale.BODY.font_size}px;
            }}
        """)
        layout.addWidget(user_label)

        # Current status
        status_label = QLabel(f"Current status: {self._user.status.display_name}")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_500};
                font-size: {TypographyScale.BODY_SMALL.font_size}px;
            }}
        """)
        layout.addWidget(status_label)

        # Warning for deactivating admin
        if not self._is_activating and self._user.role == UserRole.ADMIN:
            warning = BrunellyBanner(
                message="Deactivating this admin may affect project management. "
                "Ensure there is at least one other active admin.",
                variant=BannerVariant.WARNING,
            )
            layout.addWidget(warning)

        # Confirmation message
        if self._is_activating:
            message = f"Are you sure you want to activate {self._user.name}? They will be able to access the project."
        else:
            message = f"Are you sure you want to deactivate {self._user.name}? They will lose access to the project."

        confirm_label = QLabel(message)
        confirm_label.setWordWrap(True)
        confirm_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_600};
                font-size: {TypographyScale.BODY.font_size}px;
                margin-top: {Spacing.SM}px;
            }}
        """)
        layout.addWidget(confirm_label)

        # Error container
        self._error_banner: Optional[BrunellyBanner] = None
        self._error_container = QVBoxLayout()
        self._error_container.setContentsMargins(0, Spacing.SM, 0, 0)
        layout.addLayout(self._error_container)

        self.set_content(content)

    def _setup_actions(self) -> None:
        """Set up dialog action buttons."""
        self.add_action("Cancel", ButtonVariant.SECONDARY, self.reject)

        if self._is_activating:
            self.add_action("Activate", ButtonVariant.PRIMARY, self._on_submit)
        else:
            self.add_action("Deactivate", ButtonVariant.DANGER, self._on_submit)

    def _show_error_banner(self, message: str) -> None:
        """Show error banner."""
        if self._error_banner:
            self._error_banner.deleteLater()
        self._error_banner = BrunellyBanner(
            message=message,
            variant=BannerVariant.ERROR,
            dismissible=True,
        )
        self._error_container.addWidget(self._error_banner)

    def _on_submit(self) -> None:
        """Handle status toggle submission."""
        result = self._service.toggle_status(self._user.id)

        if result.success:
            self.status_changed.emit(result)
            self.accept()
        else:
            error_msg = (
                result.error.message if result.error else "Failed to change status"
            )
            self._show_error_banner(error_msg)
