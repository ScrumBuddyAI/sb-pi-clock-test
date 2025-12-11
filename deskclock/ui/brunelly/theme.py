"""Brunelly Design System Theme and Design Tokens.

This module defines all design tokens for the Brunelly visual design system,
including colors, typography, spacing, borders, and shadows. These tokens
ensure visual consistency across all UI components.

Design tokens are organized into logical groups:
- Colors: Primary, neutral, semantic, and component-specific colors
- Typography: Font families, sizes, weights, and line heights
- Spacing: Consistent spacing scale based on 4px base unit
- Borders: Border widths, radii, and styles
- Shadows: Elevation levels for depth

All values are defined as constants for type safety and easy refactoring.
"""

from dataclasses import dataclass
from enum import Enum


class ColorPalette:
    """Core color palette for the Brunelly design system.

    Colors are organized by semantic meaning and use case.
    All colors use hex format for Qt stylesheet compatibility.
    """

    # Primary brand colors
    PRIMARY_50 = "#EFF6FF"
    PRIMARY_100 = "#DBEAFE"
    PRIMARY_200 = "#BFDBFE"
    PRIMARY_300 = "#93C5FD"
    PRIMARY_400 = "#60A5FA"
    PRIMARY_500 = "#3B82F6"  # Main primary
    PRIMARY_600 = "#2563EB"
    PRIMARY_700 = "#1D4ED8"
    PRIMARY_800 = "#1E40AF"
    PRIMARY_900 = "#1E3A8A"

    # Neutral grays
    NEUTRAL_0 = "#FFFFFF"
    NEUTRAL_50 = "#F9FAFB"
    NEUTRAL_100 = "#F3F4F6"
    NEUTRAL_200 = "#E5E7EB"
    NEUTRAL_300 = "#D1D5DB"
    NEUTRAL_400 = "#9CA3AF"
    NEUTRAL_500 = "#6B7280"
    NEUTRAL_600 = "#4B5563"
    NEUTRAL_700 = "#374151"
    NEUTRAL_800 = "#1F2937"
    NEUTRAL_900 = "#111827"

    # Semantic colors - Success
    SUCCESS_50 = "#ECFDF5"
    SUCCESS_100 = "#D1FAE5"
    SUCCESS_300 = "#6EE7B7"
    SUCCESS_500 = "#10B981"
    SUCCESS_600 = "#059669"
    SUCCESS_700 = "#047857"

    # Semantic colors - Warning
    WARNING_50 = "#FFFBEB"
    WARNING_100 = "#FEF3C7"
    WARNING_300 = "#FCD34D"
    WARNING_500 = "#F59E0B"
    WARNING_600 = "#D97706"
    WARNING_700 = "#B45309"

    # Semantic colors - Error
    ERROR_50 = "#FEF2F2"
    ERROR_100 = "#FEE2E2"
    ERROR_300 = "#FCA5A5"
    ERROR_500 = "#EF4444"
    ERROR_600 = "#DC2626"
    ERROR_700 = "#B91C1C"

    # Semantic colors - Info
    INFO_50 = "#EFF6FF"
    INFO_100 = "#DBEAFE"
    INFO_300 = "#93C5FD"
    INFO_500 = "#3B82F6"
    INFO_600 = "#2563EB"
    INFO_700 = "#1D4ED8"


class StatusColor(Enum):
    """Colors for user status indicators."""

    ACTIVE = ("#ECFDF5", "#059669", "#047857")  # bg, text, border
    DISABLED = ("#F3F4F6", "#6B7280", "#9CA3AF")
    PENDING = ("#FFFBEB", "#D97706", "#F59E0B")


class RoleColor(Enum):
    """Colors for user role indicators."""

    ADMIN = ("#FEF2F2", "#DC2626", "#EF4444")  # bg, text, border
    USER = ("#EFF6FF", "#2563EB", "#3B82F6")


@dataclass(frozen=True)
class Typography:
    """Typography specifications for text elements.

    Attributes:
        font_size: Size in pixels
        font_weight: CSS-style weight (400=normal, 500=medium, 600=semibold, 700=bold)
        line_height: Line height multiplier
    """

    font_size: int
    font_weight: int
    line_height: float


class TypographyScale:
    """Typography scale for the Brunelly design system.

    Uses a consistent scale with appropriate weights for hierarchy.
    Font family defaults to system fonts for optimal rendering.
    """

    # Font family stack - system fonts for native feel
    FONT_FAMILY = (
        '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, '
        '"Helvetica Neue", Arial, sans-serif'
    )

    # Heading styles
    HEADING_1 = Typography(font_size=24, font_weight=600, line_height=1.25)
    HEADING_2 = Typography(font_size=20, font_weight=600, line_height=1.3)
    HEADING_3 = Typography(font_size=16, font_weight=600, line_height=1.4)

    # Body styles
    BODY_LARGE = Typography(font_size=16, font_weight=400, line_height=1.5)
    BODY = Typography(font_size=14, font_weight=400, line_height=1.5)
    BODY_SMALL = Typography(font_size=13, font_weight=400, line_height=1.5)

    # UI element styles
    LABEL = Typography(font_size=14, font_weight=500, line_height=1.4)
    CAPTION = Typography(font_size=12, font_weight=400, line_height=1.4)
    BUTTON = Typography(font_size=14, font_weight=500, line_height=1.0)
    CHIP = Typography(font_size=12, font_weight=500, line_height=1.0)


class Spacing:
    """Spacing scale based on 4px base unit.

    Provides consistent spacing values for margins, padding, and gaps.
    """

    NONE = 0
    XS = 4
    SM = 8
    MD = 12
    BASE = 16
    LG = 24
    XL = 32
    XXL = 48
    XXXL = 64

    # Component-specific spacing
    PAGE_PADDING = 32
    CARD_PADDING = 24
    FORM_GAP = 16
    TABLE_CELL_PADDING_H = 16
    TABLE_CELL_PADDING_V = 12
    BUTTON_PADDING_H = 16
    BUTTON_PADDING_V = 8
    CHIP_PADDING_H = 8
    CHIP_PADDING_V = 4
    INPUT_PADDING_H = 12
    INPUT_PADDING_V = 8


class BorderRadius:
    """Border radius values for rounded corners."""

    NONE = 0
    SM = 4
    MD = 6
    LG = 8
    XL = 12
    FULL = 9999  # For pill shapes


class BorderWidth:
    """Border width values."""

    NONE = 0
    DEFAULT = 1
    MEDIUM = 2


class Shadow:
    """Box shadow definitions for elevation levels."""

    NONE = "none"
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    DEFAULT = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)"


class Transition:
    """Transition duration values for animations."""

    FAST = 150  # milliseconds
    DEFAULT = 200
    SLOW = 300


class BrunellyTheme:
    """Central access point for all Brunelly design tokens.

    This class provides a unified interface to access all design tokens
    and helper methods for generating Qt stylesheets.

    Example:
        theme = BrunellyTheme()
        color = theme.colors.PRIMARY_500
        spacing = theme.spacing.BASE
    """

    colors = ColorPalette
    typography = TypographyScale
    spacing = Spacing
    radius = BorderRadius
    border = BorderWidth
    shadow = Shadow
    transition = Transition
    status_colors = StatusColor
    role_colors = RoleColor

    @classmethod
    def get_font_style(cls, typography: Typography) -> str:
        """Generate Qt stylesheet font properties from typography spec.

        Args:
            typography: Typography specification to convert.

        Returns:
            QString-compatible font style declaration.
        """
        return (
            f"font-size: {typography.font_size}px; "
            f"font-weight: {typography.font_weight};"
        )

    @classmethod
    def get_status_colors(cls, status: str) -> tuple[str, str, str]:
        """Get colors for a user status.

        Args:
            status: Status name (active, disabled, pending).

        Returns:
            Tuple of (background_color, text_color, border_color).
        """
        status_map = {
            "active": StatusColor.ACTIVE.value,
            "disabled": StatusColor.DISABLED.value,
            "pending": StatusColor.PENDING.value,
        }
        return status_map.get(status.lower(), StatusColor.DISABLED.value)

    @classmethod
    def get_role_colors(cls, role: str) -> tuple[str, str, str]:
        """Get colors for a user role.

        Args:
            role: Role name (admin, user).

        Returns:
            Tuple of (background_color, text_color, border_color).
        """
        role_map = {
            "admin": RoleColor.ADMIN.value,
            "user": RoleColor.USER.value,
        }
        return role_map.get(role.lower(), RoleColor.USER.value)
