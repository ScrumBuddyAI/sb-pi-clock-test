"""Main window implementation for DeskClock.

This module contains the primary application window which displays
the clock interface in full-screen, frameless kiosk mode.

All visual styling and UI configuration is contained within this module.
No application or domain logic should be added here.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

# Color constants for high-contrast kiosk display
# These values are optimized for always-on displays and OLED screens
_BACKGROUND_COLOR = "#000000"  # Pure black background
_TEXT_COLOR = "#FFFFFF"  # White text for maximum contrast

# Font configuration for desk-distance readability
_PLACEHOLDER_FONT_SIZE = 24


class MainWindow(QMainWindow):
    """Main application window for DeskClock.

    A full-screen, frameless window designed for kiosk-style display
    on Raspberry Pi. Displays the clock interface with high-contrast
    styling suitable for always-on use.

    The window is configured with:
    - Frameless mode (no title bar or window borders)
    - Stay-on-top behavior for kiosk operation
    - Full-screen display on the primary monitor
    - Dark background with light text for readability

    This class focuses purely on UI concerns. Application logic,
    time services, and configuration are injected or accessed through
    the application orchestration layer.

    Attributes:
        placeholder_label: The central label widget that will be replaced
            with the actual clock display in future implementations.
    """

    def __init__(self) -> None:
        """Initialize the main window.

        Configures the window for full-screen, frameless display
        with high-contrast styling suitable for always-on use.
        Sets up the central widget with a placeholder label.
        """
        super().__init__()
        self._configure_window()
        self._setup_ui()
        self._apply_styling()

    def _configure_window(self) -> None:
        """Configure window properties for kiosk-style display.

        Sets window flags for frameless operation and stay-on-top behavior,
        which are essential for kiosk-style deployment on Raspberry Pi.
        """
        self.setWindowTitle("DeskClock")

        # Configure window flags for kiosk mode:
        # - FramelessWindowHint: Remove title bar and window borders
        # - WindowStaysOnTopHint: Keep window above other applications
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        # Set window state to full-screen
        # This ensures the window occupies the entire primary display
        self.setWindowState(Qt.WindowState.WindowFullScreen)

    def _setup_ui(self) -> None:
        """Set up the central widget and layout structure.

        Creates a central widget with a vertical layout containing
        a placeholder label that is centered both horizontally and
        vertically within the window.
        """
        # Create central widget container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create vertical layout for central content
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create placeholder label for future clock display
        self.placeholder_label = QLabel("DeskClock - Time will be displayed here")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add label to layout with vertical centering
        # Using stretch items to center the label vertically
        layout.addStretch(1)
        layout.addWidget(self.placeholder_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)

    def _apply_styling(self) -> None:
        """Apply high-contrast visual styling for kiosk display.

        Uses Qt stylesheets to configure colors and fonts optimized
        for always-on display at desk viewing distance. The dark
        background with light text provides high contrast and is
        suitable for both LCD and OLED displays.
        """
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {_BACKGROUND_COLOR};
            }}
            QWidget {{
                background-color: {_BACKGROUND_COLOR};
                color: {_TEXT_COLOR};
            }}
            QLabel {{
                color: {_TEXT_COLOR};
                font-size: {_PLACEHOLDER_FONT_SIZE}px;
                background-color: transparent;
            }}
        """)

    def showFullScreen(self) -> None:
        """Show the window in full-screen mode.

        Overrides the base implementation to ensure window flags
        are preserved when entering full-screen mode.
        """
        # Ensure window state is set before showing
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        super().showFullScreen()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events for application control.

        Provides keyboard shortcuts for kiosk operation. In a frameless
        full-screen window, the ESC key is the primary method for users
        to exit the application.

        Supported keys:
        - ESC: Close the application and exit cleanly

        Args:
            event: The key press event containing the key that was pressed.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            # Pass unhandled keys to the base implementation
            super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close events for clean application shutdown.

        This method is called when the window is about to close, regardless
        of how the close was initiated (ESC key, Alt+F4, window manager,
        or programmatic close). It ensures the application terminates
        cleanly without zombie processes or uncaught exceptions.

        The close event acceptance causes the window to close, which in turn
        causes the Qt event loop to exit (since this is the only window),
        leading to clean process termination.

        Args:
            event: The close event to handle.
        """
        # Accept the close event to allow the window to close
        # When the last window closes, the Qt event loop will exit
        # and the application will terminate cleanly
        event.accept()
