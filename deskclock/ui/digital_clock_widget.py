"""Digital clock widget for displaying time in large, legible format.

This module contains the DigitalClockWidget which displays time text
in a large, high-contrast format suitable for desk-distance viewing
on 21-27" monitors.

The widget is designed for smooth updates without flicker by providing
a simple text update method that doesn't recreate widgets or layouts.
Time formatting logic is handled externally by the domain layer.

Font Size Guidelines for Different Resolutions:
    - 1920x1080 (Full HD): 180-220px (default 200px)
    - 1280x720 (HD): 120-160px
    - 1024x768 (XGA): 100-130px
    - 800x480 (RPi 7" display): 70-90px

These sizes are optimized for desk-distance viewing (60-80 cm) and
ensure the time dominates the display as the primary focal element.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

# Default font size optimized for Full HD (1920x1080) displays at
# desk-distance viewing (60-80 cm). For other resolutions, pass a
# custom font_size to the widget constructor.
_DEFAULT_FONT_SIZE = 200

# Font family preference list for digital clock display.
# Prioritizes fonts with clear, legible digits and good rendering
# across different platforms. Falls back to system sans-serif.
# On Raspberry Pi, DejaVu Sans and Noto Sans are commonly available.
_FONT_FAMILIES = [
    "Roboto",  # Clean, modern, excellent digit rendering
    "SF Pro Display",  # macOS system font
    "Segoe UI",  # Windows system font
    "DejaVu Sans",  # Linux/RPi default with good coverage
    "Noto Sans",  # Cross-platform fallback
    "Liberation Sans",  # Linux fallback
    "sans-serif",  # Ultimate fallback
]

# Color constants matching the main window styling
_TEXT_COLOR = "#FFFFFF"

# Letter spacing as a percentage of font size for improved digit separation
# Helps prevent digits from appearing cramped at large sizes
_LETTER_SPACING_PERCENT = 2


class DigitalClockWidget(QWidget):
    """Widget displaying time in large digital format.

    A high-contrast widget designed to show the current time as a large,
    legible digital display. The widget composes a QLabel internally and
    provides a simple interface for updating the displayed time without
    recreating widgets or layouts.

    The widget is designed for:
    - Clear visibility at desk viewing distances (60-80 cm)
    - Smooth updates without flicker on resource-constrained hardware
    - High contrast display suitable for always-on use
    - Future extensibility (seconds display can be enabled)

    The widget does not contain any time logic - it simply displays
    whatever text is passed to update_time(). Time retrieval and
    formatting should be handled by the domain layer.

    Example:
        widget = DigitalClockWidget(font_size=200)
        widget.update_time("14:35")  # Display "14:35"

    Attributes:
        font_size: The font size in pixels for the time display.
        show_seconds: Whether seconds display is enabled (for future use).
    """

    def __init__(
        self,
        *,
        font_size: int = _DEFAULT_FONT_SIZE,
        show_seconds: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the digital clock widget.

        Args:
            font_size: Font size in pixels for the time display.
                Defaults to 200px, optimized for desk-distance viewing.
            show_seconds: Whether seconds should be displayed. Currently
                stored for future use but does not affect display.
                The actual format is controlled by the text passed to
                update_time().
            parent: Optional parent widget for Qt's ownership hierarchy.
        """
        super().__init__(parent)
        self._font_size = font_size
        self._show_seconds = show_seconds
        self._time_label: QLabel

        self._setup_ui()
        self._configure_font()
        self._apply_styling()

    def _setup_ui(self) -> None:
        """Set up the widget's internal layout and components.

        Creates a vertical layout with the time label centered both
        horizontally and vertically within the widget's bounds.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create the time display label
        self._time_label = QLabel()
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set size policy to allow the label to expand and fill available space
        # while maintaining its centered position
        self._time_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )

        # Center the label in the layout
        layout.addWidget(self._time_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set minimum size to prevent layout collapse
        # Based on approximate dimensions for "00:00" at default font size
        self.setMinimumSize(self._font_size * 3, self._font_size)

    def _configure_font(self) -> None:
        """Configure the font for optimal time display.

        Sets up a large sans-serif font with good digit rendering,
        optimized for legibility on Raspberry Pi displays and smooth
        updates without visible jank.
        """
        font = QFont()

        # Set font family with fallbacks
        # QFont accepts a comma-separated family list
        font.setFamilies(_FONT_FAMILIES)

        # Set size for desk-distance visibility
        font.setPixelSize(self._font_size)

        # Use medium weight for improved visibility at desk distance
        # Slightly bolder than normal for better legibility on varied displays
        font.setWeight(QFont.Weight.Medium)

        # Disable kerning for consistent digit spacing
        # This prevents visual "jumping" when digits change
        font.setKerning(False)

        # Enable antialiasing for smoother font rendering
        # Important for good appearance on Raspberry Pi GPU
        font.setStyleStrategy(
            QFont.StyleStrategy.PreferAntialias
            | QFont.StyleStrategy.PreferQuality
        )

        # Set letter spacing for improved digit separation at large sizes
        letter_spacing = self._font_size * _LETTER_SPACING_PERCENT / 100
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter_spacing)

        self._time_label.setFont(font)

    def _apply_styling(self) -> None:
        """Apply visual styling to the widget.

        Configures high-contrast colors suitable for always-on display.
        The widget background is transparent to allow the parent's
        background to show through.
        """
        # Make widget background transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Style the time label with high contrast colors
        self._time_label.setStyleSheet(f"""
            QLabel {{
                color: {_TEXT_COLOR};
                background-color: transparent;
            }}
        """)

    def update_time(self, display_text: str) -> None:
        """Update the displayed time text.

        This method provides a smooth update mechanism that simply
        changes the label text without recreating widgets or layouts.
        This minimizes CPU usage and prevents flicker on each update.

        The method does not validate or format the input - it displays
        exactly what is passed. Time formatting should be handled by
        the domain layer before calling this method.

        Args:
            display_text: The formatted time string to display
                (e.g., "14:35" or "14:35:42").
        """
        self._time_label.setText(display_text)

    @property
    def font_size(self) -> int:
        """Get the current font size in pixels.

        Returns:
            The font size used for the time display.
        """
        return self._font_size

    @property
    def show_seconds(self) -> bool:
        """Get whether seconds display is enabled.

        Note: This property is stored for future use. The actual
        display format is controlled by the text passed to update_time().

        Returns:
            True if seconds display is enabled, False otherwise.
        """
        return self._show_seconds

    @property
    def current_text(self) -> str:
        """Get the currently displayed time text.

        Useful for testing and debugging to verify the displayed value.

        Returns:
            The current text shown in the time label.
        """
        return self._time_label.text()
