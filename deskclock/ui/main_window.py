"""Main window implementation for DeskClock.

This module contains the primary application window which displays
the clock interface in full-screen, frameless kiosk mode.
"""

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Main application window for DeskClock.

    A full-screen, frameless window designed for kiosk-style display
    on Raspberry Pi. Displays the clock interface and handles user
    input for application control.

    This class focuses purely on UI concerns. Application logic,
    time services, and configuration are injected or accessed through
    the application orchestration layer.
    """

    def __init__(self) -> None:
        """Initialize the main window.

        Configures the window for full-screen, frameless display
        with high-contrast styling suitable for always-on use.
        """
        super().__init__()
        # Stub implementation - will be replaced in Step 3
        # with full window configuration and placeholder content
        self.setWindowTitle("DeskClock")
