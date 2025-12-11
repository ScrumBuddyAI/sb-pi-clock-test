"""Brunelly Button Components.

This module provides button components following the Brunelly design system.
Buttons come in multiple variants for different use cases and importance levels.

Variants:
- Primary: Main call-to-action buttons (e.g., "Invite User")
- Secondary: Secondary actions (e.g., "Cancel")
- Tertiary: Low-emphasis actions, often text-only
- Danger: Destructive actions (e.g., "Delete")
- Icon: Icon-only buttons for compact actions
"""

from enum import Enum, auto
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QWidget

from deskclock.ui.brunelly.theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    TypographyScale,
)


class ButtonVariant(Enum):
    """Button style variants."""

    PRIMARY = auto()
    SECONDARY = auto()
    TERTIARY = auto()
    DANGER = auto()


class ButtonSize(Enum):
    """Button size options."""

    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()


def _get_size_styles(size: ButtonSize) -> str:
    """Get padding and font size styles for button size.

    Args:
        size: The button size variant.

    Returns:
        Qt stylesheet string for the size.
    """
    sizes = {
        ButtonSize.SMALL: (
            f"padding: {Spacing.XS}px {Spacing.SM}px; "
            f"font-size: {TypographyScale.CAPTION.font_size}px;"
        ),
        ButtonSize.MEDIUM: (
            f"padding: {Spacing.BUTTON_PADDING_V}px {Spacing.BUTTON_PADDING_H}px; "
            f"font-size: {TypographyScale.BUTTON.font_size}px;"
        ),
        ButtonSize.LARGE: (
            f"padding: {Spacing.MD}px {Spacing.LG}px; "
            f"font-size: {TypographyScale.BODY_LARGE.font_size}px;"
        ),
    }
    return sizes[size]


def _get_variant_styles(variant: ButtonVariant) -> str:
    """Get color and border styles for button variant.

    Args:
        variant: The button style variant.

    Returns:
        Qt stylesheet string for the variant including hover/pressed states.
    """
    styles = {
        ButtonVariant.PRIMARY: f"""
            QPushButton {{
                background-color: {ColorPalette.PRIMARY_500};
                color: {ColorPalette.NEUTRAL_0};
                border: none;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.PRIMARY_600};
            }}
            QPushButton:pressed {{
                background-color: {ColorPalette.PRIMARY_700};
            }}
            QPushButton:disabled {{
                background-color: {ColorPalette.NEUTRAL_300};
                color: {ColorPalette.NEUTRAL_500};
            }}
        """,
        ButtonVariant.SECONDARY: f"""
            QPushButton {{
                background-color: {ColorPalette.NEUTRAL_0};
                color: {ColorPalette.NEUTRAL_700};
                border: 1px solid {ColorPalette.NEUTRAL_300};
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.NEUTRAL_50};
                border-color: {ColorPalette.NEUTRAL_400};
            }}
            QPushButton:pressed {{
                background-color: {ColorPalette.NEUTRAL_100};
            }}
            QPushButton:disabled {{
                background-color: {ColorPalette.NEUTRAL_100};
                color: {ColorPalette.NEUTRAL_400};
                border-color: {ColorPalette.NEUTRAL_200};
            }}
        """,
        ButtonVariant.TERTIARY: f"""
            QPushButton {{
                background-color: transparent;
                color: {ColorPalette.PRIMARY_600};
                border: none;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.PRIMARY_50};
            }}
            QPushButton:pressed {{
                background-color: {ColorPalette.PRIMARY_100};
            }}
            QPushButton:disabled {{
                color: {ColorPalette.NEUTRAL_400};
            }}
        """,
        ButtonVariant.DANGER: f"""
            QPushButton {{
                background-color: {ColorPalette.ERROR_500};
                color: {ColorPalette.NEUTRAL_0};
                border: none;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.ERROR_600};
            }}
            QPushButton:pressed {{
                background-color: {ColorPalette.ERROR_700};
            }}
            QPushButton:disabled {{
                background-color: {ColorPalette.NEUTRAL_300};
                color: {ColorPalette.NEUTRAL_500};
            }}
        """,
    }
    return styles[variant]


class BrunellyButton(QPushButton):
    """A styled button following the Brunelly design system.

    Supports multiple variants (primary, secondary, tertiary, danger) and
    sizes (small, medium, large) with consistent styling and accessibility.

    Attributes:
        variant: The visual style variant of the button.
        size: The size of the button.

    Signals:
        Inherits clicked signal from QPushButton.

    Example:
        button = BrunellyButton(
            text="Invite User",
            variant=ButtonVariant.PRIMARY,
        )
        button.clicked.connect(on_invite_clicked)
    """

    def __init__(
        self,
        text: str = "",
        variant: ButtonVariant = ButtonVariant.PRIMARY,
        size: ButtonSize = ButtonSize.MEDIUM,
        icon: Optional[QIcon] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize a Brunelly button.

        Args:
            text: Button label text.
            variant: Visual style variant.
            size: Button size.
            icon: Optional icon to display before text.
            parent: Parent widget.
        """
        super().__init__(text, parent)
        self._variant = variant
        self._size = size

        if icon:
            self.setIcon(icon)

        self._apply_styles()
        self._configure_accessibility()

    def _apply_styles(self) -> None:
        """Apply Brunelly styles based on variant and size."""
        base_styles = f"""
            QPushButton {{
                font-weight: {TypographyScale.BUTTON.font_weight};
                border-radius: {BorderRadius.MD}px;
                {_get_size_styles(self._size)}
            }}
            QPushButton:focus {{
                outline: 2px solid {ColorPalette.PRIMARY_300};
                outline-offset: 2px;
            }}
        """
        variant_styles = _get_variant_styles(self._variant)
        self.setStyleSheet(base_styles + variant_styles)

    def _configure_accessibility(self) -> None:
        """Configure accessibility properties."""
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        if self.text():
            self.setAccessibleName(self.text())

    def set_variant(self, variant: ButtonVariant) -> None:
        """Change the button variant.

        Args:
            variant: New visual style variant.
        """
        self._variant = variant
        self._apply_styles()

    def set_size(self, size: ButtonSize) -> None:
        """Change the button size.

        Args:
            size: New button size.
        """
        self._size = size
        self._apply_styles()


class BrunellyIconButton(QPushButton):
    """An icon-only button for compact actions.

    Used for row actions in tables, toolbar buttons, and other space-constrained
    locations where an icon alone communicates the action.

    The button displays only an icon and requires an accessible name
    for screen reader support.

    Example:
        edit_btn = BrunellyIconButton(
            icon=edit_icon,
            tooltip="Edit user",
            accessible_name="Edit user",
        )
    """

    def __init__(
        self,
        icon: QIcon,
        tooltip: str = "",
        accessible_name: str = "",
        size: int = 32,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize an icon button.

        Args:
            icon: The icon to display.
            tooltip: Tooltip text shown on hover.
            accessible_name: Screen reader accessible name (required for a11y).
            size: Button size in pixels (width and height).
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setIcon(icon)
        self.setFixedSize(size, size)

        if tooltip:
            self.setToolTip(tooltip)

        # Icon size is slightly smaller than button
        icon_size = int(size * 0.6)
        self.setIconSize(
            self.iconSize().scaled(
                icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        self._apply_styles()
        self._configure_accessibility(accessible_name or tooltip)

    def _apply_styles(self) -> None:
        """Apply icon button styles."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: {BorderRadius.SM}px;
                padding: {Spacing.XS}px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.NEUTRAL_100};
            }}
            QPushButton:pressed {{
                background-color: {ColorPalette.NEUTRAL_200};
            }}
            QPushButton:focus {{
                outline: 2px solid {ColorPalette.PRIMARY_300};
                outline-offset: 1px;
            }}
            QPushButton:disabled {{
                opacity: 0.5;
            }}
        """)

    def _configure_accessibility(self, name: str) -> None:
        """Configure accessibility properties.

        Args:
            name: Accessible name for screen readers.
        """
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        if name:
            self.setAccessibleName(name)
