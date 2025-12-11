"""UI pages for DeskClock.

This package contains full page/view components that compose multiple
UI elements into complete user interfaces. Pages typically correspond
to navigation destinations in the application.
"""

from deskclock.ui.pages.users_page import UsersPage
from deskclock.ui.pages.user_dialogs import (
    InviteUserDialog,
    EditUserDialog,
    ChangeRoleDialog,
    ToggleStatusDialog,
)

__all__ = [
    "UsersPage",
    "InviteUserDialog",
    "EditUserDialog",
    "ChangeRoleDialog",
    "ToggleStatusDialog",
]
