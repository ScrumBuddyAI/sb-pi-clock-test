"""Brunelly Design System for DeskClock.

This package provides a cohesive set of UI components following the Brunelly
visual design language. All components are built on PySide6/Qt and designed
for consistency, accessibility, and maintainability.

The design system includes:
- Theme: Design tokens for colors, typography, spacing, and borders
- Buttons: Primary, secondary, tertiary, and icon button variants
- Tables: Data tables with headers, rows, sorting, and selection
- Forms: Text inputs, selects, and validation components
- Chips: Role and status badges with semantic coloring
- Dialogs: Modal dialog system for forms and confirmations
- Notifications: Banners, toasts, and inline error messages

Usage:
    from deskclock.ui.brunelly import (
        BrunellyTheme,
        BrunellyButton,
        BrunellyTable,
        BrunellyTextInput,
        BrunellyChip,
        BrunellyDialog,
        BrunellyBanner,
    )
"""

from deskclock.ui.brunelly.theme import BrunellyTheme
from deskclock.ui.brunelly.buttons import (
    BrunellyButton,
    BrunellyIconButton,
    ButtonVariant,
)
from deskclock.ui.brunelly.tables import (
    BrunellyTable,
    BrunellyTableModel,
    TableColumn,
)
from deskclock.ui.brunelly.forms import (
    BrunellyTextInput,
    BrunellySelect,
    BrunellyFormField,
)
from deskclock.ui.brunelly.chips import (
    BrunellyChip,
    ChipVariant,
)
from deskclock.ui.brunelly.dialogs import (
    BrunellyDialog,
    BrunellyConfirmDialog,
)
from deskclock.ui.brunelly.notifications import (
    BrunellyBanner,
    BrunellyInlineError,
    BannerVariant,
)
from deskclock.ui.brunelly.layouts import (
    BrunellyPageLayout,
    BrunellyCard,
    BrunellyEmptyState,
)

__all__ = [
    # Theme
    "BrunellyTheme",
    # Buttons
    "BrunellyButton",
    "BrunellyIconButton",
    "ButtonVariant",
    # Tables
    "BrunellyTable",
    "BrunellyTableModel",
    "TableColumn",
    # Forms
    "BrunellyTextInput",
    "BrunellySelect",
    "BrunellyFormField",
    # Chips
    "BrunellyChip",
    "ChipVariant",
    # Dialogs
    "BrunellyDialog",
    "BrunellyConfirmDialog",
    # Notifications
    "BrunellyBanner",
    "BrunellyInlineError",
    "BannerVariant",
    # Layouts
    "BrunellyPageLayout",
    "BrunellyCard",
    "BrunellyEmptyState",
]
