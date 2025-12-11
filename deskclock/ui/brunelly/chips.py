"""Brunelly Chip/Badge Components.

This module provides chip and badge components following the Brunelly design
system. Chips are used to display categorical information like user roles
and statuses with semantic coloring.

Chip variants:
- Role chips: Admin, User (different colors for each role)
- Status chips: Active, Disabled, Pending (semantic colors)
- Generic chips: Custom colors and labels
"""

from enum import Enum, auto
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout

from deskclock.ui.brunelly.theme import (
    BrunellyTheme,
    ColorPalette,
    Spacing,
    BorderRadius,
    TypographyScale,
)


class ChipVariant(Enum):
    """Chip style variants."""

    DEFAULT = auto()
    ROLE = auto()
    STATUS = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    INFO = auto()


class ChipSize(Enum):
    """Chip size options."""

    SMALL = auto()
    MEDIUM = auto()


def _get_variant_colors(variant: ChipVariant) -> tuple[str, str, str]:
    """Get colors for a chip variant.

    Args:
        variant: Chip variant.

    Returns:
        Tuple of (background_color, text_color, border_color).
    """
    colors = {
        ChipVariant.DEFAULT: (
            ColorPalette.NEUTRAL_100,
            ColorPalette.NEUTRAL_700,
            ColorPalette.NEUTRAL_200,
        ),
        ChipVariant.SUCCESS: (
            ColorPalette.SUCCESS_50,
            ColorPalette.SUCCESS_700,
            ColorPalette.SUCCESS_500,
        ),
        ChipVariant.WARNING: (
            ColorPalette.WARNING_50,
            ColorPalette.WARNING_700,
            ColorPalette.WARNING_500,
        ),
        ChipVariant.ERROR: (
            ColorPalette.ERROR_50,
            ColorPalette.ERROR_700,
            ColorPalette.ERROR_500,
        ),
        ChipVariant.INFO: (
            ColorPalette.INFO_50,
            ColorPalette.INFO_700,
            ColorPalette.INFO_500,
        ),
    }
    return colors.get(
        variant,
        (ColorPalette.NEUTRAL_100, ColorPalette.NEUTRAL_700, ColorPalette.NEUTRAL_200),
    )


class BrunellyChip(QWidget):
    """A styled chip/badge following the Brunelly design system.

    Chips display categorical information with semantic coloring.
    They support role-based and status-based automatic coloring,
    or custom variants.

    Example:
        # Role chip
        admin_chip = BrunellyChip.for_role("admin")

        # Status chip
        active_chip = BrunellyChip.for_status("active")

        # Custom chip
        custom_chip = BrunellyChip(
            text="Custom",
            variant=ChipVariant.INFO,
        )
    """

    def __init__(
        self,
        text: str,
        variant: ChipVariant = ChipVariant.DEFAULT,
        size: ChipSize = ChipSize.MEDIUM,
        custom_colors: Optional[tuple[str, str, str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize a chip.

        Args:
            text: Display text.
            variant: Visual style variant.
            size: Chip size.
            custom_colors: Optional (bg, text, border) color tuple.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._text = text
        self._variant = variant
        self._size = size
        self._custom_colors = custom_colors

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the chip layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._label = QLabel(self._text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        # Set size policy to prevent expansion
        self.setSizePolicy(
            self._label.sizePolicy().horizontalPolicy(),
            self._label.sizePolicy().verticalPolicy(),
        )

    def _apply_styles(self) -> None:
        """Apply Brunelly chip styles."""
        # Determine colors
        if self._custom_colors:
            bg_color, text_color, border_color = self._custom_colors
        else:
            bg_color, text_color, border_color = _get_variant_colors(self._variant)

        # Determine size
        if self._size == ChipSize.SMALL:
            padding_h = Spacing.XS
            padding_v = 2
            font_size = TypographyScale.CAPTION.font_size - 1
        else:
            padding_h = Spacing.CHIP_PADDING_H
            padding_v = Spacing.CHIP_PADDING_V
            font_size = TypographyScale.CHIP.font_size

        self._label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: {BorderRadius.SM}px;
                padding: {padding_v}px {padding_h}px;
                font-size: {font_size}px;
                font-weight: {TypographyScale.CHIP.font_weight};
            }}
        """)

    def set_text(self, text: str) -> None:
        """Update the chip text.

        Args:
            text: New display text.
        """
        self._text = text
        self._label.setText(text)

    @classmethod
    def for_role(
        cls,
        role: str,
        size: ChipSize = ChipSize.MEDIUM,
        parent: Optional[QWidget] = None,
    ) -> "BrunellyChip":
        """Create a chip for a user role.

        Args:
            role: Role name (e.g., "admin", "user").
            size: Chip size.
            parent: Parent widget.

        Returns:
            Configured chip for the role.
        """
        colors = BrunellyTheme.get_role_colors(role)
        display_text = role.capitalize()

        return cls(
            text=display_text,
            variant=ChipVariant.ROLE,
            size=size,
            custom_colors=colors,
            parent=parent,
        )

    @classmethod
    def for_status(
        cls,
        status: str,
        size: ChipSize = ChipSize.MEDIUM,
        parent: Optional[QWidget] = None,
    ) -> "BrunellyChip":
        """Create a chip for a user status.

        Args:
            status: Status name (e.g., "active", "disabled", "pending").
            size: Chip size.
            parent: Parent widget.

        Returns:
            Configured chip for the status.
        """
        colors = BrunellyTheme.get_status_colors(status)
        display_text = status.capitalize()

        return cls(
            text=display_text,
            variant=ChipVariant.STATUS,
            size=size,
            custom_colors=colors,
            parent=parent,
        )


class BrunellyRoleChip(BrunellyChip):
    """Convenience class for role chips.

    Automatically applies role-appropriate styling based on the role name.
    """

    def __init__(
        self,
        role: str,
        size: ChipSize = ChipSize.MEDIUM,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize a role chip.

        Args:
            role: Role name (e.g., "admin", "user").
            size: Chip size.
            parent: Parent widget.
        """
        colors = BrunellyTheme.get_role_colors(role)
        super().__init__(
            text=role.capitalize(),
            variant=ChipVariant.ROLE,
            size=size,
            custom_colors=colors,
            parent=parent,
        )
        self._role = role

    @property
    def role(self) -> str:
        """Get the role name."""
        return self._role


class BrunellyStatusChip(BrunellyChip):
    """Convenience class for status chips.

    Automatically applies status-appropriate styling based on the status name.
    """

    def __init__(
        self,
        status: str,
        size: ChipSize = ChipSize.MEDIUM,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize a status chip.

        Args:
            status: Status name (e.g., "active", "disabled", "pending").
            size: Chip size.
            parent: Parent widget.
        """
        colors = BrunellyTheme.get_status_colors(status)
        super().__init__(
            text=status.capitalize(),
            variant=ChipVariant.STATUS,
            size=size,
            custom_colors=colors,
            parent=parent,
        )
        self._status = status

    @property
    def status(self) -> str:
        """Get the status name."""
        return self._status
