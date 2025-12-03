"""Tests for the MainWindow UI component.

These tests validate that the MainWindow can be instantiated and
configured correctly in headless environments without raising exceptions.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


class MockTimeService:
    """Mock time service for testing MainWindow behavior."""

    def __init__(self, fixed_time: datetime | None = None) -> None:
        """Initialize with an optional fixed time."""
        self._fixed_time = fixed_time or datetime(2024, 6, 15, 14, 35, 0)

    def get_now(self) -> datetime:
        """Return the fixed test time."""
        return self._fixed_time

    def format_time(self, dt: datetime, *, show_seconds: bool = False) -> str:
        """Format time in test-friendly way."""
        if show_seconds:
            return dt.strftime("%H:%M:%S")
        return dt.strftime("%H:%M")


class TestMainWindowInstantiation:
    """Tests for MainWindow instantiation and basic configuration."""

    def test_main_window_can_be_instantiated(self, qapp: QApplication) -> None:
        """Test that MainWindow can be instantiated without errors.

        This verifies the basic construction of the window including
        window flags, layout setup, and styling application.
        """
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window is not None
        window.close()

    def test_main_window_has_clock_widget(self, qapp: QApplication) -> None:
        """Test that MainWindow has the expected clock widget.

        The clock widget should be accessible via the clock_widget property.
        """
        from deskclock.ui.digital_clock_widget import DigitalClockWidget
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window.clock_widget is not None
        assert isinstance(window.clock_widget, DigitalClockWidget)
        window.close()

    def test_main_window_has_correct_title(self, qapp: QApplication) -> None:
        """Test that MainWindow has the expected window title."""
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window.windowTitle() == "DeskClock"
        window.close()

    def test_main_window_has_central_widget(self, qapp: QApplication) -> None:
        """Test that MainWindow has a central widget configured."""
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window.centralWidget() is not None
        window.close()

    def test_main_window_accepts_custom_time_service(
        self, qapp: QApplication
    ) -> None:
        """Test that MainWindow accepts a custom time service."""
        from deskclock.ui.main_window import MainWindow

        time_service = MockTimeService()
        window = MainWindow(time_service=time_service)
        assert window is not None
        window.close()

    def test_main_window_accepts_custom_clock_widget(
        self, qapp: QApplication
    ) -> None:
        """Test that MainWindow accepts a custom clock widget."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget
        from deskclock.ui.main_window import MainWindow

        custom_widget = DigitalClockWidget(font_size=150)
        window = MainWindow(clock_widget=custom_widget)
        assert window.clock_widget is custom_widget
        window.close()

    def test_main_window_show_seconds_parameter(
        self, qapp: QApplication
    ) -> None:
        """Test that MainWindow accepts show_seconds parameter."""
        from deskclock.ui.main_window import MainWindow

        window = MainWindow(show_seconds=True)
        assert window is not None
        window.close()


class TestMainWindowClockDisplay:
    """Tests for MainWindow clock display functionality."""

    def test_clock_displays_time_when_shown(self, qapp: QApplication) -> None:
        """Test that the clock shows time when the window is displayed."""
        from deskclock.ui.main_window import MainWindow

        time_service = MockTimeService(datetime(2024, 6, 15, 9, 5, 0))
        window = MainWindow(time_service=time_service)
        window.show()

        # The clock should display the formatted time
        assert window.clock_widget.current_text == "09:05"
        window.close()

    def test_clock_displays_seconds_when_enabled(
        self, qapp: QApplication
    ) -> None:
        """Test that the clock shows seconds when show_seconds is True."""
        from deskclock.ui.main_window import MainWindow

        time_service = MockTimeService(datetime(2024, 6, 15, 14, 35, 42))
        window = MainWindow(time_service=time_service, show_seconds=True)
        window.show()

        assert window.clock_widget.current_text == "14:35:42"
        window.close()


class TestMainWindowCleanup:
    """Tests for MainWindow cleanup and shutdown behavior."""

    def test_main_window_closes_without_error(self, qapp: QApplication) -> None:
        """Test that MainWindow can be closed without raising exceptions."""
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        window.show()
        # Closing should not raise any exceptions
        window.close()

    def test_multiple_windows_can_be_created_and_closed(
        self, qapp: QApplication
    ) -> None:
        """Test that multiple MainWindow instances can be created and closed.

        This validates that window creation and cleanup is properly
        managed and doesn't leave resources in an inconsistent state.
        """
        from deskclock.ui.main_window import MainWindow

        windows = [MainWindow() for _ in range(3)]
        for window in windows:
            window.show()
        for window in windows:
            window.close()


class TestMainWindowIntegration:
    """Integration tests for MainWindow with real components."""

    def test_main_window_with_real_time_service(
        self, qapp: QApplication
    ) -> None:
        """Test MainWindow works with the actual TimeService."""
        from deskclock.domain.time_service import TimeService
        from deskclock.ui.main_window import MainWindow

        time_service = TimeService()
        window = MainWindow(time_service=time_service)
        window.show()

        # Clock should display current time in HH:MM format
        text = window.clock_widget.current_text
        assert len(text) == 5
        assert text[2] == ":"

        window.close()

    def test_main_window_import_from_package(self, qapp: QApplication) -> None:
        """Test that MainWindow can be imported from the ui package."""
        from deskclock.ui import MainWindow

        window = MainWindow()
        assert window is not None
        window.close()
