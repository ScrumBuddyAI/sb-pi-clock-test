"""Main window implementation for DeskClock.

This module contains the primary application window which displays
the clock interface in full-screen, frameless kiosk mode.

The window integrates the DigitalClockWidget as its primary focal element,
coordinated by a DigitalClockController that manages time updates. All time
retrieval and formatting logic remains in the domain layer, with the window
responsible only for UI concerns and component lifecycle management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent, QShowEvent
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from deskclock.ui.digital_clock_widget import DigitalClockWidget

if TYPE_CHECKING:
    from deskclock.app.clock_controller import DigitalClockController
    from deskclock.domain.time_service import TimeServiceProtocol

# Color constants for high-contrast kiosk display
# These values are optimized for always-on displays and OLED screens
_BACKGROUND_COLOR = "#000000"  # Pure black background
_TEXT_COLOR = "#FFFFFF"  # White text for maximum contrast


class MainWindow(QMainWindow):
    """Main application window for DeskClock.

    A full-screen, frameless window designed for kiosk-style display
    on Raspberry Pi. Displays a large digital clock as the primary
    focal element with high-contrast styling suitable for always-on use.

    The window is configured with:
    - Frameless mode (no title bar or window borders)
    - Stay-on-top behavior for kiosk operation
    - Full-screen display on the primary monitor
    - Dark background with light text for readability
    - Automatic clock updates managed by the controller

    This class focuses purely on UI concerns and lifecycle management.
    Time retrieval and formatting are handled by the injected time service
    through the controller, maintaining clean architecture separation.

    Attributes:
        clock_widget: The digital clock widget displaying the current time.
    """

    def __init__(
        self,
        *,
        time_service: TimeServiceProtocol | None = None,
        clock_widget: DigitalClockWidget | None = None,
        show_seconds: bool = False,
    ) -> None:
        """Initialize the main window.

        Configures the window for full-screen, frameless display
        with high-contrast styling suitable for always-on use.
        Sets up the digital clock as the primary focal element.

        Args:
            time_service: Optional time service for clock updates.
                If not provided, a default TimeService is created.
            clock_widget: Optional pre-configured clock widget.
                If not provided, a default DigitalClockWidget is created.
            show_seconds: Whether to display seconds in the time.
                Only used when creating the default controller.
        """
        super().__init__()

        self._show_seconds = show_seconds
        self._controller: DigitalClockController | None = None

        # Create or use provided clock widget
        self._clock_widget = clock_widget or DigitalClockWidget(
            show_seconds=show_seconds
        )

        # Store or create time service for controller setup
        self._time_service = time_service

        self._configure_window()
        self._setup_ui()
        self._apply_styling()
        self._setup_controller()

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
        the digital clock widget centered both horizontally and
        vertically within the window.
        """
        # Create central widget container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create vertical layout for central content
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add clock widget to layout with vertical centering
        # Using stretch items to center the clock vertically
        layout.addStretch(1)
        layout.addWidget(
            self._clock_widget, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addStretch(1)

    def _apply_styling(self) -> None:
        """Apply high-contrast visual styling for kiosk display.

        Uses Qt stylesheets to configure colors optimized for always-on
        display at desk viewing distance. The dark background with light
        text provides high contrast and is suitable for both LCD and
        OLED displays.
        """
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {_BACKGROUND_COLOR};
            }}
            QWidget {{
                background-color: {_BACKGROUND_COLOR};
                color: {_TEXT_COLOR};
            }}
        """)

    def _setup_controller(self) -> None:
        """Set up the clock controller for automatic time updates.

        Creates the controller that coordinates between the time service
        and the clock widget. The controller is not started here - it
        will be started when the window is shown.
        """
        # Import here to avoid circular imports
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.domain.time_service import TimeService

        # Use provided time service or create default
        time_service = self._time_service or TimeService()

        self._controller = DigitalClockController(
            time_service,
            self._clock_widget,
            show_seconds=self._show_seconds,
        )

    @property
    def clock_widget(self) -> DigitalClockWidget:
        """Get the digital clock widget.

        Returns:
            The clock widget displaying the current time.
        """
        return self._clock_widget

    def showEvent(self, event: QShowEvent) -> None:
        """Handle window show events to start clock updates.

        Starts the clock controller when the window becomes visible,
        ensuring the display shows the current time immediately.

        Args:
            event: The show event.
        """
        super().showEvent(event)
        if self._controller is not None:
            self._controller.start()

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
        or programmatic close). It ensures the clock controller is stopped
        and the application terminates cleanly.

        Args:
            event: The close event to handle.
        """
        # Stop the clock controller to clean up the timer
        if self._controller is not None:
            self._controller.stop()

        # Accept the close event to allow the window to close
        # When the last window closes, the Qt event loop will exit
        # and the application will terminate cleanly
        event.accept()
