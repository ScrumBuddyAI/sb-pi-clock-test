"""Users management page.

This module provides the UsersPage component which displays and manages
user accounts. It uses Brunelly design system components for consistent
styling and follows the admin/settings page layout pattern.

The page provides:
- User list with sortable columns
- Search functionality
- Per-row actions (edit, toggle status)
- Invite new user action
- Role and status display using chips
"""

from datetime import datetime
from typing import Any, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
)

from deskclock.domain.user import User
from deskclock.domain.enums import UserRole, UserStatus
from deskclock.services.user_service import UserService
from deskclock.ui.brunelly import (
    BrunellyPageLayout,
    BrunellyTable,
    BrunellyTableModel,
    BrunellyTextInput,
    BrunellyBanner,
    BrunellyEmptyState,
    BannerVariant,
    TableColumn,
)
from deskclock.ui.brunelly.theme import ColorPalette, Spacing, TypographyScale


class UsersTableModel(BrunellyTableModel):
    """Table model for displaying user data.

    Provides data for the users table including name, email, role,
    status, and timestamps. Supports custom rendering for role and
    status columns using chips.
    """

    def __init__(
        self,
        users: Optional[list[User]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the users table model.

        Args:
            users: Initial list of users to display.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._users: list[User] = users or []
        self._columns = [
            TableColumn(key="name", header="Name", min_width=150),
            TableColumn(key="email", header="Email", min_width=200),
            TableColumn(key="role", header="Role", width=100),
            TableColumn(key="status", header="Status", width=100),
            TableColumn(key="created_at", header="Created", width=140),
            TableColumn(key="last_login", header="Last Login", width=140),
        ]

    def columns(self) -> list[TableColumn]:
        """Return column configurations."""
        return self._columns

    def row_count(self) -> int:
        """Return the number of users."""
        return len(self._users)

    def get_value(self, row: int, column_key: str) -> Any:
        """Get the value for a cell.

        Args:
            row: Row index.
            column_key: Column key identifier.

        Returns:
            Cell value formatted for display.
        """
        if row >= len(self._users):
            return ""

        user = self._users[row]

        if column_key == "name":
            return user.name
        elif column_key == "email":
            return user.email
        elif column_key == "role":
            return user.role.display_name
        elif column_key == "status":
            return user.status.display_name
        elif column_key == "created_at":
            return self._format_datetime(user.created_at)
        elif column_key == "last_login":
            return self._format_datetime(user.last_login) if user.last_login else "Never"
        return ""

    def get_row_data(self, row: int) -> Optional[User]:
        """Get the User object for a row.

        Args:
            row: Row index.

        Returns:
            The User object, or None if invalid row.
        """
        if 0 <= row < len(self._users):
            return self._users[row]
        return None

    def set_users(self, users: list[User]) -> None:
        """Update the users list.

        Args:
            users: New list of users to display.
        """
        self._users = users
        self.refresh()

    def _format_datetime(self, dt: datetime) -> str:
        """Format a datetime for display.

        Args:
            dt: Datetime to format.

        Returns:
            Formatted date string.
        """
        now = datetime.now()
        diff = now - dt

        # Show relative time for recent dates
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                if minutes == 0:
                    return "Just now"
                return f"{minutes}m ago"
            return f"{hours}h ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        else:
            return dt.strftime("%b %d, %Y")


class UsersPage(QWidget):
    """Users management page with Brunelly design.

    Displays a list of users with search, sorting, and per-row actions.
    Uses the Brunelly page layout pattern with header, search bar, and
    data table.

    Signals:
        user_invited: Emitted when the invite button is clicked.
        user_selected: Emitted when a user row is selected.
        user_edit_requested: Emitted when edit is requested for a user.
        user_status_toggled: Emitted when status toggle is requested.
        user_role_changed: Emitted when role change is requested.

    Example:
        service = UserService()
        page = UsersPage(service)
        page.user_invited.connect(show_invite_dialog)
    """

    user_invited = Signal()
    user_selected = Signal(object)  # User object
    user_edit_requested = Signal(object)  # User object
    user_status_toggled = Signal(object)  # User object
    user_role_changed = Signal(object, object)  # User object, new role

    def __init__(
        self,
        user_service: Optional[UserService] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the users page.

        Args:
            user_service: User service for data operations.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._service = user_service or UserService()
        self._current_search = ""
        self._banner: Optional[BrunellyBanner] = None

        self._setup_ui()
        self._connect_signals()
        self._load_users()

    def _setup_ui(self) -> None:
        """Set up the page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Page layout with header
        self._page_layout = BrunellyPageLayout(
            title="Users",
            subtitle="Manage who can access your project and control their roles.",
            primary_action_text="Invite User",
            primary_action_callback=self._on_invite_clicked,
        )

        # Content container
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(Spacing.BASE)

        # Banner placeholder
        self._banner_container = QVBoxLayout()
        self._banner_container.setContentsMargins(0, 0, 0, 0)
        content_layout.addLayout(self._banner_container)

        # Search bar
        search_row = QHBoxLayout()
        search_row.setSpacing(Spacing.MD)

        self._search_input = BrunellyTextInput(
            placeholder="Search users by name or email..."
        )
        self._search_input.setMinimumWidth(300)
        self._search_input.setMaximumWidth(400)
        search_row.addWidget(self._search_input)
        search_row.addStretch()

        # User count label
        self._count_label = QLabel()
        self._count_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_500};
                font-size: {TypographyScale.BODY_SMALL.font_size}px;
            }}
        """)
        search_row.addWidget(self._count_label)

        content_layout.addLayout(search_row)

        # Users table
        self._table_model = UsersTableModel()
        self._table = BrunellyTable()
        self._table.set_model(self._table_model)
        self._table.setMinimumHeight(400)

        # Enable context menu for row actions
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        content_layout.addWidget(self._table)

        # Empty state (hidden initially)
        self._empty_state = BrunellyEmptyState(
            icon="\U0001F465",  # People emoji
            title="No users yet",
            message="Get started by inviting your first team member.",
            action_text="Invite User",
            action_callback=self._on_invite_clicked,
        )
        self._empty_state.hide()
        content_layout.addWidget(self._empty_state)

        # No results state (hidden initially)
        self._no_results_state = BrunellyEmptyState(
            icon="\U0001F50D",  # Magnifying glass emoji
            title="No results found",
            message="Try adjusting your search terms.",
        )
        self._no_results_state.hide()
        content_layout.addWidget(self._no_results_state)

        self._page_layout.set_content(content)
        layout.addWidget(self._page_layout)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self._search_input.value_changed.connect(self._on_search_changed)
        self._table.row_selected.connect(self._on_row_selected)
        self._table.row_double_clicked.connect(self._on_row_double_clicked)
        self._table.customContextMenuRequested.connect(self._show_context_menu)

    def _load_users(self) -> None:
        """Load users from the service."""
        if self._current_search:
            users = self._service.search_users(self._current_search)
        else:
            users = self._service.get_all_users()

        self._update_display(users)

    def _update_display(self, users: list[User]) -> None:
        """Update the display with the given users.

        Args:
            users: List of users to display.
        """
        self._table_model.set_users(users)

        # Update count label
        total = len(self._service.get_all_users())
        showing = len(users)

        if self._current_search:
            self._count_label.setText(f"Showing {showing} of {total} users")
        else:
            self._count_label.setText(f"{total} users")

        # Show/hide empty states
        if total == 0:
            self._table.hide()
            self._no_results_state.hide()
            self._empty_state.show()
        elif showing == 0:
            self._table.hide()
            self._empty_state.hide()
            self._no_results_state.show()
        else:
            self._empty_state.hide()
            self._no_results_state.hide()
            self._table.show()

    def _show_banner(
        self,
        message: str,
        variant: BannerVariant = BannerVariant.SUCCESS,
        auto_dismiss: bool = True,
    ) -> None:
        """Show a notification banner.

        Args:
            message: Banner message.
            variant: Banner style variant.
            auto_dismiss: Whether to auto-dismiss after a delay.
        """
        # Remove existing banner
        if self._banner:
            self._banner.deleteLater()

        self._banner = BrunellyBanner(
            message=message,
            variant=variant,
            dismissible=True,
            auto_dismiss_ms=5000 if auto_dismiss else 0,
        )
        self._banner_container.addWidget(self._banner)

    @Slot()
    def _on_invite_clicked(self) -> None:
        """Handle invite button click."""
        self.user_invited.emit()

    @Slot(str)
    def _on_search_changed(self, query: str) -> None:
        """Handle search input change.

        Args:
            query: Search query string.
        """
        self._current_search = query.strip()
        self._load_users()

    @Slot(int)
    def _on_row_selected(self, row: int) -> None:
        """Handle row selection.

        Args:
            row: Selected row index.
        """
        user = self._table_model.get_row_data(row)
        if user:
            self.user_selected.emit(user)

    @Slot(int)
    def _on_row_double_clicked(self, row: int) -> None:
        """Handle row double-click.

        Args:
            row: Double-clicked row index.
        """
        user = self._table_model.get_row_data(row)
        if user:
            self.user_edit_requested.emit(user)

    @Slot()
    def _show_context_menu(self, position) -> None:
        """Show context menu for row actions.

        Args:
            position: Menu position.
        """
        index = self._table.indexAt(position)
        if not index.isValid():
            return

        user = self._table_model.get_row_data(index.row())
        if not user:
            return

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {ColorPalette.NEUTRAL_0};
                border: 1px solid {ColorPalette.NEUTRAL_200};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {ColorPalette.NEUTRAL_100};
            }}
        """)

        # Edit action
        edit_action = menu.addAction("Edit User")
        edit_action.triggered.connect(lambda: self.user_edit_requested.emit(user))

        menu.addSeparator()

        # Role actions
        role_menu = menu.addMenu("Change Role")
        for role in UserRole:
            role_action = role_menu.addAction(role.display_name)
            role_action.setCheckable(True)
            role_action.setChecked(user.role == role)
            role_action.triggered.connect(
                lambda checked, r=role: self._on_role_action(user, r)
            )

        menu.addSeparator()

        # Status toggle
        if user.status == UserStatus.ACTIVE:
            status_action = menu.addAction("Deactivate User")
        else:
            status_action = menu.addAction("Activate User")
        status_action.triggered.connect(lambda: self._on_toggle_status(user))

        menu.exec(self._table.viewport().mapToGlobal(position))

    def _on_role_action(self, user: User, new_role: UserRole) -> None:
        """Handle role change action.

        Args:
            user: The user to update.
            new_role: The new role to assign.
        """
        if user.role != new_role:
            self.user_role_changed.emit(user, new_role)

    def _on_toggle_status(self, user: User) -> None:
        """Handle status toggle action.

        Args:
            user: The user to toggle status for.
        """
        self.user_status_toggled.emit(user)

    # Public methods for external control

    def refresh(self) -> None:
        """Refresh the users list."""
        self._load_users()

    def show_success(self, message: str) -> None:
        """Show a success banner.

        Args:
            message: Success message to display.
        """
        self._show_banner(message, BannerVariant.SUCCESS)

    def show_error(self, message: str) -> None:
        """Show an error banner.

        Args:
            message: Error message to display.
        """
        self._show_banner(message, BannerVariant.ERROR, auto_dismiss=False)

    def get_selected_user(self) -> Optional[User]:
        """Get the currently selected user.

        Returns:
            The selected user, or None if no selection.
        """
        return self._table.get_selected_data()
