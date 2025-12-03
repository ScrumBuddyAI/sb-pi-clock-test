"""Application orchestration and lifecycle management for DeskClock.

This module is responsible for:
- Bootstrapping the PySide6 QApplication
- Measuring and reporting startup time
- Creating and displaying the main window
- Managing the Qt event loop lifecycle

Domain logic and UI implementation details are kept separate from this layer.
"""

from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING, Callable

from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow


def _create_default_window() -> QMainWindow:
    """Create the default MainWindow instance.

    This factory function is used when no custom window factory is provided.
    It imports MainWindow here to avoid circular imports and to allow
    the UI layer to be swapped out for testing.

    Returns:
        A new MainWindow instance configured for kiosk display.
    """
    from deskclock.ui.main_window import MainWindow

    return MainWindow()


def run(
    *,
    window_factory: Callable[[], QMainWindow] | None = None,
) -> int:
    """Run the DeskClock application.

    This function orchestrates the complete application lifecycle:
    1. Records startup timestamp for performance measurement
    2. Creates and configures the Qt application instance
    3. Instantiates the main window (via factory for flexibility)
    4. Shows the window and processes events until visible
    5. Reports startup timing to console
    6. Runs the Qt event loop until application exit

    The window_factory parameter enables dependency injection for testing
    and future service integration. When services need to be passed to
    the main window, a factory can be provided that creates a properly
    configured window instance.

    Args:
        window_factory: Optional callable that returns a QMainWindow instance.
            If None, creates a standard MainWindow. Use this to inject
            dependencies or provide mock windows for testing.

    Returns:
        Exit code from the Qt event loop: 0 for normal exit, non-zero for errors.

    Example:
        # Default usage
        exit_code = run()

        # With custom window factory (for testing or dependency injection)
        def create_window():
            window = MainWindow()
            window.set_time_service(my_time_service)
            return window
        exit_code = run(window_factory=create_window)
    """
    # Record startup time immediately for accurate measurement
    start_time = time.perf_counter()

    # Create the Qt application instance
    # QT_QPA_PLATFORM environment variable is automatically respected by Qt
    # for headless/offscreen operation (e.g., QT_QPA_PLATFORM=offscreen)
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("DeskClock")
    app.setApplicationVersion("0.1.0")

    # Create the main window using the provided factory or default
    if window_factory is not None:
        window = window_factory()
    else:
        window = _create_default_window()

    # Show the window
    window.show()

    # Process pending events to ensure the window is actually rendered
    # This gives us an accurate measurement of time-to-visible
    app.processEvents()

    # Record time after window is visible and report startup duration
    visible_time = time.perf_counter()
    startup_ms = (visible_time - start_time) * 1000
    print(f"DeskClock startup time: {startup_ms:.0f}ms")

    # Run the Qt event loop until the application exits
    return app.exec()
